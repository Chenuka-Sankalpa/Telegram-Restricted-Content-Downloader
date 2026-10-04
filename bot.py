"""
Telegram Restricted Downloader Bot
Developed By Chenuxx
"""

import os
import re
import json
import time
import asyncio
import aiohttp
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.functions.channels import (
    LeaveChannelRequest,
    JoinChannelRequest,
)
from telethon.tl.functions.messages import (
    ImportChatInviteRequest,
    CheckChatInviteRequest,
)
from telethon.tl.types import Channel, Chat
from telethon.errors import (
    UserAlreadyParticipantError,
    InviteHashExpiredError,
    InviteHashInvalidError,
    ChannelsTooMuchError,
)

load_dotenv()

# ============================================================
# Configuration
# ============================================================
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SESSION_NAME = os.getenv("SESSION_NAME", "user_session")
LOCAL_API_URL = os.getenv("LOCAL_API_URL", "http://localhost:3333")

# Owner ID — change this to your own Telegram user ID
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
ALLOWED_FILE = "allowed_users.json"

# Pending link timeout (seconds)
PENDING_LINK_TIMEOUT = int(os.getenv("PENDING_LINK_TIMEOUT", "60"))
PENDING_LINKS = {}

# Access wait timeout (seconds)
ACCESS_WAIT_SECONDS = int(os.getenv("ACCESS_WAIT_SECONDS", "10"))

# ============================================================
# Messages
# ============================================================
FOOTER = "\n\n⚡ **Developed By Chenuxx**"

DENIED_MESSAGE = (
    "⛔ **Access Denied**\n\n"
    "You are not authorized to use this bot.\n"
    "Contact the owner for access."
    + FOOTER
)

# ============================================================
# Channel ID Helpers
# ============================================================
def normalize_channel_id(cid):
    if cid is None:
        return None
    cid_str = str(cid)
    if cid_str.startswith("-100"):
        return int(cid)
    if cid > 0:
        return int(f"-100{cid}")
    if cid < 0 and not cid_str.startswith("-100"):
        return int(f"-100{abs(cid)}")
    return int(cid)


def extract_raw_id(cid):
    if cid is None:
        return None
    cid_str = str(cid)
    if cid_str.startswith("-100"):
        return int(cid_str[4:])
    if cid > 0:
        return int(cid)
    return int(abs(cid))


# ============================================================
# JSON File Managers
# ============================================================
def load_allowed():
    if not os.path.exists(ALLOWED_FILE):
        data = {"allowed_users": [OWNER_ID]}
        with open(ALLOWED_FILE, "w") as f:
            json.dump(data, f, indent=4)
        return set(data["allowed_users"])
    try:
        with open(ALLOWED_FILE, "r") as f:
            data = json.load(f)
        return set(data.get("allowed_users", [OWNER_ID]))
    except Exception as e:
        print(f"⚠️ load_allowed error: {e}")
        return {OWNER_ID}


def save_allowed(allowed_set):
    with open(ALLOWED_FILE, "w") as f:
        json.dump({"allowed_users": list(allowed_set)}, f, indent=4)


ALLOWED_USERS = load_allowed()


# ============================================================
# Access Check
# ============================================================
def has_access(user_id):
    if user_id == OWNER_ID:
        return True
    if user_id in ALLOWED_USERS:
        return True
    return False


# ============================================================
# Decorators
# ============================================================
def restricted(func):
    async def wrapper(event):
        sender_id = event.sender_id
        if not has_access(sender_id):
            try:
                await event.reply(DENIED_MESSAGE)
            except:
                pass
            print(f"🚫 Blocked access attempt from user ID: {sender_id}")
            return
        return await func(event)
    return wrapper


def owner_only(func):
    async def wrapper(event):
        if event.sender_id != OWNER_ID:
            try:
                await event.reply("⛔ Owner only command." + FOOTER)
            except:
                pass
            return
        return await func(event)
    return wrapper


# ============================================================
# Telegram Clients
# ============================================================
bot = TelegramClient('bot_session', API_ID, API_HASH)
user = TelegramClient(SESSION_NAME, API_ID, API_HASH)

http_session = None


# ============================================================
# Utilities
# ============================================================
def format_time(seconds):
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.0f}s"


