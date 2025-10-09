// js/preview_image.js
// Adds the Manual Save button to PiePie Preview Image nodes
// 
// Note: 'js' folder = JavaScript UI extensions, nothing to do with web/internet
// ComfyUI is fully local, no external calls anywhere

import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "PiePieDesign.PreviewImage",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // Only modify our specific node
        if (nodeData.name === "PiePiePreviewImage") {
            
            const onExecuted = nodeType.prototype.onExecuted;
            
            // Capture image data after generation
            nodeType.prototype.onExecuted = function(message) {
                onExecuted?.apply(this, arguments);
                
                // Store images in memory so manual save can grab them later
                if (message?.images) {
                    this.images_data = message.images;
                }
            };
            
            // Add button immediately when node is created
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                onNodeCreated?.apply(this, arguments);
                
                // Button shows up right away, no waiting for first generation
                this.addManualSaveButton();
            };
            
            // Creates the save button widget
            nodeType.prototype.addManualSaveButton = function() {
                // Don't add duplicates
                if (this.manualSaveButton) {
                    return;
                }
                
                const saveButton = this.addWidget("button", "💾 Manual Save", null, () => {
                    this.manualSave();
                });
                
                // Don't save this button in the workflow json
                saveButton.serialize = false;
                this.manualSaveButton = saveButton;
                
                // Resize node to fit the button
                this.setSize(this.computeSize());
            };
            
            // What happens when you click the button
            nodeType.prototype.manualSave = async function() {
                if (!this.images_data || this.images_data.length === 0) {
                    alert("No images to save. Generate something first.");
                    return;
                }
                
                // Grab the current filename prefix
                const filenamePrefixWidget = this.widgets?.find(w => w.name === "filename_prefix");
                const filenamePrefix = filenamePrefixWidget?.value || "";
                
                console.log("[PiePie Manual Save] Saving:", this.images_data);
                console.log("[PiePie Manual Save] Prefix:", filenamePrefix);
                
                try {
                    // Call our backend API to do the actual file copy
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
                        // No alert popup - don't want to be annoying
                    } else {
                        const errorText = await response.text();
                        console.error("[PiePie Manual Save] Failed:", response.statusText, errorText);
                        alert("Save failed. Check console (F12) for details.");
                    }
                } catch (error) {
                    console.error("[PiePie Manual Save] Error:", error);
                    alert("Save error: " + error.message);
                }
            };
        }
    }
});