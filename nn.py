import random
import re
import sys
import threading
import time
import asyncio
import io
import os
import requests
import telebot
import aiohttp
from datetime import datetime

# --- CONFIGURATION ---
TOKENS = [
    "8407985739:AAFX565qhIvS0fsDMri85xBsrgS7qG8VhBU",
    
    "8902544541:AAFPKhwAEvXPbOOFZ3tyIPVPuq2I_rtOdcw",
    "8617420335:AAHFbE1UL47-PaFhEGny9CIqdWw96aNmUaU",
    "8682608983:AAFvzOLswei1ENHFeuPa_TdM_PlV7W8IwtA",
    "8906261514:AAF0gO71JgEEM7FDDSEE5dqtOneIFElsgR0",
    "8947676131:AAE_oIuZDSaLkAZRaGCRsUQQwHAQmUKE88o",
    "8513685287:AAFb9XCXXgH5Z76OiFPWlcHYRoWehdB7Pcw",
    "8808395572:AAEKZeLJes-GLB7Yy0kEIVwb9svt1PQ2hGY",
    "8885622757:AAHNuTc8L7wFfs1ROlgt-wEg2P6K-cTE-iw",
    "8748333859:AAEKjeojhCpN8bH5FduE4f9MPZE5KQDkUCY"
    "8407985739:AAFX565qhIvS0fsDMri85xBsrgS7qG8VhBU"
    "8902544541:AAFPKhwAEvXPbOOFZ3tyIPVPuq2I_rtOdcw"
    "8617420335:AAHFbE1UL47-PaFhEGny9CIqdWw96aNmUaU"
    "8682608983:AAFvzOLswei1ENHFeuPa_TdM_PlV7W8IwtA"
    "8906261514:AAF0gO71JgEEM7FDDSEE5dqtOneIFElsgR0"
    "8947676131:AAE_oIuZDSaLkAZRaGCRsUQQwHAQmUKE88o"
    "8513685287:AAFb9XCXXgH5Z76OiFPWlcHYRoWehdB7Pcw"
    "8808395572:AAEKZeLJes-GLB7Yy0kEIVwb9svt1PQ2hGY"
    "8885622757:AAHNuTc8L7wFfs1ROlgt-wEg2P6K-cTE-iw"
    "8748333859:AAEKjeojhCpN8bH5FduE4f9MPZE5KQDkUCY"
]
OWNER_ID_INPUT = 8213187747

# Updated Direct Image URL
PHOTO_URL = "https://cdn.photo2url.com/uploads/2026/10/62b51b2a-6818-46b4-a144-84e92b08bbff.jpg"

# --- CUSTOM SLIDE LIST ---
SLIDE_LIST = [
    "{target}ƬЄƦƖ ƇӇӇƠƬƖ ƁЄӇЄƝ ƘЄ MƲӇ MЄ ƝƲƝƝƲ ƊЄ ƊƖƳƛ" , 
    "{target}ƁƠԼ ƘƠƜƘƛ« ƬЄƦƛ» ƁƛƛƤ ӇƛƖ" , 
    "{target} ƬЄƦƖ Mƛƛ ƇӇƲƊƬЄ ƬƖMЄ ƖƬƝƛ ƇӇƖԼԼƛƬƖ ƘƳƲ ӇƛƖ ?" , 
    "{target} ƬЄƦƖ Mƛƛ ƘЄ ƁƲƦ ƤЄ ԼƛƛƬЄ ӇƖ ԼƛƛƬЄ MƛƦƲƝƓƛ ƧƛƛԼЄ 😜" , 
    "{target} ƬЄƦƖ Mƛƛ ƘƠ MƛƛƦ ƘЄ ƑЄƝƘ ƊƲƝƓƛ ƘƲƬƬƖƳƛ ƘЄ ƁƛƇӇЄ 😹😹" , 
    "{target} ƬЄƦƖ ƁЄӇЄƝ ƘЄ ƇӇƲƇӇЄ ƁƛƦЄ ƇӇӇƠƬЄ ӇƛƖ" , 
    "{target} ƬƦƖ ƁЄӇЄƝ Ƙƛ ƘƛƛԼƛ ƁӇƠƧƊƛ ӇƛƖ ƇӇƖƖƖƖ" ,
    "{target} MƛƖ ƇӇƛԼƛ ƬЄƦЄ Mƛƛ ƘЄ ƁӇƠƧƊЄ ƤЄ ԼƛƛƬ MƛƛƦƝЄ" , 
    "{target} ƬЄƦƖ ƁƛƝƊƖ ƘƠ ƓƠƊƖ MЄ ƁƛƖƬӇƛƲƝƓƛ ƑЄЄԼ ƘƦ Ɲƛ ƦƝƊƳƇЄ" , 
    "{target} ƬЄƦƖ Mƛƛ ƇӇƲƊ ƘЄ MƛƦ ƘƳƲ ʆƛƬƖ ӇƛƖ ƇƠƬЄ ƁƲƳ ??"
]

