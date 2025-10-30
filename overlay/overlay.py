import sys
import os
import json
import asyncio
import threading
import logging
from collections import defaultdict
from PyQt5 import QtCore, QtWidgets
import websockets


# -----------------------------
# Logging 설정
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("Overlay")


# -----------------------------
# WebSocket 서버
# -----------------------------
async def ws_handler(websocket, path=None):
    async for message in websocket:
        log.info(f"[WS] Word received: {message}")
        try:
            data = json.loads(message)
            word = data.get("word", "")
            if isinstance(word, list):
                word = "".join(map(str, word))
            elif not isinstance(word, str):
                word = str(word)

            log.info(f"[WS] Parsed word: {word}")

            QtCore.QMetaObject.invokeMethod(
                Overlay.instance(),
                "on_word_received_safe",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, word)
            )
        except Exception as e:
            log.error(f"[WS] Error parsing message: {e}")


async def start_ws_server():
    while True:
        try:
            async with websockets.serve(ws_handler, "127.0.0.1", 8765):
                log.info("[WS] WebSocket server started on ws://127.0.0.1:8765")
                await asyncio.Future()
        except Exception as e:
            log.error(f"[WS] Server crashed: {e}")
            await asyncio.sleep(2)


def run_ws_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_ws_server())
    loop.run_forever()


# -----------------------------
# Overlay 클래스
# -----------------------------
class Overlay(QtWidgets.QWidget):
    _instance = None

    def __init__(self):
        super().__init__()
        Overlay._instance = self

        self.words = self.load_words("words.txt")
        self.prefix_index = self.build_prefix_index(self.words)
        self.deadlocked_file = "kkutudeadlocked.txt"
        self.offset = None
        self.initUI()

        self.server_thread = threading.Thread(target=run_ws_server, daemon=True)
        self.server_thread.start()

        QtWidgets.qApp.aboutToQuit.connect(self.cleanup)

    @staticmethod
    def instance():
        if Overlay._instance is None:
            raise RuntimeError("Overlay instance not initialized yet.")
        return Overlay._instance

    def cleanup(self):
        log.info("[Overlay] Cleaning up threads and closing...")

    # -----------------------------
    # 단어 로딩 및 인덱싱
    # -----------------------------
    def load_words(self, filename):
        if not os.path.exists(filename):
            log.warning("[WARN] words.txt not found")
            return []
        with open(filename, "r", encoding="utf-8") as f:
            raw = f.read()
        cleaned = raw.replace(",", "\n").replace("'", "").replace('"', "")
        words = [line.strip() for line in cleaned.splitlines() if line.strip()]
        log.info(f"[Overlay] Loaded {len(words)} words.")
        return words

    def build_prefix_index(self, words):
        index = defaultdict(list)
        for w in words:
            if w:
                index[w[0]].append(w)
        return index

    # -----------------------------
    # UI 초기화
    # -----------------------------
    def initUI(self):
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        main_layout = QtWidgets.QVBoxLayout(self)
        top_bar = QtWidgets.QHBoxLayout()

        self.close_button = QtWidgets.QPushButton("X", self)
        self.close_button.setFixedSize(25, 25)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: darkred; }
        """)
        self.close_button.clicked.connect(QtWidgets.qApp.quit)
        top_bar.addStretch()
        top_bar.addWidget(self.close_button)

        self.label = QtWidgets.QLabel("Waiting for word...", self)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("""
            QLabel {
                background-color: rgba(40, 40, 40, 200);
                color: white;
                font-size: 15px;
                border-radius: 10px;
                padding: 8px;
            }
        """)

        main_layout.addLayout(top_bar)
        main_layout.addWidget(self.label)
        self.setLayout(main_layout)

        self.setGeometry(100, 100, 420, 150)
        self.show()

    # -----------------------------
    # 마우스 이동 (드래그)
    # -----------------------------
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == QtCore.Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)

    def mouseReleaseEvent(self, event):
        self.offset = None

    # -----------------------------
    # 단어 수신 처리
    # -----------------------------
    @QtCore.pyqtSlot(str)
    def on_word_received_safe(self, word):
        self.on_word_received(word)

    def on_word_received(self, word):
        if not isinstance(word, str):
            word = str(word)
        word = word.strip()
        if not word:
            return

        suggestions = self.suggest(word)
        if not suggestions:
            with open(self.deadlocked_file, "a", encoding="utf-8") as f:
                f.write(word + "\n")

        display_text = (
            f"현재 단어: {word}\n추천:\n" + "\n".join(suggestions)
            if suggestions else f"현재 단어: {word}\n추천: -"
        )
        self.label.setText(display_text)
        self.label.adjustSize()
        self.adjustSize()

    # -----------------------------
    # 추천 알고리즘
    # -----------------------------
    def suggest(self, word):
        if not word:
            return []

        # 괄호가 있는 경우 x(y) → [x, y], 일반 단어는 첫 글자만
        if "(" in word and ")" in word:
            start = word.find("(")
            end = word.find(")")
            base = word[:start]          # '름'
            alt = word[start + 1:end]    # '늠'
            bases = [base, alt]
        else:
            bases = [word[0]]

        candidates = []
        for b in bases:
            if not b:
                continue
            prefix_list = self.prefix_index.get(b[0], [])
            candidates += [w for w in prefix_list if w.startswith(b)]

        unique = sorted(set(candidates), key=len, reverse=True)
        return unique[:10]


# -----------------------------
# 실행부
# -----------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    overlay = Overlay()
    sys.exit(app.exec_())
