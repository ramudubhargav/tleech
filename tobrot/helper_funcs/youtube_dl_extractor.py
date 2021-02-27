#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) PublicLeech Author(s)

from tobrot.helper_funcs.display_progress import humanbytes
import yt_dlp
from pykeyboard import InlineKeyboard
from pyrogram.types import InlineKeyboardButton

from tobrot import DEF_THUMB_NAIL_VID_S


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
    with yt_dlp.YoutubeDL(info_dict) as ytdl:
        try:
            info = ytdl.extract_info(url, download=False)
        except yt_dlp.utils.DownloadError as ytdl_error:
            return None, str(ytdl_error), None

    if info:
        ikeyboard = InlineKeyboard()
        #
        thumb_image = info.get("thumbnail", None)
        # LOGGER.info(thumb_image)
        # YouTube acts weirdly,
        # and not in the same way as Telegram
        thumbnail = thumb_image if thumb_image else DEF_THUMB_NAIL_VID_S

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
                acodec = formats.get("acodec", None)
                dipslay_str_uon = (
                    f"{format_string} [{format_ext.upper()}] {approx_file_size}"
                )
                cb_string_video = f"video|{extractor_key}|{format_id}|{acodec}"
                # GDrive gets special pass, acodec is not listed here, ie acodec=None
                if extractor_key == "GoogleDrive":
                    if format_id == "source":
                        ikeyboard.row(
                            InlineKeyboardButton(
                                dipslay_str_uon, callback_data=cb_string_video
                            )
                        )
                else:
                    if format_string and "audio only" not in format_string:
                        ikeyboard.row(
                            InlineKeyboardButton(
                                dipslay_str_uon, callback_data=cb_string_video
                            )
                        )
                    else:
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