def format_size(size_bytes):
    mb = size_bytes / (1024 * 1024)
    if mb >= 1024:
        return f"{mb / 1024:.2f} GB"
    return f"{mb:.2f} MB"


async def live_timer(status_msg, start_time, label, get_progress=None):
    last_update = 0
    while True:
        await asyncio.sleep(2)
        elapsed = time.time() - start_time
        if elapsed - last_update < 1.5:
            continue
        last_update = elapsed
        try:
            if get_progress:
                current_size = get_progress()
                if current_size > 0 and elapsed > 0:
                    speed = (current_size / (1024 * 1024)) / elapsed
                    text = (
                        f"{label}\n\n"
                        f"⏱️ Time: {format_time(elapsed)}\n"
                        f"📊 Downloaded: {format_size(current_size)}\n"
                        f"⚡ Speed: {speed:.2f} MB/s"
                    )
                else:
                    text = f"{label}\n\n⏱️ Time: {format_time(elapsed)}"
            else:
                text = f"{label}\n\n⏱️ Time: {format_time(elapsed)}"
            await status_msg.edit(text)
        except Exception:
            break


def parse_link(link: str):
    link = link.strip()

    private_match = re.match(r"(?:https?://)?t\.me/c/(\d+)(?:/(\d+))?", link)
    if private_match:
        raw_id = int(private_match.group(1))
        channel_id = normalize_channel_id(raw_id)
        msg_id = int(private_match.group(2)) if private_match.group(2) else None
        return "private", channel_id, msg_id

    invite_match = re.match(r"(?:https?://)?t\.me/(?:\+|joinchat/)([a-zA-Z0-9_-]+)", link)
    if invite_match:
        return "invite", invite_match.group(1), None

    public_match = re.match(r"(?:https?://)?t\.me/([a-zA-Z0-9_]+)(?:/(\d+))?", link)
    if public_match:
        username = public_match.group(1)
        msg_id = int(public_match.group(2)) if public_match.group(2) else None
        return "public", username, msg_id

    return "unknown", None, None


# ============================================================
# Pending Link Manager
# ============================================================
def save_pending_link(user_id, channel_id, msg_id):
    PENDING_LINKS[user_id] = {
        "channel_id": channel_id,
        "msg_id": msg_id,
        "timestamp": time.time(),
    }
    print(f"📌 Pending link saved for user {user_id}: channel={channel_id}, msg={msg_id}")


def get_pending_link(user_id):
    if user_id not in PENDING_LINKS:
        return None
    data = PENDING_LINKS[user_id]
    if time.time() - data["timestamp"] > PENDING_LINK_TIMEOUT:
        del PENDING_LINKS[user_id]
        print(f"⌛ Pending link expired for user {user_id}")
        return None
    return data


def clear_pending_link(user_id):
    if user_id in PENDING_LINKS:
        del PENDING_LINKS[user_id]
        print(f"🗑️ Cleared pending link for user {user_id}")


# ============================================================
# Entity Resolvers
# ============================================================
async def resolve_invite_entity(invite_hash):
    try:
        invite_info = await user(CheckChatInviteRequest(invite_hash))
        if hasattr(invite_info, 'chat') and invite_info.chat:
            return invite_info.chat
        return None
    except Exception as e:
        print(f"⚠️ resolve_invite_entity error: {e}")
        return None


async def find_entity_by_title(title):
    try:
        async for dialog in user.iter_dialogs():
            if dialog.name and dialog.name.strip() == title.strip():
                return dialog.entity
    except Exception as e:
        print(f"⚠️ find_entity_by_title error: {e}")
    return None


async def has_channel_access(entity):
    try:
        await user.get_messages(entity, limit=1)
        return True
    except:
        return False


