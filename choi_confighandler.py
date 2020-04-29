import json
import os
import os.path


class GuiConfig:
    def __init__(self):
        self.config_dict = dict()
        self.first_time_conf = True
        self.init_val = dict()
        self.filename = None

    def load_conf(self):
        if not os.path.exists(self.filename):
            self.first_time_conf = True
            for k, v in self.init_val.items():
                self.config_dict[k] = v

        else:
            self.first_time_conf = False
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.config_dict = json.load(f)

        return self.config_dict

    def update_conf(self, update_val):
        try:
            for k, v in update_val.items():
                self.config_dict[k] = v

            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.config_dict, f)

            return True

        except Exception as e:
            return False


class AmazonSrcConfig(GuiConfig):
    def __init__(self):
        super().__init__()
        homedir = os.path.expanduser("~").replace("\\", "/")
        self.init_val = {
            "user_name_selected": "관리자 이름을 선택하세요",
            "chrome_profile_selected": "크롬 프로필 이름을 선택하세요",
            "chrome_dir": "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
            "user_data_dir": os.path.join(homedir, "AppData/Local/Google/Chrome/User Data").replace("\\", '/'),
            "shortcut_dir": "",
            "profile_dict": dict(),
            "always_on_top": 1,
            "tab2_delay": 1.5,
            "tab3_delay": 1.5
        }
        self.filename = 'amzsrc.cfg'


class SrcConfig(GuiConfig):
    def __init__(self):
        super().__init__()
        homedir = os.path.expanduser("~").replace("\\", "/")
        self.init_val = {
            "user_name_selected": "관리자 이름을 선택하세요",
            "chrome_account_selected": "크롬 프로필 이름을 선택하세요",
            "chrome_dir": "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
            "user_data_dir": os.path.join(homedir, "AppData/Local/Google/Chrome/User Data").replace("\\", '/'),
            "shortcut_dir": "",
            "chrome_account_dict": dict(),
            "always_on_top": 1,
            "tab2_delay": 1.5,
            "tab3_delay": 1.5
        }
        self.filename = 'amazon_src.cfg'


class TimeTableConfig(GuiConfig):
    def __init__(self):
        super().__init__()
        self.init_val = {
            "output_dir": os.getcwd()
        }
        self.filename = 'timetable.cfg'