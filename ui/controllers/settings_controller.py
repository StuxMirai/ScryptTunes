import os.path

import customtkinter as ctk
import json
from os import path

import constants
from ui.models.song_blacklist import SongBlacklist
from ui.models.user_blacklist import UserBlacklist
from ui.models.config import Config, PermissionConfig, PermissionSetting
from ui.views.general_settings_view import GeneralSettingsView
from ui.views.permission_settings_view import PermissionSettingsView


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

        # TODO: find better way to prevent backward compatibility issues
        if os.path.exists(constants.CONFIG):
            with open(constants.CONFIG) as f:
                config_data = json.load(f)
                if 'welcome_message' not in config_data:
                    config_data['welcome_message'] = ""
                # Remove deprecated commands if they exist
                if 'permissions' in config_data:
                    if 'recent_played_command' in config_data['permissions']:
                        del config_data['permissions']['recent_played_command']
                    if 'queue_command' in config_data['permissions']:
                        del config_data['permissions']['queue_command']
                if 'permissions' not in config_data:
                    config_data['permissions'] = {  # todo: find way not to hardcode so much
                        "ping_command": PermissionSetting(
                            command_name="ping_command",
                            permission_config=PermissionConfig()
                        ),
                        "np_command": PermissionSetting(
                            command_name="np_command",
                            permission_config=PermissionConfig()
                        ),
                        "songrequest_command": PermissionSetting(
                            command_name="songrequest_command",
                            permission_config=PermissionConfig()
                        ),
                    }
                self.config_model = Config(**config_data)
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
        try:
            with open(constants.CONFIG, "w") as f:
                json.dump(self.config_model.model_dump(), f, indent=4)
            return True
        except Exception as e:
            return False, str(e)

    def save_user_blacklist(self):
        with open(constants.USER_BLACKLIST, "w") as f:
            json.dump(self.user_blacklist.model_dump(), f, indent=4)

    def save_song_blacklist(self):
        with open(constants.SONG_BLACKLIST, "w") as f:
            json.dump(self.song_blacklist.model_dump(), f, indent=4)

    def show_general_settings_window(self):
        x_offset, y_offset = map(int, self.root.geometry().split('+')[1:3])
        GeneralSettingsView(self, geometry=f"{800}x{600}+{x_offset}+{y_offset}").grab_set()  # grab focus until closed

    def show_permissions_settings_window(self):
        x_offset, y_offset = map(int, self.root.geometry().split('+')[1:3])
        PermissionSettingsView(self, geometry=f"{800}x{600}+{x_offset}+{y_offset}").grab_set()  # grab focus until closed
