#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) PublicLeech Author(s)

import asyncio
import functools
from concurrent.futures import ThreadPoolExecutor

from tobrot.helper_funcs.display_progress import humanbytes
import yt_dlp
from pykeyboard import InlineKeyboard
from pyrogram.types import InlineKeyboardButton

from tobrot.config import Config


# https://stackoverflow.com/a/64506715
def run_in_executor(_func):
    @functools.wraps(_func)
    async def wrapped(*args, **kwargs):
        loop = asyncio.get_event_loop()
        func = functools.partial(_func, *args, **kwargs)
        return await loop.run_in_executor(executor=ThreadPoolExecutor(), func=func)

    return wrapped


@run_in_executor
def yt_extract_info(video_url, download, ytdl_opts, ie_key):
    with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
        info = ytdl.extract_info(video_url, download=download, ie_key=ie_key)
    return info


async def extract_youtube_dl_formats(
    url, yt_dl_user_name, yt_dl_pass_word, user_working_dir
):
    info_dict = {}
    if yt_dl_user_name and yt_dl_pass_word:
        info_dict.update(
            {
                "username": yt_dl_user_name,
                "password": yt_dl_pass_word,
            }
        )
    if "hotstar" in url:
        info_dict.update(
            {
                "geo_bypass_country": "IN",
            }
        )
    try:
        info = await yt_extract_info(
            video_url=url,
            download=False,
            ytdl_opts=info_dict,
            ie_key=None,
        )
    except yt_dlp.utils.DownloadError as ytdl_error:
        return None, str(ytdl_error), None

    if info:
        ikeyboard = InlineKeyboard()
        #
        thumb_image = info.get("thumbnail", None)
        # LOGGER.info(thumb_image)
        # YouTube acts weirdly,
        # and not in the same way as Telegram
        thumbnail = thumb_image or Config.DEF_THUMB_NAIL_VID_S

        extractor_key = info.get("extractor_key", "Generic")
        duration = info.get("duration", None)
        if info.get("formats"):
            for formats in info.get("formats"):
                format_id = formats.get("format_id")
                format_string = formats.get("format_note")
                if format_string is None:
                    format_string = formats.get("format")
                # don't display formats, without audio
                # https://t.me/c/1434259219/269937
                if "DASH" in format_string.upper():
                    continue
                format_ext = formats.get("ext")
                approx_file_size = (
                    humanbytes(formats.get("filesize"))
                    if formats.get("filesize")
                    else ""
                )
                av_codec = "empty"
                if formats.get("acodec") == "none" or formats.get("vcodec") == "none":
                    av_codec = "none"
                dipslay_str_uon = (
                    f"{format_string} [{format_ext.upper()}] {approx_file_size}"
                )
                cb_string_video = f"video|{extractor_key}|{format_id}|{av_codec}"
                # GDrive gets special pass, acodec is not listed here, ie acodec=None
                if (
                    extractor_key == "GoogleDrive"
                    and format_id == "source"
                    or extractor_key != "GoogleDrive"
                    and format_string
                    and "audio only" not in format_string
                ):
                    ikeyboard.row(
                        InlineKeyboardButton(
                            dipslay_str_uon, callback_data=cb_string_video
                        )
                    )
                elif extractor_key != "GoogleDrive":
                    # special weird case :\
                    ikeyboard.row(
                        InlineKeyboardButton(
                            f"SVideo ({approx_file_size})",
                            callback_data=cb_string_video,
                        )
                    )
            if duration:
                ikeyboard.row(
                    InlineKeyboardButton(
                        "MP3 (64 kbps)", callback_data=f"audio|{extractor_key}|64|mp3"
                    ),
                    InlineKeyboardButton(
                        "MP3 (128 kbps)", callback_data=f"audio|{extractor_key}|128|mp3"
                    ),
                )
                ikeyboard.row(
                    InlineKeyboardButton(
                        "MP3 (320 kbps)", callback_data=f"audio|{extractor_key}|320|mp3"
                    )
                )
        else:
            format_id = info.get("format_id", None)
            format_ext = info.get("ext", None)
            ikeyboard.row(
                InlineKeyboardButton(
                    "SVideo", callback_data=f"video|{extractor_key}|{format_id}|DL"
                )
            )
            # LOGGER.info(ikeyboard)
    succss_mesg = "Select the desired format: 👇<br> <u>mentioned</u> <i>file size might be approximate</i>"
    return thumbnail, succss_mesg, ikeyboard
