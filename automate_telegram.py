from telethon import TelegramClient
from telethon.tl.types import Channel
from telethon.tl.types import User
from telethon.tl.types import ChannelParticipant
from telethon.tl.types import InputMessagesFilterDocument
from telethon.tl.types import MessageService
from telethon.tl.types import MessageMediaPhoto
from telethon.tl.types import MessageMediaWebPage
from telethon.tl.types import MessageMediaDocument
import time
import sys
import re
import random
import string
import datetime

#https://my.telegram.org/auth -> API_ID & API_HASH
#python3.10.exe -m pip install telethon
API_ID = 0
API_HASH = ""
SESSION_NAME = "first_session"
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def get_dialogs_by_entity_type(list_dialogs, entity_type):
    dialogs = await client.get_dialogs()
    for dialog in dialogs:
        if (isinstance(dialog.entity, entity_type)):
            list_dialogs.append(dialog)


def get_dialog_by_entity_title(entity_title, list_dialogs):
    for dialog in list_dialogs:
        title = ""
        if (isinstance(dialog.entity, User)):
            title = dialog.entity.username

        else:
            title = dialog.entity.title    
        
        if (title == entity_title):
            return dialog

    return None


async def kick_all_users_channel(channel_name):
    list_channels = []
    await get_dialogs_by_entity_type(list_dialogs=list_channels, type_entity=Channel)
    channel_dialog = get_dialog_by_entity_title(channel_name, list_dialogs=list_channels)
    CHANNEL_NOT_FOUND = None

    if (channel_dialog != CHANNEL_NOT_FOUND):
        users = await client.get_participants(channel_dialog.entity.id)
        for user in users:
            if (isinstance(user.participant, ChannelParticipant)):
                await client.kick_participant(channel_dialog.entity.id, user.id)
                time.sleep(5)


def get_files_name(messages):
    list_files = []
    list_delete_values = []
    list_randoms = []
    for i in range(len(messages)):
        isMessageText = messages[i].media == None
        if isinstance(messages[i], MessageService) \
                or isMessageText:
            list_delete_values.append(messages[i])

        elif isinstance(messages[i].media, MessageMediaPhoto):
            random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
            while random_string in list_randoms:
                random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
            
            list_randoms.append(random_string)
            list_files.append(random_string)

        elif isinstance(messages[i].media, MessageMediaWebPage):
            list_files.append(messages[i].media.webpage.title)      

        elif isinstance(messages[i].media, MessageMediaDocument):
            list_files.append(messages[i].file.name)

        
    for value in list_delete_values:
        messages.remove(value)

    return list_files


def get_message_matches(messages):
    files = get_files_name(messages)
    messages_final = []
    message_matches = []
    if (len(files) > 0):
        filename = files[0]
        filematch = re.sub(r'\..*', '', filename)
        for i in range(len(files)):
            filename = files[i]
            if (filematch in filename):
                message_matches.append(messages[i])
            else:
                messages_final.append(message_matches)
                message_matches = []
                filematch = re.sub(r'\..*', '', filename)
                message_matches.append(messages[i])

            if (i == len(files) - 1):
                messages_final.append(message_matches)

    return messages_final


async def send_all_messages(entity_dialog_src, entity_dialog_dst):
    from_date = datetime.datetime.strptime('23-11-2022 00:00:00', '%d-%m-%Y %H:%M:%S')
    messages_src = await client.get_messages(
        entity_dialog_src.entity.id, 
        reverse=True,
        offset_date=from_date,
        limit=None)
   # messages_src.reverse()
    message_matches = get_message_matches(messages_src)
    for messages in message_matches: 
        if len(messages) > 1:
            await client.send_file(entity_dialog_dst.entity, messages)
            time.sleep(3)
            continue
        
        for message in messages:
            await client.send_message(entity_dialog_dst.entity, message)
            time.sleep(3)
        

async def send_files(entity_dialog_src, entity_dialog_dst):
    messages_src = await client.get_messages(
        entity_dialog_src.entity.id, 
        filter=InputMessagesFilterDocument, 
        limit=None
    )

    messages_src.reverse()
    message_matches = get_message_matches(messages_src)    
    for messages in message_matches:
        await client.send_file(entity_dialog_dst.entity, messages)
        time.sleep(3)


def help():
    help_command = f"""
    {sys.argv[0]} --src "channel/chat/username" --dst "channel/chat/username"
    """
    print(help_command)

                
async def main():
    argc = len(sys.argv) - 1
    if (argc != 4):
        help()
        sys.exit(1)

    parameter_src = sys.argv[1]
    entity_name_src = sys.argv[2]
    parameter_dst = sys.argv[3]
    entity_name_dst = sys.argv[4]
    if (parameter_src == "--src" \
        and parameter_dst =="--dst"):
        list_dialogs = await client.get_dialogs()
        entity_dialog_src = get_dialog_by_entity_title(
            entity_name_src, 
            list_dialogs)
        entity_dialog_dst = get_dialog_by_entity_title(
            entity_name_dst, 
            list_dialogs)
        ENTITY_NOT_FOUND = None
        if (entity_dialog_src == ENTITY_NOT_FOUND \
            or entity_dialog_dst == ENTITY_NOT_FOUND):
            print()
            print("'" + entity_name_src + "' y/o '" + entity_name_dst + "' not found!")
            print()
            sys.exit(1)

        await send_all_messages(
            entity_dialog_src,
            entity_dialog_dst)
    else:
        help()

with client:
    client.loop.run_until_complete(main())
