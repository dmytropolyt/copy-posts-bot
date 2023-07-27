import os
import re
import logging
import asyncio

import config
from models import GroupDAL, async_session
from helpers import get_media_type

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.builtin import ChatTypeFilter

from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError


bot = Bot(config.TOKEN)
dp = Dispatcher(bot=bot)


logging.basicConfig(level=logging.INFO)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
client = TelegramClient(
    config.USERNAME, config.API_ID,
    config.API_HASH, loop=loop).start(phone=config.PHONE)


async def get_member_groups(message: types.Message):
    async with async_session() as session:
        groups_dal = GroupDAL(session)
        all_groups = await groups_dal.select_all_groups()

        # Get updates for adding a new groups where bot is admin to db
        updates = await bot.get_updates(limit=100)

        if updates:
            for update in updates:
                if update.message.chat:
                    # Get chat id
                    chat = update.message.chat.id

                    # Check if chat has been already in db
                    if str(chat) not in all_groups:
                        # Get chat admins
                        admins = await bot.get_chat_administrators(chat)

                        # Add chat to db
                        for admin in admins:
                            if bot.id == admin.user.id:
                                await groups_dal.create_group(str(chat))
                                break


async def send_posts(event: events.NewMessage):
    message = event.message

    # Check if that is album, if it isn't - proceed
    if not message.grouped_id:
        async with async_session() as session:
            groups_dal = GroupDAL(session)
            groups = await groups_dal.select_all_groups()
        
        for chat in groups:
            if message.media:
                await message.download_media(file='media')
                media_path = config.MEDIA_PATH
                for file in media_path.iterdir():

                    # Check type of media
                    file_type = get_media_type(file)
                    if file_type == 'image':
                        await bot.send_photo(
                            int(chat), photo=types.InputFile(file), caption=message.message
                        )
                    elif file_type == 'video':
                        await bot.send_video(
                            int(chat), video=types.InputFile(file), caption=message.message
                        )

                    # Delete file
                    file.unlink()

            elif message.message:
                await bot.send_message(int(chat), message.message)


async def send_album_posts(event: events.Album):
    # Create MediaGroup
    media = types.MediaGroup()

    # Download and attach all media to MediaGroup
    for message in event.messages:
        await message.download_media(file='media')
        media_files = [config.MEDIA_PATH / path
                       for path in os.listdir(config.MEDIA_PATH)]
        media_files.sort(key=os.path.getctime)
        file_path = media_files[-1]

        # Get type of media
        file_type = get_media_type(file_path)

        if file_type == 'image':
            media.attach_photo(
                types.InputFile(file_path),
                message.message
            )
        elif file_type == 'video':
            media.attach_video(
                types.InputFile(file_path),
                caption=message.message
            )

    async with async_session() as session:
        groups_dal = GroupDAL(session)
        groups = await groups_dal.select_all_groups()

    # Send it to groups where bot is admin
    for chat in groups:
        await bot.send_media_group(int(chat), media=media)

    # Clear media files
    for file in config.MEDIA_PATH.iterdir():
        file.unlink()


async def cmd_start(message: types.Message):
    await message.answer('Hi! Send me telegram channel URL!')


async def take_channel(message: types.Message):
    channel_url = re.search(r"(?i)t\.me\/[a-zA-Z0-9_+]+", message.text).group(0)
    await message.answer('I got it')
    channel_url = await client.get_entity(channel_url)

    client.add_event_handler(send_posts, events.NewMessage(chats=[channel_url]))
    client.add_event_handler(send_album_posts, events.Album(chats=[channel_url]))
    async with client:
        await client.run_until_disconnected()


def register_handlers(dp: Dispatcher) -> Dispatcher:
    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_message_handler(take_channel, regexp="(?i)t\.me\/[a-zA-Z0-9_+]+")
    dp.register_message_handler(
        get_member_groups,
        ChatTypeFilter(chat_type=types.ChatType.GROUP)
    )

    return dp


if __name__ == '__main__':
    dp = register_handlers(dp)
    executor.start_polling(dp)
