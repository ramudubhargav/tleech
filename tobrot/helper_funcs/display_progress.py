#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

import asyncio
import math
import time

from pyrogram.errors import FloodWait

from tobrot.config import Config


async def progress_for_pyrogram(current, total, status_text, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        elapsed_time = round(diff)
        if elapsed_time == 0:
            return
        speed = current / elapsed_time
        time_to_completion = round((total - current) / speed)
        estimated_total_time = time_formatter(time_to_completion)

        progress_block = "[{}{}]\n".format(
            "".join(
                Config.FINISHED_PROGRESS_STR
                for _ in range(math.floor(percentage / 5))
            ),
            "".join(
                Config.UN_FINISHED_PROGRESS_STR
                for _ in range(20 - math.floor(percentage / 5))
            ),
        )

        progress_text = (
            f"{progress_block}"
            f"Uploading {round(percentage, 2)}% of "
            f"{humanbytes(total)} @ {humanbytes(speed)}/s, "
            f"ETA: {estimated_total_time}\n"
        )
        try:
            if not message.photo:
                await message.edit_text(text=f"{status_text}\n {progress_text}")
            else:
                await message.edit_caption(caption=f"{status_text}\n {progress_text}")
        except FloodWait as e:
            await asyncio.sleep(e.x)


def humanbytes(size):
    # https://stackoverflow.com/a/43690506
    for unit in ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]:
        if size < 1024.0 or unit == "PiB":
            break
        size /= 1024.0
    return f"{size:.2f} {unit}"


def time_formatter(seconds: int) -> str:
    result = ""
    remainder = seconds
    r_ange_s = {"days": (24 * 60 * 60), "hours": (60 * 60), "minutes": 60, "seconds": 1}
    for age, divisor in r_ange_s.items():
        v_m, remainder = divmod(remainder, divisor)
        v_m = int(v_m)
        if v_m != 0:
            result += f"{v_m} {age} "
    return result or "0 seconds"
