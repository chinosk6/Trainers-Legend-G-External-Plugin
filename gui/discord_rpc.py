from pypresence import Presence
from threading import Thread
import time
import json
import os
import asyncio
from typing import Optional


class RpcSaveData:
    def __init__(self):
        self.chara_icon_name: Optional[str] = None
        self.chara_icon_id: Optional[str] = None
        self.chara_icon_text1: Optional[str] = None
        self.chara_icon_text2: Optional[str] = None
        self.chara_show_timestamp = False
        self.auto_conn = False
        self.edge_path: Optional[str] = None
        self.email: Optional[str] = None
        self.password: Optional[str] = None
        self.proxy_url: Optional[str] = None
        self.enable_proxy = False
        self.login_open_edge = False
        self.dmm_cookie_cache: Optional[dict] = None
        self.dmm_browser_type = 0  # 0-edge 1-chrome 2-firefox

        self.more_settings_data = {}
        self.window_settings_groups = {"Default": {"hori": {}, "vert": {}}}
        self.read_config()

    def read_config(self):
        if os.path.isfile("epconf.json"):
            with open("epconf.json", "r", encoding="utf8") as f:
                try:
                    data = json.load(f)
                    self.chara_icon_name = self.noneifempty(data["chara_icon_name"])
                    self.chara_icon_id = self.noneifempty(data["chara_icon_id"])
                    self.chara_icon_text1 = self.noneifempty(data["chara_icon_text1"], cut=128)
                    self.chara_icon_text2 = self.noneifempty(data["chara_icon_text2"], cut=128)
                    self.chara_show_timestamp = self.noneifempty(data["chara_show_timestamp"])
                    self.auto_conn = self.noneifempty(data["auto_conn"])

                    self.edge_path = data["edge_path"] if "edge_path" in data else "msedgedriver.exe"
                    self.email = data["email"] if "email" in data else ""
                    self.password = data["password"] if "password" in data else ""
                    self.proxy_url = data["proxy_url"] if "proxy_url" in data else ""
                    self.enable_proxy = data["enable_proxy"] if "enable_proxy" in data else False
                    self.login_open_edge = data["login_open_edge"] if "login_open_edge" in data else False
                    self.dmm_cookie_cache = data["dmm_cookie_cache"] if "dmm_cookie_cache" in data else None
                    self.dmm_browser_type = data["dmm_browser_type"] if "dmm_browser_type" in data else 0
                    self.more_settings_data = data.get("more_settings_data", {})
                    self.window_settings_groups = data.get("window_settings_groups", self.window_settings_groups)
                except BaseException as e:
                    # print(f"配置文件读取失败: {e}")
                    pass


    @staticmethod
    def noneifempty(data, cut=None):
        if isinstance(data, str):
            data = data.strip()
            if data == "":
                return None
            return data if cut is None else data[:cut]
        return data

    def get_data_dict(self):
        return {"chara_icon_name": self.noneifempty(self.chara_icon_name),
                "chara_icon_id": self.noneifempty(self.chara_icon_id),
                "chara_icon_text1": self.noneifempty(self.chara_icon_text1, cut=128),
                "chara_icon_text2": self.noneifempty(self.chara_icon_text2, cut=128),
                "chara_show_timestamp": self.noneifempty(self.chara_show_timestamp),
                "auto_conn": self.noneifempty(self.auto_conn),
                "edge_path": self.edge_path,
                "email": self.email,
                "password": self.password,
                "proxy_url": self.proxy_url,
                "enable_proxy": self.enable_proxy,
                "login_open_edge": self.login_open_edge,
                "dmm_cookie_cache": self.dmm_cookie_cache,
                "dmm_browser_type": self.dmm_browser_type,
                "more_settings_data": self.more_settings_data,
                "window_settings_groups": self.window_settings_groups
                }

    def write_config(self):
        data = self.get_data_dict()
        with open("epconf.json", "w", encoding="utf8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def change_dict_key(data: dict, key_before, key_after):
        if key_before == key_after:
            return data
        new_dict = {}
        for k in data:
            new_key = key_after if k == key_before else k
            new_dict[new_key] = data[k]
        return new_dict

class DiscordRpc:
    def __init__(self, client_id="988041478251114547"):
        self.client_id = client_id
        self.rich_presence = Presence(self.client_id)
        self.main_loop = asyncio.get_event_loop()
        self.base_data = {}
        self.server_start = False
        self.close_server_callback = None
        self._in_loop = False

    def set_close_server_callback(self, func):
        self.close_server_callback = func

    def set_value(self, key, value, empty_is_none=True):
        if empty_is_none and value == "":
            self.base_data[key] = None
            return
        if value is not None:
            self.base_data[key] = value

    def set_image(self, large_image=None, small_image=None):
        self.set_value("large_image", large_image)
        self.set_value("small_image", small_image)

    def set_text(self, state=None, details=None, large_icon_text=None, small_icon_text=None):
        self.set_value("state", state)
        self.set_value("details", details)
        self.set_value("large_text", large_icon_text)
        self.set_value("small_text", small_icon_text)

    def set_start_time(self, stime: int = None):
        self.base_data["start"] = stime

    def connect_server(self):
        # if not self._in_loop:
            # self.rich_presence.update_event_loop(self.main_loop)
        self.rich_presence.update_event_loop(asyncio.new_event_loop())
            # self._in_loop = True
        self.rich_presence.connect()

    def close_server(self):
        try:
            if self.close_server_callback is not None:
                self.close_server_callback()
            self.server_start = False
            # self.rich_presence.close()
        except BaseException as e:
            print("close server failed", e)

    def check_base_data(self):
        rm_k = []
        for k in self.base_data:
            v = self.base_data[k]
            if isinstance(v, str):
                if not 2 < len(v.strip()) < 128:
                    rm_k.append(k)
        for i in rm_k:
            self.base_data.pop(i)

    def update_state(self):
        self.check_base_data()
        self.rich_presence.update(**self.base_data)


    def start(self):
        # def inner():
        try:
            if self.server_start:
                return
            self.server_start = True
            self.connect_server()
            while True:
                if self.server_start:
                    self.update_state()
                else:
                    break
                time.sleep(10)
        except BaseException as e:
            print("connect discord server failed", e)
            raise e

        self.close_server()
        self.rich_presence.close()

        # Thread(target=inner).start()

    def change_state(self):
        if self.server_start:
            self.close_server()
            return "closed"
        else:
            # self.start()
            Thread(target=self.start).start()
            return "started"


if __name__ == "__main__":
    rpc = DiscordRpc(client_id="988041478251114547")
    rpc.set_image(large_image="icon_main", small_image="chr_icon_1001_100102_01")
    rpc.set_text(state="state", details="details", large_icon_text="large_text", small_icon_text="small_text")
    rpc.set_start_time(int(time.time()))
    rpc.start()
