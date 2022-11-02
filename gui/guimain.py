import threading
import time
import requests
from .qtui.ui_import import DMMUI, DMMHelpUI
from .qtui import msrc_rc  # 不能删
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QWidget, QFileDialog
import sys
import os
from . import dmmlogin
from . import guiextends


def timestamp_to_text(timestamp: int, _format="%Y-%m-%d %H:%M:%S"):
    if (timestamp > 9999999999):
        timestamp = timestamp / 1000
    ret = time.strftime(_format, time.localtime(timestamp))
    return ret


class GuiMain(guiextends.UIChange):
    def __init__(self):
        super(GuiMain, self).__init__()
        self.check_res_file()

        self.window_dmm = guiextends.QMn(self.window)
        self.window_dmm.setWindowIcon(QtGui.QIcon(":/img/jia.ico"))
        self.ui_dmm = DMMUI()
        self.ui_dmm.setupUi(self.window_dmm)

        self.window_dmmhelp = guiextends.QMn(self.window)
        self.window_dmmhelp.setWindowIcon(QtGui.QIcon(":/img/jia.ico"))
        self.ui_dmmhelp = DMMHelpUI()
        self.ui_dmmhelp.setupUi(self.window_dmmhelp)

        self.regist_callback()
        self.init_gui()

    @staticmethod
    def check_res_file():
        if not os.path.isfile("7z.dll"):
            QtCore.QFile.copy(":dll/7z.dll", "7z.dll")

    def regist_callback(self):
        super(GuiMain, self).regist_callback()
        self.ui.pushButton_fast_login.clicked.connect(self.window_dmm_show)
        self.ui_dmm.checkBox_use_proxy.clicked.connect(self.check_proxy_lineedit_state)
        self.ui_dmm.pushButton_select_edge.clicked.connect(self.select_edge_onclick)
        self.ui_dmm.pushButton_login.clicked.connect(self.dmm_login_btn_onclick)
        self.ui_dmm.pushButton_login_cache.clicked.connect(self.dmm_login_cache_btn_onclick)
        self.update_dmm_log.connect(self.on_dmm_log)
        self.update_dmm_login_btn_signal.connect(self.update_dmm_button_text(self.ui_dmm.pushButton_login))
        self.dmm_button_login_cache_signal.connect(self.update_dmm_button_text(self.ui_dmm.pushButton_login_cache))
        self.dmm_login_success_signal.connect(self.dmm_login_success)
        self.ui_dmm.pushButton_help.clicked.connect(lambda *x: self.window_dmmhelp.show())

    def init_gui(self):
        super(GuiMain, self).init_gui()
        # self.ui_dmm.pushButton_login.setEnabled(os.path.isfile(f"{self.uma_path}/umamusume.exe"))
        self.ui_dmm.lineEdit_edge_path.setText(guiextends.rpc_data.edge_path)
        self.ui_dmm.lineEdit_dmm_account.setText(guiextends.rpc_data.email)
        self.ui_dmm.lineEdit_dmm_passwd.setText(guiextends.rpc_data.password)
        self.ui_dmm.lineEdit_proxy_url.setText(guiextends.rpc_data.proxy_url)
        self.ui_dmm.checkBox_use_proxy.setChecked(guiextends.rpc_data.enable_proxy)
        self.ui_dmm.checkBox_open_browser_window.setChecked(guiextends.rpc_data.login_open_edge)
        self.ui_dmm.comboBox_browser_type.setCurrentIndex(guiextends.rpc_data.dmm_browser_type)

        self.ui_dmm.label_4.setText(f"• {self.ui_dmm.label_4.text()}")
        self.ui_dmm.label_5.setText(f"• {self.ui_dmm.label_5.text()}")
        self.ui_dmm.label_6.setText(f"• {self.ui_dmm.label_6.text()}")

    def check_proxy_lineedit_state(self):
        self.ui_dmm.lineEdit_proxy_url.setEnabled(self.ui_dmm.checkBox_use_proxy.isChecked())
        self.ui_dmm.pushButton_login_cache.setEnabled(True if guiextends.rpc_data.dmm_cookie_cache else False)

    def window_dmm_show(self):
        self.check_proxy_lineedit_state()
        self.window_dmm.show()

    def select_edge_onclick(self, *args):
        filename, filetype = QFileDialog.getOpenFileName(self, '选择文件', os.getcwd(),
                                                         "EXE Files(*.exe);;All Files(*)")
        if filename != "":
            self.ui_dmm.lineEdit_edge_path.setText(filename)

    @staticmethod
    def update_dmm_button_text(button):
        def _(s: str):
            if s == "false":
                button.setEnabled(False)
            elif s == "true":
                button.setEnabled(True)
            else:
                button.setText(s)
        return _

    def _login(self, cookie_cache=None):
        self.update_dmm_login_btn_signal.emit("false")
        self.dmm_button_login_cache_signal.emit("false")
        self.update_dmm_login_btn_signal.emit("Logging in...")
        dmm = dmmlogin.UmaDmm(guiextends.rpc_data.email, guiextends.rpc_data.password, self.update_dmm_log.emit,
                              guiextends.rpc_data.edge_path,
                              guiextends.rpc_data.proxy_url if guiextends.rpc_data.enable_proxy else None,
                              not guiextends.rpc_data.login_open_edge,
                              driver_type=guiextends.rpc_data.dmm_browser_type)
        get_args = dmm.get_launch_args(cookie_cache=cookie_cache)
        is_success = False
        if isinstance(get_args, dmmlogin.ReturnDMM):
            guiextends.rpc_data.dmm_cookie_cache = get_args.cookies
            guiextends.rpc_data.write_config()
            is_success = True
        else:
            self.update_dmm_login_btn_signal.emit(f"Login failed: {get_args}")

        self.update_dmm_login_btn_signal.emit("Login")
        self.update_dmm_login_btn_signal.emit("true")
        self.dmm_button_login_cache_signal.emit("true")
        if is_success:
            self.dmm_login_success_signal.emit(get_args.launch_args)

    def update_save_data(self):
        guiextends.rpc_data.edge_path = self.ui_dmm.lineEdit_edge_path.text()
        guiextends.rpc_data.email = self.ui_dmm.lineEdit_dmm_account.text()
        guiextends.rpc_data.password = self.ui_dmm.lineEdit_dmm_passwd.text()
        guiextends.rpc_data.proxy_url = self.ui_dmm.lineEdit_proxy_url.text()
        guiextends.rpc_data.enable_proxy = self.ui_dmm.checkBox_use_proxy.isChecked()
        guiextends.rpc_data.login_open_edge = self.ui_dmm.checkBox_open_browser_window.isChecked()
        guiextends.rpc_data.dmm_browser_type = self.ui_dmm.comboBox_browser_type.currentIndex()

        guiextends.rpc_data.write_config()

    def dmm_login_btn_onclick(self, *args):
        self.update_save_data()

        if not os.path.isfile(guiextends.rpc_data.edge_path):
            self.update_dmm_log.emit(f"Edge Driver Not Found. "
                                     f"Download: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver")
            return

        self.update_dmm_login_btn_signal.emit("false")
        self.dmm_button_login_cache_signal.emit("false")
        threading.Thread(target=self._login).start()

    def dmm_login_cache_btn_onclick(self, *args):
        self.update_save_data()

        if not os.path.isfile(guiextends.rpc_data.edge_path):
            self.update_dmm_log.emit(f"Edge Driver Not Found. "
                                     f"Download: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver")
            return

        self.update_dmm_login_btn_signal.emit("false")
        self.dmm_button_login_cache_signal.emit("false")
        threading.Thread(target=self._login, kwargs={"cookie_cache": guiextends.rpc_data.dmm_cookie_cache}).start()

    def dmm_login_success(self, gameargs: str):
        sys.argv = [sys.argv[0], f"{self.uma_path}/umamusume.exe"] + [i for i in gameargs.split(" ")]
        self.load_args()
        is_reboot = self.show_message_box("Login Success", "Launch the game immediately?")
        if is_reboot == QtWidgets.QMessageBox.Yes:
            self.game_fast_reboot()


    def on_dmm_log(self, message: str):
        log_text = f"[{timestamp_to_text(int(time.time()))}] {message}"
        self.ui_dmm.textEdit_logs.append(log_text)


    def ui_run_main(self):
        super(GuiMain, self).ui_run_main()


