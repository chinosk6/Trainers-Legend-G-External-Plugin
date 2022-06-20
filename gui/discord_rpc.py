from pypresence import Presence
from threading import Thread
import time
import json
import os
import asyncio


class RpcSaveData:
    def __init__(self):
        self.chara_icon_name = ""
        self.chara_icon_id = ""
        self.chara_icon_text1 = ""
        self.chara_icon_text2 = ""
        self.chara_show_timestamp = False
        self.auto_conn = False

        self.read_config()

    def read_config(self):
        if os.path.isfile("epconf.json"):
            with open("epconf.json", "r", encoding="utf8") as f:
                data = json.load(f)
                self.chara_icon_name = data["chara_icon_name"]
                self.chara_icon_id = data["chara_icon_id"]
                self.chara_icon_text1 = data["chara_icon_text1"][:128]
                self.chara_icon_text2 = data["chara_icon_text2"][:128]
                self.chara_show_timestamp = data["chara_show_timestamp"]
                self.auto_conn = data["auto_conn"]

    def write_config(self):
        with open("epconf.json", "w", encoding="utf8") as f:
            data = {"chara_icon_name": self.chara_icon_name,
                    "chara_icon_id": self.chara_icon_id,
                    "chara_icon_text1": self.chara_icon_text1[:128],
                    "chara_icon_text2": self.chara_icon_text2[:128],
                    "chara_show_timestamp": self.chara_show_timestamp,
                    "auto_conn": self.auto_conn
                    }
            json.dump(data, f, indent=4, ensure_ascii=False)


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

    def update_state(self):
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
