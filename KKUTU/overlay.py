# overlay.py
# Dependencies: PySide6, keyboard
# pip install PySide6 keyboard

import sys
import os
import threading
import ctypes
from ctypes import wintypes
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QCheckBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
import random
import time
import keyboard  # for global hotkeys
import pyperclip  # optional: pip install pyperclip

# ---------- Config ----------
WORDS_FILE = "words.txt"
USED_LOG = "used_words.txt"
HOTKEY_CAPTURE = "ctrl+shift+c"   # 클립보드 단어를 현재 단어로 설정
HOTKEY_TOGGLE = "ctrl+shift+s"    # overlay 토글
# ----------------------------

# Win32 constants
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOPMOST = 0x00000008
WS_EX_TOOLWINDOW = 0x00000080
LWA_ALPHA = 0x02

SetWindowLongPtr = ctypes.windll.user32.SetWindowLongPtrW
GetWindowLongPtr = ctypes.windll.user32.GetWindowLongPtrW
SetLayeredWindowAttributes = ctypes.windll.user32.SetLayeredWindowAttributes

def set_overlay_exstyle(hwnd):
    ex = GetWindowLongPtr(hwnd, GWL_EXSTYLE)
    # 추가: TOOLWINDOW(작업표시줄 숨김), TRANSPARENT(클릭통과 toggle 가능), LAYERED(알파)
    ex |= (WS_EX_LAYERED | WS_EX_TOPMOST | WS_EX_TOOLWINDOW)
    SetWindowLongPtr(hwnd, GWL_EXSTYLE, ex)
    SetLayeredWindowAttributes(hwnd, 0, 255, LWA_ALPHA)

def set_clickthrough(hwnd, enable=True):
    ex = GetWindowLongPtr(hwnd, GWL_EXSTYLE)
    if enable:
        ex |= WS_EX_TRANSPARENT
    else:
        ex &= ~WS_EX_TRANSPARENT
    SetWindowLongPtr(hwnd, GWL_EXSTYLE, ex)

# ---------- Word helper ----------
def load_words():
    if not os.path.exists(WORDS_FILE):
        # create sample file
        with open(WORDS_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(["사랑","강아지","지하철","철수","수박","박쥐","쥐덫","지구","가방","바다","다리"]))
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        words = [w.strip() for w in f if w.strip()]
    return words

def append_used(word):
    with open(USED_LOG, "a", encoding="utf-8") as f:
        f.write(word + "\n")

def next_candidates(current, words):
    if not current:
        return []
    last_char = current[-1]
    # 간단 구현: 단어의 첫 글자와 last_char가 같으면 후보
    # (한글 받침·초성 규칙을 완벽 지원하려면 별도 로직 필요)
    cands = [w for w in words if w[0] == last_char]
    return cands

# ---------- UI ----------
class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("끝말잇기 도우미 (Overlay)")
        self.setGeometry(100, 100, 420, 120)

        font = QFont("맑은 고딕", 12)
        layout = QVBoxLayout()
        layout.setContentsMargins(8,8,8,8)

        self.input = QLineEdit()
        self.input.setPlaceholderText("현재 단어를 입력하거나 Ctrl+Shift+C로 클립보드 내용 가져오기")
        self.input.setFont(font)
        layout.addWidget(self.input)

        self.result = QLabel("추천 단어: -")
        self.result.setFont(font)
        self.result.setStyleSheet("background: rgba(0,0,0,0.5); color: white; padding:6px; border-radius:6px;")
        layout.addWidget(self.result)

        controls = QVBoxLayout()
        self.btn_save = QPushButton("사용 단어 저장")
        self.btn_save.clicked.connect(self.save_used)
        self.cb_clickthrough = QCheckBox("클릭 통과 (Click-through)")
        self.cb_clickthrough.setChecked(True)
        self.cb_clickthrough.stateChanged.connect(self.update_clickthrough)
        controls_widget = QWidget()
        ctr_layout = QVBoxLayout()
        ctr_layout.addWidget(self.btn_save)
        ctr_layout.addWidget(self.cb_clickthrough)
        controls_widget.setLayout(ctr_layout)
        layout.addWidget(controls_widget)

        self.setLayout(layout)

        self.words = load_words()
        self.input.textChanged.connect(self.on_text_change)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_words_from_file)
        self.refresh_timer.start(5000)  # 5초마다 words.txt 재로딩

        # Make window styles native after shown
        QTimer.singleShot(100, self.apply_native_styles)

    def apply_native_styles(self):
        hwnd = self.winId().__int__()
        set_overlay_exstyle(hwnd)
        set_clickthrough(hwnd, self.cb_clickthrough.isChecked())

    def update_clickthrough(self):
        hwnd = self.winId().__int__()
        set_clickthrough(hwnd, self.cb_clickthrough.isChecked())

    def on_text_change(self, text):
        cands = next_candidates(text.strip(), self.words)
        if not cands:
            self.result.setText("추천 단어: 없음")
        else:
            # 상위 5개 무작위 제시
            sample = cands if len(cands) <= 5 else random.sample(cands, 5)
            self.result.setText("추천 단어: " + ", ".join(sample))

    def save_used(self):
        w = self.input.text().strip()
        if w:
            append_used(w)

    def refresh_words_from_file(self):
        self.words = load_words()

# ---------- Hotkey handling ----------
def start_hotkeys(window: Overlay):
    def on_capture():
        try:
            txt = pyperclip.paste()
        except Exception:
            txt = ""
        txt = txt.strip()
        if txt:
            # set in GUI thread
            window.input.setText(txt)
    def on_toggle():
        if window.isVisible():
            window.hide()
        else:
            window.show()
            # reapply styles (sometimes need)
            window.apply_native_styles()
    keyboard.add_hotkey(HOTKEY_CAPTURE, on_capture)
    keyboard.add_hotkey(HOTKEY_TOGGLE, on_toggle)

# ---------- main ----------
def main():
    app = QApplication(sys.argv)
    w = Overlay()
    w.show()

    # start hotkey thread so it doesn't block Qt
    t = threading.Thread(target=start_hotkeys, args=(w,), daemon=True)
    t.start()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
