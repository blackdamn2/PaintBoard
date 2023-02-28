# coding = utf-8

from src.view.MainWindow import Ui_MainWindow
from src.BaseAdjustDialog import BaseAdjustDialog
from PyQt5.QtWidgets import (QWidget,QApplication,QMainWindow,QFileDialog)
from PyQt5 import uic
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.Qt import *
from src.util import ImageUtil
from functools import partial
import qdarkstyle
import qtmodern.styles
import qtmodern.windows
from MyWidgets import *


class PaintBoard(QMainWindow,Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super(PaintBoard, self).__init__(*args, **kwargs)
        self.setupUi(self)
        #uic.loadUi('./view/MainWindow.ui',self)
        self._initParam()
        self._initDefaultBoard()
        self._establishConnections()
        self._initPainter()
        self.scaleFactor = 1
        self.scrollArea.setAlignment(Qt.AlignCenter)
        self.textList = []
        self.textFont = None
        self.textSize = None
        self.fontSelectBtn.currentFontChanged.connect(self.onSetFont)
        # self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)



    def _initPainter(self,board = None):
        painter = QPainter(board or self.img)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(QPen(self.penColor, self.penSize,Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        return painter


    def _initParam(self):
        self.drawing = False
        self.adjusting = False
        self.lastPoint = QPoint()
        self.endPoint = QPoint()
        self.penSize = 2
        self.penColor = Qt.black
        self.preColor = Qt.black
        self.backColor = Qt.white
        self.toolBtns = [self.penBtn,self.bucketBtn,self.rectBtn,self.lineBtn,self.ellipseBtn,self.eraseButton, self.textLineBtn]
        self.toolBtnEvents = [self._drawPen,self._drawBucket,self._drawRect,self._drawLine,self._drawEllipse,self._drawErase, self._drawText]

    def wheelEvent(self, event: QWheelEvent) -> None:
        # 滚轮事件
        if event.modifiers() == Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.scaleFactor *= 1.1
                self.board.resize(self.board.pixmap().size() * self.scaleFactor)
                self.scrollAreaWidgetContents.resize(self.board.pixmap().size() * self.scaleFactor)
            else:
                self.scaleFactor *= 0.9
                self.board.resize(self.board.pixmap().size() * self.scaleFactor)
                self.scrollAreaWidgetContents.resize(self.board.pixmap().size() * self.scaleFactor)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.penColor = self.preColor
        elif event.button() == Qt.RightButton:
            self.penColor = self.backColor

        self.drawing = True
        print(self.scaleFactor)
        self.lastPoint = self._getPosFromGlobal(event.pos()) / self.scaleFactor
        self.startPoint = self._getPosFromGlobal(event.pos()) / self.scaleFactor
        self.update()



    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton or event.button() == Qt.RightButton:
            self.endPoint = self._getPosFromGlobal(event.pos()) / self.scaleFactor
            self.drawing = False
            [toolBtnEvent(event) for toolBtn,toolBtnEvent in  zip(self.toolBtns,self.toolBtnEvents) if toolBtn.isChecked()]

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() and Qt.LeftButton and self.drawing:
            [toolBtnEvent(event) for toolBtn,toolBtnEvent in  zip(self.toolBtns,self.toolBtnEvents) if toolBtn.isChecked()]
            self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        if self.drawing and True in [btn.isChecked() for btn in self.toolBtns[2:5]] or self.adjusting:
            self.board.setPixmap(QPixmap.fromImage(self.bufferImg))
        else:
            pix = QPixmap.fromImage(self.img)
            self.board.setPixmap(pix)


    def _getPosFromGlobal(self,pos):
        globalPos = self.mapToGlobal(pos)
        boardPos = self.board.mapFromGlobal(globalPos)
        return boardPos

    def _initDefaultBoard(self):
        self.img = QImage(self.scrollAreaWidgetContents.size(), QImage.Format_RGB32)
        self.img.fill(Qt.white)
        self.bufferImg = self.img.copy()
        self.oriImg = self.img.copy()
        self._refreshBoard()

    def onSetFont(self, font):
        # font, ok = QFontDialog.getFont()
        # if ok:
        print(font)
        self.textFont = QFont(font.family(), 16)
        print(self.textFont)

    def _establishConnections(self):
        self.actionNew.triggered.connect(self._clear)
        self.actionClear.triggered.connect(self._clear)
        self.actionSave.triggered.connect(self._save)
        self.actionOpenImg.triggered.connect(self._openImg)
        self.actionClearDraw.triggered.connect(self._clearDraw)
        self.actionClockWise.triggered.connect(partial(self._wiseAction,'clock'))
        self.actionAntiClockWise.triggered.connect(partial(self._wiseAction,'antiClock'))
        self.actionVerFilp.triggered.connect(partial(self._wiseAction,'verFilp'))
        self.actionHorFilp.triggered.connect(partial(self._wiseAction,'horFilp'))
        self.preColorBtn.clicked.connect(self._choosePreColor)
        self.backColorBtn.clicked.connect(self._chooseBackColor)
        self.penSizeBtn.currentIndexChanged.connect(self._choosePenSize)
        self.sizeSelectBtn.currentIndexChanged.connect(self._chooseTextSize)
        self.baseAdjustBtn.clicked.connect(self._openBaseAdjustDialog)

        self.blurBtn.clicked.connect(self._blur)
        self.sharpenBtn.clicked.connect(self._sharpen)
        self.cannyBtn.clicked.connect(self._canny)
        self.binaryBtn.clicked.connect(self._binaryzation)
        self.invertBtn.clicked.connect(self._invert)
        self.grayBtn.clicked.connect(self._gray)
        self.embossBtn.clicked.connect(self._emboss)
        # self.blurBtn.setHidden(True)
        # self.sharpenBtn.setHidden(True)
        self.cannyBtn.setHidden(True)
        # self.binaryBtn.setHidden(True)
        self.invertBtn.setHidden(True)
        # self.grayBtn.setHidden(True)
        # self.embossBtn.setHidden(True)
        self.baseAdjustBtn.setHidden(True)


        list(map(lambda btn:btn.clicked.connect(self._toolBoxClicked),self.toolBtns))


    def _openBaseAdjustDialog(self):
        self.baseAdjustDialog = BaseAdjustDialog()
        self.baseAdjustDialog.dialogRejected.connect(self._baseAdjustDialogRejected)
        self.baseAdjustDialog.dialogAccepted.connect(self._baseAdjustDialogAccepted)
        self.baseAdjustDialog.brightSliderReleased.connect(self._adjustBright)
        self.baseAdjustDialog.warmSliderReleased.connect(self._adjustWarm)
        self.baseAdjustDialog.saturabilitySliderReleased.connect(self._adjustSaturation)
        self.baseAdjustDialog.contrastSliderReleased.connect(self._adjustContrast)
        self.baseAdjustDialog.show()

    def _baseAdjustDialogAccepted(self):
        self.adjusting = False
        self.img = self.bufferImg
        self.update()

    def _baseAdjustDialogRejected(self):
        self.adjusting = False
        self.update()

    def _adjustContrast(self,value):
        self.adjusting = True
        self.bufferImg = ImageUtil.adjustContrast(self.img, value)
        self.update()

    def _adjustBright(self,value):
        self.adjusting = True
        self.bufferImg = ImageUtil.adjustBright(self.img,value)
        self.update()

    def _adjustWarm(self,value):
        self.adjusting = True
        self.bufferImg = ImageUtil.adjustWarm(self.img,value)
        self.update()

    def _adjustSaturation(self,value):
        self.adjusting = True
        self.bufferImg = ImageUtil.adjustSaturation(self.img, value)
        self.update()

    def _drawLine(self,event):
        boardPos = self._getPosFromGlobal(event.pos()) / self.scaleFactor
        if self.drawing:
            self.bufferImg = self.img.copy()
            painter = self._initPainter(board=self.bufferImg)
            painter.drawLine(self.startPoint, boardPos)
        else:
            painter = self._initPainter()
            painter.drawLine(self.startPoint, self.endPoint)

    def _drawEllipse(self,event):
        boardPos = self._getPosFromGlobal(event.pos()) / self.scaleFactor
        if self.drawing:
            self.bufferImg = self.img.copy()
            painter = self._initPainter(board=self.bufferImg)
            painter.drawEllipse(QRect(self.startPoint, boardPos))

        else:
            painter = self._initPainter()
            painter.drawEllipse(QRect(self.startPoint, self.endPoint))

    def _drawRect(self,event):
        boardPos = self._getPosFromGlobal(event.pos()) / self.scaleFactor
        if self.drawing:
            self.bufferImg = self.img.copy()
            painter = self._initPainter(board=self.bufferImg)
            painter.drawRect(QRect(self.startPoint, boardPos))
        else:
            painter = self._initPainter()
            painter.drawRect(QRect(self.startPoint, self.endPoint))

    def _drawBucket(self,event):
        boardPos = self._getPosFromGlobal(event.pos()) / self.scaleFactor
        fillPositions = ImageUtil.floodFill(self.img,boardPos)
        painter = self._initPainter()
        [painter.drawPoint(x,y) for x,y in fillPositions]

    def _drawErase(self,event):
        self.penColor = self.backColor
        self._drawPen(event)

    def _drawPen(self,event):
        painter = self._initPainter()
        boardPos = self._getPosFromGlobal(event.pos()) / self.scaleFactor
        painter.drawLine(self.lastPoint, boardPos)
        self.lastPoint = boardPos
        self.update()

    def _drawText(self, event):
        painter = self._initPainter()
        font = QFont(self.fontSelectBtn.currentFont())
        font.setPointSize(int(self.sizeSelectBtn.currentText()))
        font.setUnderline(self.underLineBtn.isChecked())
        font.setItalic(self.italicBtn.isChecked())
        font.setBold(self.boldBtn.isChecked())
        painter.setFont(font)
        painter.drawText(self.lastPoint, self.textLineEdit.toPlainText())

    def _toolBoxClicked(self):
        self._refreshButtons()
        toolBtn = self.sender()
        toolBtn.setChecked(True)


    def _choosePenSize(self):
        self.penSize = int(self.penSizeBtn.currentText()[0:-2])

    def _chooseTextSize(self):
        self.textSize = int(self.sizeSelectBtn.currentText())

    def _choosePreColor(self):
        colorName,self.preColor= self._getColor()
        self.preColorBtn.setStyleSheet("background-color:%s" % colorName)

    def _chooseBackColor(self):
        colorName,self.backColor= self._getColor()
        self.backColorBtn.setStyleSheet("background-color:%s" % colorName)

    def _getColor(self):
        color = QColorDialog.getColor()
        colorName = color.name()
        return colorName,color

    def _blur(self):
        self.img.save("../img/temp.jpg")
        self.img = ImageUtil.blur()
        self._refreshBoard()

    def _canny(self):
        self.img.save("../img/temp.jpg")
        self.img = ImageUtil.canny()
        self._refreshBoard()

    def _sharpen(self):
        self.img.save("../img/temp.jpg")
        self.img = ImageUtil.sharpen()
        self._refreshBoard()

    def _gray(self):
        self.img.save("../img/temp.jpg")
        self.img = ImageUtil.gray()
        self._refreshBoard()

    def _invert(self):
        self.img.save("../img/temp.jpg")
        self.img = ImageUtil.invert()
        self._refreshBoard()

    def _emboss(self):
        self.img.save("../img/temp.jpg")
        self.img = ImageUtil.emboss()
        self._refreshBoard()

    def _binaryzation(self):
        self.img.save("../img/temp.jpg")
        self.img = ImageUtil.binaryzation()
        self._refreshBoard()

    def _refreshButtons(self):
        [btn.setChecked(False) for btn in self.toolBtns]

    def _refreshBoard(self):
        pix = QPixmap.fromImage(self.img)
        self.board.resize(pix.size())
        self.board.setPixmap(pix)
        self.scrollAreaWidgetContents.resize(pix.size())

    def _save(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "保存图像", "","PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")
        if filePath == "": return
        self.img.save(filePath)

    def _clear(self):
        self.img.fill(Qt.white)
        self._refreshBoard()

    def _clearDraw(self):
        self.img = self.oriImg.copy()
        self._refreshBoard()

    def _wiseAction(self,action):
        if action == 'clock':
            transform = QTransform()
            transform.rotate(90)
            self.img = self.img.transformed(transform)
        elif action == 'antiClock':
            transform = QTransform()
            transform.rotate(-90)
            self.img = self.img.transformed(transform)
        elif action == 'verFilp':
            self.img = self.img.mirrored(True,False)
        else:
            self.img = self.img.mirrored(False,True)
        self._refreshBoard()

    def _openImg(self):
        fileName, fileType = QFileDialog.getOpenFileName(self,"选取文件",r'D:\11 - 作业\研一下学期\数字图像处理\Paint-master\Paint-master\img','Image files (*.jpg *.gif *.png *.jpeg)')
        self.img = QImage(fileName)
        self.oriImg = self.img.copy()
        self._refreshBoard()

def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    qtmodern.styles.light(app)
    application = PaintBoard()
    mw = qtmodern.windows.ModernWindow(application)
    mw.show()
    sys.exit(app.exec_())



if __name__ == '__main__':
    main()