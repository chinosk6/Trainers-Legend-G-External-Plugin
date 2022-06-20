from pypresence import Presence
import time
import os


client_id = "860796517240274994"
rich_presence = Presence(client_id)



def connect():
    return rich_presence.connect()


def connect_loop(retries=0):
    if retries > 10:
        return
    try:
        connect()
    except Exception as e:
        print("Error connecting to Discord", e)
        time.sleep(10)
        retries += 1
        connect_loop(retries)
    else:
        update_loop()


def get_data():
    return (
        {'state': "目前对立占上风",
         'small_image': "grass_2",
         'large_image': "grass_1",
         'large_text': "Tairitsu",
         'small_text': "Hikari",
         'details': "光和对立正在打架",
         'buttons': [{"label": "去劝架", "url": "http://127.0.0.1:11451/qwq"},
                     {"label": "我也要和她们打架!", "url": "http://127.0.0.1:11451/owo"}]
         }
    )


def data2():
    return {'state': "state",
            'small_image': "grass_2",
            'large_image': "main_icon",
            'large_text': "Arcaea",
            'small_text': "Hikari",
            'details': "now_score",
            'buttons': [{"label": "去劝架", "url": "http://127.0.0.1:11451/qwq"},
                        {"label": "我也要和她们打架!", "url": "http://127.0.0.1:11451/owo"}]
            }


def update_loop():
    start_time = int(time.time())
    try:
        model = str(os.popen("adb -d shell getprop ro.product.model").read())

        while True:
            rpc_data = data2()
            if (rpc_data['details'] == "Device"):
                det = model.replace('\n', '')
            else:
                det = "Score:" + rpc_data['details']

            rich_presence.update(state=rpc_data['state'],
                                 small_image=rpc_data["small_image"],
                                 large_image=rpc_data['large_image'],
                                 large_text=rpc_data['large_text'],
                                 # small_text = rpc_data['small_text'],
                                 details=det,
                                 # buttons = rpc_data['buttons'],
                                 start=start_time)
            print("状态已更新:" + det + ' - ' + rpc_data['state'])
            time.sleep(5)
    except Exception as sb:
        print(sb)
        return


if __name__ == '__main__':
    while True:
        connect_loop()