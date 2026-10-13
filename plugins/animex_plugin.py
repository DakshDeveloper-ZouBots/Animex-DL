# Animex Multi-Quality & Batch Plugin Handler
import os
from wzgram import Client, filters
from wzgram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from script import Dead
from scrapers.animex import AnimexClient
from utils.downloader import download_m3u8, download_batch_episodes

animex_api = AnimexClient()

@Client.on_message(filters.command("animex"))
async def animex_search(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("<b>Usage:</b> <code>/animex <anime_name></code>")
    query = " ".join(message.command[1:])
    status = await message.reply_text(Dead.ANIMEX_SEARCH.format(query=query))
    
    results = animex_api.search(query, limit=1)
    if not results:
        return await status.edit_text(Dead.ANIMEX_NOT_FOUND.format(query=query))
        
    anime = results[0]
    anime_id = anime["id"]
    title = anime.get("titleEnglish") or anime.get("titleRomaji") or "Unknown"
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎬 Sub (Ep 1)", callback_data=f"axep|{anime_id}|1|sub"),
            InlineKeyboardButton("🎙️ Dub (Ep 1)", callback_data=f"axep|{anime_id}|1|dub")
        ]
    ])
    
    caption = Dead.ANIMEX_CARD.format(title=title, anime_id=anime_id, episodes=anime.get("episodeCount", "N/A"))
    cover_url = anime.get("coverImage")
    
    try:
        if cover_url:
            # Pyrogram accepts HTTP URLs directly for send_photo if passed properly, 
            # otherwise fallback to text message if it fails local path checks.
            await message.reply_photo(photo=cover_url, caption=caption, reply_markup=buttons)
        else:
            await message.reply_text(caption, reply_markup=buttons)
        await status.delete()
    except Exception:
        # Fallback if image URL parsing fails
        await status.edit_text(caption, reply_markup=buttons)

@Client.on_callback_query(filters.regex(r"^axep\|"))
async def animex_episode_callback(client: Client, callback: CallbackQuery):
    _, anime_id, ep_str, type_ = callback.data.split("|")
    ep_num = int(ep_str)
    
    sources = animex_api.get_all_sources(anime_id, ep_num, type_)
    if not sources:
        return await callback.message.edit_caption(caption=f"❌ No {type_} sources found for Episode {ep_num}.")
        
    quality_buttons = []
    row = []
    for src in sources:
        q = src.get("quality", "720p")
        row.append(InlineKeyboardButton(f"📥 {q}", callback_data=f"axdl|{anime_id}|{ep_num}|{q}"))
        if len(row) == 2:
            quality_buttons.append(row)
            row = []
    if row:
        quality_buttons.append(row)
        
    quality_buttons.append([
        InlineKeyboardButton("📦 Batch Download (Ep 1–12)", callback_data=f"axbatch|{anime_id}|1|12|720p")
    ])
    
    await callback.message.edit_caption(
        caption=f"📺 <b>Select Resolution for Episode {ep_num} ({type_.upper()})</b>:",
        reply_markup=InlineKeyboardMarkup(quality_buttons)
    )

@Client.on_callback_query(filters.regex(r"^axdl\|"))
async def animex_download_callback(client: Client, callback: CallbackQuery):
    _, anime_id, ep_str, quality = callback.data.split("|")
    ep_num = int(ep_str)
    
    await callback.answer(f"Starting {quality} download...", show_alert=False)
    await callback.message.edit_caption(caption=f"⏳ Preparing download stream for <b>{quality}</b>...")
    
    sources = animex_api.get_all_sources(anime_id, ep_num, "sub")
    target_source = next((s for s in sources if s.get("quality") == quality), sources[0] if sources else None)
    
    if not target_source or not target_source.get("url"):
        return await callback.message.edit_caption(caption=f"❌ Could not resolve link for {quality}.")
        
    output_name = f"{anime_id}_Ep{ep_num}"
    await callback.message.edit_caption(caption=f"📥 Downloading <b>{quality}</b> via N_m3u8DL-RE...")
    
    file_path = await download_m3u8(target_source["url"], output_name, quality_label=quality)
    if file_path and os.path.exists(file_path):
        await callback.message.edit_caption(caption=f"✨ Uploading {quality} file...")
        await client.send_document(chat_id=callback.message.chat.id, document=file_path)
        os.remove(file_path)
    else:
        await callback.message.edit_caption(caption="❌ Download process failed.")

@Client.on_callback_query(filters.regex(r"^axbatch\|"))
async def animex_batch_callback(client: Client, callback: CallbackQuery):
    _, anime_id, start_str, end_str, quality = callback.data.split("|")
    start_ep, end_ep = int(start_str), int(end_str)
    
    await callback.answer(f"Starting batch (Ep {start_ep}–{end_ep})...", show_alert=True)
    await callback.message.edit_caption(caption=f"📦 <b>Batch Download Started</b>\nResolving episodes {start_ep} to {end_ep} ({quality})...")
    
    tasks = []
    for ep in range(start_ep, end_ep + 1):
        sources = animex_api.get_all_sources(anime_id, ep, "sub")
        target = next((s for s in sources if s.get("quality") == quality), sources[0] if sources else None)
        if target and target.get("url"):
            tasks.append({"anime_id": anime_id, "ep_num": ep, "url": target["url"]})
            
    if not tasks:
        return await callback.message.edit_caption(caption="❌ Could not resolve any episode links for this batch range.")
        
    await callback.message.edit_caption(caption=f"📥 Downloading batch ({len(tasks)} episodes) via N_m3u8DL-RE...")
    
    downloaded_files = await download_batch_episodes(tasks, quality_label=quality)
    
    if downloaded_files:
        await callback.message.edit_caption(caption=f"✨ Batch complete! Uploading {len(downloaded_files)} files...")
        for file_path in downloaded_files:
            await client.send_document(chat_id=callback.message.chat.id, document=file_path)
            os.remove(file_path)
        await callback.message.reply_text("✅ All batch files delivered successfully!")
    else:
        await callback.message.edit_caption(caption="❌ Batch download failed during execution.")
