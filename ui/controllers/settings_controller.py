import os.path

import customtkinter as ctk
import json
from os import path

import constants
from ui.models.song_blacklist import SongBlacklist
from ui.models.user_blacklist import UserBlacklist
from ui.models.config import Config
from ui.views.settings_view import SettingsView


class SettingsController:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.default = False

        # ensure song blacklist exists
        if path.exists(constants.SONG_BLACKLIST):
            with open(constants.SONG_BLACKLIST) as f:
                self.blacklist_model = SongBlacklist(**json.load(f))
        else:
            self.song_blacklist = SongBlacklist()
            self.save_song_blacklist()

        # ensure user blacklist exists
        if path.exists(constants.USER_BLACKLIST):
            with open(constants.USER_BLACKLIST) as f:
                self.user_blacklist = UserBlacklist(**json.load(f))
        else:
            self.user_blacklist = UserBlacklist()
            self.save_user_blacklist()

        if os.path.exists(constants.CONFIG):
            with open(constants.CONFIG) as f:
                self.config_model = Config(**json.load(f))
        else:
            self.config_model = Config()
            self.save_config()

    def get(self, key):
        # todo, validate and handle errors
        return getattr(self.config_model, key)

    def set(self, key, value):
        # todo, validate and handle errors
        setattr(self.config_model, key, value)
        return True

    def save_config(self):
        with open(constants.CONFIG, "w") as f:
            json.dump(self.config_model.model_dump(), f, indent=4)

    def save_user_blacklist(self):
        with open(constants.USER_BLACKLIST, "w") as f:
            json.dump(self.user_blacklist.model_dump(), f, indent=4)

    def save_song_blacklist(self):
        with open(constants.SONG_BLACKLIST, "w") as f:
            json.dump(self.song_blacklist.model_dump(), f, indent=4)

    def show_settings_window(self):
        x_offset, y_offset = map(int, self.root.geometry().split('+')[1:3])
        SettingsView(self, geometry=f"{800}x{600}+{x_offset}+{y_offset}").grab_set()  # grab focus until closed
