from PyQt5 import QtWidgets, QtGui, QtCore
from .qtui import msrc_rc
import os


class TrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, MainWindow, parent=None):
        self._parent = parent
        super(TrayIcon, self).__init__(parent)
        self.ui = MainWindow
        self.createMenu()

    def createMenu(self):
        self.menu = QtWidgets.QMenu(self._parent)
        self.menu.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.showAction1 = QtWidgets.QAction("Show", self, triggered=self.show_window)
        # self.showAction2 = QtWidgets.QAction("显示通知", self, triggered=self.showMsg)
        self.quitAction = QtWidgets.QAction("Exit", self, triggered=self.quit)

        self.menu.addAction(self.showAction1)
        # self.menu.addAction(self.showAction2)
        self.menu.addAction(self.quitAction)
        self.setContextMenu(self.menu)

        self.setIcon(QtGui.QIcon(":/img/jishao.ico"))
        self.icon = self.MessageIcon()

        self.activated.connect(self.onIconClicked)

    def showMsg(self):
        self.showMessage("Message", "skr at here", self.icon)

    def show_window(self):
        self.ui.showNormal()
        self.ui.activateWindow()
        self.ui.setWindowFlags(QtCore.Qt.Window)
        self.ui.show()

    def quit(self):
        self.setVisible(False)
        QtWidgets.qApp.quit()
        os._exit(0)

    def onIconClicked(self, reason):
        if reason == 2 or reason == 3:
            if self.ui.isMinimized() or not self.ui.isVisible():
                self.ui.showNormal()
                self.ui.activateWindow()
                self.ui.setWindowFlags(QtCore.Qt.Window)
                self.ui.show()
            else:
                self.ui.showMinimized()
                self.ui.setWindowFlags(QtCore.Qt.SplashScreen)
                self.ui.show()
