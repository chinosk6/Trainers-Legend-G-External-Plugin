import msgpack
import json
import sqlite3
import os
from .. import uma_tools

profile_path = os.environ.get("UserProfile")
base_path = f"{profile_path}/AppData/LocalLow/Cygames/umamusume"


def dec_msgpack(data: bytes):
    return msgpack.unpackb(data, strict_map_key=False)


def get_uma_ids():
    ut = uma_tools.UmaTools()
    plain_cloth_ids = ut.get_plain_cloth_ids()
    uma_card_ids, uma_chara_ids = ut.get_uma_card_ids()
    return plain_cloth_ids, uma_card_ids, uma_chara_ids
    # return [], uma_card_ids, uma_chara_ids


def unlock_live_dress(datain: bytes):
    try:
        data = dec_msgpack(datain)
        if "data" in data:
            if "cloth_list" in data["data"] and "card_list" in data["data"]:
                had_cloth_ids = [i for i in data["data"]["cloth_list"]]
                had_uma_ids = [i["card_id"] for i in data["data"]["card_list"]]
                had_chara_ids = [i["chara_id"] for i in data["data"]["chara_list"]]

                cloth_ids, umas, uma_chara_ids = get_uma_ids()
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
                        "love_point": 1,
                        "fan": 1,
                        "max_grade": 1,
                        "dress_id": 2,
                        "mini_dress_id": 2
                    })

                return True, json.dumps(data, ensure_ascii=False)

        return False, "not match"
    except BaseException as e:
        return False, repr(e)
