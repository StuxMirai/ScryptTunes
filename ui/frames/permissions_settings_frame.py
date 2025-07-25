from customtkinter import CTkFrame, CTkButton
from tkinter import messagebox

from ui.frames.permission_setting_row import PermissionSettingRow
from ui.models.config import PermissionSettingDict


class PermissionSettingsFrame(CTkFrame):
    def __init__(self, master, settings_controller):
        """
        TODO: dead settings can be created if command names change, find workaround or fix/autoclean somehow

        :param master:
        :param settings_controller:
        """

        super().__init__(master)

        self.settings_controller = settings_controller
        self.current_settings = settings_controller.get("permissions")  # type: PermissionSettingDict

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Configure row 0 to expand vertically

        self.ping_command_setting = PermissionSettingRow(
            parent=self,
            setting_name="Ping Command",
            setting_description="Change permissions on the ping command",
            initial_values=self.current_settings.ping_command.permission_config,
            command_name="ping_command"  # todo: reference command in non-hardcoded way
        )
        self.ping_command_setting.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        self.np_command = PermissionSettingRow(
            parent=self,
            setting_name="Now Playing Command",
            setting_description="Change permissions on the !np or !song command",
            initial_values=self.current_settings.np_command.permission_config,
            command_name="np_command"  # todo: reference command in non-hardcoded way
        )
        self.np_command.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.songrequest_command = PermissionSettingRow(
            parent=self,
            setting_name="Song Request Command",
            setting_description="Change permissions on the !sr command",
            initial_values=self.current_settings.songrequest_command.permission_config,
            command_name="songrequest_command"  # todo: reference command in non-hardcoded way
        )
        self.songrequest_command.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Save Settings
        self.save_button = CTkButton(self, text="Save", command=self.save_settings)
        self.save_button.grid(
            row=999, column=0, columnspan=2, padx=10, pady=5, sticky="ew"
        )

    def save_settings(self):
        new_settings = {
            "ping_command": self.ping_command_setting.get(),
            "np_command": self.np_command.get(),
            "songrequest_command": self.songrequest_command.get(),
        }

        self.settings_controller.set('permissions', PermissionSettingDict(**new_settings))
        
        result = self.settings_controller.save_config()
        if result is True:
            messagebox.showinfo("Settings Saved", "Permission settings saved successfully!")
        else:
            error_message = result[1] if isinstance(result, tuple) and len(result) > 1 else "Unknown error occurred"
            messagebox.showerror("Settings Error", f"Failed to save permission settings.\n\nError: {error_message}")

