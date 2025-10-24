console.log("[KKUTU FF EXT] content loaded");

function sendWord(word) {
  try {
    browser.runtime.sendMessage({ type: "word", word });
    console.log("[KKUTU FF EXT] Sent:", word);
  } catch (e) {
    console.error("[KKUTU FF EXT] Send error:", e);
  }
}

function startObserver() {
  const target = document.querySelector(".jjo-display.ellipse");
  if (!target) {
    console.warn("[KKUTU FF EXT] No target found, retrying...");
    setTimeout(startObserver, 1000);
    return;
  }

  console.log("[KKUTU FF EXT] Observer started");

  const observer = new MutationObserver(() => {
    const text = target.innerText.trim();
    if (text.length > 0) sendWord([text]);
  });

  observer.observe(target, { childList: true, subtree: true, characterData: true });
}

startObserver();
