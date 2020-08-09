import os
import time
import math
from dotenv import load_dotenv
import telegram
from telegram.ext import (
    Updater,
    Handler,
    MessageHandler,
    Filters,
)
from telegram import ChatPermissions

load_dotenv()

TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
BOT = telegram.Bot(TOKEN)
WARNINGS = {}


def welcome(update, context):
    ''' Check if there is a new user and send a greeting message if any. '''
    if update.message.new_chat_members:
        for chat_member in update.message.new_chat_members:
            new_user = chat_member
            update.message.reply_text(
                f'Dear {new_user.first_name.title()}, welcome to Cool Cash Hub Investment Platform.')


def check_url(update):
    '''Check of a post has a link in it.'''
    has_url = False
    if update.message.entities:
        for entity in update.message.entities:
            if entity.type == 'url':
                has_url = True
    return has_url


def check_status(bot, user):
    return bot.get_chat_member(CHAT_ID, user.id).status


def warn_against_links(update, context, *args, **kwargs):
    """Warn non-admin users who post links on the wall."""
    def ordinal(n): return "%d%s" % (
        n, "tsnrhtdd"[(math.floor(n/10) % 10 != 1)*(n % 10 < 4)*n % 10::4])
    if check_url(update):
        user = update.message.from_user
        if check_status(BOT, user) not in ['creator', 'administrator']:
            if user.id in WARNINGS:
                WARNINGS[user.id] += 1
                update.message.reply_text(
                    f'{user.first_name.title()} please do not post links on the wall.\nThis is your {ordinal(WARNINGS[user.id])} warning.\n{5-WARNINGS[user.id]} warnings left before ban.')
                if WARNINGS[user.id] > 5:
                    # BOT.kick_chat_member(update.message.chat.id, *args, **kwargs)
                    permission = ChatPermissions(can_send_messages=False)
                    BOT.restrict_chat_member(CHAT_ID, user.id, permission)
            else:
                WARNINGS[user.id] = 1
                update.message.reply_text(
                    f'{user.first_name.title()} please do not post links on the wall.\nThis is your {ordinal(WARNINGS[user.id])} warning.\n{5-WARNINGS[user.id]} warnings left before ban.')


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(
        Filters.status_update.new_chat_members, welcome))
    dispatcher.add_handler(MessageHandler(Filters.text, warn_against_links))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


while True:
    try:
        main()
    except Exception:
        time.sleep(3)
