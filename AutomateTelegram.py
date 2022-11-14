from telethon import TelegramClient
from telethon.tl.types import Channel
from telethon.tl.types import Chat
from telethon.tl.types import User
from telethon.tl.types import ChannelParticipant
from telethon.tl.types import InputMessagesFilterDocument
from telethon.tl.types import MessageService
import time
import sys
import re

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


async def send_all(channel_name_src, channel_name_dst):
    list_dialogs = await client.get_dialogs()
    channel_dialog_src = get_dialog_by_entity_title(
        channel_name_src, 
        list_dialogs
    )

    channel_dialog_dst = get_dialog_by_entity_title(
        channel_name_dst, 
        list_dialogs
    )

    CHANNEL_NOT_FOUND = None
    if (channel_dialog_src != CHANNEL_NOT_FOUND and \
        channel_dialog_dst != CHANNEL_NOT_FOUND):
        messages = await client.get_messages(
            channel_dialog_src.entity.id, 
            limit=None)
        
        messages.reverse()
        for message in messages:
            if (not isinstance(message, MessageService)):
                #print(message)
                await client.send_message(channel_dialog_dst.entity, message)
                time.sleep(4)

        return True

    return False


async def send_documents(channel_name_src, channel_name_dst):
    #list_channels = []
    #await get_dialogs_by_entity_type(list_dialogs=list_channels, entity_type=Channel)

    list_dialogs = await client.get_dialogs()
    channel_dialog_src = get_dialog_by_entity_title(
        channel_name_src, 
        list_dialogs
    )

    channel_dialog_dst = get_dialog_by_entity_title(
        channel_name_dst, 
        list_dialogs
    )

    CHANNEL_NOT_FOUND = None
    if (channel_dialog_src != CHANNEL_NOT_FOUND and \
        channel_dialog_dst != CHANNEL_NOT_FOUND):
        messages = await client.get_messages(
            channel_dialog_src.entity.id, 
            filter=InputMessagesFilterDocument, 
            limit=None)
        
        files = [message.file.name for message in messages]

        messages_final = []
        messages_matches = []
        filematch = re.sub(r'\..*', '', files[0])
        for i in range(len(files)):
            filename = files[i]
            if (filematch in filename):
                messages_matches.append(messages[i])
                if (i == len(files) - 1):
                    messages_final.append(messages_matches)
            else:
                messages_final.append(messages_matches)
                messages_matches = []
                filematch = re.sub(r'\..*', '', files[i])
                print(filematch)
                messages_matches.append(messages[i])

        
        for messages in messages_final:
            await client.send_file(channel_dialog_dst.entity, messages)
            time.sleep(4)
        
        return True


    return False


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
    channel_name_src = sys.argv[2]
    parameter_dst = sys.argv[3]
    channel_name_dst = sys.argv[4]

    if (parameter_src == "--src" and parameter_dst =="--dst"):
        success = await send_all(
            channel_name_src,
            channel_name_dst
        )

        if (not success):
            print("Entity (Chat/Channel/User) not found.")
    else:
        help()

with client:
    client.loop.run_until_complete(main())
