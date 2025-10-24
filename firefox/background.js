let ws = null;

function connectWS() {
    ws = new WebSocket("ws://127.0.0.1:8765/");
    ws.onopen = () => console.log("[FF-BG] Connected to overlay");
    ws.onclose = () => {
        console.log("[FF-BG] Closed, reconnecting...");
        setTimeout(connectWS, 1000);
    };
    ws.onerror = (e) => console.log("[FF-BG] Error", e);
}

connectWS();

browser
    .runtime
    .onMessage
    .addListener((msg) => {
        if (msg.type === "word" && ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(msg));
            console.log("[FF-BG] Sent to overlay:", msg);
        }
    });
