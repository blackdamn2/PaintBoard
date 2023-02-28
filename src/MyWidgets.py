from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.Qt import *

class TextWorker(QObject):
    # 操作信号
    # send_task_signal = QtCore.Signal(dict)
    finished_signal = pyqtSignal(list)

    # 初始化时传入相关数据参数及线程对象
    def __init__(self, lastPoint, thread, parent=None) -> None:
        super(TextWorker, self).__init__(parent)
        self.lastPoint = lastPoint
        self.thread = thread
        self.text = None

    # 执行方法，启锁、关锁、执行动作、退出线程
    def start_task(self):
        self.lock.lock()
        self.textLine = QTextEdit()
        self.textLine.move(self.lastPoint)
        self.textLine.show()
        self.textLine.setFocus()
        self.textLine.exec()
        self.text = self.textLine.text()
        self.lock.unlock()
        self.thread.quit()

    def deleteLater(self) -> None:
        super(TextWorker, self).deleteLater()
        self.finished_signal.emit([self.text, self.lastPoint])