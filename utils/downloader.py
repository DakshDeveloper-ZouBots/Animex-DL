# N_m3u8DL-RE Subprocess Wrapper for Single & Batch Downloads
import asyncio
import os
import logging

logger = logging.getLogger("Downloader")

async def download_m3u8(stream_url: str, output_name: str, quality_label: str = "720p", referer: str = "https://animex.one/") -> str | None:
    final_file = f"{output_name}_{quality_label}.mp4"
    cmd = [
        "./N_m3u8DL-RE",
        stream_url,
        "--save-name", output_name,
        "--auto-select", "true",
        "--header", f"Referer: {referer}",
        "--header", f"Origin: {referer}"
    ]
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await process.communicate()
    
    if process.returncode == 0:
        if os.path.exists(final_file):
            return final_file
        for f in os.listdir("."):
            if f.startswith(output_name) and f.endswith(".mp4"):
                return f
                
    logger.error(f"Download failed: {stderr.decode()}")
    return None

async def download_batch_episodes(episode_tasks: list[dict], quality_label: str = "720p") -> list[str]:
    downloaded_files = []
    for task in episode_tasks:
        file_path = await download_m3u8(task["url"], f"{task['anime_id']}_Ep{task['ep_num']}", quality_label=quality_label)
        if file_path:
            downloaded_files.append(file_path)
    return downloaded_files
