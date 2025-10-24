"""Combined LucidFlux node that handles loading, caching and execution."""

from __future__ import annotations

import os
from typing import Dict, Optional, Tuple

import torch
from omegaconf import OmegaConf

import comfy.utils
import folder_paths
import nodes

from . import inference, model_loader_utils
from .src.flux import align_color

# Extracted helpers from supporting modules
tensor2pillist_upscale = model_loader_utils.tensor2pillist_upscale
load_lucidflux_model = inference.load_lucidflux_model
lucidflux_inference = inference.lucidflux_inference
get_cond = inference.get_cond
get_cond_from_embeddings = inference.get_cond_from_embeddings
preprocess_data_cached = inference.preprocess_data_cached
aggressive_cleanup = inference.aggressive_cleanup
wavelet_reconstruction = align_color.wavelet_reconstruction

MAX_SEED = (1 << 31) - 1
LOGGER_PREFIX = "[PiePie LucidFlux]"


def _detect_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda:0")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


device = _detect_device()

weights_lucidflux_current_path = os.path.join(folder_paths.models_dir, "LucidFlux")
if not os.path.exists(weights_lucidflux_current_path):
    os.makedirs(weights_lucidflux_current_path)
folder_paths.add_model_folder_path("LucidFlux", weights_lucidflux_current_path)


