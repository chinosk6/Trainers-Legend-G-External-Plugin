import wmi
import pythoncom
import requests
import json
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from getmac import get_mac_address
import hashlib
import typing as t


class ReturnDMM:
    def __init__(self, cookies, launch_args):
        self.cookies = cookies
        self.launch_args = launch_args


class LoginException(Exception):
    def __init__(self, data: str):
        self.data = data

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.data


class UmaDmm:
    def __init__(self, username, password, log_callback: t.Callable[[str], t.Any], driver_path="msedgedriver.exe",
                 proxy_url: t.Optional[str] = None, headless=True, driver_type=0):
        self.username = username
        self.password = password
        self.driver_path = driver_path
        self.proxy_url = proxy_url
        self.log_callback = log_callback
        self.headless = headless
        self.driver_type = driver_type  # 0-edge, 1-chrome, 2-firefox
        self.driver_options = [webdriver.EdgeOptions, webdriver.ChromeOptions, webdriver.FirefoxOptions]

    def get_user_cookie(self):
        login_id = self.username
        password = self.password
        driver_path = self.driver_path
        proxy_url = self.proxy_url

        if proxy_url is None:
            proxy = {}
        else:
            proxy = {"http": proxy_url, "https": proxy_url}

        session = requests.session()

        req = session.get("https://apidgp-gameplayer.games.dmm.com/v5/loginurl", proxies=proxy)
        loginurl = json.loads(req.text)["data"]["url"]

        self.log_callback("Setting up login browser...")

        if_stable_login = False  # stable_login

        def set_options(option):
            if not if_stable_login:
                if self.headless:
                    option.add_argument("--headless")
                option.add_argument("--disable-gpu")
                option.add_argument("--no-sandbox")
                option.add_argument("--disable-dev-shm-usage")
                option.add_argument("--disable-extensions")
                option.add_argument("blink-settings=imagesEnabled=false")
                prefs = {
                    "profile.managed_default_content_settings.images": 2,
                    "permissions.default.stylesheet": 2
                }
                option.add_experimental_option("prefs", prefs)
                option.add_experimental_option("excludeSwitches", ["enable-logging"])
            if proxy_url is not None:
                self.log_callback("Browser will use proxy: " + proxy_url)
                option.add_argument("--proxy-server=" + proxy_url)
            return option

        # Simulate manual login
        self.log_callback("Connecting to the login website...")

        driver = webdriver.Edge(service=Service(driver_path),
                                options=set_options(self.driver_options[self.driver_type]()))
        driver.get(loginurl)

        if driver.page_source.find("not available in your region") != -1:
            self.log_callback("Your IP address is forbidden. Please use Japan IP to login.")
            return None
        driver.find_element(by=By.ID, value='login_id').send_keys(login_id)
        driver.find_element(by=By.ID, value='password').send_keys(password)
        driver.find_element(by=By.XPATH, value='//*[@id="loginbutton_script_on"]/span/input').click()

        # Wait until get login cookies
        self.log_callback("Waiting for cookies...")
        while True:
            try:
                txt_error = driver.find_element(by=By.CLASS_NAME, value="box-txt-error").text.strip()
                if txt_error != "":
                    raise LoginException(f"Login Failed: {txt_error}")

            except NoSuchElementException:
                pass

            if driver.get_cookie("login_session_id") is not None:
                driver_cookies = driver.get_cookies()
                break

        for cookies in driver_cookies:
            if cookies['name'] == 'login_session_id':
                break
        else:
            self.log_callback("Fail to get login_session_id")

        driver.close()
        user_cookies = {c['name']: c['value'] for c in driver_cookies}
        self.log_callback("Get cookies successfully.")
        return user_cookies


    def _get_game_launch_args(self, game_info, user_cookies, mac_address, hdd_serial, motherboard):
        self.log_callback("Get game launching arguments...")
        if self.proxy_url is None:
            proxy = {}
        else:
            proxy = {"http": self.proxy_url, "https": self.proxy_url}

        header = {
            "Accept-Encoding": "gzip, deflate, br",
            "User-Agent": "DMMGamePlayer5-Win/5.0.119 Electron/17.2.0",
            "Client-App": "DMMGamePlayer5",
            "Client-version": "5.0.119",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "none"
        }

        get_game_info_json = {
            "product_id": game_info["product_id"],
            "game_type": game_info["game_type"],
            "game_os": "win",
            "launch_type": game_info["launch_type"],
            "mac_address": mac_address,
            "hdd_serial": hdd_serial,
            "motherboard": motherboard,
            "user_os": "win"
        }

        session = requests.session()
        session.post(
            "https://apidgp-gameplayer.games.dmm.com/v5/gameinfo",
            json=get_game_info_json,
            headers=header,
            cookies=user_cookies,
            proxies=proxy
        )

        args = session.post(
            "https://apidgp-gameplayer.games.dmm.com/v5/launch/cl",
            json=get_game_info_json,
            headers=header,
            cookies=user_cookies,
            proxies=proxy
        )

        session.post(
            "https://apidgp-gameplayer.games.dmm.com/v5/report",
            json={
                "type": "start",
                "product_id": game_info["product_id"],
                "game_type": game_info["game_type"]
            },
            headers=header,
            cookies=user_cookies,
            proxies=proxy
        )

        try:
            ret = json.loads(args.text)["data"]["execute_args"]
            self.log_callback(f"Get game launching arguments successfully.")
            return ret
        except:
            raise LoginException(f"登录失败: {args.text}")


    def get_launch_args(self, cookie_cache=None):
        try:
            pythoncom.CoInitialize()
            if cookie_cache is None:
                get_ck = self.get_user_cookie()
                if get_ck is None:
                    return "login failed"
            else:
                get_ck = cookie_cache

            game_info = {
                "product_id": "umamusume",
                "game_type": "GCL",
                "launch_type": "LIB"
            }
            mac_address = get_mac_address()
            try:
                hdd_serial = hashlib.sha256((",".join(
                            item.SerialNumber.strip(" ") for item in wmi.WMI().Win32_PhysicalMedia()
                        )).encode('UTF-8')).hexdigest()
            except:
                hdd_serial = hashlib.sha256(f"{self.username}w{self.password}".encode('UTF-8')).hexdigest()
            motherboard = hashlib.sha256((hdd_serial + mac_address).encode('UTF-8')).hexdigest()
            launch_args = self._get_game_launch_args(game_info, get_ck, mac_address, hdd_serial, motherboard)
            return ReturnDMM(get_ck, launch_args)

        except BaseException as e:
            log = f"Error: {repr(e)}"
            self.log_callback(log)
            return log
