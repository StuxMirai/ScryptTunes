# Standard Library
import asyncio
import datetime
import json
import logging
import os
import re
import traceback
from urllib import request as url_request
from urllib.parse import quote

# Third-Party
import requests as req
import spotipy
from pydantic import ValidationError, HttpUrl
from spotipy.oauth2 import SpotifyOAuth
from twitchio.ext import commands
from twitchio.ext.commands import Context
import urllib3

# Local
from bot.blacklists import read_json, write_json
from bot.models.discord import DiscordWebhook, Embed, Author
from constants import CACHE, CONFIG
from ui.models.config import Config



async def is_valid_media_url(url: str, ctx: Context) -> bool:
    spotify_track_regex = r"^(https:\/\/open.spotify.com\/track\/|spotify:track:)([a-zA-Z0-9]+)(\?.*)?$"
    if "spotify" in url and not re.match(spotify_track_regex, url):
        for filter_term in ["artist", "album"]:
            if filter_term in url:
                logging.info(f"{filter_term} URLs are not supported")
                await ctx.send(f"@{ctx.author.name}, {filter_term} URLs are not supported.")
                return False
        logging.info(f"Spotify track URL is invalid or unsupported")
        await ctx.send(f"@{ctx.author.name}, the provided Spotify track URL is invalid or unsupported.")
        return False

    youtube_video_regex = r"^(https?:\/\/)?(www\.|m\.)?(youtube\.com\/watch\?v=|youtu\.be\/)([\w\-]+)(\?.*)?$"
    if "youtu" in url and not re.match(youtube_video_regex, url):
        logging.info(f"YouTube url is invalid or unsupported: {url}")
        await ctx.send(f"@{ctx.author.name}, the provided YouTube url is invalid or unsupported.")
        return False

    return True


