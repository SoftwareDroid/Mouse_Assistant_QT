import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyautogui
from enum import Enum


class Phase(Enum):
    WAIT_FOR_MOVE = 1
    IDLE_AFTER_MOVE = 2
    ANIMATION = 3
    CLICK_ANIMATION = 4


class CustomWindow(QMainWindow):

    def __init__(self, parent=None):
        super(CustomWindow, self).__init__(parent)

        self.WIN_SIZE = 60
        self.last_mouse_pos = (0, 0)
        self.phase = Phase.WAIT_FOR_MOVE
        self.timer = QElapsedTimer()
        self.timer.start()
        self.idle_time = 300  # 300ms
        self.wait_before_click = 1000
        self.progress_factor = 0

        self._timer = QTimer()
        self._timer.timeout.connect(self.update)
        self._timer.setInterval(50)
        self._timer.start()

    def update(self):

        pos = pyautogui.position()
        self.move(int(pos[0] - self.WIN_SIZE / 2), int(pos[1] - self.WIN_SIZE / 2))

        if self.last_mouse_pos != pos and self.phase != Phase.CLICK_ANIMATION:
            self.timer.restart()
            self.progress_factor = 0
            self.last_mouse_pos = pos
            self.phase = Phase.IDLE_AFTER_MOVE
        else:
            if self.phase == Phase.IDLE_AFTER_MOVE and self.timer.elapsed() > self.idle_time:
                self.phase = Phase.ANIMATION
                self.timer.restart()
            elif self.phase == Phase.ANIMATION:
                elapsed_time = self.timer.elapsed()
                if elapsed_time == 0:
                    return
                self.progress_factor = float(min(elapsed_time, self.wait_before_click)) / float(self.wait_before_click)
                if elapsed_time > self.wait_before_click:
                    self.progress_factor = 0
                    self.phase = Phase.WAIT_FOR_MOVE
                    pyautogui.click()  # click the mouse
                    self.timer.restart()
        self.repaint()

    def paintEvent(self, event=None):
        if self.progress_factor == 0:
            return
        painter = QPainter(self)
        strenght = 3
        painter.setPen(QPen(QColor(255, 163, 0, 255), strenght, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        startAngle = 90 * 16
        spanAngle = 1 - self.progress_factor * 360 * 16
        painter.drawPie(QRectF(0, 0, int(self.WIN_SIZE - strenght), int(self.WIN_SIZE - strenght)), startAngle, spanAngle)


app = QApplication(sys.argv)

# Create the main window
window = CustomWindow()

window.setWindowFlags(Qt.FramelessWindowHint)
window.setAttribute(Qt.WA_NoSystemBackground, True)
window.setAttribute(Qt.WA_TranslucentBackground, True)
window.setAttribute(Qt.WA_TransparentForMouseEvents)
window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
window.setFixedHeight(window.WIN_SIZE)
window.setFixedWidth(window.WIN_SIZE)

window.show()
sys.exit(app.exec_())