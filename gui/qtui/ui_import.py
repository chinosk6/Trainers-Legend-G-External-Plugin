import ctypes
from . import main_ui, ui_config, ui_rpc, ui_dmmlogin, ui_dmm_help, more_ui, window_settings
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtGui

local_language = ctypes.windll.kernel32.GetUserDefaultUILanguage()

sChinese_lang_id = [0x0004, 0x0804, 0x1004]  # zh-Hans, zh-CN, zh-SG
tChinese_lang_id = [0x0404, 0x0c04, 0x1404, 0x048E]  # zh-TW, zh-HK, zh-MO, zh-yue-HK
JPN_lang_id = [0x0011, 0x0411]  # ja, ja-JP


def init_font(MainWindow):
    font = QtGui.QFont()
    if local_language in JPN_lang_id:
        font.setFamily("Yu Gothic UI")
    else:
        font.setFamily("Microsoft YaHei")
    MainWindow.setFont(font)


class MainUI(main_ui.Ui_MainWindow, QWidget):
    def __init__(self):
        super(MainUI, self).__init__()

    def setupUi(self, MainWindow):
        super(MainUI, self).setupUi(MainWindow)
        # MainWindow.setFixedSize(MainWindow.rect().width(), MainWindow.rect().height())
        init_font(MainWindow)


class ConfigUI(ui_config.Ui_MainWindow, QWidget):
    def __init__(self):
        super(ConfigUI, self).__init__()

    def setupUi(self, MainWindow):
        super(ConfigUI, self).setupUi(MainWindow)
        # MainWindow.setFixedSize(MainWindow.rect().width(), MainWindow.rect().height())
        init_font(MainWindow)


class RPCUI(ui_rpc.Ui_MainWindow, QWidget):
    def __init__(self):
        super(RPCUI, self).__init__()

    def setupUi(self, MainWindow):
        super(RPCUI, self).setupUi(MainWindow)
        # MainWindow.setFixedSize(MainWindow.rect().width(), MainWindow.rect().height())
        init_font(MainWindow)


class DMMUI(ui_dmmlogin.Ui_MainWindow, QWidget):
    def __init__(self):
        super(DMMUI, self).__init__()

    def setupUi(self, MainWindow):
        super(DMMUI, self).setupUi(MainWindow)
        # MainWindow.setFixedSize(MainWindow.rect().width(), MainWindow.rect().height())
        init_font(MainWindow)


class DMMHelpUI(ui_dmm_help.Ui_MainWindow, QWidget):
    def __init__(self):
        super(DMMHelpUI, self).__init__()

    def setupUi(self, MainWindow):
        super(DMMHelpUI, self).setupUi(MainWindow)
        # MainWindow.setFixedSize(MainWindow.rect().width(), MainWindow.rect().height())
        init_font(MainWindow)


class MoreSettingsUI(more_ui.Ui_MainWindow, QWidget):
    def __init__(self):
        super(MoreSettingsUI, self).__init__()

    def setupUi(self, MainWindow):
        super(MoreSettingsUI, self).setupUi(MainWindow)
        init_font(MainWindow)


class WindowSettingsUI(window_settings.Ui_MainWindow, QWidget):
    def __init__(self):
        super(WindowSettingsUI, self).__init__()

    def setupUi(self, MainWindow):
        super(WindowSettingsUI, self).setupUi(MainWindow)
        init_font(MainWindow)
