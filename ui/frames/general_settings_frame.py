from customtkinter import CTkFrame, CTkButton

from ui.frames.checkbox_setting_row import CheckboxSettingRow
from ui.frames.text_setting_row import TextSettingRow


class GeneralSettingsFrame(CTkFrame):
    def __init__(self, master, settings_controller):
        super().__init__(master)

        self.settings_controller = settings_controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Configure row 0 to expand vertically

        # Bot account
        self.nickname_row = TextSettingRow(
            self,
            setting_name="Bot Account",
            setting_description="The username of your bot account",
            initial_value=settings_controller.get("nickname"),
        )
        self.nickname_row.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # Prefix
        self.prefix_row = TextSettingRow(
            self,
            setting_name="Prefix",
            setting_description="Text that goes before your bot command",
            initial_value=settings_controller.get("prefix"),
        )
        self.prefix_row.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Welcome Message
        self.welcome_message_row = TextSettingRow(
            self,
            setting_name="Welcome Message",
            setting_description="Message to send when a user joins the channel",
            initial_value=settings_controller.get("welcome_message"),
        )
        self.welcome_message_row.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Rate-limit checkbox
        self.rate_limit_row = CheckboxSettingRow(
            self,
            setting_name="Rate Limit",
            setting_description="Limit song requests to once every 5 minutes",
            initial_value=settings_controller.get("rate_limit"),
        )
        self.rate_limit_row.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Watch-Channel
        self.channel_row = TextSettingRow(
            self,
            setting_name="Watch Channel",
            setting_description="Your twitch channel",
            initial_value=settings_controller.get("channel"),
        )
        self.channel_row.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        # Token
        self.token_row = TextSettingRow(
            self,
            setting_name="Token",
            setting_description="Twitch OAuth Token",
            initial_value=settings_controller.get("token"),
            hidden=True,
        )
        self.token_row.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

        # Client Id
        self.client_id_row = TextSettingRow(
            self,
            setting_name="client_id",
            setting_description="Twitch Client ID",
            initial_value=settings_controller.get("client_id"),
            hidden=True,
        )
        self.client_id_row.grid(row=6, column=0, padx=10, pady=5, sticky="ew")

        # client_secret
        self.client_secret = TextSettingRow(
            self,
            setting_name="client_secret",
            setting_description="Twitch Client Secret",
            initial_value=settings_controller.get("client_secret"),
            hidden=True,
        )
        self.client_secret.grid(row=7, column=0, padx=10, pady=5, sticky="ew")

        # # channel_points_reward
        # self.channel_points_reward = TextSettingRow(
        #     self,
        #     setting_name="channel_points_reward",
        #     setting_description="(Optional) Name of your song request redeem",
        #     initial_value=settings_controller.get("channel_points_reward"),
        # )
        # self.channel_points_reward.grid(row=8, column=0, padx=10, pady=5, sticky="ew")

        # spotify_client_id
        self.spotify_client_id = TextSettingRow(
            self,
            setting_name="spotify_client_id",
            setting_description="Spotify Client ID",
            initial_value=settings_controller.get("spotify_client_id"),
            hidden=True,
        )
        self.spotify_client_id.grid(row=9, column=0, padx=10, pady=5, sticky="ew")

        # spotify_secret
        self.spotify_secret = TextSettingRow(
            self,
            setting_name="spotify_secret",
            setting_description="Spotify Client Secret",
            initial_value=settings_controller.get("spotify_secret"),
            hidden=True,
        )
        self.spotify_secret.grid(row=10, column=0, padx=10, pady=5, sticky="ew")

        # Save Settings
        self.save_button = CTkButton(self, text="Save", command=self.save_settings)
        self.save_button.grid(
            row=11, column=0, columnspan=2, padx=10, pady=5, sticky="ew"
        )

    def save_settings(self):
        self.settings_controller.set("nickname", self.nickname_row.get())
        self.settings_controller.set("prefix", self.prefix_row.get())
        self.settings_controller.set("welcome_message", self.welcome_message_row.get())
        self.settings_controller.set("channel", self.channel_row.get())
        self.settings_controller.set("token", self.token_row.get())
        self.settings_controller.set("client_id", self.client_id_row.get())
        self.settings_controller.set("client_secret", self.client_secret.get())
        # self.settings_controller.set(
        #     "channel_points_reward", self.channel_points_reward.get()
        # )
        self.settings_controller.set("spotify_client_id", self.spotify_client_id.get())
        self.settings_controller.set("spotify_secret", self.spotify_secret.get())
        self.settings_controller.set("rate_limit", self.rate_limit_row.get())
        self.settings_controller.save_config()