# Global tracking & security variables
lock = threading.Lock()
total_spam_sent = 0
total_nc_changed = 0
valid_tokens = []
bot_tokens = []
main_bot_instance = None
OWNER_ID = None
sudo_users = set()

# Chat states & Sync dictionaries
slide_running = {}
nc_running = {}
chat_states = {}
chat_state_users = {}
chat_targets = {}
chat_nc_style = {}

HEART_EMOJIS = [
    "❤️", "🖤", "🤍", "🩷", "💙", "💚", "💛", "💜",
    "🤎", "💖", "🧡", "❣️", "💕", "💞", "💓", "💗"
]

NC7_ROTATING_EMOJIS = ["💥", "💢", "⚡", "🌈", "❄️", "🌪️", "☄️", "🪐", "💧", "🌀"]
NC17_FLOWER_EMOJIS = ["🌼", "🌻", "🌺", "🌷", "🪷", "🌸", "💮", "🏵️", "🪻"]

CUSTOM_EMOJIS_16 = ["🦋", "🔥", "💫", "💐", "🌺", "🌀", "🌈", "🐼"]
CUSTOM_EMOJIS_18 = ["😎", "😋", "🤪", "🤩", "😍", "🥵"]
CUSTOM_EMOJIS_19 = ["🎭", "🔥", "❤️", "💀", "👑", "✨"]
CUSTOM_EMOJIS_20 = ["❤️", "🔥", "🦋", "🌸", "⭐", "💎"]

NC_NEW_BLOCK = (
    "𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫\n"
    "𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫\n"
    "𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫\n"
    "𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫\n"
    "𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫\n"
    "𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫\n"
    "𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫\n"
    "𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫\n"
    "𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫\n"
    "𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫"
)

def banner():
    print("=" * 65)
    print("  KOWKA HIGH-SPEED NON-BLOCKING ENGINE")
    print("=" * 65)

def is_owner(user_id):
    return OWNER_ID and user_id == OWNER_ID

def is_authorized(user_id, username):
    if OWNER_ID and user_id == OWNER_ID:
        return True
    if str(user_id) in sudo_users:
        return True
    if username and username.lower() in [str(s).lower() for s in sudo_users]:
        return True
    return False

def get_slide_messages(target_name):
    if not SLIDE_LIST:
        return [f"{target_name} Default Slide Message"]
    return [msg.replace("{target}", target_name) for msg in SLIDE_LIST]