# ============================================================
# Join Channel
# ============================================================
async def try_join_channel(link_type, link_value):
    try:
        if link_type == "public":
            entity = await user.get_entity(link_value)
            try:
                await user(JoinChannelRequest(entity))
                return True, entity, f"✅ Joined public channel: @{link_value}"
            except UserAlreadyParticipantError:
                return True, entity, f"ℹ️ Already a member of @{link_value}"

        elif link_type == "invite":
            invite_title = None
            try:
                invite_info = await user(CheckChatInviteRequest(link_value))
                if hasattr(invite_info, 'title'):
                    invite_title = invite_info.title
                if hasattr(invite_info, 'chat') and invite_info.chat:
                    return True, invite_info.chat, "ℹ️ Already a member"
            except Exception as e:
                print(f"⚠️ CheckChatInvite error: {e}")

            try:
                await user(ImportChatInviteRequest(link_value))
            except UserAlreadyParticipantError:
                pass
            except InviteHashExpiredError:
                return False, None, "❌ Invite link has expired"
            except InviteHashInvalidError:
                return False, None, "❌ Invalid invite link"
            except ChannelsTooMuchError:
                return False, None, "❌ Too many channels joined"

            await asyncio.sleep(1)

            entity = await resolve_invite_entity(link_value)
            if entity:
                return True, entity, "✅ Joined via invite link"

            if invite_title:
                entity = await find_entity_by_title(invite_title)
                if entity:
                    return True, entity, "✅ Joined via invite link (found in dialogs)"

            await asyncio.sleep(1)
            try:
                async for dialog in user.iter_dialogs(limit=5):
                    if isinstance(dialog.entity, (Channel, Chat)):
                        if await has_channel_access(dialog.entity):
                            return True, dialog.entity, "✅ Joined via invite link (recent dialog)"
            except Exception as e:
                print(f"⚠️ iter_dialogs error: {e}")

            return False, None, "❌ Joined but could not resolve the channel. Try again."

        elif link_type == "private":
            return False, None, "❌ Cannot join internal private link. Need invite link."

        return False, None, "❌ Unknown link type"

    except Exception as e:
        return False, None, f"❌ Join failed: {str(e)}"


# ============================================================
# Leave Channel
# ============================================================
async def leave_entity(entity):
    try:
        if isinstance(entity, (Channel, Chat)):
            await user(LeaveChannelRequest(entity))
            print(f"🚪 Left: {entity.id}")
            return True
        return False
    except Exception as e:
        print(f"⚠️ Leave failed: {e}")
        return False


# ============================================================
# Wait for Access
# ============================================================
async def wait_for_access(entity, status_msg):
    start = time.time()
    while time.time() - start < ACCESS_WAIT_SECONDS:
        remaining = ACCESS_WAIT_SECONDS - int(time.time() - start)
        try:
            await user.get_messages(entity, limit=1)
            return True, entity
        except:
            pass
        try:
            await status_msg.edit(
                f"⏳ **Waiting for access...**\n\n"
                f"⏱️ Time remaining: **{remaining}s**"
                + FOOTER
            )
        except:
            pass
        await asyncio.sleep(1)
    return False, None


