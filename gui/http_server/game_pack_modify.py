import msgpack
import json
import sqlite3
import os
from .. import uma_tools

profile_path = os.environ.get("UserProfile")
base_path = f"{profile_path}/AppData/LocalLow/Cygames/umamusume"


def dec_msgpack(data: bytes):
    return msgpack.unpackb(data, strict_map_key=False)


class DataQuery:
    def __init__(self):
        self.ut = uma_tools.UmaTools()

    def get_uma_ids(self):
        plain_cloth_ids = self.ut.get_plain_cloth_ids()
        uma_card_ids, uma_chara_ids = self.ut.get_uma_card_ids()
        return plain_cloth_ids, uma_card_ids, uma_chara_ids
        # return [], uma_card_ids, uma_chara_ids

    def unlock_stories(self, datain: dict) -> dict:
        ids = self.ut.get_story_ids([1098, 1100])
        unlocked_ids = [i["data_id"] for i in datain["data"]["event_data_array"]]
        for c, i in ids:
            try:
                story_id = int(i)
                if story_id in unlocked_ids:
                    continue
                datain["data"]["event_data_array"].append({
                    "chara_id": c,
                    "data_id": story_id,
                    "create_time": "2021-07-20 14:11:16",
                    "new_flag": 0
                })
            except:
                pass
        return datain


def unlock_live_dress(datain: bytes, is_unlock_stories=False):
    try:
        data = dec_msgpack(datain)
        if "data" in data:
            if "cloth_list" in data["data"] and "card_list" in data["data"]:
                had_cloth_ids = [i for i in data["data"]["cloth_list"]]
                had_uma_ids = [i["card_id"] for i in data["data"]["card_list"]]
                had_chara_ids = [i["chara_id"] for i in data["data"]["chara_list"]]

                dq = DataQuery()

                cloth_ids, umas, uma_chara_ids = dq.get_uma_ids()
                for i in cloth_ids:
                    if i in had_cloth_ids:
                        continue
                    data["data"]["cloth_list"].append({
                        "cloth_id": i
                    })

                for i in umas:
                    if i < 100000:
                        continue
                    if i in had_uma_ids:
                        continue
                    data["data"]["card_list"].append({
                        "null": 1,
                        "card_id": i,
                        "rarity": 3,
                        "talent_level": 3,
                        "create_time": "2022-11-15 17:11:32",
                        "skill_data_array": []
                    })

                for i in uma_chara_ids:
                    if i in had_chara_ids:
                        continue
                    data["data"]["chara_list"].append({
                        "chara_id": i,
                        "training_num": 1,
                        "love_point": 10000,
                        "fan": 1,
                        "max_grade": 1,
                        "dress_id": 2,
                        "mini_dress_id": 2
                    })

                if is_unlock_stories:
                    data = dq.unlock_stories(data)

                return True, json.dumps(data, ensure_ascii=False)

        return False, "not match"
    except BaseException as e:
        return False, repr(e)
