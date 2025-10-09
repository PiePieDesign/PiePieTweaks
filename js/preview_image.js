import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "PiePieDesign.PreviewImage",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "PiePiePreviewImage") {
            
            const onExecuted = nodeType.prototype.onExecuted;
            
            nodeType.prototype.onExecuted = function(message) {
                onExecuted?.apply(this, arguments);
                
                if (message?.images) {
                    this.images_data = message.images;
                }
            };
            
            // add button immediately when node is created instead of after i process the image
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                onNodeCreated?.apply(this, arguments);
                
                this.addManualSaveButton();
            };
            
            nodeType.prototype.addManualSaveButton = function() {
                if (this.manualSaveButton) {
                    return;
                }
                
                const saveButton = this.addWidget("button", "💾 Manual Save", null, () => {
                    this.manualSave();
                });
                
                saveButton.serialize = false; // is this needed? 
                this.manualSaveButton = saveButton;
                
                // Resize node to fit the button
                this.setSize(this.computeSize());
            };
            
            nodeType.prototype.manualSave = async function() {
                if (!this.images_data || this.images_data.length === 0) {
                    alert("No images to save. Generate something first.");
                    return;
                }
                
                // get prefix
                const filenamePrefixWidget = this.widgets?.find(w => w.name === "filename_prefix");
                const filenamePrefix = filenamePrefixWidget?.value || "";
                
                console.log("[PiePie Manual Save] Saving:", this.images_data);
                console.log("[PiePie Manual Save] Prefix:", filenamePrefix);
                
                try {
                    // this is the temp to save logic
                    const response = await api.fetchApi("/piepie_tweaks/manual_save", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            images: this.images_data,
                            filename_prefix: filenamePrefix,
                        }),
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        console.log("[PiePie Manual Save] Success:", result);
                    } else {
                        const errorText = await response.text();
                        console.error("[PiePie Manual Save] Failed:", response.statusText, errorText);
                        alert("Save failed. Check console (F12) for details."); // Is this best practice? I see this done a few ways but will keep this for now.
                    }
                } catch (error) {
                    console.error("[PiePie Manual Save] Error:", error);
                    alert("Save error: " + error.message);
                }
            };
        }
    }
});