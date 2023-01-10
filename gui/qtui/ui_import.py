from . import main_ui, ui_config, ui_rpc, ui_dmmlogin, ui_dmm_help, more_ui, window_settings
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget


class MainUI(main_ui.Ui_MainWindow, QWidget):
    def __init__(self):
        super(MainUI, self).__init__()

    def setupUi(self, MainWindow):
        super(MainUI, self).setupUi(MainWindow)
        # MainWindow.setFixedSize(MainWindow.rect().width(), MainWindow.rect().height())


class ConfigUI(ui_config.Ui_MainWindow, QWidget):
    def __init__(self):
        super(ConfigUI, self).__init__()

    def setupUi(self, MainWindow):
        super(ConfigUI, self).setupUi(MainWindow)
        # MainWindow.setFixedSize(MainWindow.rect().width(), MainWindow.rect().height())


class RPCUI(ui_rpc.Ui_MainWindow, QWidget):
    def __init__(self):
        super(RPCUI, self).__init__()

    def setupUi(self, MainWindow):
        super(RPCUI, self).setupUi(MainWindow)
        # MainWindow.setFixedSize(MainWindow.rect().width(), MainWindow.rect().height())


class DMMUI(ui_dmmlogin.Ui_MainWindow, QWidget):
    def __init__(self):
        super(DMMUI, self).__init__()

    def setupUi(self, MainWindow):
        super(DMMUI, self).setupUi(MainWindow)
        # MainWindow.setFixedSize(MainWindow.rect().width(), MainWindow.rect().height())


class DMMHelpUI(ui_dmm_help.Ui_MainWindow, QWidget):
    def __init__(self):
        super(DMMHelpUI, self).__init__()

    def setupUi(self, MainWindow):
        super(DMMHelpUI, self).setupUi(MainWindow)
        # MainWindow.setFixedSize(MainWindow.rect().width(), MainWindow.rect().height())


class MoreSettingsUI(more_ui.Ui_MainWindow, QWidget):
    def __init__(self):
        super(MoreSettingsUI, self).__init__()

    def setupUi(self, MainWindow):
        super(MoreSettingsUI, self).setupUi(MainWindow)


class WindowSettingsUI(window_settings.Ui_MainWindow, QWidget):
    def __init__(self):
        super(WindowSettingsUI, self).__init__()

    def setupUi(self, MainWindow):
        super(WindowSettingsUI, self).setupUi(MainWindow)
