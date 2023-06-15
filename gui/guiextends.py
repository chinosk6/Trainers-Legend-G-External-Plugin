from threading import Thread
import time
import requests
from hashlib import md5
from .qtui.ui_import import MainUI, ConfigUI, RPCUI, MoreSettingsUI, WindowSettingsUI
from .qtui import msrc_rc  # 不能删
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QWidget, QInputDialog
import sys
from .qt_jsonschema_form import WidgetBuilder
import json
import os
import ctypes
import webbrowser
import pyperclip
from pynput import keyboard
from base64 import b64decode as bbq
from . import uma_icon_data
from . import discord_rpc
from . import unzip_file
from . import qtray
from . import http_server
from . import uma_tools
try:
    from . import umauitools
    import_cpp_success = True
except:
    import_cpp_success = False


ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
local_language = ctypes.windll.kernel32.GetUserDefaultUILanguage()
sChinese_lang_id = [0x0004, 0x0804, 0x1004]  # zh-Hans, zh-CN, zh-SG
tChinese_lang_id = [0x0404, 0x0c04, 0x1404, 0x048E]  # zh-TW, zh-HK, zh-MO, zh-yue-HK

rpc = discord_rpc.DiscordRpc()
rpc_data = discord_rpc.RpcSaveData()
start_time = int(time.time())
AUTOUPDATE_SUPPORT_SOURCE = ["github"]

if local_language in sChinese_lang_id:
    now_ver_label_fmt = "当前版本: {0}"
    latest_ver_label_fmt = "最新版本: {0}"
elif local_language in tChinese_lang_id:
    now_ver_label_fmt = "當前版本: {0}"
    latest_ver_label_fmt = "最新版本: {0}"
else:
    now_ver_label_fmt = "Now Version: {0}"
    latest_ver_label_fmt = "Latest Version: {0}"

last_sub_close_time = 0

uma_server = http_server.UmaServer()

class AutoUpdateError(Exception):
    pass


class Qm2(QMainWindow):
    def __init__(self):
        super(Qm2, self).__init__()
        self.close_callback = None
        self.quit_callback = None

    def add_close_callback(self, func):
        self.close_callback = func

    def add_quit_callback(self, func):
        self.quit_callback = func

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        if a0.type() == QtCore.QEvent.WindowStateChange:
            if self.windowState() == QtCore.Qt.WindowMinimized:
                if self.close_callback is not None:
                    self.close_callback()
                self.showMinimized()
                self.setWindowFlags(QtCore.Qt.SplashScreen)
                self.show()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        # if 0 <= time.time() - last_sub_close_time < 1.5:
        #     a0.ignore()
        #     return

        # req = QtWidgets.QMessageBox.information(self, "Exit", "Are you sure?",
        #                                         QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        req = QtWidgets.QMessageBox.Yes
        if req != QtWidgets.QMessageBox.Yes:
            a0.ignore()
        else:
            if self.quit_callback is not None:
                self.quit_callback()
            a0.accept()
            QtWidgets.qApp.quit()
            os._exit(0)


