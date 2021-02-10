#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
LOGGER = logging.getLogger(__name__)

import os
import shutil
from datetime import datetime
import youtube_dlc
from tobrot import (
    DOWNLOAD_LOCATION,
    TG_MAX_FILE_SIZE
)
from tobrot.helper_funcs.extract_link_from_message import extract_link
from tobrot.helper_funcs.upload_to_tg import upload_to_tg


async def youtube_dl_call_back(bot, update):
    # LOGGER.info(update)
    cb_data = update.data
    # youtube_dl extractors
    tg_send_type, youtube_dl_format, youtube_dl_ext, so_type = cb_data.split("|")
    #
    current_user_id = update.message.reply_to_message.from_user.id
    current_message = update.message.reply_to_message
    current_message_id = current_message.message_id
    current_touched_user_id = update.from_user.id

    user_working_dir = os.path.join(
        DOWNLOAD_LOCATION,
        str(current_user_id),
        str(update.message.reply_to_message.message_id)
    )
    # create download directory, if not exist
    if not os.path.isdir(user_working_dir):
        await bot.delete_messages(
            chat_id=update.message.chat.id,
            message_ids=[
                update.message.message_id,
                update.message.reply_to_message.message_id,
            ],
            revoke=True
        )
        return

    youtube_dl_url, cf_name, yt_dl_user_name, yt_dl_pass_word = await extract_link(
        current_message, "YTDL"
    )
    LOGGER.info(youtube_dl_url)
    #
    custom_file_name = "%(title)s.%(ext)s"
    # Assign custom filename if specified
    if cf_name:
        custom_file_name = f"{cf_name}.%(ext)s"
    # https://superuser.com/a/994060
    # LOGGER.info(custom_file_name)
    #
    await update.message.edit_caption(
        caption="trying to download"
    )
    tmp_directory_for_each_user = user_working_dir
    download_directory = tmp_directory_for_each_user
    download_directory = os.path.join(
        tmp_directory_for_each_user,
        custom_file_name
    )
    ytdl_opts = {
        "outtmpl": download_directory,
        "ignoreerrors": True,
        "nooverwrites": True,
        "continuedl": True,
        "noplaylist": True,
        "max_filesize": TG_MAX_FILE_SIZE,
    }
    if yt_dl_user_name and yt_dl_pass_word:
        ytdl_opts.update({
            "username": yt_dl_user_name,
            "password": yt_dl_pass_word,
        })
    if "hotstar" in youtube_dl_url:
        ytdl_opts.update({
            "geo_bypass_country": "IN",
        })
    if tg_send_type == "audio":
        ytdl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": youtube_dl_ext,
                "preferredquality": youtube_dl_format
            }, {
                "key": "FFmpegMetadata"
            }],
        })
    elif tg_send_type == "video":
        minus_f_format = youtube_dl_format
        if "youtu" in youtube_dl_url:
            minus_f_format = f"{youtube_dl_format}+bestaudio"

        ytdl_opts.update({
            "format": minus_f_format,
            "postprocessors": [{
                "key": "FFmpegMetadata"
            }],
        })

    start = datetime.now()
    with youtube_dlc.YoutubeDL(ytdl_opts) as ytdl:
        try:
            info = ytdl.extract_info(youtube_dl_url, download=False)
            yt_task = ytdl.download([youtube_dl_url])
        except youtube_dlc.utils.DownloadError as ytdl_error:
            await update.message.edit_caption(caption=str(ytdl_error))
            return False, None
    if yt_task == 0:
        end_one = datetime.now()
        time_taken_for_download = (end_one - start).seconds
        dir_contents = len(os.listdir(tmp_directory_for_each_user))
        # dir_contents.sort()
        await update.message.edit_caption(
            caption=f"Download completed in {time_taken_for_download} seconds"
                    f"\nfound {dir_contents} file(s)"
        )
        user_id = update.from_user.id
        #
        final_response = await upload_to_tg(
            update.message,
            tmp_directory_for_each_user,
            user_id,
            {},
            True,
            cf_name if cf_name else info.get("title", None)
        )
        LOGGER.info(final_response)
        #
        try:
            shutil.rmtree(tmp_directory_for_each_user)
        except OSError:
            pass
        #
