# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
from info import *
from utils import *
from time import time 
from plugins.generate import database
from pyrogram import Client, filters 
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message 
import re
import time

async def send_message_in_chunks(client, chat_id, text):
    max_length = 4096  # Maximum length of a message
    for i in range(0, len(text), max_length):
        msg = await client.send_message(chat_id=chat_id, text=text[i:i+max_length])
        asyncio.create_task(delete_after_delay(msg, 1800))



async def delete_after_delay(message: Message, delay):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except:
        pass

@Client.on_message(filters.text & filters.group & filters.incoming & ~filters.command(["verify", "connect", "id"]))
async def search(bot, message):
    vj = database.find_one({"chat_id": ADMIN})
    if vj == None:
        return await message.reply("**Contact Admin Then Say To Login In Bot.**")
    User = Client("post_search", session_string=vj['session'], api_hash=API_HASH, api_id=API_ID)
    await User.connect()
    f_sub = await force_sub(bot, message)
    if f_sub==False:
       return     
    channels = (await get_group(message.chat.id))["channels"]
    if bool(channels)==False:
       return     
    if message.text.startswith("/"):
       return    
    sts = await message.reply('Searching...💥')
    query = message.text.lower()  # Convert the query to lowercase
    query_words = query.split()  # Split the query into individual words
    filtered_query_words = [word for word in query_words if word not in ["the", "dubbed", "movie", "download", "movies", "hindi", "english", "punjabi", "marathi", "tamil", "gujarati", "bengali", "kannada", "telugu", "malayalam", "to", "of", "org", "hd", "dub", "pls", "please", "2023", "2022", "new", "2024", "2025", "2020", "2021"]]
    query = " ".join(filtered_query_words)  # Reconstruct the filtered query
    start_time = time.time()  # Start measuring elapsed time
    results = ""
    try:
       for channel in channels:
           async for msg in User.search_messages(chat_id=channel, query=query):
               name = (msg.text or msg.caption).split("\n")[0]
               if name in results:
                  continue 
               results += f"<b><I>♻️ {name}\n🔗 {msg.link}</I></b>\n\n"    
       elapsed_time = time.time() - start_time - 2  # Calculate elapsed time
       if bool(results)==False:
          movies = await search_imdb(query)
          buttons = []
          for movie in movies: 
              buttons.append([InlineKeyboardButton(movie['title'], callback_data=f"recheck_{movie['id']}")])
          msg = await sts.edit_text(text="<b><I>I Couldn't find anything related to Your Query😕.\nDid you mean any of these?</I></b>", 
                                          reply_markup=InlineKeyboardMarkup(buttons))
       else:
          msg = await sts.edit_text(text=f"Showing results in {elapsed_time:.2f} sec\n\n{results}", disable_web_page_preview=True)
       _time = (int(time()) + (15*60))
       await save_dlt_message(msg, _time)
    except:
       pass
       


@Client.on_callback_query(filters.regex(r"^recheck"))
async def recheck(bot, update):
    vj = database.find_one({"chat_id": ADMIN})
    User = Client("post_search", session_string=vj['session'], api_hash=API_HASH, api_id=API_ID)
    if vj == None:
        return await update.message.edit("**Contact Admin Then Say To Login In Bot.**")
    await User.connect()
    clicked = update.from_user.id
    try:      
       typed = update.message.reply_to_message.from_user.id
    except:
       return await update.message.delete(2)       
    if clicked != typed:
       return await update.answer("That's not for you! 👀", show_alert=True)

    m=await update.message.edit("**Searching..💥**")
    start_time = time.time()  # Start measuring elapsed time
    id      = update.data.split("_")[-1]
    query   = await search_imdb(id)
    channels = (await get_group(update.message.chat.id))["channels"]
    head    = "<u>⭕ I Have Searched Movie With Wrong Spelling But Take care next time"
    results = ""
    try:
       for channel in channels:
           async for msg in User.search_messages(chat_id=channel, query=query):
               name = (msg.text or msg.caption).split("\n")[0]
               if name in results:
                  continue 
               results += f"<b><I>♻️🍿 {name}</I></b>\n\n🔗 {msg.link}</I></b>\n\n"
       elapsed_time = time.time() - start_time - 2  # Calculate elapsed time
       if bool(results)==False:          
          return await update.message.edit("Still no results found! Please Request To Group Admin", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎯 Request To Admin 🎯", callback_data=f"request_{id}")]]))
       await update.message.edit(text=f"{head}\n\nShowing results in {elapsed_time:.2f} sec\n\n{results}", disable_web_page_preview=True)
    except Exception as e:
       await update.message.edit(f"❌ Error: `{e}`")


@Client.on_callback_query(filters.regex(r"^request"))
async def request(bot, update):
    clicked = update.from_user.id
    try:      
       typed = update.message.reply_to_message.from_user.id
    except:
       return await update.message.delete()       
    if clicked != typed:
       return await update.answer("That's not for you! 👀", show_alert=True)

    admin = (await get_group(update.message.chat.id))["user_id"]
    id    = update.data.split("_")[1]
    name  = await search_imdb(id)
    url   = "https://www.imdb.com/title/tt"+id
    text  = f"#RequestFromYourGroup\n\nName: {name}\nIMDb: {url}"
    await bot.send_message(chat_id=admin, text=text, disable_web_page_preview=True)
    await update.answer("✅ Request Sent To Admin", show_alert=True)
    await update.message.delete(60)