class QMn(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(QMn, self).__init__(*args, **kwargs)
        self.onclose_callback = None
        self.onshow_callback = None

    def set_onclose_callback(self, func):
        self.onclose_callback = func

    def set_onshow_callback(self, func):
        self.onshow_callback = func

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        global last_sub_close_time
        last_sub_close_time = time.time()
        if self.onclose_callback is not None:
            self.onclose_callback()

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        super().showEvent(a0)
        if self.onshow_callback is not None:
            self.onshow_callback()


class UIChange(QWidget):
    rpc_disconnect_signal = QtCore.pyqtSignal()
    rpc_change_connect_btn_text_signal = QtCore.pyqtSignal(str)
    now_version_label_signal = QtCore.pyqtSignal(str)
    latest_version_label_signal = QtCore.pyqtSignal(str)
    update_btn_signal = QtCore.pyqtSignal(str)
    update_btn_click_signal = QtCore.pyqtSignal()
    show_message_signal = QtCore.pyqtSignal(str, str)
    update_finish_signal = QtCore.pyqtSignal()
    update_dmm_log = QtCore.pyqtSignal(str)
    update_dmm_login_btn_signal = QtCore.pyqtSignal(str)
    dmm_login_success_signal = QtCore.pyqtSignal(str)
    dmm_button_login_cache_signal = QtCore.pyqtSignal(str)
    update_btn_enable = QtCore.pyqtSignal(bool)
    kb_event_pass = QtCore.pyqtSignal()
    set_files_update_btn_signal = QtCore.pyqtSignal(bool)
    set_live_hook_btn_signal = QtCore.pyqtSignal(bool)
    start_update_local_files_signal = QtCore.pyqtSignal(str, dict, bool)

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.tlg_http_port = None

        self.more_settings_i18n_file = None
        if local_language in sChinese_lang_id + tChinese_lang_id:
            self.trans = QtCore.QTranslator()
            self.trans2 = QtCore.QTranslator()
            self.trans3 = QtCore.QTranslator()
            self.trans4 = QtCore.QTranslator()
            self.trans5 = QtCore.QTranslator()
            self.trans6 = QtCore.QTranslator()

            if local_language in sChinese_lang_id:
                self.trans.load(":/trans/main_ui.qm")
                self.trans2.load(":/trans/ui_rpc.qm")
                self.trans3.load(":/trans/ui_config.qm")
                self.trans4.load(":/trans/ui_dmmlogin.qm")
                self.trans5.load(":/trans/more_ui.qm")
                self.trans6.load(":/trans/window_settings.qm")
                self.more_settings_i18n_file = "./localized_data/config_schema/text_data_info_i18n_zh.json"
            if local_language in tChinese_lang_id:
                self.trans.load(":/trans/ts_zh_tw/main_ui_zh_tw.qm")
                self.trans2.load(":/trans/ts_zh_tw/ui_rpc_zh_tw.qm")
                self.trans3.load(":/trans/ts_zh_tw/ui_config_zh_tw.qm")
                self.trans4.load(":/trans/ts_zh_tw/ui_dmmlogin_zh_tw.qm")
                self.trans5.load(":/trans/ts_zh_tw/more_ui_zh_tw.qm")
                self.trans6.load(":/trans/ts_zh_tw/window_settings.qm")
                self.more_settings_i18n_file = "./localized_data/config_schema/text_data_info_i18n_zh_tw.json"

            self.app.installTranslator(self.trans)
            self.app.installTranslator(self.trans2)
            self.app.installTranslator(self.trans3)
            self.app.installTranslator(self.trans4)
            self.app.installTranslator(self.trans5)
            self.app.installTranslator(self.trans6)

        try:
            self.listener = keyboard.Listener(on_press=self.check_hotk)
        except:
            pass
        self.listener_status = 0
        self.listener_steps = [keyboard.Key.up, keyboard.Key.up, keyboard.Key.down, keyboard.Key.down,
                               keyboard.Key.left, keyboard.Key.right, keyboard.Key.left, keyboard.Key.right,
                               keyboard.KeyCode(char='b'), keyboard.KeyCode(char='a'),
                               keyboard.KeyCode(char='b'), keyboard.KeyCode(char='a')]
        self._more_settings_ui_inited = False
        self.more_settings_i18n_data = {}
        if self.more_settings_i18n_file is not None:
            if os.path.isfile(self.more_settings_i18n_file):
                with open(self.more_settings_i18n_file, "r", encoding="utf8") as f:
                    self.more_settings_i18n_data = json.load(f)

        super(UIChange, self).__init__()
        self.uma_path = os.path.abspath(".").replace("\\", "/")
        self.cache_config_changes = None
        self.uma_load_cmd = None

        self.window = Qm2()
        self.window.setWindowIcon(QtGui.QIcon(":/img/jia.ico"))
        self.ui = MainUI()
        self.ui.setupUi(self.window)

        self.mti = qtray.TrayIcon(self.window, self)

        self.window_config = QMn(self.window)
        self.window_config.setWindowIcon(QtGui.QIcon(":/img/jileba.ico"))
        self.ui_config = ConfigUI()
        self.ui_config.setupUi(self.window_config)

        self.window_rpc = QMn(self.window)
        self.window_rpc.setWindowIcon(QtGui.QIcon(":/img/jishao.ico"))
        self.ui_rpc = RPCUI()
        self.ui_rpc.setupUi(self.window_rpc)

        self.window_moresettings = QMn(self.window)
        self.window_moresettings.setWindowIcon(QtGui.QIcon(":/img/jia.ico"))
        self.window_moresettings.set_onclose_callback(self.more_settings_close)
        self.window_moresettings.set_onshow_callback(self.more_settings_show)
        self.ui_moresettings = MoreSettingsUI()
        self.ui_moresettings.setupUi(self.window_moresettings)
        self.ui_moresettings.checkBox_unlock_plain_dress.setChecked(
            rpc_data.more_settings_data.get("unlock_plain_dress", False)
        )

        self.window_windowsettings = QMn(self.window)
        self.window_windowsettings.setWindowIcon(QtGui.QIcon(":/img/jishao.ico"))
        self.ui_windowsettings = WindowSettingsUI()
        self.ui_windowsettings.setupUi(self.window_windowsettings)

        self.check_inner()

        self.window.add_close_callback(self.close_other_window)  # 主窗口最小化时关闭其它窗口
        self.window.add_quit_callback(self.main_on_quit)

        self.config_form = self.get_schema_form()
        self.load_args()
        if self.config_form is None:
            self.ui.pushButton_config_settings.setEnabled(False)

        # self.regist_callback()
        # self.init_gui()
        self._rpc_btnc_running = False
        self._autoupdate_source = None
        self._autoupdate_url = None
        self._autoupdate_response_cache = None
        self._fastreboot_btn_clicked_time = 0
        self._fastreboot_btn_is_long = False

        self.checkBox_more_info = {}
        self.text_data_info = {}
        self.aspect_ratio_set = 16.0 / 9.0
        self.last_window_item_text = None
        self.window_settings_key_edit_cache = {}

    def server_load_onfailed(self, errinfo: str):
        self.show_message_signal.emit("Start Server Error", errinfo)

    def load_args(self):
        args = sys.argv
        if len(args) > 1:
            for i in args:
                if i.startswith("--tlgport="):
                    self.tlg_http_port = i[len("--tlgport="):]
                    _cp = i
                    break

            if self.tlg_http_port is not None:
                try:
                    _tlg_port = int(self.tlg_http_port)
                    uma_server.start_server(_tlg_port, _tlg_port + 1, self.server_load_onfailed)
                except BaseException as e:
                    self.show_message_box("Exception Occurred", f"Start server failed!\n{e}")

                self.more_settings_save()
                if f"--tlgport={self.tlg_http_port}" in args:
                    args.remove(f"--tlgport={self.tlg_http_port}")

            self.ui.pushButton_reload_config.setEnabled(self.tlg_http_port is not None)

            if len(args) > 1:
                if "umamusume.exe" in args[1]:
                    base_path = os.path.split(args[1])[0]
                    if base_path != "":
                        self.uma_path = base_path
                    self.uma_load_cmd = "\"" + "\" \"".join(args[1:]) + "\""
                    self.ui.pushButton_fast_reboot.setEnabled(True)
                    self.ui.pushButton_fast_reboot.setToolTip(self.uma_load_cmd)

        if os.path.isfile(f"{self.uma_path}/umamusume.exe"):
            self.ui.pushButton_fast_login.setEnabled(True)
        else:
            self.ui.pushButton_fast_login.setEnabled(False)

        self.check_uma_window_resize()

    def load_rules(self):
        reg = QtCore.QRegExp("-?\\d+$")
        validator = QtGui.QRegExpValidator(self)
        validator.setRegExp(reg)
        self.ui_windowsettings.lineEdit_move_step.setValidator(validator)
        self.ui_windowsettings.lineEdit_x_hori.setValidator(validator)
        self.ui_windowsettings.lineEdit_y_hori.setValidator(validator)
        self.ui_windowsettings.lineEdit_w_hori.setValidator(validator)
        self.ui_windowsettings.lineEdit_h_hori.setValidator(validator)
        self.ui_windowsettings.lineEdit_x_vert.setValidator(validator)
        self.ui_windowsettings.lineEdit_y_vert.setValidator(validator)
        self.ui_windowsettings.lineEdit_w_vert.setValidator(validator)
        self.ui_windowsettings.lineEdit_h_vert.setValidator(validator)

    def regist_callback(self):
        self.ui.pushButton_config_settings.clicked.connect(self.show_config_settings_window)
        self.ui_config.pushButton_save.clicked.connect(self.save_config_changes)
        self.ui.pushButton_about_father.clicked.connect(lambda *x: webbrowser.open(
            "https://github.com/MinamiChiwa/Trainers-Legend-G"
        ))
        self.ui.pushButton_about_this.clicked.connect(lambda *x: webbrowser.open(
            "https://github.com/chinosk114514/Trainers-Legend-G-External-Plugin"
        ))
        self.ui.pushButton_fast_reboot.clicked.connect(self.game_fast_reboot)
        self.ui.pushButton_fast_reboot.pressed.connect(self.fast_reboot_btn_press)
        self.ui.pushButton_fast_reboot.released.connect(self.fast_reboot_btn_released)
        self.ui.pushButton_discord_rpc.clicked.connect(self.show_rpc_window)
        self.ui_rpc.comboBox_char_icon.activated.connect(self.rpc_char_icon_onclick)
        self.ui_rpc.pushButton_connect.clicked.connect(self.rpc_button_connect_onclick)
        self.ui_rpc.pushButton_save_changes.clicked.connect(self.rpc_button_save_onclick)
        self.ui_rpc.textEdit_text_1.textChanged.connect(self.textedit_lenth_limit_on_change(self.ui_rpc.textEdit_text_1,
                                                                                            127))
        self.ui_rpc.textEdit_text_2.textChanged.connect(self.textedit_lenth_limit_on_change(self.ui_rpc.textEdit_text_2,
                                                                                            127))
        self.rpc_disconnect_signal.connect(self.rpc_on_disconnect)
        rpc.set_close_server_callback(lambda *x: self.rpc_disconnect_signal.emit())
        self.rpc_change_connect_btn_text_signal.connect(self.change_rpc_connect_btn_string)
        self.now_version_label_signal.connect(lambda x: self.ui.label_version_now.setText(x))
        self.latest_version_label_signal.connect(lambda x: self.ui.label_version_latest.setText(x))
        self.update_btn_signal.connect(self.change_update_button_text)
        self.ui.pushButton_plugin_update.clicked.connect(self.update_button_onclick)
        self.show_message_signal.connect(lambda x, y: self.show_message_box(x, y))
        self.update_finish_signal.connect(self.update_finish)
        self.update_btn_click_signal.connect(lambda *x: self.ui.pushButton_plugin_update.click())
        self.ui.pushButton_reload_config.clicked.connect(self.reload_config)
        self.update_btn_enable.connect(lambda x: self.ui.pushButton_plugin_update.setEnabled(x))
        self.kb_event_pass.connect(self.kb_pass)

        self.ui.pushButton_more.clicked.connect(self.more_settings_ui_show)
        self.ui_moresettings.pushButton_save.clicked.connect(self.more_settings_save)
        self.ui_moresettings.pushButton_unlock_dress.clicked.connect(self.unlock_cloth)
        self.ui_moresettings.pushButton_check_pwd.clicked.connect(self.check_inpwd)
        self.ui_moresettings.pushButton_window_settings.clicked.connect(self.window_settings_show)

        self.ui_windowsettings.pushButton_refresh.clicked.connect(self.refresh_window_position)
        self.ui_windowsettings.pushButton_up.clicked.connect(self.move_window(1))
        self.ui_windowsettings.pushButton_left.clicked.connect(self.move_window(2))
        self.ui_windowsettings.pushButton_right.clicked.connect(self.move_window(3))
        self.ui_windowsettings.pushButton_down.clicked.connect(self.move_window(4))
        self.ui_windowsettings.pushButton_sync_pos.clicked.connect(self.sync_pos_data)
        self.ui_windowsettings.pushButton_update_pos.clicked.connect(self.update_window_positoon)
        self.ui_windowsettings.lineEdit_w_hori.textChanged.connect(self.window_text_changed(0))
        self.ui_windowsettings.lineEdit_h_hori.textChanged.connect(self.window_text_changed(1))
        self.ui_windowsettings.lineEdit_x_hori.textChanged.connect(self.window_text_changed(-1))
        self.ui_windowsettings.lineEdit_y_hori.textChanged.connect(self.window_text_changed(-1))
        self.ui_windowsettings.lineEdit_w_vert.textChanged.connect(self.window_text_changed(2))
        self.ui_windowsettings.lineEdit_h_vert.textChanged.connect(self.window_text_changed(3))
        self.ui_windowsettings.lineEdit_x_vert.textChanged.connect(self.window_text_changed(-1))
        self.ui_windowsettings.lineEdit_y_vert.textChanged.connect(self.window_text_changed(-1))
        self.ui_windowsettings.pushButton_set_ratio.clicked.connect(self.set_ratio_clicked)
        self.ui_windowsettings.comboBox_window_size_set.currentIndexChanged.connect(self.refresh_settings_group)
        self.ui_windowsettings.comboBox_window_size_set.editTextChanged.connect(self.settings_group_name_changed)
        self.ui_windowsettings.pushButton_add_set.clicked.connect(self.add_settings_item)
        self.ui_windowsettings.pushButton_remove_set.clicked.connect(self.remove_settings_item)
        self.ui.pushButton_set_api.clicked.connect(self.change_files_api)
        self.ui.pushButton_update_files.clicked.connect(self.check_files_update)
        self.set_files_update_btn_signal.connect(lambda x: self.ui.pushButton_update_files.setEnabled(x))
        self.start_update_local_files_signal.connect(self.start_update_local_file)
        self.ui_moresettings.pushButton_live_pos_hook.clicked.connect(self.all_live_pos_hook_onclick)
        self.set_live_hook_btn_signal.connect(lambda x: self.ui_moresettings.pushButton_live_pos_hook.setEnabled(x))

        self.load_rules()

    def close_other_window(self):
        mwindows = [self.window_rpc, self.window_config]
        for w in mwindows:
            if w.isVisible() or w.isMinimized():
                w.close()

    def main_on_quit(self):
        self.mti.quit()

    def init_gui(self):
        self.get_update_version()
        self.load_rpc_ui()
        if rpc_data.auto_conn:
            self.ui_rpc.pushButton_connect.click()

    def game_fast_reboot(self, *args):
        if self._fastreboot_btn_is_long:
            self._fastreboot_btn_is_long = False
            return

        if self.uma_load_cmd is not None:
            with open("reboot.bat", "w", encoding=None) as f:
                f.write(f"""@echo off
setlocal
taskkill /im "umamusume.exe" >NUL

:waitloop
tasklist | find /i "umamusume.exe" >NUL
if %ERRORLEVEL% == 0 goto waitloop

start "" {self.uma_load_cmd}
del reboot.bat & exit"""
                        )
            os.system("start reboot.bat & exit")
            self.setVisible(False)
            self.main_on_quit()
            QtWidgets.qApp.quit()
            os._exit(0)

    def fast_reboot_btn_press(self, *args):
        self._fastreboot_btn_clicked_time = time.time()

    def fast_reboot_btn_released(self, *args):
        time_passed = time.time() - self._fastreboot_btn_clicked_time
        if time_passed > 1.2:
            try:
                pyperclip.copy(self.uma_load_cmd)
                self.show_message_box("Copy Load Parameter", f"Copied: {self.uma_load_cmd}")
            except BaseException as e:
                self.show_message_box("Copy Load Parameter Failed", f"Copy Content: {self.uma_load_cmd}\n"
                                                                    f"Error: {e}")
            self._fastreboot_btn_is_long = True

    def save_config_changes(self, *args):
        if self.cache_config_changes is not None:
            if os.path.isfile(f"{self.uma_path}/config.json"):
                with open(f"{self.uma_path}/config.json", "r", encoding="utf8") as f:
                    orig_data = json.load(f)

                with open(f"{self.uma_path}/config.json", "w", encoding="utf8") as f:
                    orig_data.update(self.cache_config_changes)
                    json.dump(orig_data, f, ensure_ascii=False, indent=4)
        self.window_config.close()
        self.reload_config()

    def show_config_settings_window(self, *args):
        self.cache_config_changes = None
        self.load_schma_form()
        self.window_config.show()

    def show_message_box(self, title, text, btn=QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No):
        return QtWidgets.QMessageBox.information(self.window, title, text, btn)

    def load_schma_form(self):
        self.config_form = self.get_schema_form()
        self.ui_config.scrollArea_config.setWidget(self.config_form)

    @staticmethod
    def textedit_lenth_limit_on_change(textedit: QtWidgets.QTextEdit, limit: int):
        def inner(*args):
            if len(textedit.toPlainText()) > limit:
                textedit.setText(textedit.toPlainText()[:limit])

        return inner

    def get_schema_form(self):
        base_path = self.uma_path

        if local_language in sChinese_lang_id:
            schema_file = f"{base_path}/localized_data/config_schema/config.schema.json"
        elif local_language in tChinese_lang_id:
            schema_file = f"{base_path}/localized_data/config_schema/config_zh_tw.schema.json"
        else:
            schema_file = f"{base_path}/localized_data/config_schema/config_en.schema.json"
        if not os.path.isfile(schema_file):
            schema_file = f"{base_path}/localized_data/config_schema/config.schema.json"

        if os.path.isfile(schema_file):
            builder = WidgetBuilder()
            with open(schema_file, "r", encoding="utf8") as f:
                schema = json.load(f)
            form = builder.create_form(schema, None)

            if os.path.isfile(f"{base_path}/config.json"):
                with open(f"{base_path}/config.json", "r", encoding="utf8") as f:
                    json_data = json.load(f)
                    form.widget.state = json_data
                    self.ui_moresettings.checkBox_bypass_205.setChecked(json_data.get("bypass_live_205", False))
            else:
                form.widget.state = {}

            form.widget.on_changed.connect(self.config_form_onchanged)
            return form

    def config_form_onchanged(self, data, *args):
        self.cache_config_changes = data

    def show_rpc_window(self, *args):
        self.window_rpc.show()
        self.load_rpc_ui()

    def load_rpc_ui(self):
        self.ui_rpc.comboBox_char_icon.clear()
        for uma_name in uma_icon_data.icon_index:
            self.ui_rpc.comboBox_char_icon.addItem(uma_name)

        self.ui_rpc.comboBox_char_icon.setCurrentText(rpc_data.chara_icon_name)
        self.ui_rpc.lineEdit_char_icon.setText(rpc_data.chara_icon_id)
        self.ui_rpc.textEdit_text_1.setText(rpc_data.chara_icon_text1)
        self.ui_rpc.textEdit_text_2.setText(rpc_data.chara_icon_text2)
        self.ui_rpc.checkBox_show_timestamp.setChecked(rpc_data.chara_show_timestamp)
        self.ui_rpc.checkBox_auto_conn.setChecked(rpc_data.auto_conn)
        self.update_rpc_data()

    def rpc_char_icon_onclick(self, selectindex, *args):
        self.ui_rpc.lineEdit_char_icon.setText(
            uma_icon_data.icon_index[self.ui_rpc.comboBox_char_icon.currentText()]
        )

    def rpc_button_save_onclick(self, *args):
        rpc_data.chara_icon_name = self.ui_rpc.comboBox_char_icon.currentText()
        rpc_data.chara_icon_id = self.ui_rpc.lineEdit_char_icon.text()
        rpc_data.chara_icon_text1 = self.ui_rpc.textEdit_text_1.toPlainText()
        rpc_data.chara_icon_text2 = self.ui_rpc.textEdit_text_2.toPlainText()
        rpc_data.chara_show_timestamp = self.ui_rpc.checkBox_show_timestamp.isChecked()
        rpc_data.auto_conn = self.ui_rpc.checkBox_auto_conn.isChecked()
        rpc_data.write_config()
        self.update_rpc_data()

    @staticmethod
    def update_rpc_data():
        rpc.set_text(state=rpc_data.chara_icon_text2, details=rpc_data.chara_icon_text1,
                     large_icon_text="ウマ娘 プリティーダービー",
                     small_icon_text=rpc_data.chara_icon_name)
        rpc.set_image(large_image="icon_main", small_image=rpc_data.chara_icon_id)
        rpc.set_start_time(start_time if rpc_data.chara_show_timestamp else None)

    def rpc_button_connect_onclick(self, *args):
        state = rpc.change_state()
        if state == "started":

            def _inner():
                self.rpc_change_connect_btn_text_signal.emit("false")
                for i in range(10, 0, -1):
                    self.rpc_change_connect_btn_text_signal.emit(f"Connect To Discord ({i})")
                    time.sleep(1)
                self.rpc_change_connect_btn_text_signal.emit("true")
                self.ui_rpc.pushButton_connect.setText("Disconnect Discord")

            Thread(target=_inner).start()

        elif state == "closed":
            self.ui_rpc.pushButton_connect.setText("Connect To Discord")

    def rpc_on_disconnect(self):
        self.ui_rpc.pushButton_connect.setText("Connect To Discord")

        def _inner():
            if self._rpc_btnc_running:
                return
            self._rpc_btnc_running = True
            self.rpc_change_connect_btn_text_signal.emit("false")
            for i in range(10, 0, -1):
                self.rpc_change_connect_btn_text_signal.emit(f"Disconnect Discord ({i})")
                time.sleep(1)
            self.rpc_change_connect_btn_text_signal.emit(f"Connect To Discord")
            self.rpc_change_connect_btn_text_signal.emit("true")
            self._rpc_btnc_running = False

        Thread(target=_inner).start()

    def change_rpc_connect_btn_string(self, s: str):
        if s == "false":
            self.ui_rpc.pushButton_connect.setEnabled(False)
        elif s == "true":
            self.ui_rpc.pushButton_connect.setEnabled(True)
        else:
            self.ui_rpc.pushButton_connect.setText(s)

    def get_update_version(self):
        def _():
            self.update_btn_signal.emit("false")

            version_txt_path = f"{self.uma_path}/version.txt"
            config_path = f"{self.uma_path}/config.json"
            if os.path.isfile(version_txt_path):
                with open(version_txt_path, "r", encoding="utf8") as f:
                    current_version = f.read().strip()
            else:
                current_version = "Unknown"

            self.now_version_label_signal.emit(now_ver_label_fmt.format(current_version))
            self.latest_version_label_signal.emit(latest_ver_label_fmt.format("Loading..."))

            if not os.path.isfile(config_path):
                self.update_btn_signal.emit("false")
                self.latest_version_label_signal.emit(latest_ver_label_fmt.format("Unknown"))
                return

            with open(config_path, "r", encoding="utf8") as f:
                data = json.load(f)
            try:
                if "autoUpdate" in data:
                    if "source" in data["autoUpdate"] and "path" in data["autoUpdate"]:
                        if data["autoUpdate"]["source"] not in AUTOUPDATE_SUPPORT_SOURCE:
                            raise AutoUpdateError("")

                        self._autoupdate_source = data["autoUpdate"]["source"]
                        self._autoupdate_url = data["autoUpdate"]["path"]
                        response = requests.get(self._autoupdate_url)
                        data = json.loads(response.text)
                        latest_version = data["tag_name"].strip()
                        self.latest_version_label_signal.emit(latest_ver_label_fmt.format(latest_version))
                        if latest_version != current_version:
                            if os.path.isfile(f"{self.uma_path}/umamusume.exe"):
                                self._autoupdate_response_cache = data
                                self.update_btn_signal.emit("true")
                                self.update_btn_click_signal.emit()
                    else:
                        raise AutoUpdateError("")
                else:
                    raise AutoUpdateError("")
            except AutoUpdateError:
                self.update_btn_signal.emit("false")
                self.latest_version_label_signal.emit(latest_ver_label_fmt.format("Unknown"))
                return

        Thread(target=_).start()
        self.check_files_update(show_msgbox=False)

    def change_update_button_text(self, s: str):
        if s == "false":
            self.ui.pushButton_plugin_update.setEnabled(False)
        elif s == "true":
            self.ui.pushButton_plugin_update.setEnabled(True)
        else:
            self.ui.pushButton_plugin_update.setText(s)

    def update_button_onclick(self, *args):
        save_name = f"{self.uma_path}/auto_p_update.zip"

        def download_file():
            config_old = {}
            try:
                if os.path.isfile(f"{self.uma_path}/config.json"):
                    with open(f"{self.uma_path}/config.json", "r", encoding="utf8") as fc:
                        config_old = json.load(fc)

                for i in self._autoupdate_response_cache["assets"]:
                    down_url = i["browser_download_url"]
                    file_name = i["name"]
                    if file_name.endswith(".zip"):
                        url = down_url
                        self.update_btn_signal.emit("false")
                        resp = requests.get(url, stream=True)
                        total = int(resp.headers.get('content-length', 0))
                        with open(save_name, "wb") as f:
                            down_size = 0
                            for data in resp.iter_content(chunk_size=1024):
                                size = f.write(data)
                                down_size += size
                                if total == 0:
                                    self.update_btn_signal.emit("downloading")
                                else:
                                    self.update_btn_signal.emit(f"{int(down_size / total * 100)}%")
                        self.update_btn_signal.emit("unzipping")
                        time.sleep(0.5)
                        unzip_file.unzip_file(save_name, f"{self.uma_path}/")
                        os.remove(save_name)

                self.update_btn_signal.emit("Done.")
                self.update_finish_signal.emit()
            except BaseException as ex:
                self.update_btn_signal.emit("Failed.")
                self.update_btn_enable.emit(True)
                self.show_message_signal.emit("Update Failed!", f"{repr(ex)}\n\n"
                                                                f"缓存文件已保存: auto_p_update.zip")
            finally:
                if os.path.isfile(f"{self.uma_path}/config.json"):
                    with open(f"{self.uma_path}/config.json", "r", encoding="utf8") as fc:
                        config_new = json.load(fc)
                    config_update = unzip_file.config_update(config_old, config_new)
                    with open(f"{self.uma_path}/config.json", "w", encoding="utf8") as fc:
                        json.dump(config_update, fc, indent=4, ensure_ascii=False)

        def unzip_from_cache():
            config_old = {}
            try:
                if os.path.isfile(f"{self.uma_path}/config.json"):
                    with open(f"{self.uma_path}/config.json", "r", encoding="utf8") as fc:
                        config_old = json.load(fc)

                self.update_btn_signal.emit("unzipping")
                time.sleep(0.5)
                unzip_file.unzip_file(save_name, f"{self.uma_path}/")
                self.update_btn_signal.emit("Done.")
                self.update_finish_signal.emit()
            except BaseException as e:
                self.update_btn_signal.emit("Failed.")
                self.update_btn_enable.emit(True)
                self.show_message_signal.emit("Exception Occurred", repr(e))
            finally:
                if os.path.isfile(f"{self.uma_path}/config.json"):
                    with open(f"{self.uma_path}/config.json", "r", encoding="utf8") as fc:
                        config_new = json.load(fc)
                    config_update = unzip_file.config_update(config_old, config_new)
                    with open(f"{self.uma_path}/config.json", "w", encoding="utf8") as fc:
                        json.dump(config_update, fc, indent=4, ensure_ascii=False)
                os.remove(save_name)
            return

        if self._autoupdate_response_cache is None:
            return
        res = self.show_message_box("Plugin Update", f"{self._autoupdate_response_cache['body']}")
        if res == QtWidgets.QMessageBox.Yes:
            self.ui.pushButton_plugin_update.setEnabled(False)
            open(f"{self.uma_path}/dontcloseext.lock", "wb").close()
            with open("gkill.bat", "w", encoding="utf8") as f:
                f.write(f"""@echo off
            setlocal
            taskkill /im "umamusume.exe"
            del gkill.bat & exit"""
                        )
            os.system("gkill.bat")

            if os.path.isfile(save_name):
                useCache = self.show_message_box("Plugin Update",
                                                 "检测到残留的更新文件, 可能是您上次更新出现错误, 是否尝试重新解压?\n"
                                                 "Residual update file detected. It may be an error occurred"
                                                 " in your last update. Would you like to try unzip again?")
                if useCache == QtWidgets.QMessageBox.Yes:
                    Thread(target=unzip_from_cache).start()
                    return
            Thread(target=download_file).start()

    def update_finish(self, *args):
        resu = self.show_message_box("更新完成", "更新完成, 是否立即启动游戏?")
        if resu == QtWidgets.QMessageBox.Yes:
            if self.ui.pushButton_fast_reboot.isEnabled():
                self.ui.pushButton_fast_reboot.click()

    def reload_config(self, *args):
        if self.tlg_http_port is not None:
            rp = self.show_message_box("Reload Config", "Reload Config Right Now?")
            if rp == QtWidgets.QMessageBox.Yes:
                self.more_settings_save()
                def _():
                    try:
                        resp = requests.post(f"http://127.0.0.1:{self.tlg_http_port}/sets",
                                             headers={'Content-Type': 'application/json'},
                                             data=json.dumps({"type": "reload_all"}))
                        if resp.status_code == 200:
                            self.show_message_signal.emit("Reload Success", resp.text)
                        else:
                            self.show_message_signal.emit("Reload Failed", resp.text)
                    except BaseException as e:
                        self.show_message_signal.emit("Reload Failed", repr(e))

                Thread(target=_).start()

        else:
            self.show_message_box("Reload Config", "Please Restart the Game.", QtWidgets.QMessageBox.Yes)

    def more_settings_trans(self, kw1: str, kw2=None):
        if kw1 in self.more_settings_i18n_data:
            if isinstance(self.more_settings_i18n_data[kw1], dict):
                if kw2 is None:
                    return kw1
                else:
                    if kw2 in self.more_settings_i18n_data[kw1]:
                        return str(self.more_settings_i18n_data[kw1][kw2])
            elif isinstance(self.more_settings_i18n_data[kw1], str):
                return self.more_settings_i18n_data[kw1]
        return kw1 if kw2 is None else kw2

    def more_settings_ui_show(self, *args):
        try:
            self.more_settings_ui_init()
        except BaseException as e:
            self.show_message_box("Exception Occurred", f"function: more_settings_ui_show - more_settings_ui_init\n"
                                                        f"{repr(e)}")
        self.window_moresettings.show()

    def more_settings_ui_init(self, *args):
        def get_label(parent, text, tooltip, min_wid=250, max_wid=250):
            _label = QtWidgets.QLabel(parent)
            _label.setToolTip(tooltip)
            _label.setText(text)
            if min_wid is not None:
                _label.setMinimumWidth(min_wid)
            if max_wid is not None:
                _label.setMaximumWidth(max_wid)
            return _label


        self.checkBox_more_info = {}

        if not os.path.isfile("./localized_data/config_schema/text_data_info.json"):
            return

        with open("./localized_data/config_schema/text_data_info.json", "r", encoding="utf8") as f:
            self.text_data_info = json.load(f)
            text_data_info = self.text_data_info

        widg = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()

        for k in text_data_info:
            if k == "bool":
                gbg = QtWidgets.QGroupBox(widg)
                gbg.setTitle("General")
                sub_bool_layout = QtWidgets.QFormLayout(gbg)
                for i in text_data_info["bool"]:
                    label = get_label(gbg, self.more_settings_trans(i), i)
                    aa = QtWidgets.QCheckBox(gbg)
                    sub_bool_layout.addRow(label, aa)

                    if i in rpc_data.more_settings_data:
                        aa.setChecked(bool(rpc_data.more_settings_data[i]))

                    gbg.setLayout(sub_bool_layout)
                    self.checkBox_more_info[i] = aa
                layout.addRow(gbg)

            if k not in ["bool", "boolable"]:
                if isinstance(text_data_info[k], dict):
                    gb = QtWidgets.QGroupBox(widg)
                    gb.setTitle(k)
                    self.checkBox_more_info[k] = {}

                    sub_layout = QtWidgets.QFormLayout(gb)
                    if k in text_data_info.get("boolable", []):
                        label = get_label(gb, self.more_settings_trans("closeAll"), None)
                        aa = QtWidgets.QCheckBox(gb)
                        sub_layout.addRow(label, aa)
                        if k in rpc_data.more_settings_data:
                            if "closeAll" in rpc_data.more_settings_data[k]:
                                aa.setChecked(bool(rpc_data.more_settings_data[k]["closeAll"]))
                        self.checkBox_more_info[k]["closeAll"] = aa

                    for kw in text_data_info[k]:
                        label = get_label(gb, self.more_settings_trans(k, kw), kw)
                        aa = QtWidgets.QCheckBox(gb)
                        sub_layout.addRow(label, aa)
                        if k in rpc_data.more_settings_data:
                            if kw in rpc_data.more_settings_data[k]:
                                aa.setChecked(bool(rpc_data.more_settings_data[k][kw]))
                        self.checkBox_more_info[k][kw] = aa

                    gb.setLayout(sub_layout)
                    layout.addRow(gb)

        widg.setLayout(layout)
        self.ui_moresettings.scrollArea_trans_settings.setWidget(widg)
        self._more_settings_ui_inited = True

    def more_settings_save(self, *args):
        try:
            is_enable_unlock_plain_cloth = self.ui_moresettings.checkBox_unlock_plain_dress.isChecked()
            uma_server.set_enable_unlock_plain_cloth(is_enable_unlock_plain_cloth)

            if os.path.isfile(f"{self.uma_path}/config.json"):
                with open(f"{self.uma_path}/config.json", "r", encoding="utf8") as f:
                    config_data = json.load(f)
                orig_stat = config_data.get("bypass_live_205", False)
                if "bypass_live_205" in config_data:
                    config_data["bypass_live_205"] = self.ui_moresettings.checkBox_bypass_205.isChecked()
                elif self.ui_moresettings.checkBox_bypass_205.isChecked():
                    config_data["bypass_live_205"] = True

                if orig_stat != self.ui_moresettings.checkBox_bypass_205.isChecked():
                    with open(f"{self.uma_path}/config.json", "w", encoding="utf8") as fw:
                        fw.write(json.dumps(config_data, indent=4, ensure_ascii=False))
                    self.reload_config()

            if not self._more_settings_ui_inited:
                self.more_settings_ui_init()

            result = {}
            for k in self.checkBox_more_info:
                if isinstance(self.checkBox_more_info[k], dict):
                    result[k] = {}
                    for kw in self.checkBox_more_info[k]:
                        if isinstance(self.checkBox_more_info[k][kw], QtWidgets.QCheckBox):
                            result[k][kw] = self.checkBox_more_info[k][kw].isChecked()
                        else:
                            print("暂不支持两层以上的嵌套")
                elif isinstance(self.checkBox_more_info[k], QtWidgets.QCheckBox):
                    result[k] = self.checkBox_more_info[k].isChecked()

            rpc_data.more_settings_data.update(result)
            rpc_data.more_settings_data["unlock_plain_dress"] = is_enable_unlock_plain_cloth
            rpc_data.write_config()
            self.result_to_post_data(result)
            if self.window_moresettings.isActiveWindow():
                self.window_moresettings.close()
        except BaseException as e:
            self.show_message_box("Exception Occurred", f"function: more_settings_save\n{repr(e)}")

    def result_to_post_data(self, result: dict):
        body = {}
        for k in self.text_data_info:
            if k == "bool":
                for i in self.text_data_info["bool"]:
                    if i in result:
                        if isinstance(result[i], bool):
                            body[i] = result[i]
            elif k == "boolable":
                continue
            else:
                body[k] = []
                if k in result:
                    if isinstance(result[k], dict):
                        if k in self.text_data_info.get("boolable", []):
                            if result[k].get("closeAll", False):
                                body[k] = True
                                continue
                        for kw in result[k]:
                            if result[k][kw]:
                                if kw in self.text_data_info[k]:
                                    body[k] += self.text_data_info[k][kw]

        def _():
            try:
                if self.tlg_http_port is None:
                    return
                requests.post(f"http://127.0.0.1:{self.tlg_http_port}/set_untrans",
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(body))
            except BaseException as e:
                self.show_message_signal.emit("Set Trans Failed", repr(e))

        Thread(target=_).start()

    def unlock_cloth(self, *argsm):
        try:
            res = self.show_message_box("Unlock Dress", f"Need to quit the game first, do you want to continue?")
            if res == QtWidgets.QMessageBox.Yes:
                open(f"{self.uma_path}/dontcloseext.lock", "wb").close()
                os.system("taskkill /im \"umamusume.exe\"")
                time.sleep(2)
                ut = uma_tools.UmaTools()
                ut.unlock_live_dress()
                rs2 = self.show_message_box("Unlock Success", f"Success!\nRestart Game?")
                if rs2 == QtWidgets.QMessageBox.Yes:
                    self.game_fast_reboot()
        except BaseException as e:
            rs2 = self.show_message_box("Exception Occurred", f"Unlocking failed or you already unlocked."
                                                              f"\n{repr(e)}\n\nRestart Game?")
            if rs2 == QtWidgets.QMessageBox.Yes:
                self.game_fast_reboot()

    def more_settings_show(self):
        try:
            self.listener.start()
        except BaseException:
            try:
                self.listener = keyboard.Listener(on_press=self.check_hotk)
                self.listener.start()
            except BaseException as e:
                self.show_message_box("Exception Occurred", f"Can't catch input: {e}")

    def more_settings_close(self):
        try:
            self.listener.stop()
            del self.listener
            self.listener = keyboard.Listener(on_press=self.check_hotk)
        except:
            pass

    def check_hotk(self, key):
        if self.listener_status <= len(self.listener_steps) - 1:
            if key == self.listener_steps[self.listener_status]:
                self.listener_status += 1
                if self.listener_status == len(self.listener_steps):
                    self.kb_event_pass.emit()
                return
        self.listener_status = 0

    def kb_pass(self, *args):
        self.ui_moresettings.groupBox_2.show()
        self.ui_moresettings.groupBox__pwd.show()

    def check_inner(self):
        self.ui_moresettings.groupBox__pwd.hide()
        if rpc_data.more_settings_data.get("tlg_inner", 0) < 5:
            self.ui_moresettings.groupBox_bypass.hide()

    def check_inpwd(self, *args):
        if self.ui_moresettings.lineEdit_pwd.text() == bbq("aGFjaGltaQ==").decode("utf8"):
            rpc_data.more_settings_data["tlg_inner"] = 5
            rpc_data.write_config()
            self.ui_moresettings.groupBox_bypass.show()
        self.ui_moresettings.groupBox__pwd.hide()

    def get_window_controller(self):
        window_name = self.ui_windowsettings.lineEdit_window_name.text()
        class_name = self.ui_windowsettings.lineEdit_class_name.text()
        wc = umauitools.WindowController(window_name)
        if class_name:
            wc.setClassName(class_name)
        return wc

    def move_window(self, clicked_index: int):  # 上左右下
        def _(*args):
            move_step = int(self.ui_windowsettings.lineEdit_move_step.text().strip())
            move_x = move_y = 0
            if clicked_index == 1:
                move_y = -move_step
            elif clicked_index == 2:
                move_x = -move_step
            elif clicked_index == 3:
                move_x = move_step
            elif clicked_index == 4:
                move_y = move_step
            wc = self.get_window_controller()
            wc.moveWindow(move_x, move_y)
            self.refresh_window_position()
        return _

    def update_window_positoon(self, *args):
        try:
            now_pos = self.get_window_now_pos()
            if now_pos is None:
                self.show_message_box("Update Window Position Failed.", f"Can't find target window.",
                                      btn=QtWidgets.QMessageBox.Yes)
                return
            x, y, w, h = now_pos
            if w < h:
                nx = self.ui_windowsettings.lineEdit_x_vert.text().strip()
                ny = self.ui_windowsettings.lineEdit_y_vert.text().strip()
                nw = self.ui_windowsettings.lineEdit_w_vert.text().strip()
                nh = self.ui_windowsettings.lineEdit_h_vert.text().strip()
                config_base = "vert"
            else:
                nx = self.ui_windowsettings.lineEdit_x_hori.text().strip()
                ny = self.ui_windowsettings.lineEdit_y_hori.text().strip()
                nw = self.ui_windowsettings.lineEdit_w_hori.text().strip()
                nh = self.ui_windowsettings.lineEdit_h_hori.text().strip()
                config_base = "hori"
            if not all([nx, ny, nw, nh]):
                self.show_message_box("Error", "Please insert numbers.", btn=QtWidgets.QMessageBox.Yes)
                return
            wc = self.get_window_controller()
            wc.resizeWindow(int(nx), int(ny), int(nw), int(nh))
            self.refresh_window_position()

            # if "hori" not in rpc_data.window_settings_data:
            #     rpc_data.window_settings_data["hori"] = {}
            # if "vert" not in rpc_data.window_settings_data:
            #     rpc_data.window_settings_data["vert"] = {}
            # rpc_data.window_settings_data[config_base]["x"] = int(nx)
            # rpc_data.window_settings_data[config_base]["y"] = int(ny)
            # rpc_data.window_settings_data[config_base]["w"] = int(nw)
            # rpc_data.window_settings_data[config_base]["h"] = int(nh)
            self.refresh_settings_group()
            rpc_data.write_config()
        except BaseException as e:
            self.show_message_box("Exception Occurred", f"Exception Occurred in update_window_positoon:\n{e}",
                                  btn=QtWidgets.QMessageBox.Yes)

    def sync_pos_data(self, *args):
        try:
            x = self.ui_windowsettings.lineEdit_x.text()
            y = self.ui_windowsettings.lineEdit_y.text()
            w = int(self.ui_windowsettings.lineEdit_w.text())
            h = int(self.ui_windowsettings.lineEdit_h.text())
            if w < h:
                self.ui_windowsettings.lineEdit_x_vert.setText(x)
                self.ui_windowsettings.lineEdit_y_vert.setText(y)
                self.ui_windowsettings.lineEdit_w_vert.setText(str(w))
                self.ui_windowsettings.lineEdit_h_vert.setText(str(h))
            else:
                self.ui_windowsettings.lineEdit_x_hori.setText(x)
                self.ui_windowsettings.lineEdit_y_hori.setText(y)
                self.ui_windowsettings.lineEdit_w_hori.setText(str(w))
                self.ui_windowsettings.lineEdit_h_hori.setText(str(h))

        except BaseException as e:
            self.show_message_box("Exception Occurred", f"Exception Occurred in sync_pos_data:\n{e}",
                                  btn=QtWidgets.QMessageBox.Yes)
            return None

    def get_window_now_pos(self, parse_int=True):
        try:
            wc = self.get_window_controller()
            get_pos = wc.getWindowPos()
            if not get_pos:
                return None
            x, y, w, h = [int(i) if parse_int else i for i in get_pos.split(",")]
            return (x, y, w, h)
        except BaseException as e:
            self.show_message_box("Exception Occurred", f"Exception Occurred in get_window_now_pos:\n{e}",
                                  btn=QtWidgets.QMessageBox.Yes)
            return None

    def refresh_window_position(self, *args):
        try:
            get_pos = self.get_window_now_pos(parse_int=False)
            if get_pos is None:
                self.ui_windowsettings.pushButton_sync_pos.setEnabled(False)
                self.show_message_box("Get Window Position Failed.", f"Can't find target window.",
                                      btn=QtWidgets.QMessageBox.Yes)
                return
            self.ui_windowsettings.pushButton_sync_pos.setEnabled(True)
            x, y, w, h = get_pos
            self.ui_windowsettings.lineEdit_x.setText(x)
            self.ui_windowsettings.lineEdit_y.setText(y)
            self.ui_windowsettings.lineEdit_w.setText(w)
            self.ui_windowsettings.lineEdit_h.setText(h)
        except BaseException as e:
            self.show_message_box("Exception Occurred", f"Exception Occurred in refresh_window_position:\n{e}",
                                  btn=QtWidgets.QMessageBox.Yes)

    def window_text_changed(self, pos_index: int):
        def _(new_value: str, *args):
            if new_value == "" or new_value == "-":
                return
            hori_is_checked = self.ui_windowsettings.checkBox_keep_ratio_hori.isChecked()
            vert_is_checked = self.ui_windowsettings.checkBox_keep_ratio_vert.isChecked()
            if pos_index == 0:  # hori_w
                if hori_is_checked:
                    if self.ui_windowsettings.lineEdit_w_hori.hasFocus():
                        self.ui_windowsettings.lineEdit_h_hori.setText(str(int(int(new_value) / self.aspect_ratio_set)))
            elif pos_index == 1:  # hori_h
                if hori_is_checked:
                    if self.ui_windowsettings.lineEdit_h_hori.hasFocus():
                        self.ui_windowsettings.lineEdit_w_hori.setText(str(int(int(new_value) * self.aspect_ratio_set)))
            elif pos_index == 2:  # vert_w
                if vert_is_checked:
                    if self.ui_windowsettings.lineEdit_w_vert.hasFocus():
                        self.ui_windowsettings.lineEdit_h_vert.setText(str(int(int(new_value) * self.aspect_ratio_set)))
            elif pos_index == 3:  # vert_h
                if vert_is_checked:
                    if self.ui_windowsettings.lineEdit_h_vert.hasFocus():
                        self.ui_windowsettings.lineEdit_w_vert.setText(str(int(int(new_value) / self.aspect_ratio_set)))
        return _

    def all_live_pos_hook_onclick(self):
        def _():
            try:
                self.set_live_hook_btn_signal.emit(False)
                count = http_server.story_patch.make_all_live_pos_hookable()
                self.show_message_signal.emit("success", f"Changed {count} files.")
            except BaseException as e:
                self.show_message_signal.emit("Exception Occurred", repr(e))
            finally:
                self.set_live_hook_btn_signal.emit(True)

        def _rst():
            try:
                self.set_live_hook_btn_signal.emit(False)
                count = http_server.story_patch.restore_all_live_pos_hookable()
                self.show_message_signal.emit("success", f"Restored {count} files.")
            except BaseException as e:
                self.show_message_signal.emit("Exception Occurred", repr(e))
            finally:
                self.set_live_hook_btn_signal.emit(True)

        msgbox = QtWidgets.QMessageBox(self.window)
        yesButton = QtWidgets.QPushButton("Yes")
        restoreButton = QtWidgets.QPushButton("Restore")
        noButton = QtWidgets.QPushButton("No")
        msgbox.setText("Are you sure?\n"
                       "It will take a little time.")
        msgbox.setWindowTitle("Edit AssetBundle")
        msgbox.addButton(yesButton, QtWidgets.QMessageBox.ResetRole)
        msgbox.addButton(restoreButton, QtWidgets.QMessageBox.YesRole)
        msgbox.addButton(noButton, QtWidgets.QMessageBox.NoRole)

        ret = msgbox.exec_()
        if (ret == 0):
            Thread(target=_).start()
        elif (ret == 1):
            Thread(target=_rst).start()


    def set_ratio_clicked(self, *args):
        if self.ui.pushButton_config_settings.isEnabled():
            self.ui.pushButton_config_settings.click()
        else:
            self.show_message_box("Edit Config", "Please edit \"aspect_ratio_new\" in config.json "
                                                 "and restart the game.")

    def switch_window_settings(self):
        orig_text = self.last_window_item_text
        orig_text = self.window_settings_key_edit_cache.get(orig_text, orig_text)
        if orig_text is None:
            return
        if orig_text not in rpc_data.window_settings_groups:
            # rpc_data.window_settings_groups[orig_text] = {"hori": {}, "vert": {}}
            return
        rpc_data.window_settings_groups[orig_text]["hori"]["x"] = self.ui_windowsettings.lineEdit_x_hori.text()
        rpc_data.window_settings_groups[orig_text]["hori"]["y"] = self.ui_windowsettings.lineEdit_y_hori.text()
        rpc_data.window_settings_groups[orig_text]["hori"]["w"] = self.ui_windowsettings.lineEdit_w_hori.text()
        rpc_data.window_settings_groups[orig_text]["hori"]["h"] = self.ui_windowsettings.lineEdit_h_hori.text()
        rpc_data.window_settings_groups[orig_text]["vert"]["x"] = self.ui_windowsettings.lineEdit_x_vert.text()
        rpc_data.window_settings_groups[orig_text]["vert"]["y"] = self.ui_windowsettings.lineEdit_y_vert.text()
        rpc_data.window_settings_groups[orig_text]["vert"]["w"] = self.ui_windowsettings.lineEdit_w_vert.text()
        rpc_data.window_settings_groups[orig_text]["vert"]["h"] = self.ui_windowsettings.lineEdit_h_vert.text()
        rpc_data.write_config()
        self.window_settings_key_edit_cache.clear()

    def check_uma_window_resize(self):
        try:
            for k in rpc_data.window_settings_groups:
                if k.lower() == "onload":
                    now_pos = self.get_window_now_pos()
                    if now_pos is None:
                        print("check_uma_window_resize - Can't find target window.")
                        return

                    with open(os.path.join(self.uma_path, "config.json"), "r", encoding="utf8") as f:
                        data = json.load(f)
                        force_landscape = data.get("aspect_ratio_new", {}).get("forceLandscape", False)
                    direction_key = "hori" if force_landscape else "vert"

                    nx = rpc_data.window_settings_groups[k].get(direction_key, {}).get("x", "")
                    ny = rpc_data.window_settings_groups[k].get(direction_key, {}).get("y", "")
                    nw = rpc_data.window_settings_groups[k].get(direction_key, {}).get("w", "")
                    nh = rpc_data.window_settings_groups[k].get(direction_key, {}).get("h", "")

                    if not all([nx, ny, nw, nh]):
                        print(f"check_uma_window_resize - Invalid numbers: {[nx, ny, nw, nh]}")
                        return
                    wc = self.get_window_controller()
                    wc.resizeWindow(int(nx), int(ny), int(nw), int(nh))
        except BaseException as e:
            print(f"check_uma_window_resize - Error: {e}")

    def refresh_settings_group(self, *args):
        self.switch_window_settings()
        group_ids = rpc_data.window_settings_groups.keys()
        in_list = []
        for n in range(self.ui_windowsettings.comboBox_window_size_set.count()):
            in_list.append(self.ui_windowsettings.comboBox_window_size_set.itemText(n))
        for i in group_ids:
            if i not in in_list:
                self.ui_windowsettings.comboBox_window_size_set.addItem(i)
        dec = 0
        for n in range(self.ui_windowsettings.comboBox_window_size_set.count()):
            text = self.ui_windowsettings.comboBox_window_size_set.itemText(n - dec)
            if text not in group_ids:
                self.ui_windowsettings.comboBox_window_size_set.removeItem(n - dec)
                dec += 1

        current_index = self.ui_windowsettings.comboBox_window_size_set.currentIndex()
        orig_text = self.ui_windowsettings.comboBox_window_size_set.itemText(current_index)
        self.last_window_item_text = orig_text
        # print("orig_text", orig_text)
        now_data = rpc_data.window_settings_groups.get(orig_text, {})
        # if now_data:
        self.ui_windowsettings.lineEdit_x_hori.setText(str(now_data.get("hori", {}).get("x", "")))
        self.ui_windowsettings.lineEdit_y_hori.setText(str(now_data.get("hori", {}).get("y", "")))
        self.ui_windowsettings.lineEdit_w_hori.setText(str(now_data.get("hori", {}).get("w", "")))
        self.ui_windowsettings.lineEdit_h_hori.setText(str(now_data.get("hori", {}).get("h", "")))
        self.ui_windowsettings.lineEdit_x_vert.setText(str(now_data.get("vert", {}).get("x", "")))
        self.ui_windowsettings.lineEdit_y_vert.setText(str(now_data.get("vert", {}).get("y", "")))
        self.ui_windowsettings.lineEdit_w_vert.setText(str(now_data.get("vert", {}).get("w", "")))
        self.ui_windowsettings.lineEdit_h_vert.setText(str(now_data.get("vert", {}).get("h", "")))

    def add_settings_item(self, *args):
        in_list = []
        for n in range(self.ui_windowsettings.comboBox_window_size_set.count()):
            text = self.ui_windowsettings.comboBox_window_size_set.itemText(n)
            in_list.append(text)
        add_count = len(in_list)
        new_name = f"newItem{add_count}"
        while new_name in in_list:
            add_count += 1
            new_name = f"newItem{add_count}"
        self.ui_windowsettings.comboBox_window_size_set.addItem(new_name)
        rpc_data.window_settings_groups[new_name] = {"hori": {}, "vert": {}}
        self.refresh_settings_group()
        self.ui_windowsettings.comboBox_window_size_set.setCurrentIndex(len(in_list))

    def remove_settings_item(self, *args):
        current_index = self.ui_windowsettings.comboBox_window_size_set.currentIndex()
        orig_text = self.ui_windowsettings.comboBox_window_size_set.itemText(current_index)
        self.ui_windowsettings.comboBox_window_size_set.removeItem(current_index)
        if orig_text in rpc_data.window_settings_groups:
            rpc_data.window_settings_groups.pop(orig_text)
        rpc_data.write_config()
        self.refresh_settings_group()

    def settings_group_name_changed(self, text: str, *args):
        current_index = self.ui_windowsettings.comboBox_window_size_set.currentIndex()
        orig_text = self.ui_windowsettings.comboBox_window_size_set.itemText(current_index)
        self.window_settings_key_edit_cache[orig_text] = text
        rpc_data.window_settings_groups = rpc_data.change_dict_key(rpc_data.window_settings_groups, orig_text, text)
        self.ui_windowsettings.comboBox_window_size_set.setItemText(current_index, text)

    def window_settings_show(self, *args):
        if not import_cpp_success:
            self.ui_moresettings.pushButton_window_settings.setEnabled(False)
            self.show_message_box("Module Import Error", "Can't import c++ module!",
                                  btn=QtWidgets.QMessageBox.Yes)
            return
        self.window_windowsettings.show()
        self.window_moresettings.hide()
        self.refresh_window_position()
        if os.path.isfile(f"{self.uma_path}/config.json"):
            with open(f"{self.uma_path}/config.json", "r", encoding="utf8") as f:
                data = json.load(f).get("aspect_ratio_new", {})
                set_w = data.get("w", 16.0)
                set_h = data.get("h", 9.0)
            if set_w > set_h:
                self.aspect_ratio_set = set_w / set_h
                self.ui_windowsettings.label_aspect_ratio.setText(f"{set_w} : {set_h}")
            else:
                self.ui_windowsettings.label_aspect_ratio.setText("Invalid value")
        self.refresh_settings_group()

    def change_files_api(self):
        text, ok = QInputDialog.getText(self.window, "Change API", "API Endpoint")
        if ok:
            rpc_data.files_api_endpoint = text.strip()
            rpc_data.write_config()

    def check_files_update(self, *args, show_msgbox=True):
        self.uma_path = self.uma_path.replace("\\", "/")
        api_endpoint = rpc_data.files_api_endpoint.strip()
        if not api_endpoint:
            if local_language in sChinese_lang_id:
                api_endpoint = "https://uma.bbq.chinosk6.cn"
            elif local_language in tChinese_lang_id:
                api_endpoint = "https://update-tlg.snowmaple.top"
        if not api_endpoint:
            if show_msgbox:
                self.show_message_box("Error", "Please set an API Endpoint.")
            return

        if not os.path.isfile(f"{self.uma_path}/umamusume.exe"):
            if show_msgbox:
                self.show_message_box("Error", "Target not found.")
            return

        def _():
            self.set_files_update_btn_signal.emit(False)
            try:
                file_root = f"{self.uma_path}/localized_data"

                send_bdy = {}
                for root, dirs, files in os.walk(file_root):
                    for f in files:
                        full_name = os.path.normpath(os.path.join(root, f)).replace("\\", "/")
                        relative_path = full_name.replace(self.uma_path, "")
                        send_bdy[relative_path] = self.get_file_md5(full_name, True)

                headers = {'Content-Type': 'application/json'}
                data = json.loads(
                    requests.request("POST", f"{api_endpoint}/file/get_list",
                                     data=json.dumps(send_bdy), headers=headers).text)
                if data.get("success", False):
                    self.start_update_local_files_signal.emit(api_endpoint, data, show_msgbox)
                else:
                    if show_msgbox:
                        self.show_message_signal.emit("Failed", "Update Local Files Failed")
            except BaseException as e:
                if show_msgbox:
                    self.show_message_signal.emit("Update Local Files Failed", repr(e))
            finally:
                self.set_files_update_btn_signal.emit(True)

        Thread(target=_).start()

    def start_update_local_file(self, api_endpoint, data: dict, show_msgbox=True):
        upd_file_count = len(data["data"])
        if upd_file_count <= 0:
            if show_msgbox:
                self.show_message_box("Tip", self.get_ts("All files are up to date."))
            return

        user_names = set({})
        desc = set({})
        for fname in data["data"]:
            user_names.add(data["data"][fname]["user"])
            desc.add(data["data"][fname]["desc"])
        print_desc = "\n".join(desc)
        print_users = ", ".join(user_names)
        res = self.show_message_box("File Update", self.get_ts("File update detected, do you want to update it now?") +
                                    f"\nTotal {upd_file_count} files.\n\n"
                                    f"{print_desc}\n\nCommitters:\n{print_users}")
        if res != QtWidgets.QMessageBox.Yes:
            return

        if upd_file_count >= 5000:
            self.show_message_box("Error", self.get_ts("Too many files, please update directly."))
            return

        def _():
            self.set_files_update_btn_signal.emit(False)
            try:
                count = 0
                for fname in data["data"]:
                    file_hash = data["data"][fname]["hash"]
                    file_resp = requests.get(f"{api_endpoint}/file/get", params={
                        "filename": fname,
                        "hash": file_hash
                    })
                    if file_resp.status_code == 200:
                        write_name = f"{self.uma_path}{fname}"
                        fpath = os.path.split(write_name)[0]
                        if not os.path.isdir(fpath):
                            os.makedirs(fpath)
                        with open(write_name, "wb") as f:
                            f.write(file_resp.content)
                            count += 1
                try:
                    requests.post(f"http://127.0.0.1:{self.tlg_http_port}/sets",
                                  headers={'Content-Type': 'application/json'},
                                  data=json.dumps({"type": "reload_all"}), timeout=3)
                except:
                    pass
                self.show_message_signal.emit("Update Finished", f"Updated {count} files.")
            except BaseException as e:
                self.show_message_signal.emit("Update Files Failed", repr(e))
            finally:
                self.set_files_update_btn_signal.emit(True)
        Thread(target=_).start()

    @staticmethod
    def get_file_md5(file_name, remove_starts_zero=False):
        try:
            md = md5()
            with open(file_name, "rb") as f:
                block = f.read(1024)
                while block:
                    md.update(block)
                    block = f.read(1024)
            ret = md.hexdigest()
            if remove_starts_zero:
                while ret[0] == "0":
                    ret = ret[1:]
            return ret
        except BaseException:
            return None

    @staticmethod
    def get_ts(text: str):
        dict_scn = {
            "All files are up to date.": "所有文件都是最新的",
            "File update detected, do you want to update it now?": "检测到有文件更新，是否立刻更新？",
            "Too many files, please update directly.": "文件过多，请直接进行完整更新"
        }
        dict_tcn = {
            "All files are up to date.": "所有檔案都是最新的",
            "File update detected, do you want to update it now?": "檢測到有檔案更新，是否立刻更新？",
            "Too many files, please update directly.": "檔案過多，請直接進行完整更新"
        }
        if local_language in sChinese_lang_id:
            return dict_scn.get(text, text)
        if local_language in tChinese_lang_id:
            return dict_tcn.get(text, text)
        return text

    def ui_run_main(self):
        self.window.show()
        self.mti.show()
        exit_code = self.app.exec_()
        # QtWidgets.qApp.quit()
        sys.exit(exit_code)
        os._exit(exit_code)
