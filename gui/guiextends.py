import threading
import time
import requests
from .qtui.ui_import import MainUI, ConfigUI, RPCUI
from .qtui import msrc_rc  # 不能删
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QWidget
import sys
from .qt_jsonschema_form import WidgetBuilder
import json
import os
import ctypes
import webbrowser
from . import uma_icon_data
from . import discord_rpc
from . import unzip_file
from . import qtray


ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
local_language = ctypes.windll.kernel32.GetSystemDefaultUILanguage()
chinese_lang_id = [0x0c04, 0x1404, 0x0804, 0x1004, 0x0404]
# chinese_lang_id = []
rpc = discord_rpc.DiscordRpc()
rpc_data = discord_rpc.RpcSaveData()
start_time = int(time.time())
now_ver_label_fmt = "当前版本: {0}" if local_language in chinese_lang_id else "Now Version: {0}"
latest_ver_label_fmt = "最新版本: {0}" if local_language in chinese_lang_id else "Latest Version: {0}"
AUTOUPDATE_SUPPORT_SOURCE = ["github"]

last_sub_close_time = 0


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

        req = QtWidgets.QMessageBox.information(self, "确定要退出吗?", "退出后将断开Discord RPC等服务",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if req != QtWidgets.QMessageBox.Yes:
            a0.ignore()
        else:
            if self.quit_callback is not None:
                self.quit_callback()
            a0.accept()
            QtWidgets.qApp.quit()
            os._exit(0)


class QMn(QMainWindow):
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        global last_sub_close_time
        last_sub_close_time = time.time()


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

    def __init__(self):
        self.app = QApplication(sys.argv)

        if local_language in chinese_lang_id:
            self.trans = QtCore.QTranslator()
            self.trans.load(":/trans/main_ui.qm")
            self.trans2 = QtCore.QTranslator()
            self.trans2.load(":/trans/ui_rpc.qm")
            self.trans3 = QtCore.QTranslator()
            self.trans3.load(":/trans/ui_config.qm")
            self.trans4 = QtCore.QTranslator()
            self.trans4.load(":/trans/ui_dmmlogin.qm")

            self.app.installTranslator(self.trans)
            self.app.installTranslator(self.trans2)
            self.app.installTranslator(self.trans3)
            self.app.installTranslator(self.trans4)

        super(UIChange, self).__init__()
        self.uma_path = "."
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

        self.window.add_close_callback(self.close_other_window)  # 主窗口最小化时关闭其它窗口
        self.window.add_quit_callback(self.main_on_quit)

        self.load_args()
        self.config_form = self.get_schema_form()
        if self.config_form is None:
            self.ui.pushButton_config_settings.setEnabled(False)

        # self.regist_callback()
        # self.init_gui()
        self._rpc_btnc_running = False
        self._autoupdate_source = None
        self._autoupdate_url = None
        self._autoupdate_response_cache = None

    def load_args(self):
        args = sys.argv
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
            self.ui.pushButton_fast_login.setEnabled(False)  # TODO 记得改回False

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

    def save_config_changes(self, *args):
        if self.cache_config_changes is not None:
            if os.path.isfile(f"{self.uma_path}/config.json"):
                with open(f"{self.uma_path}/config.json", "w", encoding="utf8") as f:
                    json.dump(self.cache_config_changes, f, ensure_ascii=False, indent=4)

    def show_config_settings_window(self, *args):
        self.cache_config_changes = None
        self.load_schma_form()
        self.window_config.show()

    def show_message_box(self, title, text):
        return QtWidgets.QMessageBox.information(self, title,
                                                 text,
                                                 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

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
        if local_language not in chinese_lang_id:
            schema_file = f"{base_path}/localized_data/config_schema/config_en.schema.json"
            if not os.path.isfile(schema_file):
                schema_file = f"{base_path}/localized_data/config_schema/config.schema.json"
        else:
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

            threading.Thread(target=_inner).start()

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

        threading.Thread(target=_inner).start()

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

        threading.Thread(target=_).start()

    def change_update_button_text(self, s: str):
        if s == "false":
            self.ui.pushButton_plugin_update.setEnabled(False)
        elif s == "true":
            self.ui.pushButton_plugin_update.setEnabled(True)
        else:
            self.ui.pushButton_plugin_update.setText(s)

    def update_button_onclick(self, *args):
        def download_file():
            if os.path.isfile(f"{self.uma_path}/config.json"):
                with open(f"{self.uma_path}/config.json", "r", encoding="utf8") as fc:
                    config_old = json.load(fc)
            else:
                config_old = {}

            for i in self._autoupdate_response_cache["assets"]:
                down_url = i["browser_download_url"]
                file_name = i["name"]
                if file_name.endswith(".zip"):
                    url = down_url
                    self.update_btn_signal.emit("false")
                    resp = requests.get(url, stream=True)
                    total = int(resp.headers.get('content-length', 0))
                    save_name = f"{self.uma_path}/auto_p_update.zip"
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
                    unzip_file.unzip_file(save_name, f"{self.uma_path}/")
                    os.remove(save_name)

            if os.path.isfile(f"{self.uma_path}/config.json"):
                with open(f"{self.uma_path}/config.json", "r", encoding="utf8") as fc:
                    config_new = json.load(fc)
                config_update = unzip_file.config_update(config_old, config_new)
                with open(f"{self.uma_path}/config.json", "w", encoding="utf8") as fc:
                    json.dump(config_update, fc, indent=4, ensure_ascii=False)

            self.update_btn_signal.emit("Done.")
            self.update_finish_signal.emit()

        if self._autoupdate_response_cache is None:
            return
        res = self.show_message_box("插件更新", f"更新说明:\n\n{self._autoupdate_response_cache['body']}"
                                            f"\n\n点击确认将关闭游戏进行更新, 您确认要更新吗?")
        if res == QtWidgets.QMessageBox.Yes:
            self.ui.pushButton_plugin_update.setEnabled(False)

            with open("gkill.bat", "w", encoding="utf8") as f:
                f.write(f"""@echo off
            setlocal
            taskkill /im "umamusume.exe"
            del gkill.bat"""
                        )
            os.system("gkill.bat")

            threading.Thread(target=download_file).start()

    def update_finish(self, *args):
        resu = self.show_message_box("更新完成", "更新完成, 是否立即启动游戏?")
        if resu == QtWidgets.QMessageBox.Yes:
            if self.ui.pushButton_fast_reboot.isEnabled():
                self.ui.pushButton_fast_reboot.click()

    def ui_run_main(self):
        self.window.show()
        self.mti.show()
        exit_code = self.app.exec_()
        # QtWidgets.qApp.quit()
        sys.exit(exit_code)
        os._exit(exit_code)
