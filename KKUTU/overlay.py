import sys
import os
import json
import asyncio
import threading
import websockets
from PyQt5 import QtCore, QtWidgets


# -----------------------------
# WebSocket 서버 (호환 수정)
# -----------------------------
async def ws_handler(websocket, path=None):
    async for message in websocket:
        print(f"[WS] Word received: {message}")
        try:
            data = json.loads(message)
            word = data.get("word", "")
            if isinstance(word, list):
                word = "".join(map(str, word))
            elif not isinstance(word, str):
                word = str(word)

            print(f"[WS] Parsed word: {word}")

            QtCore.QMetaObject.invokeMethod(
                Overlay.instance(),
                "on_word_received_safe",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, word)
            )
        except Exception as e:
            print("[WS] Error parsing message:", e)


async def start_ws_server():
    async with websockets.serve(
        lambda ws, p=None: ws_handler(ws, p),
        "127.0.0.1",
        8765,
    ):
        print("[WS] WebSocket server started on ws://127.0.0.1:8765")
        await asyncio.Future()


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
        self.deadlocked_file = "kkutudeadlocked.txt"
        self.offset = None
        self.initUI()

        self.server_thread = threading.Thread(target=run_ws_server, daemon=True)
        self.server_thread.start()

    @staticmethod
    def instance():
        return Overlay._instance

    def load_words(self, filename):
        if not os.path.exists(filename):
            print("[WARN] words.txt not found")
            return []
        with open(filename, "r", encoding="utf-8") as f:
            raw = f.read()
        cleaned = raw.replace(",", "\n").replace("'", "").replace('"', "")
        return [line.strip() for line in cleaned.splitlines() if line.strip()]

    def initUI(self):
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        layout = QtWidgets.QVBoxLayout(self)

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
        layout.addWidget(self.label)

        self.close_button = QtWidgets.QPushButton("X", self)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                border: none;
                font-weight: bold;
                border-radius: 8px;
                width: 25px;
                height: 25px;
            }
            QPushButton:hover {
                background-color: darkred;
            }
        """)
        self.close_button.setFixedSize(25, 25)
        self.close_button.clicked.connect(QtWidgets.qApp.quit)
        layout.addWidget(self.close_button, alignment=QtCore.Qt.AlignRight)

        self.setLayout(layout)
        self.setGeometry(100, 100, 420, 150)
        self.show()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == QtCore.Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)

    def mouseReleaseEvent(self, event):
        self.offset = None

    @QtCore.pyqtSlot(str)
    def on_word_received_safe(self, word):
        self.on_word_received(word)

    def on_word_received(self, word):
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

    def suggest(self, word):
        if not word:
            return []
        base = word
        alts = []
        if "(" in word and ")" in word:
            start = word.find("(")
            end = word.find(")")
            alt = word[start + 1:end]
            base = word[:start]
            alts = [alt]
        candidates = [w for w in self.words if w.startswith(base)]
        for alt in alts:
            candidates += [w for w in self.words if w.startswith(alt)]
        unique = sorted(set(candidates), key=len, reverse=True)
        return unique[:20]


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    overlay = Overlay()
    sys.exit(app.exec_())
