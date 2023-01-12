import UnityPy
import os
from .. import uma_tools
import json
import hashlib


class StoryTextCache:
    def __init__(self):
        self.cache_dir = "./localized_data"
        if not os.path.isdir(self.cache_dir):
            os.makedirs(self.cache_dir)
        self.cache_file_name = f"{self.cache_dir}/ext_text_data_cache.json"
        self.cache_data = {}
        if os.path.isfile(self.cache_file_name):
            with open(f"{self.cache_file_name}", "r", encoding="utf8") as f:
                self.cache_data = json.load(f)

    def save_cache_data(self):
        with open(f"{self.cache_file_name}", "w", encoding="utf8") as f:
            json.dump(self.cache_data, f, ensure_ascii=False)

    @staticmethod
    def get_home_paths():
        ret = []
        if not os.path.isdir("./localized_data/stories/home"):
            return ret
        for root, dirs, files in os.walk("./localized_data/stories/home"):
            for f in files:
                now_path = os.path.normpath(os.path.join(root, f)).replace("\\", "/")
                ret.append(now_path)
        return ret

    @staticmethod
    def get_file_hash(filepath: str):
        with open(filepath, 'rb') as f:
            md5obj = hashlib.md5()
            md5obj.update(f.read())
            return md5obj.hexdigest()

    def get_text_list_from_cache(self, filepath):
        file_name = os.path.split(filepath)[1]
        if file_name in self.cache_data:
            if self.cache_data[file_name].get("hash") == self.get_file_hash(filepath):
                return self.cache_data[file_name].get("textdata", None)
            else:
                self.cache_data.pop(file_name)
        return None

    def add_text_cache_data(self, filepath, data):
        file_name = os.path.split(filepath)[1]
        self.cache_data[file_name] = {
            "hash": self.get_file_hash(filepath),
            "textdata": data
        }

def get_stories_japanese_data():
    story = StoryTextCache()
    umatool = uma_tools.UmaTools()

    ret_texts = []
    for i in story.get_home_paths():
        nm_path = os.path.normpath(i).replace("\\", "/")
        if nm_path.startswith("localized_data/stories/"):
            nm_path = nm_path[23:]
        if nm_path.endswith(".json"):
            nm_path = nm_path[:-5]
        bundle_hash = umatool.get_bundle_hashes_from_paths([nm_path])
        if not bundle_hash:
            continue
        bundle_hash = bundle_hash[0]

        file_path = umatool.get_bundle_path_from_hash(bundle_hash)
        cache_data = story.get_text_list_from_cache(file_path)
        if isinstance(cache_data, list):
            ret_texts += cache_data
            continue
        env = UnityPy.load(file_path)
        objects = env.objects
        obj_texts = []
        for obj in objects:
            try:
                if obj.type.name == "MonoBehaviour":
                    script_name = obj.read().m_Script.read().name
                    obj.read_typetree()
                    if script_name == "StoryTimelineTextClipData":
                        mono_tree = obj.read_typetree()
                        text = mono_tree.get("Text", "")
                        next_block = mono_tree.get("NextBlock", -1)
                        uma_name = mono_tree.get("Name", "")
                        if text:
                            obj_texts.append({"path": nm_path, "Text": text, "NextBlock": next_block, "Name": uma_name})
                    else:
                        continue
            except BaseException as e:
                raise e
                pass
        ret_texts += obj_texts
        story.add_text_cache_data(file_path, obj_texts)
    story.save_cache_data()
    return ret_texts


def get_stories_text():
    jpn_data = get_stories_japanese_data()
    sorted_data = {}
    for i in jpn_data:
        nm_path = i["path"]
        text_jpn = i["Text"]
        next_block = i["NextBlock"]
        uma_name_jpn = i["Name"]
        if nm_path not in sorted_data:
            sorted_data[nm_path] = []
        sorted_data[nm_path].append({"Text": text_jpn, "NextBlock": next_block, "Name": uma_name_jpn})

    ret = []
    uma_names = []
    for nm_path in sorted_data:
        localized_path = f"./localized_data/stories/{nm_path}.json"
        if not os.path.isfile(localized_path):
            continue
        with open(localized_path, "r", encoding="utf8") as f:
            local_data = json.load(f)
        local_textlist = local_data.get("TextBlockList", [])
        local_text_len = len(local_textlist)

        current_block_data = []
        for i in sorted_data[nm_path]:
            text_jpn = i["Text"].replace("\r\n", "\n")
            next_block = i["NextBlock"]
            uma_name = i["Name"]
            if text_jpn == "":
                continue
            if next_block == -1:
                current_index = local_text_len - 1
            else:
                current_index = next_block - 1
            if current_index >= local_text_len:
                # print(f"格式不符: {nm_path}")
                current_block_data = []
                break
            text_local = local_textlist[current_index]["Text"]
            name_local = local_textlist[current_index]["Name"]
            if text_local == text_jpn:
                continue
            current_block_data.append([text_jpn, text_local])
            if uma_name not in uma_names:
                uma_names.append([uma_name, name_local])
        ret += current_block_data
    ret += uma_names
    return ret
