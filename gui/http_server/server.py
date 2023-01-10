from flask import Flask, request
import threading
from . import game_pack_modify as gmp
import requests


class UmaServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.port = -1

        self.enable_unlock_plain_cloth = False
        self.unlock_stories = False

    def set_port(self, value: int):
        self.port = value

    def set_enable_unlock_plain_cloth(self, value: bool):
        self.enable_unlock_plain_cloth = value

    def set_unlock_stories(self, value: bool):
        self.unlock_stories = value

    def on_live_unlock(self):
        p_data = request.data
        if not self.enable_unlock_plain_cloth:
            return "not match", 202

        success, data = gmp.unlock_live_dress(p_data, self.unlock_stories)
        if success:
            return data
        else:
            if data == "not match":
                return "not match", 202
            else:
                return str(data), 500

    def port_register(self):
        self.app.route("/tools/unlock_live_dress", methods=["POST"])(self.on_live_unlock)

    def start_server(self, tlg_port: int, port=None):
        if port is not None:
            self.set_port(value=int(port))

        self.port_register()
        threading.Thread(target=lambda: self.app.run(host="127.0.0.1", port=self.port)).start()
        try:
            requests.post(f"http://127.0.0.1:{tlg_port}/postmsg/serverstart", timeout=3)
        except:
            pass
        return "ok"
