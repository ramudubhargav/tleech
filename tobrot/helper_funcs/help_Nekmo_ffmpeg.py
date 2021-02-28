#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

import os
import time
from tobrot.helper_funcs.run_shell_command import run_command


async def take_screen_shot(video_file, output_directory, ttl):
    # https://stackoverflow.com/a/13891070/4723940
    out_put_file_name = os.path.join(output_directory, str(time.time()) + ".jpg")
    if video_file.upper().endswith(("MKV", "MP4", "WEBM")):
        file_generator_command = [
            "ffmpeg",
            "-ss",
            str(ttl),
            "-i",
            video_file,
            "-vframes",
            "1",
            out_put_file_name,
        ]
        # width = "90"
        _, __ = await run_command(file_generator_command)
        # Wait for the subprocess to finish
    #
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None