# ============================================================
# Process Media (Download + Upload)
# ============================================================
async def process_media(event, status, entity, msg_id, joined_entity, need_leave):
    global http_session
    total_start = time.time()
    timer_task = None

    try:
        if msg_id is None:
            async for msg in user.iter_messages(entity, limit=1):
                msg_id = msg.id
                break

        message = await user.get_messages(entity, ids=msg_id)

        if not message:
            await status.edit("❌ Message not found in this channel." + FOOTER)
            if need_leave and joined_entity:
                await leave_entity(joined_entity)
            return

        if message.photo:
            media_type = "photo"
        elif message.video:
            media_type = "video"
        elif message.document:
            media_type = "document"
        else:
            await status.edit("❌ No media found in that message." + FOOTER)
            if need_leave and joined_entity:
                await leave_entity(joined_entity)
            return

        # DOWNLOAD
        download_start = time.time()
        os.makedirs("downloads", exist_ok=True)
        file_path = f"downloads/{message.id}_{media_type}"
        downloaded_size = {"value": 0}

        def get_downloaded():
            return downloaded_size["value"]

        timer_task = asyncio.create_task(
            live_timer(status, download_start, "⬇️ **Downloading...**", get_downloaded)
        )

        async def progress_callback(current, total):
            downloaded_size["value"] = current

        file_path = await user.download_media(
            message, file=file_path, progress_callback=progress_callback
        )

        if timer_task:
            timer_task.cancel()
            timer_task = None

        download_end = time.time()
        download_time = download_end - download_start
        file_size = os.path.getsize(file_path)
        size_str = format_size(file_size)
        download_speed = (file_size / (1024 * 1024)) / download_time if download_time > 0 else 0

        # UPLOAD
        upload_start = time.time()
        upload_label = (
            f"📤 **Uploading...**\n\n"
            f"📦 Size: {size_str}\n"
            f"⬇️ Download: {format_time(download_time)} ({download_speed:.2f} MB/s)"
        )

        timer_task = asyncio.create_task(
            live_timer(status, upload_start, upload_label)
        )

        if http_session is None:
            http_session = aiohttp.ClientSession()

        if media_type == "photo":
            method, field_name = "sendPhoto", "photo"
        elif media_type == "video":
            method, field_name = "sendVideo", "video"
        else:
            method, field_name = "sendDocument", "document"

        url = f"{LOCAL_API_URL}/bot{BOT_TOKEN}/{method}"
        timeout = aiohttp.ClientTimeout(total=3600)

        with open(file_path, 'rb') as f:
            form = aiohttp.FormData()
            form.add_field('chat_id', str(event.chat_id))
            form.add_field(field_name, f, filename=os.path.basename(file_path))
            if message.text:
                form.add_field('caption', message.text[:1024])
            if media_type == "video":
                form.add_field('supports_streaming', 'true')

            async with http_session.post(url, data=form, timeout=timeout) as resp:
                result = await resp.json()
                if not result.get('ok'):
                    raise Exception(f"Upload failed: {result}")

        if timer_task:
            timer_task.cancel()
            timer_task = None

        upload_end = time.time()
        upload_time = upload_end - upload_start
        upload_speed = (file_size / (1024 * 1024)) / upload_time if upload_time > 0 else 0

        # LEAVE
        leave_msg = ""
        if need_leave and joined_entity:
            await status.edit("🚪 **Leaving the channel...**" + FOOTER)
            left = await leave_entity(joined_entity)
            if left:
                leave_msg = "\n🚪 **Left the channel** (auto-leave)"

        total_end = time.time()
        total_time = total_end - total_start

        emoji = {"photo": "🖼️", "video": "🎥", "document": "📄"}.get(media_type, "📦")
        summary = (
            f"✅ **{emoji} {media_type.capitalize()} sent successfully!**\n\n"
            f"📦 **Size:** {size_str}\n"
            f"⬇️ **Download:** {format_time(download_time)} ({download_speed:.2f} MB/s)\n"
            f"⬆️ **Upload:** {format_time(upload_time)} ({upload_speed:.2f} MB/s)\n"
            f"⏱️ **Total Time:** {format_time(total_time)}"
            f"{leave_msg}"
            + FOOTER
        )
        await status.edit(summary)

        try:
            os.remove(file_path)
        except:
            pass

    except Exception as e:
        if timer_task:
            timer_task.cancel()
        if need_leave and joined_entity:
            try:
                await leave_entity(joined_entity)
            except:
                pass
        total_end = time.time()
        total_time = total_end - total_start
        await status.edit(
            f"⚠️ **Error:** `{str(e)}`\n\n"
            f"⏱️ Time wasted: {format_time(total_time)}"
            + FOOTER
        )


# ============================================================
# /start
# ============================================================
@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    sender_id = event.sender_id

    if not has_access(sender_id):
        await event.reply(DENIED_MESSAGE)
        print(f"🚫 Blocked /start from user ID: {sender_id}")
        return

    await event.reply(
        "👋 **Welcome!**\n\n"
        "Send me a link and I will download the media for you.\n\n"
        "**Supported Links:**\n"
        "• Public: `https://t.me/channelname/12`\n"
        "• Private: `https://t.me/c/1234567890/12`\n"
        "• Invite: `https://t.me/+xxxxxxxxx`\n\n"
        "**How it works:**\n"
        "1️⃣ Send a `t.me/c/...` link\n"
        "2️⃣ If no access, bot asks for invite link\n"
        "3️⃣ Send `t.me/+xxx` invite link within **60s**\n"
        "4️⃣ Bot joins, downloads the original content, then leaves\n\n"
        "**Supported Media:**\n"
        "🖼️ Photos | 🎥 Videos | 📄 Documents\n\n"
        "📦 Max file size: 2GB"
        + FOOTER
    )


