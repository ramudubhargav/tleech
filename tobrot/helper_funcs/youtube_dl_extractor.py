#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) PublicLeech Author(s)

from tobrot.helper_funcs.display_progress import humanbytes
import youtube_dlc
from pykeyboard import InlineKeyboard
from pyrogram.types import InlineKeyboardButton

from tobrot import DEF_THUMB_NAIL_VID_S


async def extract_youtube_dl_formats(url, yt_dl_user_name, yt_dl_pass_word, user_working_dir):
    info_dict = {"no_warnings": True,
                 "youtube_include_dash_manifest": True}
    if yt_dl_user_name and yt_dl_pass_word:
        info_dict.update({
            "username": yt_dl_user_name,
            "password": yt_dl_pass_word,
        })
    if "hotstar" in url:
        info_dict.update({
            "geo_bypass_country": "IN",
        })
    with youtube_dlc.YoutubeDL(info_dict) as ytdl:
        try:
            info = ytdl.extract_info(url, download=False)
        except youtube_dlc.utils.DownloadError as ytdl_error:
            return None, str(ytdl_error), None

    if info:
        ikeyboard = InlineKeyboard()
        #
        thumb_image = DEF_THUMB_NAIL_VID_S
        #
        for current_r_json in info:
            # LOGGER.info(current_r_json)
            #
            thumb_image = current_r_json.get("thumbnails", None)
            # LOGGER.info(thumb_image)
            if thumb_image is not None:
                # YouTube acts weirdly,
                # and not in the same way as Telegram
                thumb_image = thumb_image[-1]["url"]
            if thumb_image is None:
                thumb_image = DEF_THUMB_NAIL_VID_S

            duration = None
            if "duration" in current_r_json:
                duration = current_r_json["duration"]
            if "formats" in current_r_json:
                for formats in current_r_json["formats"]:
                    format_id = formats.get("format_id")
                    format_string = formats.get("format_note")
                    if format_string is None:
                        format_string = formats.get("format")
                    # don't display formats, without audio
                    # https://t.me/c/1434259219/269937
                    if "DASH" in format_string.upper():
                        continue
                    format_ext = formats.get("ext")
                    approx_file_size = ""
                    if "filesize" in formats:
                        approx_file_size = humanbytes(formats["filesize"])
                    n_ue_sc = bool("video only" in format_string)
                    scneu = "DL" if not n_ue_sc else "XM"
                    dipslay_str_uon = " " + format_string + " (" + format_ext.upper() + ") " + approx_file_size + " "
                    cb_string_video = f"video|{format_id}|{format_ext}|{scneu}"
                    if "drive.google.com" in url:
                        if format_id == "source":
                            ikeyboard.row(
                                    InlineKeyboardButton(
                                        dipslay_str_uon,
                                        callback_data=cb_string_video
                                        )
                                    )
                    else:
                        if format_string and "audio only" not in format_string:
                            ikeyboard.row(
                                    InlineKeyboardButton(
                                        dipslay_str_uon,
                                        callback_data=cb_string_video
                                        )
                                    )
                        else:
                            # special weird case :\
                            ikeyboard.row(
                                    InlineKeyboardButton(
                                        f"SVideo ({approx_file_size})",
                                        callback_data=cb_string_video
                                        )
                                    )
                if duration is not None:
                    cb_string_64 = "audio|64k|mp3"
                    cb_string_128 = "audio|128k|mp3"
                    cb_string = "audio|320k|mp3"
                    ikeyboard.row(
                            InlineKeyboardButton(
                                "MP3 (64 kbps)",
                                callback_data=cb_string_64
                                ),
                            InlineKeyboardButton(
                                "MP3 (128 kbps)",
                                callback_data=cb_string_128
                                ))
                    ikeyboard.row(
                            InlineKeyboardButton(
                                "MP3 (320 kbps)",
                                callback_data=cb_string
                            ))
            else:
                format_id = current_r_json["format_id"]
                format_ext = current_r_json["ext"]
                cb_string_video = f"video|{format_id}|{format_ext}|DL"
                ikeyboard.row(
                        InlineKeyboardButton(
                            "SVideo",
                            callback_data=cb_string_video
                            )
                        )
            # TODO: :\
            break
        # LOGGER.info(ikeyboard)
        succss_mesg = """Select the desired format: 👇
<u>mentioned</u> <i>file size might be approximate</i>"""
        return thumb_image, succss_mesg, ikeyboard
