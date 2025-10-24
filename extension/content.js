console.log("[KKUTU EXT] content script loaded");

function sendWordToBackground(word) {
    try {
        chrome
            .runtime
            .sendMessage({type: "word", word});
        console.log("[KKUTU EXT] Sent:", word);
    } catch (err) {
        console.error("[KKUTU EXT] send error:", err);
    }
}

// 단어 변화 감시
function startObserver() {
    const target = document.querySelector(".jjo-display.ellipse");
    if (!target) {
        console.warn("[KKUTU EXT] no target found, retrying...");
        setTimeout(startObserver, 1000);
        return;
    }

    console.log("[KKUTU EXT] observer started");

    const observer = new MutationObserver(() => {
        const text = target
            .innerText
            .trim();
        if (text.length > 0) {
            // 괄호 포함된 글자 (예: 라(나))를 그대로 전송
            sendWordToBackground([text]);
        }
    });

    observer.observe(target, {
        childList: true,
        subtree: true,
        characterData: true
    });
}

startObserver();
