let ws = null;

function connectWS() {
    ws = new WebSocket("ws://127.0.0.1:8765/");
    ws.onopen = () => console.log("[BG] Connected to overlay");
    ws.onclose = () => {
        console.log("[BG] Closed, reconnecting...");
        setTimeout(connectWS, 1000);
    };
    ws.onerror = (e) => console.log("[BG] Error", e);
}

connectWS();

// content.js → background.js → overlay.py
chrome
    .runtime
    .onMessage
    .addListener((msg, sender) => {
        if (msg.type === "word" && ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(msg));
            console.log("[BG] Sent to overlay:", msg);
        }
    });
