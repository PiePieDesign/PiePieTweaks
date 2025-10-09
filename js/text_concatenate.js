import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

app.registerExtension({
    name: "PiePieDesign.TextConcatenate",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "PiePieTextConcatenate") {
            
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                onNodeCreated?.apply(this, arguments);
                
                // Rename widget labels for better display
                const delimiterWidget = this.widgets?.find(w => w.name === "delimiter");
                if (delimiterWidget) {
                    delimiterWidget.label = "Delimiter";
                }
                
                const newlineWidget = this.widgets?.find(w => w.name === "newline_after_each");
                if (newlineWidget) {
                    newlineWidget.label = "Newline After Each";
                }
                
                const customDelimWidget = this.widgets?.find(w => w.name === "custom_delimiter");
                if (customDelimWidget) {
                    customDelimWidget.label = "Custom Delimiter";
                }
                
                // Create preview widget to display the processed result
                const previewWidget = ComfyWidgets.STRING(this, "processed_text", ["STRING", { multiline: true }], app).widget;
                previewWidget.inputEl.readOnly = true;
                previewWidget.inputEl.style.opacity = "0.6";
                previewWidget.value = "";
                
                setTimeout(() => {
                    if (previewWidget.inputEl) {
                        previewWidget.inputEl.placeholder = "";
                    }
                }, 10);
                
                this.previewWidget = previewWidget;
                this.setSize(this.computeSize());
            };
            
            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function(message) {
                onExecuted?.apply(this, arguments);
                
                if (this.previewWidget && message?.string) {
                    const result = message.string[0] || "";
                    this.previewWidget.value = result;
                }
            };
            
            const onDrawForeground = nodeType.prototype.onDrawForeground;
            nodeType.prototype.onDrawForeground = function(ctx) {
                onDrawForeground?.apply(this, arguments);
                
                if (this.previewWidget) {
                    const widgetIndex = this.widgets.indexOf(this.previewWidget);
                    if (widgetIndex > 0) {
                        let y = 0;
                        for (let i = 0; i < widgetIndex; i++) {
                            y += this.widgets[i].computedHeight || LiteGraph.NODE_WIDGET_HEIGHT;
                        }
                        
                        ctx.save();
                        ctx.fillStyle = "#AAA";
                        ctx.font = "12px Arial";
                        ctx.fillText("Processed Text:", 15, y - 5);
                        ctx.restore();
                    }
                }
            };
        }
    }
});