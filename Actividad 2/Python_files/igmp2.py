from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(750, 901)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.bomba_atomica = QtWidgets.QPushButton(parent=self.centralwidget)
        self.bomba_atomica.setGeometry(QtCore.QRect(0, 700, 700, 50))
        self.bomba_atomica.setObjectName("bomba_atomica")
        self.bomba_vida = QtWidgets.QPushButton(parent=self.centralwidget)
        self.bomba_vida.setGeometry(QtCore.QRect(0, 750, 700, 50))
        self.bomba_vida.setObjectName("bomba_vida")
        self.label_temp = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_temp.setGeometry(QtCore.QRect(300, 10, 100, 30))
        self.label_temp.setObjectName("label_temp")
        self.label_temp.setStyleSheet("color: red; background-color: rgba(255,255,255,0.8);")
        self.label_juego = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_juego.setGeometry(QtCore.QRect(0, 0, 700, 700))
        self.label_juego.setObjectName("label_juego")
        self.temp = QtWidgets.QPushButton(parent=self.centralwidget)
        self.temp.setGeometry(QtCore.QRect(0, 800, 700, 50))
        self.temp.setObjectName("temp")
        self.verticalSlider = QtWidgets.QSlider(parent=self.centralwidget)
        self.verticalSlider.setGeometry(QtCore.QRect(710, 0, 40, 850))
        self.verticalSlider.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.verticalSlider.setObjectName("verticalSlider")
        self.bomba_atomica.raise_()
        self.bomba_vida.raise_()
        self.label_juego.raise_()
        self.temp.raise_()
        self.verticalSlider.raise_()
        self.label_temp.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 750, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.bomba_atomica.setText(_translate("MainWindow", "Bomba Atómica"))
        self.bomba_vida.setText(_translate("MainWindow", "Bomba de vida"))
        self.label_temp.setText(_translate("MainWindow", "TextLabel"))
        self.label_juego.setText(_translate("MainWindow", "TextLabel"))
        self.temp.setText(_translate("MainWindow", "Temp Arduino / Temp Manual"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