# ============================================================
# /add
# ============================================================
@bot.on(events.NewMessage(pattern=r'^/add(?:@\w+)?\s+(@?\w+)'))
@owner_only
async def add_user_handler(event):
    match = re.match(r'^/add(?:@\w+)?\s+(@?\w+)', event.message.text)
    if not match:
        await event.reply("❌ Format: `/add @username`" + FOOTER)
        return

    username = match.group(1).replace("@", "")
    status = await event.reply(f"🔍 Searching for @{username}...")

    try:
        entity = await user.get_entity(username)
        user_id = entity.id
        if user_id in ALLOWED_USERS:
            await status.edit(f"⚠️ @{username} is already allowed.\n🆔 ID: `{user_id}`" + FOOTER)
            return
        ALLOWED_USERS.add(user_id)
        save_allowed(ALLOWED_USERS)
        await status.edit(
            f"✅ **@{username} added successfully!**\n\n"
            f"🆔 ID: `{user_id}`\n"
            f"👥 Total allowed users: `{len(ALLOWED_USERS)}`"
            + FOOTER
        )
    except Exception as e:
        await status.edit(f"⚠️ Error: `{str(e)}`\n\nCould not find @{username}." + FOOTER)


# ============================================================
# /remove
# ============================================================
@bot.on(events.NewMessage(pattern=r'^/remove(?:@\w+)?\s+(@?\w+)'))
@owner_only
async def remove_user_handler(event):
    match = re.match(r'^/remove(?:@\w+)?\s+(@?\w+)', event.message.text)
    if not match:
        await event.reply("❌ Format: `/remove @username`" + FOOTER)
        return

    username = match.group(1).replace("@", "")
    status = await event.reply(f"🔍 Searching for @{username}...")

    try:
        entity = await user.get_entity(username)
        user_id = entity.id
        if user_id == OWNER_ID:
            await status.edit("⛔ Cannot remove the owner." + FOOTER)
            return
        if user_id not in ALLOWED_USERS:
            await status.edit(f"⚠️ @{username} is not in the allowed list." + FOOTER)
            return
        ALLOWED_USERS.discard(user_id)
        save_allowed(ALLOWED_USERS)
        await status.edit(
            f"✅ **@{username} removed successfully!**\n\n"
            f"🆔 ID: `{user_id}`\n"
            f"👥 Total allowed users: `{len(ALLOWED_USERS)}`"
            + FOOTER
        )
    except Exception as e:
        await status.edit(f"⚠️ Error: `{str(e)}`" + FOOTER)


# ============================================================
# /list
# ============================================================
@bot.on(events.NewMessage(pattern=r'^/list(?:@\w+)?$'))
@owner_only
async def list_users_handler(event):
    lines = ["👥 **Allowed Users:**\n"]
    for i, uid in enumerate(ALLOWED_USERS, 1):
        tag = " (Owner)" if uid == OWNER_ID else ""
        lines.append(f"{i}. `{uid}`{tag}")
    lines.append(f"\n**Total: {len(ALLOWED_USERS)}**")
    await event.reply("\n".join(lines) + FOOTER)


