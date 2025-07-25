from typing import List

from pydantic import BaseModel


class PermissionConfig(BaseModel):
    unsubbed: bool = False
    subscriber: bool = False
    vip: bool = False
    mod: bool = True
    broadcaster: bool = True


class PermissionSetting(BaseModel):
    command_name: str
    permission_config: PermissionConfig


class PermissionSettingDict(BaseModel):
    ping_command: PermissionSetting
    np_command: PermissionSetting
    songrequest_command: PermissionSetting


class Config(BaseModel):
    nickname: str = ""
    prefix: str = "!"
    channel: str = ""
    token: str = ""
    client_id: str = ""
    client_secret: str = ""
    channel_points_reward: str = ""
    spotify_client_id: str = ""
    spotify_secret: str = ""
    spotify_redirect_uri: str = "http://localhost:8080"
    rate_limit: int = 0
    welcome_message: str = ""
    permissions: PermissionSettingDict = PermissionSettingDict(
        ping_command=PermissionSetting(
            command_name="ping_command",
            permission_config=PermissionConfig()
        ),
        np_command=PermissionSetting(
            command_name="np_command",
            permission_config=PermissionConfig()
        ),
        songrequest_command=PermissionSetting(
            command_name="songrequest_command",
            permission_config=PermissionConfig()
        )
    )