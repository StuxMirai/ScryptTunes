<div style="border: 1px solid #ffa500; background-color: #fff4e5; padding: 10px; border-radius: 5px;">
<strong>⚠️ Warning:</strong> Currently we are using a crappy way to do oauth tokens. Everything works but I'm using a <a href="#oauth-Workaround">workaround<a> that isn't ideal. 
</div>


# ScryptTunes

Welcome to ScryptTunes! This application allows you to control your Spotify playlist through Twitch chat commands. This guide will walk you through the installation and setup process, step-by-step.

NOTE: This bot requires Spotify Premium. This is a Spotify API reqirement and there's nothing I can do about it

### Dev Announcements:
 - Channel points redeem is broken, working on a fix. I will disable it in the next release. Don't use it, just doesnt work at all!

## Table of Contents
1. [Install](#install)
2. [Setup](#setup)
3. [Usage](#usage)

 ## Install
1. Go to the latest release page here: [ScrypTunes Latest Release](https://github.com/StuxVT/ScryptTunes/releases/latest)
2. Download `ScryptTunesInstaller.exe` and run it
3. ScryptTunes will now show up in your start menu and as a desktop shortcut

## Setup
### 1. General
1. Open ScryptTunes and click the "General Settings" button.
2. Fill in the following fields:
    - **Nickname**: Name of bot account.
      - If you don't use a separate twitch account for your bot, just put your channel name here.
    - **(Optional) Prefix**: Enter the command indicator for Twitch chat (e.g., `!`). 
    - **Channel**: Channel to listen for commands from. (Very likely to be your twitch channel name)
    - **Token**: [See workaround](#OAuth-Workaround) for now. Working on a better solution
  
 ![image](https://github.com/user-attachments/assets/9f06212e-30ed-4c20-9c18-9b2851478889)



### 2. Setting Up Spotify
1. Visit the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications).
2. Click "Create an App" and fill in the necessary details.
 a. The only important one to get is to fill the "redirect uri" as `http://127.0.0.1:8080` WITHOUT A SLASH AT THE END 

3. Once the app is created, click settings.

4. You'll see a "Client ID" and "Client Secret". Enter these in the Settings view of ScryptTunes.

![image](https://github.com/user-attachments/assets/7a6456b1-9469-43d5-92e9-9b564998cfd3)


### 3. Setting Up Twitch
1. Visit the [Twitch Developer Console](https://dev.twitch.tv/console).
2. Click "Applications" >> "Register Your Application" and fill in the necessary details.
3. Click on "Manage" for your app
4. You'll see a "Client ID" and "Client Secret". Enter these in the Settings view as well.

![image](https://github.com/user-attachments/assets/57b52867-ae39-412d-b1d4-059d38dfbf66)


### 4. App Settings
### ${\color{red}BE \space SURE \space TO \space CLICK \space SAVE}$

### 5. (New) Make sure to set your "Permission Settings" as well! 
- Setting everything allowed is how I use it. There's nothing here that isn't okay for regular chatters to access, but I've given you the choice to switch them off for certain roles if needed!

Note: This is white-list based. If a chatter has ANY of these roles, the command is allowed. For example, if you disable VIP, but have "Unsubbed" still enabled, your VIP's will still be able to use the command. (will improve this but its low priority)

![image](https://github.com/user-attachments/assets/c661b01a-0a24-4cf3-baaf-bc3b595c0832)
 
## Usage
1. Start playing music on Spotify
2. Click "Start" on the main page to start the bot
3. If you need help with commands see the [Commands Guide](https://github.com/StuxVT/ScryptTunes/wiki/Commands#scrypttunes-commands-guide)

---

## OAuth Workaround
This is a temporary workaround until I implement a built-in solution for oauth. You may use this if you like but it's not the recommended solution as it exposes your chat token to a third party. 

(Unlikely to be a problem, as this is the same thing as connecting your twitch to any other app, but still less safe nonetheless and not the indtended purpose)

### Steps:
- Go to [Twitch Token Generator](https://twitchtokengenerator.com/) and select "Bot Chat Token"
- Ensure you're signing in with the account you want sending bot messages into your stream
- Get the access token and add "oauth:" to the beginning of it like this: `oauth:jd9rtifin45jgfijh45bfkc9kl3l84d`
- Paste it into the "Token" field of your "General Settings"

![image](https://github.com/user-attachments/assets/e3160a34-25ca-48dc-9f24-90f3c7cd72f2)

---


## Credits
### `🎶` [TwitchTunes](https://github.com/mmattDonk/TwitchTunes)
- Originally forked from this project, has grown to have many more features, fixes, etc, but [mattDonk](https://github.com/mmattDonk) deserves credit for the starting point.

---
## Dev Notes
You can just run main.py, or build locally if necessary. Feel free to ask questions in DMs on my
[Twitter](https://twitter.com/stuxvt) or [Discord](http://discord.stux.ai) -- there's no such thing as a dumb question, happy to help 💙
### Build Locally
`python -m nuitka --standalone --enable-plugin=tk-inter --include-data-file=icon.ico=icon.ico --output-dir="build" --output-filename="ScryptTunes.exe" .\main.py`
### Create Installer
`makensis installer.nsi`