# ============================================================
# Link Handler
# ============================================================
@bot.on(events.NewMessage(pattern=r'(https?://)?t\.me/'))
@restricted
async def link_handler(event):
    global http_session
    sender_id = event.sender_id
    link = event.message.text.strip()
    link_type, link_value, msg_id = parse_link(link)

    if link_type == "unknown":
        await event.reply("❌ Invalid link. Please check and try again." + FOOTER)
        return

    status = await event.reply("🔍 Processing link..." + FOOTER)

    try:
        # CASE 1: Private internal link
        if link_type == "private":
            try:
                entity = await user.get_entity(link_value)
                if await has_channel_access(entity):
                    await process_media(event, status, entity, msg_id, None, False)
                    return
            except:
                pass

            save_pending_link(sender_id, link_value, msg_id)

            await status.edit(
                "❌ **Cannot access this private channel.**\n\n"
                "This is an internal link (`t.me/c/...`). The bot cannot join it directly.\n\n"
                "📩 **Please send the invite link** (`t.me/+xxx`) for this channel **within 60 seconds**.\n\n"
                "The bot will join, download the content from your original link, then leave."
                + FOOTER
            )
            return

        # CASE 2: Invite link
        elif link_type == "invite":
            pending = get_pending_link(sender_id)

            await status.edit("🔓 **Joining channel via invite link...**" + FOOTER)

            success, entity, msg = await try_join_channel(link_type, link_value)

            if not success:
                await status.edit(msg + FOOTER)
                clear_pending_link(sender_id)
                return

            joined_entity = entity

            await status.edit(
                f"✅ **Joined successfully!**\n\n"
                f"⏳ Waiting for access to propagate..."
                + FOOTER
            )
            await asyncio.sleep(2)

            has_access_ch, entity = await wait_for_access(entity, status)
            if not has_access_ch:
                await status.edit("❌ Access not available. Leaving..." + FOOTER)
                if joined_entity:
                    await leave_entity(joined_entity)
                clear_pending_link(sender_id)
                return

            if pending:
                pending_channel_id = pending["channel_id"]
                pending_msg_id = pending["msg_id"]

                joined_raw = extract_raw_id(entity.id)
                pending_raw = extract_raw_id(pending_channel_id)

                print(f"🔍 Channel ID check:")
                print(f"   Joined raw: {joined_raw}")
                print(f"   Pending raw: {pending_raw}")

                if joined_raw == pending_raw:
                    await status.edit(
                        f"✅ **Channel matched!**\n\n"
                        f"📥 Downloading the original content..."
                        + FOOTER
                    )
                    await process_media(event, status, entity, pending_msg_id, joined_entity, True)
                    clear_pending_link(sender_id)
                    return
                else:
                    await status.edit(
                        f"⚠️ **Channel mismatch!**\n\n"
                        f"Expected: `{pending_raw}`\n"
                        f"Got: `{joined_raw}`\n\n"
                        f"Leaving the channel..."
                        + FOOTER
                    )
                    await leave_entity(joined_entity)
                    clear_pending_link(sender_id)
                    return
            else:
                await process_media(event, status, entity, None, joined_entity, True)
                return

        # CASE 3: Public link
        elif link_type == "public":
            try:
                entity = await user.get_entity(link_value)
                if not await has_channel_access(entity):
                    success, entity, msg = await try_join_channel(link_type, link_value)
                    if not success:
                        await status.edit(msg + FOOTER)
                        return
                    await process_media(event, status, entity, msg_id, entity, True)
                else:
                    await process_media(event, status, entity, msg_id, None, False)
            except Exception as e:
                await status.edit(f"❌ Could not find this public channel: `{str(e)}`" + FOOTER)
            return

    except Exception as e:
        await status.edit(f"⚠️ **Error:** `{str(e)}`" + FOOTER)


# ============================================================
# Cleanup Pending Links
# ============================================================
async def cleanup_pending_links():
    while True:
        await asyncio.sleep(30)
        now = time.time()
        expired = [
            uid for uid, data in PENDING_LINKS.items()
            if now - data["timestamp"] > PENDING_LINK_TIMEOUT
        ]
        for uid in expired:
            del PENDING_LINKS[uid]
            print(f"⌛ Expired pending link for user {uid}")


# ============================================================
# Main
# ============================================================
async def main():
    global http_session

    await bot.start(bot_token=BOT_TOKEN)
    await user.start()

    http_session = aiohttp.ClientSession()

    asyncio.create_task(cleanup_pending_links())

    print("=" * 50)
    print("✅ User client ready!")
    print("🤖 Bot is running")
    print(f"📡 Local Bot API URL: {LOCAL_API_URL}")
    print(f"📦 Max file size: 2GB")
    print("🖼️ Media: Photo + Video + Document")
    print("⏱️ LIVE Timer + Speed: ENABLED")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"👥 Allowed Users: {len(ALLOWED_USERS)}")
    print(f"⏳ Pending Link Timeout: {PENDING_LINK_TIMEOUT}s")
    print("🔓 Auto-Join + 🚪 Auto-Leave: ENABLED")
    print("⚡ Developed By Chenuxx")
    print("=" * 50)

    try:
        await bot.run_until_disconnected()
    finally:
        await http_session.close()


if __name__ == "__main__":
    asyncio.run(main())