class Bot(commands.Bot):
    def __init__(self):
        with open(CONFIG) as config_file:
            config_data = json.load(config_file)
        try:
            self.config = Config(**config_data)
        except ValidationError:
            self.config = Config()
        super().__init__(
            token=self.config.token,
            client_id=self.config.client_id,
            nick=self.config.nickname,
            prefix=self.config.prefix,
            initial_channels=[self.config.channel],
            case_insensitive=True
        )

        self.token = os.environ.get("SPOTIFY_AUTH")
        self.version = "0.3"

        self.request_history = {}
        self.last_song = None

        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=self.config.spotify_client_id,
                client_secret=self.config.spotify_secret,
                redirect_uri="http://127.0.0.1:8080",
                cache_path=CACHE,
                scope=[
                    "user-modify-playback-state",
                    "user-read-currently-playing",
                    "user-read-playback-state",
                    "user-read-recently-played",
                ]
            ),
            requests_timeout=10,
        )

        self.URL_REGEX = (
            r"(?i)\b("
            r"(?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)"
            r"(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+"
            r"(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|"
            r"[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        )

    def _check_permissions(self, ctx, command_name):
        """
        RBAC for commands

        todo: higher permissions are allowed when unchkecked if lower permissions are checked

        :param ctx: context param from twitchio
        :param permission_set: list of permission strings
        :return: boolean (allow or disallow run)
        """

        command_perms = self.config.permissions.model_dump()[command_name]['permission_config']

        allow_all = command_perms['unsubbed']

        for permission in command_perms:
            if command_perms[permission]:
                if (permission in ctx.author.badges) or allow_all:
                    return True

        return False

    async def event_ready(self):
        logging.info("\n" * 100)
        logging.info(f"ScryptTunes ready, logged in as: {self.nick}")
        if self.config.welcome_message:
            channel = self.get_channel(self.config.channel)
            if channel:
                await channel.send(self.config.welcome_message)

    @commands.command(name="ping", aliases=["ding"])
    async def ping_command(self, ctx):
        if self._check_permissions(ctx=ctx, command_name="ping_command"):
            await ctx.send(f":) ScryptTunes v{self.version} is online!")
        else:
            return await ctx.send(f"@{ctx.author.name} You don't have permission to do that!")
        

    @commands.command(name="blacklistuser")
    async def blacklist_user(self, ctx, *, user: str):
        user = user.lower()
        if ctx.author.is_mod:
            file = read_json("blacklist_user")
            if user not in file["users"]:
                file["users"].append(user)
                write_json(file, "blacklist_user")
                await ctx.send(f"{user} added to blacklist")
            else:
                await ctx.send(f"{user} is already blacklisted")
        else:
            await ctx.send("You don't have permission to do that.")

    @commands.command(name="unblacklistuser")
    async def unblacklist_user(self, ctx, *, user: str):
        user = user.lower()
        if ctx.author.is_mod:
            _file = read_json("blacklist_user")
            if user in _file["users"]:
                _file["users"].remove(user)
                write_json(_file, "blacklist_user")
                await ctx.send(f"{user} removed from blacklist")
            else:
                await ctx.send(f"{user} is not blacklisted")
        else:
            await ctx.send("You don't have permission to do that.")

    @commands.command(name="blacklist", aliases=["blacklistsong", "blacklistadd"])
    async def blacklist_command(self, ctx, *, song_uri: str):
        if ctx.author.is_mod:
            jscon = read_json("blacklist")

            song_uri = song_uri.replace("spotify:track:", "")

            if song_uri not in jscon["blacklist"]:
                if re.match(self.URL_REGEX, song_uri):
                    data = self.sp.track(song_uri)
                    song_uri = data["uri"]
                    song_uri = song_uri.replace("spotify:track:", "")

                track = self.sp.track(song_uri)

                track_name = track["name"]

                jscon["blacklist"].append(song_uri)

                write_json(jscon, "blacklist")

                await ctx.send(f"Added {track_name} to blacklist.")

            else:
                await ctx.send("Song is already blacklisted.")

        else:
            await ctx.send("You are not authorized to use this command.")

    @commands.command(
        name="unblacklist", aliases=["unblacklistsong", "blacklistremove"]
    )
    async def unblacklist_command(self, ctx, *, song_uri: str):
        if ctx.author.is_mod:
            jscon = read_json("blacklist")

            song_uri = song_uri.replace("spotify:track:", "")

            if re.match(self.URL_REGEX, song_uri):
                data = self.sp.track(song_uri)
                song_uri = data["uri"]
                song_uri = song_uri.replace("spotify:track:", "")

            if song_uri in jscon["blacklist"]:
                jscon["blacklist"].remove(song_uri)
                write_json(jscon, "blacklist")
                await ctx.send("Removed that song from the blacklist.")

            else:
                await ctx.send("Song is not blacklisted.")
        else:
            await ctx.send("You are not authorized to use this command.")

    @commands.command(name="np", aliases=["nowplaying", "song"])
    async def np_command(self, ctx):
        if self._check_permissions(ctx=ctx, command_name="np_command"):
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    data = self.sp.currently_playing()
                    if data is None or data["item"] is None:
                        await ctx.send("No song is currently playing on Spotify!")
                        return
                    song_artists = data["item"]["artists"]
                    song_artists_names = [artist["name"] for artist in song_artists]

                    min_through = int(data["progress_ms"] / (1000 * 60) % 60)
                    sec_through = int(data["progress_ms"] / (1000) % 60)
                    time_through = f"{min_through} mins, {sec_through} secs"

                    min_total = int(data["item"]["duration_ms"] / (1000 * 60) % 60)
                    sec_total = int(data["item"]["duration_ms"] / (1000) % 60)
                    time_total = f"{min_total} mins, {sec_total} secs"

                    logging.info(
                        f"Now Playing - {data['item']['name']} by {', '.join(song_artists_names)} | Link: {data['item']['external_urls']['spotify']} | {time_through} - {time_total}")
                    await ctx.send(
                        f"Now Playing - {data['item']['name']} by {', '.join(song_artists_names)} | Link: {data['item']['external_urls']['spotify']} | {time_through} - {time_total}"
                    )
                    return  # Success! Exit the retry loop

                except (req.exceptions.ConnectionError, 
                        urllib3.exceptions.ProtocolError,
                        spotipy.exceptions.SpotifyException) as e:
                    
                    if attempt < max_retries - 1:  # Still have retries left
                        logging.info(f"Spotify connection failed, attempt {attempt + 1}/{max_retries}. Recreating client...")
                        # Recreate the Spotify client
                        self.sp = spotipy.Spotify(
                            auth_manager=SpotifyOAuth(
                                client_id=self.config.spotify_client_id,
                                client_secret=self.config.spotify_secret,
                                redirect_uri="http://localhost:8080",
                                cache_path=CACHE,
                                scope=[
                                    "user-modify-playback-state",
                                    "user-read-currently-playing",
                                    "user-read-playback-state",
                                    "user-read-recently-played",
                                ],
                            )
                        )
                        await asyncio.sleep(2 ** attempt)
                        continue
                    
                    # If we're here, we've exhausted all retries
                    logging.error(f"Error: {str(e)}\nStack trace:\n{traceback.format_exc()}")
                    await ctx.send(f"@{ctx.author.name}, there was an error getting the current song after {max_retries} attempts!")
                    DiscordWebhook.send_message(
                        content="<@948699796066144337> WE HAVE A PROBLEM",
                        username="Scrypt",
                        avatar_url="https://stux.ai/static/cryy.png",
                        embeds=[
                            Embed(
                                author=Author(name=f"{ctx.author.name}"),
                                title=f"Now Playing Error in {ctx.author.channel.name}'s Channel",
                                description=f"Error: {str(e)}\nStack trace:\n{traceback.format_exc()}",
                                timestamp=datetime.datetime.now(),
                            )
                        ]
                    )
        else:
            return await ctx.send(f"@{ctx.author.name} You don't have permission to do that!")

    @commands.command(name="srhelp", aliases=[])
    async def help_command(self, ctx):
        await ctx.send("!sr <song name and artist> | or !sr <Spotify URL> - "
                       "Request a song to be added to the queue. "
                       "Example: !sr Never Gonna Give You Up - Rick Astley")

    @commands.command(name="songrequest", aliases=["sr", "addsong"])
    async def songrequest_command(self, ctx, *, song: str = None):
        if self._check_permissions(ctx=ctx, command_name="songrequest_command"):
            if not song:
                return await self.help_command(ctx)
        
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    song_uri = None
                    if re.match(self.URL_REGEX, song):
                        if not await is_valid_media_url(song, ctx):
                            return
                        song_uri = song
                        await self.chat_song_request(ctx, song_uri, song_uri, album=False)
                    else:
                        await self.chat_song_request(ctx, song, song_uri, album=False)

                    logging.info(f"Song request successful for user: {ctx.author.name}, Song: {song}")
                    return  # Success! Exit the retry loop
                    
                except (req.exceptions.ConnectionError, 
                        urllib3.exceptions.ProtocolError,
                        spotipy.exceptions.SpotifyException) as e:
                    
                    if attempt < max_retries - 1:  # Still have retries left
                        logging.info(f"Spotify connection failed, attempt {attempt + 1}/{max_retries}. Recreating client...")
                        # Recreate the Spotify client
                        self.sp = spotipy.Spotify(
                            auth_manager=SpotifyOAuth(
                                client_id=self.config.spotify_client_id,
                                client_secret=self.config.spotify_secret,
                                redirect_uri="http://localhost:8080",
                                cache_path=CACHE,
                                scope=[
                                    "user-modify-playback-state",
                                    "user-read-currently-playing",
                                    "user-read-playback-state",
                                    "user-read-recently-played",
                                ],
                            )
                        )
                        await asyncio.sleep(2 ** attempt)
                        continue
                    
                    # If we're here, we've exhausted all retries
                    logging.error(f"Error: {str(e)}\nStack trace:\n{traceback.format_exc()}")
                    await ctx.send(f"@{ctx.author.name}, there was an error with your request after {max_retries} attempts!")
                    DiscordWebhook.send_message(
                        content="<@948699796066144337> WE HAVE A PROBLEM",
                        username="Scrypt",
                        avatar_url="https://stux.ai/static/cryy.png",
                        embeds=[
                            Embed(
                                author=Author(name=f"{ctx.author.name}"),
                                title=f"Song Request Error in {ctx.author.channel.name}'s Channel",
                                description=f"Error: {str(e)}\nStack trace:\n{traceback.format_exc()}",
                                timestamp=datetime.datetime.now(),
                            )
                        ]
                    )
        else:
            return await ctx.send(f"@{ctx.author.name} You don't have permission to do that!")

    async def chat_song_request(self, ctx, song, song_uri, album: bool, requests=None):
        blacklisted_users = read_json("blacklist_user")["users"]
        if ctx.author.name.lower() in blacklisted_users:
            logging.warning(f"Blacklisted user @{ctx.author.name} attempted request: Song:{song} - URI:{song_uri}")
            await ctx.send("You are blacklisted from requesting songs.")
        else:
            jscon = read_json("blacklist")

            if song_uri is None:
                data = self.sp.search(song, limit=1, type="track", market="US")
                song_uri = data["tracks"]["items"][0]["uri"]

            elif re.match(self.URL_REGEX, song_uri):
                if 'spotify' in song_uri:
                    if '.link/' in song_uri:  # todo: better way to handle this?
                        ctx.send(
                            f'@{ctx.author.name} Mobile link detected, attempting to get full url.')  # todo: verify this is sending?????
                        req_data = req.get(
                            song_uri,
                            allow_redirects=True,
                            headers={
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                                              'like Gecko) Chrome/119.0.0.0 Safari/537.36'
                            }

                        )
                        data = self.sp.track(req_data.url)
                    else:
                        data = self.sp.track(song_uri)
                    song_uri = data["uri"]
                    song_uri = song_uri.replace("spotify:track:", "")
                if 'youtube' in song_uri or 'youtu.be' in song_uri:
                    song_uri = song_uri.strip()  # Removing any leading/trailing whitespace
                    encoded_url = quote(song_uri,
                                        safe=":/?&=")  # Safely encode URL special characters except for a few allowed
                    with url_request.urlopen(f'https://noembed.com/embed?url={encoded_url}') as url:
                        data = json.load(url)
                        title = data['title'], data['author_name']
                    logging.info(f"YouTube Link Detected <{encoded_url}> - Searching song name on Spotify as fallback")
                    await ctx.send(f"YouTube Link Detected - Searching song name on Spotify as fallback")
                    await self.chat_song_request(ctx, f'{title}', song_uri=None, album=False)
                    return

            song_id = song_uri.replace("spotify:track:", "")

            if not album:
                data = self.sp.track(song_id)
                song_name = data["name"]
                song_artists = data["artists"]
                song_artists_names = [artist["name"] for artist in song_artists]
                duration = data["duration_ms"] / 60000

            if song_uri != "not found":
                if song_id in jscon["blacklist"]:
                    logging.warning(f"User @{ctx.author.name} requested blacklisted song: {song_id}")
                    return await ctx.send(f"@{ctx.author.name} That song is blacklisted.")

                if duration > 17:
                    return await ctx.send(f"@{ctx.author.name} Send a shorter song please! :3")

                if self.config.rate_limit:
                    if (ctx.author.name in self.request_history
                            and ctx.author.name.lower() != self.config.channel.lower()):
                        if (
                                datetime.datetime.now() - self.request_history[ctx.author.name]["last_request_time"]
                        ).seconds < 300:
                            return await ctx.send(f"@{ctx.author.name} You need to wait 5 minutes between requests!")

                        self.request_history[ctx.author.name]["last_request_time"] = datetime.datetime.now()
                        self.request_history[ctx.author.name]["last_requested_song_id"] = song_id
                        self.last_song = song_id
                    else:
                        self.request_history[ctx.author.name] = {
                            "last_request_time": datetime.datetime.now(),
                            "last_requested_song_id": song_id
                        }
                        self.last_song = song_id

                self.sp.add_to_queue(song_uri)
                await ctx.send(
                    f"@{ctx.author.name}, Your song ({song_name} by {', '.join(song_artists_names)}) [ {data['external_urls']['spotify']} ] has been added to the queue!"
                )