async def async_token_slide_loop(chat_id, token, target_msg_id, bot_index, total_bots):
    global total_spam_sent
    msg_counter = random.randint(0, 100000)
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    token_interval = 0.3
    phase_offset = bot_index * (token_interval / total_bots)
    await asyncio.sleep(phase_offset)

    connector = aiohttp.TCPConnector(limit=500, limit_per_host=100, force_close=False, enable_cleanup_closed=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        while True:
            loop_start = asyncio.get_event_loop().time()
            try:
                if not slide_running.get(chat_id, False):
                    await asyncio.sleep(0.05)
                    continue

                current_target = chat_targets.get(chat_id, "TARGET")
                all_msgs = get_slide_messages(current_target)
                message = all_msgs[msg_counter % len(all_msgs)]
                
                payload = {
                    "chat_id": chat_id, 
                    "text": message,
                    "reply_to_message_id": target_msg_id
                }
                async with session.post(url, json=payload, timeout=3.0) as resp:
                    if resp.status == 200:
                        with lock:
                            total_spam_sent += 1
                    elif resp.status == 429:
                        try:
                            data = await resp.json()
                            retry_after = data.get("parameters", {}).get("retry_after", 1.5)
                            await asyncio.sleep(retry_after)
                        except Exception:
                            await asyncio.sleep(1.5)

                msg_counter += 1
                elapsed = asyncio.get_event_loop().time() - loop_start
                sleep_time = max(0.01, token_interval - elapsed)
                await asyncio.sleep(sleep_time)

            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(0.1)

async def run_async_slide_engine(chat_id, target_msg_id):
    slide_running[chat_id] = True
    total_bots = len(bot_tokens)
    tasks = [
        asyncio.create_task(async_token_slide_loop(chat_id, token, target_msg_id, idx, total_bots))
        for idx, token in enumerate(bot_tokens)
    ]
    while slide_running.get(chat_id, False):
        await asyncio.sleep(0.05)
    for task in tasks:
        task.cancel()

def start_async_slide_thread(chat_id, target_msg_id):
    slide_running[chat_id] = False
    time.sleep(0.05)
    def runner():
        asyncio.run(run_async_slide_engine(chat_id, target_msg_id))
    t = threading.Thread(target=runner)
    t.daemon = True
    t.start()

async def async_token_nc_loop(chat_id, token, bot_index, total_bots):
    global total_nc_changed
    url = f"https://api.telegram.org/bot{token}/setChatTitle"

    token_nc_interval = 3.0
    phase_offset = bot_index * (token_nc_interval / total_bots)
    await asyncio.sleep(phase_offset)

    nc_counter = 0
    connector = aiohttp.TCPConnector(limit=100, limit_per_host=20, force_close=False, enable_cleanup_closed=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        while True:
            loop_start = asyncio.get_event_loop().time()
            try:
                if not nc_running.get(chat_id, False):
                    await asyncio.sleep(0.1)
                    continue

                current_target = chat_targets.get(chat_id, "TARGET")
                style = chat_nc_style.get(chat_id, "1")
                h = random.choice(HEART_EMOJIS)
                ce16 = random.choice(CUSTOM_EMOJIS_16)
                ce18 = random.choice(CUSTOM_EMOJIS_18)
                ce19 = random.choice(CUSTOM_EMOJIS_19)
                ce20 = random.choice(CUSTOM_EMOJIS_20)

                line1 = f"{current_target}  𝙈𝘼𝘿𝘼𝙍𝘾𝙃O𝘿"
                line2 = f"𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}"
                line3 = f"𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}"
                line4 = f"𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫??𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}𒐫𒐫𒐫{h}"
                original_nc = f"{line1} {line2} {line3} {line4}"

                new_nc_line = f"{current_target}  𝙈𝘼𝘿𝘼𝙍𝘾𝙃O𝘿 {h}"
                block_nc = f"{new_nc_line}\n{NC_NEW_BLOCK}"

                nc_3 = (
                    f"{current_target} tmkc\n"
                    f"{h}𒐫{h}⸻{h}𒈙꧅{h}𒐫{h}⸻{h}𒈙꧅{h}𒐫{h}⸻{h}𒈙꧅{h}𒐫{h}⸻{h}𒈙꧅{h}𒐫{h}⸻{h}𒈙꧅{h}𒐫{h}⸻{h}𒈙꧅{h}𒐫{h}⸻{h}𒈙꧅{h}𒐫{h}⸻{h}𒈙꧅{h}𒐫{h}⸻{h}𒈙꧅{h}𒐫{h}⸻{h}𒈙꧅{h}𒐫{h}⸻{h}𒈙꧅{h}𒐫{h}⸻{h}𒈙꧅{h}𒐫{h}⸻{h}𒈙꧅{h}𒐫{h}⸻{h}𒈙꧅{h}𒐫{h}⸻{h}𒈙꧅{h}𒐫{h}⸻{h}𒈙꧅{h}𒐫{h}⸻{h}𒈙꧅{h}𒐫{h}⸻{h}𒈙꧅{h}𒐫{h}⸻{h}𒈙꧅{h}𒐫{h}⸻{h}𒈙"
                )

                nc_4 = (
                    f"{current_target}~𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴛ 𝐒ɪʟ𝐚ʏ𝐢 𝐊ʀ {h}\n"
                    "𒈙💜𒈙💢𒈙💋𒈙☘️𒈙🌗𒈙🕊️𒈙💜𒈙💢𒈙💋𒈙🍀𒈙🌗𒈙🕊️𒈙💜𒈙💢𒈙💋𒈙🍀𒈙🌗𒈙🕊️𒈙💜𒈙💢𒈙💋𒈙🍀𒈙🌗𒈙🕊️𒈙💜𒈙💢𒈙💋𒈙☘️𒈙🌗𒈙🕊️𒈙💜𒈙💢𒈙💋𒈙☘️𒈙🌗𒈙🕊️𒈙💜𒈙💋𒈙☘️𒈙🌗𒈙🕊️𒈙💜𒈙💢𒈙💋𒈙☘️𒈙🌗𒈙🕊️𒈙💋"
                )

                nc_5 = (
                    f"{current_target} 𝘾𝙃𝙐𝘿𝘼𝙄 𝘼𝙍𝘾 "
                    f"જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h} "
                    f"જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h} "
                    f"જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h} "
                    f"જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}જ⁀➴{h}"
                )

                nc_6 = (
                    f"{current_target} ƇӇƲƤ ƦƝƊƳƘƎ {h}\n"
                    " 𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂 𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂𓍯𓍯😂"
                )

                r7_segment = "".join([random.choice(NC7_ROTATING_EMOJIS) for _ in range(200)])
                nc_7 = f"{current_target} tmkc {r7_segment}"

                nc_8 = (
                    f"{current_target} bhagode {h}\n"
                    "𒈙🟪⸻🟦𒈙🟩⸻🟨𒈙🟧⸻🟥𒈙🟪⸻🟦𒈙🟩⸻🟨𒈙🟧⸻🟥𒈙🟪⸻🟦𒈙🟩⸻🟨𒈙🟧⸻🟥𒈙🟪⸻🟦𒈙🟩⸻🟨𒈙🟧⸻🟥𒈙🟪⸻🟦𒈙🟩⸻🟨𒈙🟧⸻🟥𒈙🟪⸻🟦𒈙🟩⸻🟨𒈙🟧⸻🟥𒈙🟪⸻🟦𒈙🟩⸻🟨𒈙🟧⸻🟥𒈙🟪⸻🟦𒈙🟩⸻🟨𒈙🟧⸻🟥𒈙🟪⸻🟦𒈙🟩⸻🟨𒈙🟧⸻🟥𒈙🟪⸻🟦𒈙🟩⸻🟨𒈙🟧⸻🟥"
                )

                nc_9 = f"{current_target} MADRCHOD {h}\n" + ("᳄" * 150)
                nc_10 = f"{current_target} <{h}>"

                r11 = "".join([f"𒐫{h}" for _ in range(100)])
                nc_11 = (
                    f"{current_target}  {h}\n"
                    f"{r11}\n{r11}\n{r11}\n{r11}"
                )

                r12_segment = f"-{h}-𓍯𓂃⚚  "
                nc_12 = (
                    f"{current_target}  {h}\n"
                    f"{r12_segment * 100}\n"
                    f"-{h}-𓍯𓂃-{h}-𓍯𓂃⚚"
                )

                r13_segment = "".join([f"𓂸{h}" for _ in range(100)])
                nc_13 = f"{current_target} TMKC {r13_segment}"

                r14_segment = "".join([f"𓇽🍁" for _ in range(100)])
                nc_14 = f"{current_target} CHUD RNDYYCEH {h}\n{r14_segment}"

                nc_15 = (
                    f"{current_target} rndyyceh {h}\n"
                    "𓂃𓊆❤︎𓊇𓂃𓊆🤍𓊇𓂃𓊆🤎𓊇𓂃𓊆🩷𓊇𓂃𓊆💜𓊇𓂃𓊆💙𓊇𓂃𓊆🩵𓊇𓂃𓊆❤️𓊇𓂃𓊆🧡𓊇𓂃𓊆🤍𓊇𓂃𓊆🤎𓊇𓂃𓊆🩷𓊇𓂃𓊆💜𓊇𓂃𓊆💙𓊇𓂃𓊆🩵𓊇𓂃𓊆❤️𓊇𓂃𓊆🧡𓊇𓂃𓊆🤍𓊇𓂃𓊆🤎𓊇𓂃𓊆🩷𓊇𓂃𓊆💜𓊇𓂃𓊆💙𓊇𓂃𓊆🩵𓊇𓂃𓊆❤️𓊇𓂃𓊆🧡𓊇𓂃𓊆🤍𓊇𓂃𓊆🤎𓊇𓂃𓊆🩷𓊇𓂃𓊆💜𓊇𓂃𓊆💙𓊇𓂃𓊆🩵𓊇𓂃𓊆❤️𓊇𓂃𓊆🧡𓊇𓂃𓊆🤍𓊇𓂃𓊆🤎𓊇𓂃𓊆🩷𓊇𓂃𓊆💜𓊇𓂃𓊆💙𓊇𓂃𓊆🩵𓊇𓂃𓊆❤️𓊇𓂃𓊆🧡𓊇𓂃𓊆🤍𓊇𓂃𓊆🤎𓊇𓂃𓊆🩷𓊇𓂃𓊆💜𓊇𓂃𓊆💙𓊇𓂃𓊆🩵𓊇𓂃𓊆❤️𓊇𓂃𓊆🧡𓊇𓂃𓊆🤍𓊇𓂃𓊆🤎𓊇𓂃𓊆🩷𓊇𓂃𓊆💜𓊇𓂃𓊆💙𓊇𓂃𓊆🩵𓊇𓂃𓊆❤️𓊇"
                )

                r16_segment = "".join([f"𒋨{ce16}" for _ in range(100)])
                nc_16 = f"{current_target} tmkc {r16_segment}"

                r17_flowers = "".join([f"𓇢𓆸 {random.choice(NC17_FLOWER_EMOJIS)} " for _ in range(50)])
                nc_17 = f"{current_target} CHUD {r17_flowers}"

                r18_segment = "".join([f"➤{ce18}" for _ in range(100)])
                nc_18 = f"{current_target} TERI MAA CHODTE HUE ENTRY\n{r18_segment}"

                r19_segment = "".join([f"~{ce19}~" for _ in range(100)])
                nc_19 = f"{current_target} TMKC {r19_segment}"

                nc_20 = f"{current_target} Tmkc {ce20} ᥫ᭡.ִֶָ𓂃 🦋 𓂃˖˳·˖ ִֶָ ⋆♡⋆ ִֶָ˖·˳˖ 🧿  ִֶָ𓍯𓂃𓏧♡ ᥫ᭡.ִֶָ𓂃 🦋 𓂃˖˳·˖ ִֶָ ⋆♡⋆ ִֶָ˖·˳˖ 🧿  ִֶָ𓍯𓂃𓏧♡𝗕ᴏ𝗟 Ƙ๏Ꮗᴋ𝐀 𝗔ʙ𝗕ᴜᥫ᭡.ִֶָ𓂃🌀𓂃˖˳·˖ ִֶָ ⋆♡⋆ ִֶָ˖·˳˖𓂃🩷 ִֶָ𓍯𓂃𓏧♡ᥫ᭡.ִֶָ𓂃🌀𓂃˖˳·˖ ִֶָ ⋆♡⋆ ִֶָ˖·˳˖𓂃🩷 ִֶָ𓍯𓂃𓏧♡"

                if style == "1":
                    raw_title = original_nc
                elif style == "2":
                    raw_title = block_nc
                elif style == "3":
                    raw_title = nc_3
                elif style == "4":
                    raw_title = nc_4
                elif style == "5":
                    raw_title = nc_5
                elif style == "6":
                    raw_title = nc_6
                elif style == "7":
                    raw_title = nc_7
                elif style == "8":
                    raw_title = nc_8
                elif style == "9":
                    raw_title = nc_9
                elif style == "10":
                    raw_title = nc_10
                elif style == "11":
                    raw_title = nc_11
                elif style == "12":
                    raw_title = nc_12
                elif style == "13":
                    raw_title = nc_13
                elif style == "14":
                    raw_title = nc_14
                elif style == "15":
                    raw_title = nc_15
                elif style == "16":
                    raw_title = nc_16
                elif style == "17":
                    raw_title = nc_17
                elif style == "18":
                    raw_title = nc_18
                elif style == "19":
                    raw_title = nc_19
                elif style == "20":
                    raw_title = nc_20
                else:
                    raw_title = original_nc

                new_title = raw_title[:255]
                nc_counter += 1

                payload = {"chat_id": chat_id, "title": new_title}
                async with session.post(url, json=payload, timeout=3.0) as resp:
                    if resp.status == 200:
                        with lock:
                            total_nc_changed += 1

                elapsed = asyncio.get_event_loop().time() - loop_start
                sleep_time = max(0.1, token_nc_interval - elapsed)
                await asyncio.sleep(sleep_time)

            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(0.5)

async def run_async_nc_engine(chat_id):
    nc_running[chat_id] = True
    total_bots = len(bot_tokens)
    tasks = [
        asyncio.create_task(async_token_nc_loop(chat_id, token, idx, total_bots))
        for idx, token in enumerate(bot_tokens)
    ]
    while nc_running.get(chat_id, False):
        await asyncio.sleep(0.05)
    for task in tasks:
        task.cancel()

def start_async_nc_thread(chat_id):
    nc_running[chat_id] = False
    time.sleep(0.05)
    def runner():
        asyncio.run(run_async_nc_engine(chat_id))
    t = threading.Thread(target=runner)
    t.daemon = True
    t.start()

def setup_telegram_listeners():
    if not main_bot_instance:
        return

    main_bot = main_bot_instance

    def send_photo_safely(message, caption_text):
        try:
            main_bot.send_photo(
                message.chat.id, 
                PHOTO_URL, 
                caption=caption_text, 
                reply_to_message_id=message.message_id
            )
        except Exception as e3:
            print(f"❌ Photo Send Error: {e3}")
            try:
                main_bot.reply_to(message, caption_text)
            except Exception as e4:
                print(f"Text fallback error: {e4}")

    @main_bot.message_handler(func=lambda message: message.text and message.text.startswith('π'))
    def handle_prefixed_commands(message):
        user_id = message.from_user.id
        username = f"@{message.from_user.username}" if message.from_user.username else ""
        chat_id = message.chat.id
        text = message.text.strip()
        parts = text.split(maxsplit=2)
        if not parts:
            return
        cmd = parts[0][1:].lower()

        target_name = message.from_user.first_name if message.from_user else "User"
        unauthorized_box = (
            "╔═══════✦✧✦═══════╗\n"
            "                  𝗞𝗼𝘄𝗸𝗮 𝗔𝗯𝗯𝘂 \n"
            "╚═══════✦✧✦═══════╝\n"
            "  \n"
            f"  {target_name} > 𝐒ᴜɴ 𝐑ᴀɴᴅʏᴄᴇ\n\n"
            "𝗞𝗼𝘄𝗸𝗮 𝗸𝗼 𝗕𝗮𝗮𝗽 𝗕𝗮𝗻𝗮 𝗟𝗲 𝗖𝗵𝗼𝗺𝘂 😝 \n"
            "   \n"
            "👤 ᴏᴡɴᴇʀ =@Hyyloser\n\n"
            "━━━━━━━━━━━━━━━\n"
            "𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ 𝗞𝗼𝘄𝗸𝗮\n"
            "━━━━━━━━━━━━━━━"
        )

        if not is_authorized(user_id, username):
            send_photo_safely(message, unauthorized_box)
            return

        if cmd in ['start', 'help', 'menu']:
            help_text = (
                "╭─══━─══─≪ ✠ ≫─══━─══─╮\n"
                "               ㅤ 𝗞๏Ꮗᴋ𝘈 𝐄ɴɢɪɴᴇ\n"
                "┗─══─━══─≪ ✠ ≫─══━─══─┛\n\n"
                "╭────┈┈┈┄┄╌╌╌╌┄┄┈┈┈────╮\n"
                "ㅤㅤㅤ《⚡ 𝗞๏Ꮗᴋ𝘈 Ɲᴄˢ ⚡》\n\n"
                "➠ kowkanc1    ➠ kowkanc2\n"
                "➠ kowkanc3    ➠ kowkanc4\n"
                "➠ kowkanc5    ➠ kowkanc6\n"
                "➠ kowkanc7    ➠ kowkanc8\n"
                "➠ kowkanc9    ➠ kowkanc10\n"
                "➠ kowkanc11  ➠ kowkanc12\n"
                "➠ kowkanc13  ➠ kowkanc14\n"
                "➠ kowkanc15  ➠ kowkanc16\n"
                "➠ kowkanc17  ➠ kowkanc18\n"
                "➠ kowkanc19  ➠kowkanc20\n\n"
                "╰────┈┈┈┄┄╌╌╌╌┄┄┈┈┈────╯\n\n"
                "╭────┈┈┈┄┄╌╌╌╌┄┄┈┈┈────╮\n"
                "ㅤㅤㅤ《🌀 𝗞๏Ꮗᴋ𝘈 Ƨʟ𝚒ᴅꫀ 🌀》\n\n"
                "➠ xslide\n\n"
                "╰────┈┈┈┄┄╌╌╌╌┄┄┈┈┈────╯\n\n"
                "╭────┈┈┈┄┄╌╌╌╌┄┄┈┈┈────╮\n"
                "ㅤㅤㅤ《🛑 𝗞๏Ꮗᴋ𝘈 𝐒𝚃ꪮ𝗣 🛑》\n\n"
                "➠ stopnc\n"
                "➠ stopslide\n"
                "➠ stopall\n\n"
                "╰────┈┈┈┄┄╌╌╌╌┄┄┈┈┈────╯\n\n"
                "╭────┈┈┈┄┄╌╌╌╌┄┄┈┈┈────╮\n"
                "ㅤㅤㅤ《🤍 𝗞๏Ꮗᴋ𝘈 𝐒ᴘꫀᥴɪƛʟ 🤍》\n\n"
                "➠ ping\n"
                "➠ status\n"
                "➠ leave\n"
                "➠ over\n\n"
                "╰────┈┈┈┄┄╌╌╌╌┄┄┈┈┈────╯\n"
                "ㅤ ㅤ ㅤ┏•━•━•━ ◎ ━•━•━•┓\n"
                "ㅤㅤ  ㅤㅤㅤ ᴘʀᴇғɪx - π\n"
                "ㅤㅤㅤ  ┗•━•━•━ ◎ ━•━•━•┛"
            )
            send_photo_safely(message, help_text)

        elif cmd.startswith('kowkanc') and cmd[7:].isdigit():
            style_num = cmd[7:]
            if 1 <= int(style_num) <= 20:
                if len(parts) > 1:
                    target = parts[1].strip()
                    with lock:
                        chat_targets[chat_id] = target
                    chat_nc_style[chat_id] = style_num
                    start_async_nc_thread(chat_id)
                    main_bot.reply_to(message, f"⚡ Kowka NC Style {style_num} started with target: {target}")
                else:
                    chat_states[chat_id] = f"WAITING_KOWKANC_TARGET_STYLE_{style_num}"
                    chat_state_users[chat_id] = user_id
                    main_bot.reply_to(message, f"🎯 Kowka NC Style {style_num} Selected!\n👉 Please send the Target Name directly:")
            else:
                main_bot.reply_to(message, "❌ Invalid style number! Use kowkanc1 to kowkanc20.")

        elif cmd == 'xslide':
            if message.reply_to_message:
                target_msg_id = message.reply_to_message.message_id
                target_user = message.reply_to_message.from_user
                
                if target_user.username:
                    target_display = f"@{target_user.username}"
                else:
                    target_display = target_user.first_name if target_user.first_name else "TARGET"
                
                with lock:
                    chat_targets[chat_id] = target_display
                
                start_async_slide_thread(chat_id, target_msg_id)
                main_bot.reply_to(message, f"🌀 𝖧𝖺𝗍𝖾𝗋 𝗄𝗂 𝗆𝗄𝖻 𝗆𝖺𝗋𝗇𝖺 𝗌𝗍𝖺𝗋𝗍: {target_display}!")
            else:
                main_bot.reply_to(message, "❌ 𝖱𝖺𝗇𝖽𝗒𝖼𝖾 𝖻𝖺𝖼𝗁𝖾 𝗄𝗈 𝗋𝖾𝗉𝗅𝗒 𝗄𝗋𝗈 𝗌𝗂𝗋 𝗃𝗂")

        elif cmd == 'stopslide':
            slide_running[chat_id] = False
            main_bot.reply_to(message, "🛑 𝖪𝗈𝗐𝗄𝖠 𝗌𝗂𝗋 𝗌𝗅𝗂𝖽𝖾 𝗌𝗍𝗈𝗉")

        elif cmd == 'stopnc':
            nc_running[chat_id] = False
            main_bot.reply_to(message, "🛑 𝖪𝗈𝗐𝗄𝖠 𝗌𝗂𝗋 𝗇𝖼 𝖼𝗅𝗈𝗌𝖾 𝗄𝗋 𝖽𝗂")

        elif cmd == 'stopall':
            slide_running[chat_id] = False
            nc_running[chat_id] = False
            main_bot.reply_to(message, "🛑 𝐊ᴏᴡᴋ𝖠 सब चुदाई 𝗢𝖿𝖿")

        elif cmd == 'leave':
            left_text = (
                "╔═══════✦✧✦═══════╗\n"
                "                     𝗞𝗼𝘄𝗸𝗮 \n"
                "╚═══════✦✧✦═══════╝\n\n"
                "    𝐑ᴀɴᴅʏᴄᴇ ʙᴀᴄʜᴇ    \n\n"
                "    𝗞𝗼𝘄𝗸𝗮 𝗯𝗮𝗮𝗽 𝗸𝗼 𝗯𝗵𝘂𝗹𝗻𝗮 𝗺𝗮𝘁 \n"
                "    𝐁ʏᴇ 𝐁ʏᴇ \n\n"
                "👤 ᴏᴡɴᴇʀ =@Hyyloser\n\n"
                "━━━━━━━━━━━━━━━\n"
                "𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ 𝗞𝗼𝘄𝗸𝗮\n"
                "━━━━━━━━━━━━━━━"
            )
            slide_running[chat_id] = False
            nc_running[chat_id] = False
            send_photo_safely(message, left_text)
            
            def leave_group():
                for token in bot_tokens:
                    try:
                        requests.post(f"https://api.telegram.org/bot{token}/leaveChat", json={"chat_id": chat_id}, timeout=3)
                    except Exception:
                        pass
            threading.Thread(target=leave_group, daemon=True).start()

        elif cmd == 'over':
            target = parts[1].strip() if len(parts) > 1 else chat_targets.get(chat_id, "TARGET")
            now = datetime.now()
            over_text = (
                "╔═══════✦✧✦═══════╗\n"
                "         𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ 𝗞𝗼𝘄𝗸𝗮\n"
                "╚═══════✦✧✦═══════╝\n\n"
                f"{target} 𝐓ᴇʀɪ ᴍᴀᴀ ᴍᴀʀ ɢʏɪ \n"
                "𝐀ʙ 𝐓ᴜ 𝐌ᴀᴀ 𝐂ʜᴜᴅᴀ 𝐘ᴀ 𝐑ʀ 𝐊ᴀʀ 𝐈ᴅᴋ\n\n"
                f"𝐂ᴜʀʀᴇɴᴛ ᴅᴀᴛᴇ = {now.strftime('%d-%m-%Y')}\n"
                f"𝐂ᴜʀʀᴇɴᴛ ᴛɪᴍᴇ = {now.strftime('%H:%M:%S')}\n\n"
                "👤 ᴏᴡɴᴇʀ =@Hyyloser\n\n"
                "━━━━━━━━━━━━━━━\n"
                f" {target}  𝖥ᴜᴄᴋᴇᴅ ʙʏ 𝗞𝗼𝘄𝗸𝗮\n"
                "━━━━━━━━━━━━━━━"
            )
            send_photo_safely(message, over_text)

        elif cmd in ['ping', 'status']:
            start_t = time.time()
            try:
                requests.get(f"https://api.telegram.org/bot{valid_tokens[0]}/getMe", timeout=2)
                ping_ms = int((time.time() - start_t) * 1000)
            except Exception:
                ping_ms = "N/A"

            status_text = (
                "╔═══════✦✧✦═══════╗\n"
                "                      𝗞𝗼𝘄𝗸𝗮\n"
                "╚═══════✦✧✦═══════╝\n\n"
                f"🌬️ Ping = {ping_ms}ms\n\n"
                f"🌬️ Nc task = {'Running 🟢' if nc_running.get(chat_id, False) else 'Stopped 🔴'}\n\n"
                f"🌬️ Slide task = {'Running 🟢' if slide_running.get(chat_id, False) else 'Stopped 🔴'}\n\n"
                f"🌬️ Total Bots = {len(bot_tokens)}\n\n"
                "👤 ᴏᴡɴᴇʀ =@Hyyloser\n\n"
                "━━━━━━━━━━━━━━━\n"
                "   Ƙᴀʀᴛᴀ Ɗʜᴀʀᴛᴀ 𝗞𝗈𝗐𝗄𝖠\n"
                "━━━━━━━━━━━━━━━"
            )
            send_photo_safely(message, status_text)

    @main_bot.message_handler(func=lambda message: message.chat.id in chat_states and chat_states[message.chat.id] != "IDLE")
    def handle_states(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        if chat_id in chat_state_users and chat_state_users[chat_id] != user_id:
            return

        state = chat_states.get(chat_id, "IDLE")
        text = message.text.strip() if message.text else ""

        if state.startswith("WAITING_KOWKANC_TARGET_STYLE_"):
            style_num = state.split("_")[-1]
            with lock:
                chat_targets[chat_id] = text
            chat_nc_style[chat_id] = style_num
            chat_states[chat_id] = "IDLE"
            if chat_id in chat_state_users:
                del chat_state_users[chat_id]
            start_async_nc_thread(chat_id)
            main_bot.reply_to(message, f"⚡ Kowka kowkanc style {style_num} started with target: {text}")

    def run_polling():
        while True:
            try:
                print("🚀 Fast Polling Active...")
                main_bot.infinity_polling(
                    none_stop=True,
                    skip_pending=True,
                    timeout=10,
                    long_polling_timeout=5,
                    interval=0  # Instant response trigger
                )
            except Exception as e:
                print(f"⚠️ Network Reset Handled: {e}. Reconnecting instantly...")
                if "409" in str(e):
                    time.sleep(2)
                else:
                    time.sleep(1)

    threading.Thread(target=run_polling, daemon=True).start()

def main():
    global valid_tokens, bot_tokens, main_bot_instance, OWNER_ID
    banner()
    OWNER_ID = OWNER_ID_INPUT
    token_list = [str(t).strip() for t in TOKENS_INPUT if str(t).strip()]

    print(f"\n[+] Total Tokens Loaded: {len(token_list)}")
    print(f"[+] Authenticated Owner ID: {OWNER_ID}")

    print("\n[+] Initializing High-Speed Non-Blocking Engine Pool...")
    for idx, token in enumerate(token_list, 1):
        try:
            r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=3)
            if r.status_code == 200:
                valid_tokens.append(token)
                bot_tokens.append(token)
                print(f"[✔] Bot {idx}: Ready & Verified!")
            else:
                print(f"[-] Bot {idx}: Invalid Token!")
        except Exception as e:
            print(f"[-] Bot {idx}: Connection Error!")

    if not valid_tokens:
        print("[-] Error: No valid tokens found! Exiting.")
        return

    main_bot_instance = telebot.TeleBot(valid_tokens[0])
    print("\n" + "=" * 65)
    print("🚀 HIGH-SPEED NON-BLOCKING ROTATING ENGINE FULLY ACTIVATED")
    print("=" * 65)

    setup_telegram_listeners()

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("\n[!] Bot stopped manually.")
        sys.exit(0)

if __name__ == "__main__":
    main()