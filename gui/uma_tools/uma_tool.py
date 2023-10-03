import os
import sqlite3
import time
import json
from typing import Optional


class UmaTools:
    def __init__(self):
        self.base_path = ""
        self.conn: Optional[sqlite3.Connection] = None
        self.master_conn: Optional[sqlite3.Connection] = None
        self.init_conn()

    def init_conn(self):
        profile_path = os.environ.get("UserProfile")
        self.base_path = f"{profile_path}/AppData/LocalLow/Cygames/umamusume"

        try:
            uma_path = os.path.abspath(".").replace("\\", "/")
            if os.path.isfile(f"{uma_path}/config.json"):
                with open(f"{uma_path}/config.json", "r", encoding="utf8") as f:
                    orig_data = json.load(f)
                if "customPath" in orig_data:
                    if orig_data["customPath"].get("enableCustomPersistentDataPath", False):
                        self.base_path = orig_data["customPath"].get("customPersistentDataPath", "")
        except BaseException as e:
            raise ValueError(f"Load config failed.\n{e}")

        meta_path = f"{self.base_path}/meta"
        master_path = f"{self.base_path}/master/master.mdb"

        if not os.path.isfile(meta_path):
            raise FileNotFoundError(f"meta database not found in {meta_path}")
        if not os.path.isfile(master_path):
            raise FileNotFoundError(f"master database not found in {master_path}")

        if self.conn is not None:
            self.conn.close()
        if self.master_conn is not None:
            self.master_conn.close()

        self.conn = sqlite3.connect(meta_path, check_same_thread=False)
        self.master_conn = sqlite3.connect(master_path, check_same_thread=False)

    def get_bundle_path_from_hash(self, bundle_hash: str):
        return f"{self.base_path}/dat/{bundle_hash[:2]}/{bundle_hash}"

    def unlock_live_dress(self):

        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        def get_all_dress_in_table():
            self.master_conn.row_factory = dict_factory
            cursor = self.master_conn.cursor()
            cursor.execute("SELECT * FROM dress_data")
            # fetchall as result
            query = cursor.fetchall()
            # close connection
            cursor.close()
            return query

        def get_unique_in_table():
            self.conn.row_factory = dict_factory
            cursor = self.conn.cursor()
            cursor.execute("SELECT n FROM a WHERE n like '%pfb_chr1____90'")
            # fetchall as result
            names = cursor.fetchall()
            # close connection
            cursor.close()
            list = []
            for name in names:
                list.append(name["n"][-7:-3])
            return list

        def create_data(dress, unique):
            dress['id'] = dress['id'] + 89
            dress['body_type_sub'] = 90
            if str(dress['id'])[:-2] in set(unique):
                dress['head_sub_id'] = 90
            else:
                dress['head_sub_id'] = 0
            self.master_conn.row_factory = dict_factory
            cursor = self.master_conn.cursor()
            cursor.execute("INSERT INTO dress_data VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                           [dress['id'], dress['condition_type'], dress['have_mini'], dress['general_purpose'],
                            dress['costume_type'], dress['chara_id'], dress['use_gender'], dress['body_shape'],
                            dress['body_type'], dress['body_type_sub'], dress['body_setting'], dress['use_race'],
                            dress['use_live'], dress['use_live_theater'], dress['use_home'], dress['use_dress_change'],
                            dress['is_wet'], dress['is_dirt'], dress['head_sub_id'], dress['use_season'],
                            dress['dress_color_main'], dress['dress_color_sub'], dress['color_num'],
                            dress['disp_order'],
                            dress['tail_model_id'], dress['tail_model_sub_id'], dress['mini_mayu_shader_type'],
                            dress['start_time'], dress['end_time']])
            self.master_conn.commit()
            cursor.close()

        def unlock_data():
            self.master_conn.row_factory = dict_factory
            cursor = self.master_conn.cursor()
            cursor.execute("UPDATE dress_data SET use_live = 1, use_live_theater = 1")
            self.master_conn.commit()
            cursor.close()

        dresses = get_all_dress_in_table()
        unique = get_unique_in_table()
        for dress in dresses:
            if 100000 < dress['id'] < 200000 and str(dress['id']).endswith('01'):
                try:
                    create_data(dress, unique)
                except:
                    pass

        cursor_m = self.master_conn.cursor()
        now_time = int(time.time())
        cursor_m.execute("UPDATE chara_data SET start_date=? WHERE start_date>?", [1000000000, now_time])
        cursor_m.execute("UPDATE dress_data SET body_type=230 WHERE id>100000 AND body_type=100")
        self.master_conn.commit()

        unlock_data()


    def get_plain_cloth_ids(self):
        cursor = self.conn.cursor()
        query = cursor.execute("SELECT n FROM a WHERE n like '%pfb_bdy_____90'").fetchall()
        uma_ids = [int(f"90{i[0][-7:-3]}") for i in query]
        cursor.close()

        cursor = self.master_conn.cursor()
        query = cursor.execute("SELECT id FROM dress_data WHERE id>100000").fetchall()
        cursor.close()
        for i in query:
            cloth_id = int(i[0])
            if cloth_id not in uma_ids:
                uma_ids.append(cloth_id)
        return uma_ids


    def get_uma_card_ids(self):
        cursor = self.master_conn.cursor()
        query = cursor.execute("SELECT id, chara_id FROM card_data WHERE id <= 999999").fetchall()
        ret = []
        card_ids = []
        for i in query:
            ret.append(int(i[0]))
            card_ids.append(int(i[1]))

        query = cursor.execute("SELECT id FROM chara_data").fetchall()
        for i in query:
            chara_id = int(i[0])
            if chara_id not in card_ids:
                card_ids.append(chara_id)
        cursor.close()
        return ret, list(set(card_ids))

    def get_story_ids(self, chara: list = None):
        cursor = self.conn.cursor()
        chara_ids = chara if chara is not None else self.get_uma_card_ids()[1]
        ret_ids = []
        for i in chara_ids:
            query = cursor.execute("SELECT n FROM a WHERE n like ?", [f"%story/data/50/{i}/storytimeline_%"]).fetchall()
            ret_ids += [(i, ids[0][-9:]) for ids in query]
        cursor.close()
        return ret_ids

    def get_bundle_hashes_from_paths(self, paths: list, m_type="home"):
        cursor = self.conn.cursor()
        results = []
        for i in paths:
            query = cursor.execute("SELECT h FROM a WHERE n=? and m=?", [i, m_type]).fetchone()
            if query:
                results.append(query[0])
        cursor.close()
        return results

    def get_all_live_ids(self):
        cursor = self.master_conn.cursor()
        query = cursor.execute("SELECT music_id FROM live_data WHERE has_live=1").fetchall()
        cursor.close()
        return [i[0] for i in query]