class PiePie_Lucidflux:
    """Run LucidFlux inference with cached weights and progress reporting."""

    _model_cache: Dict[str, Tuple[dict, dict]] = {}
    _swinir_cache: Dict[str, dict] = {}
    _redux_cache: Dict[str, dict] = {}

    @classmethod
    def INPUT_TYPES(cls):
        lucidflux_files, swinir_files, prompt_files = cls._list_available_assets()

        return {
            "required": {
                "flux_model": ("MODEL",),
                "LucidFlux": (lucidflux_files,),
                "image": ("IMAGE",),
                "vae": ("VAE",),
                "swinir": (swinir_files,),
                "width": ("INT", {
                    "default": 1024,
                    "min": 64,
                    "max": nodes.MAX_RESOLUTION,
                    "step": 64
                }),
                "height": ("INT", {
                    "default": 1024,
                    "min": 64,
                    "max": nodes.MAX_RESOLUTION,
                    "step": 64
                }),
                "CLIP_VISION": ("CLIP_VISION",),
                "steps": ("INT", {
                    "default": 20,
                    "min": 1,
                    "max": 10000
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": MAX_SEED
                }),
                "cfg": ("FLOAT", {
                    "default": 4.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 0.1,
                    "round": 0.01
                }),
                "use_embeddings": ("BOOLEAN", {"default": True}),
                "prompt_embeddings": (prompt_files,),
                "enable_offload": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "positive": ("CONDITIONING",),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "process"
    CATEGORY = "PiePie"
    DESCRIPTION = "Combined LucidFlux node - loads model and processes images with optional prompt embeddings"

    def process(
        self,
        flux_model,
        LucidFlux: str,
        image: torch.Tensor,
        vae,
        swinir: str,
        width: int,
        height: int,
        CLIP_VISION,
        steps: int,
        seed: int,
        cfg: float,
        use_embeddings: bool = True,
        prompt_embeddings: str = "none",
        enable_offload: bool = False,
        positive=None,
    ):

        LucidFlux_path = folder_paths.get_full_path("LucidFlux", LucidFlux) if LucidFlux != "none" else None

        if LucidFlux_path is None:
            raise ValueError("LucidFlux checkpoint is required")
        if flux_model is None:
            raise ValueError("Flux model is required - connect from CheckpointLoader")

        model_type = self._detect_flux_variant(flux_model)
        print(f"{LOGGER_PREFIX} Detected model type: {model_type}")

        cache_key = f"{LucidFlux_path}_{id(flux_model)}_{model_type}"
        model, state = self._load_or_get_cached_model(cache_key, LucidFlux_path, flux_model, enable_offload, model_type)

        prompt_emb_data = self._load_prompt_embeddings(prompt_embeddings) if use_embeddings else None

        print(f"{LOGGER_PREFIX} Starting LucidFlux processing...")

        swinir_path = folder_paths.get_full_path("LucidFlux", swinir) if swinir != "none" else None
        if swinir_path is None:
            raise ValueError("SwinIR checkpoint is required")

        adjusted_width, adjusted_height = self._snap_dimensions(width, height)

        input_pli_list = tensor2pillist_upscale(image, adjusted_width, adjusted_height)

        if use_embeddings and prompt_emb_data is not None:
            inp_cond = get_cond_from_embeddings(prompt_emb_data, adjusted_height, adjusted_width, device)
        else:
            if positive is None:
                raise ValueError("Either prompt_embeddings (with use_embeddings=True) or positive conditioning is required")
            inp_cond = get_cond(positive, adjusted_height, adjusted_width, device)

        print(f"{LOGGER_PREFIX} Encoding image...")
        condition = preprocess_data_cached(
            self._swinir_cache,
            self._redux_cache,
            state,
            swinir_path,
            CLIP_VISION,
            input_pli_list,
            inp_cond,
            device,
            enable_offload
        )

        pipe = model.get("model")
        dual_condition_branch = model.get("dual_condition_branch")
        offload = model.get("offload", False)

        pbar = comfy.utils.ProgressBar(steps)

        def progress_callback(step, total_steps, img_latent):
            del step, total_steps, img_latent  # Parameters required by API but unused
            pbar.update(1)

        x = lucidflux_inference(
            pipe,
            dual_condition_branch,
            condition,
            cfg,
            steps,
            seed,
            device,
            model.get("is_schnell", False),
            offload,
            progress_callback=progress_callback,
        )

        print(f"{LOGGER_PREFIX} Decoding latents...")

        images = []
        for idx, (latent, cond) in enumerate(zip(x, condition)):
            decoded_image = vae.decode(latent).squeeze(0)

            x1 = decoded_image.clamp(-1, 1).to(device)
            hq = wavelet_reconstruction((x1.permute(2, 0, 1) + 1.0) / 2, cond.get("ci_pre_origin").squeeze(0).to(device))
            hq = hq.clamp(0, 1)
            hq = hq.unsqueeze(0).permute(0, 2, 3, 1)
            images.append(hq)

            del decoded_image, x1, latent
            if idx % 2 == 0:
                aggressive_cleanup()

        output = torch.cat(images, dim=0)

        del x, images, condition
        aggressive_cleanup()

        print(f"{LOGGER_PREFIX} Processing complete")

        return (output,)

    @classmethod
    def _list_available_assets(cls) -> Tuple[Tuple[str, ...], Tuple[str, ...], Tuple[str, ...]]:
        files = folder_paths.get_filename_list("LucidFlux")
        lucidflux = tuple(["none"] + [name for name in files if "lucid" in name.lower()])
        swinir = tuple(["none"] + [name for name in files if "swinir" in name.lower()])
        prompts = tuple(["none"] + [name for name in files if "prompt" in name.lower() or name.endswith(".pt")])
        return lucidflux, swinir, prompts

    def _detect_flux_variant(self, flux_model) -> str:
        is_dev = True
        try:
            if hasattr(flux_model, "model") and hasattr(flux_model.model, "model_config"):
                unet_config = flux_model.model.model_config.unet_config
                if hasattr(unet_config, "get"):
                    is_dev = unet_config.get("guidance_embeds", True)
                elif hasattr(unet_config, "guidance_embeds"):
                    is_dev = unet_config.guidance_embeds
        except Exception:
            print(f"{LOGGER_PREFIX} Could not auto-detect model type, defaulting to flux-dev")
        return "flux-dev" if is_dev else "flux-schnell"

    def _load_or_get_cached_model(
        self,
        cache_key: str,
        checkpoint_path: str,
        flux_model,
        enable_offload: bool,
        model_type: str,
    ) -> Tuple[dict, dict]:
        if cache_key in self._model_cache:
            print(f"{LOGGER_PREFIX} Using cached LucidFlux model")
            return self._model_cache[cache_key]

        origin_dict = {
            "name": model_type,
            "offload": enable_offload,
            "device": "cuda:0",
            "output_dir": folder_paths.get_output_directory(),
            "checkpoint": checkpoint_path,
        }
        args = OmegaConf.create(origin_dict)
        model, state = load_lucidflux_model(args, None, flux_model, device, enable_offload)
        self._model_cache[cache_key] = (model, state)
        return model, state

    def _load_prompt_embeddings(self, prompt_embeddings: str) -> Optional[torch.Tensor]:
        if prompt_embeddings == "none":
            return None

        prompt_emb_path = folder_paths.get_full_path("LucidFlux", prompt_embeddings)
        if prompt_emb_path is None:
            print(f"{LOGGER_PREFIX} Prompt embeddings {prompt_embeddings} not found")
            return None

        print(f"{LOGGER_PREFIX} Loading prompt embeddings from {prompt_emb_path}")
        return torch.load(prompt_emb_path, map_location="cpu", weights_only=False)

    def _snap_dimensions(self, width: int, height: int) -> Tuple[int, int]:
        SWINIR_MULTIPLE = 64
        adjusted_width = max(SWINIR_MULTIPLE, (width // SWINIR_MULTIPLE) * SWINIR_MULTIPLE)
        adjusted_height = max(SWINIR_MULTIPLE, (height // SWINIR_MULTIPLE) * SWINIR_MULTIPLE)

        if adjusted_width != width or adjusted_height != height:
            print(
                f"{LOGGER_PREFIX} SwinIR dimension adjustment: {width}x{height} → {adjusted_width}x{adjusted_height} "
                f"(must be divisible by {SWINIR_MULTIPLE})"
            )

        return adjusted_width, adjusted_height


NODE_CLASS_MAPPINGS = {
    "PiePie_Lucidflux": PiePie_Lucidflux,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PiePie_Lucidflux": "PiePie - Lucidflux",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
