import requests
from telegram_menu import BaseMessage, TelegramMenuSession, NavigationHandler

import time
from datetime import datetime, timedelta
from telegram.ext import Updater, CommandHandler, MessageHandler, run_async

# Setting up logger
import logging
logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',level = logging.INFO)

TOKEN = "1840357751:AAFe-yBkxyMjh1-qF6PaSxsjV2LWooFpjnU"

# Setting up polling
updater = Updater(token = TOKEN, use_context = True)
dispatcher = updater.dispatcher

class Appliance():

    def __init__(self, name, start_time = datetime(2021, 1, 1, 0, 0, 0)):
        self.name = name
        self.start_time = start_time

    def get_name(self):
        return self.name

    def get_start_time(self):
        return self.start_time

# A subclass of appliance
class Dryer(Appliance):
    DRY_CYCLE = timedelta(minutes = 40)

    def __init__(self, name, start_time = datetime(2021, 1, 1, 0, 0, 0)):
        super(Dryer, self).__init__(name, start_time)

    def get_next_available_time(self):
        return self.start_time + self.DRY_CYCLE

    def is_available(self, query_time):
        return self.get_next_available_time() < query_time

# A subclass of appliance
class Washer(Appliance):
    WASH_CYCLE = timedelta(minutes = 30)

    def __init__(self, name, start_time = datetime(2021, 1, 1, 0, 0, 0)):
        super(Washer, self).__init__(name, start_time)

    def get_next_available_time(self):
        return self.start_time + self.WASH_CYCLE

    def is_available(self, query_time):
        return self.get_next_available_time() < query_time

# Creating dryer and washer objects
coin_dryer = Dryer("Coin Dryer")
qr_dryer = Dryer("QR Dryer")
qr_washer = Washer("QR Washer")
coin_washer = Washer("Coin Washer")

both_dryers = Dryer("Both dryers")
both_washers = Washer("Both washers")

# Placing dryers and washers in an array
appliance_arr = [coin_dryer, qr_dryer, qr_washer, coin_washer]

# Specifying availability
# ESP32 will perform this in the future
coin_washer.start_time = datetime.now() - timedelta(minutes = 20)
qr_washer.start_time = datetime.now() - timedelta(minutes = 23)

# Functions to handle each commands
# Additional features: method to cancel reminder queue? option to set reminder X min in advance
# Booking feature. Take down telegram handle?
# /stats to see when's a good time?

# Display start message
def start(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id,
                             text = "Hey, I'm LaundroBot! How can I help you? Here are the commands to interact with me: "
                             + "\n" + "To check washer/dryer availability status: /check"
                             + "\n" + "To remind when a washer becomes available: /washer"
                             + "\n" + "To remind when a dryer becomes available: /dryer")

# Run through array and display availability
def check(update, context):
    results = ""
    for appliance in range(4):
        results += appliance_arr[appliance].get_name() + ": "
        if (appliance_arr[appliance].is_available(datetime.now())):
            results += "is available." + "\n"
        else:
            time_remaining = appliance_arr[appliance].get_next_available_time() - datetime.now()
            results += "is unavailable. Available in " + time_remaining + " min" + "\n"
    context.bot.send_message(chat_id = update.effective_chat.id, text = results)

# Schedule reminder for specified appliance
def set_reminder(schedule_min, appliance, update, context):
    time.sleep(schedule_min * 60)
    context.bot.send_message(chat_id = update.effective_chat.id,
                         text = "Reminder: " + appliance + " available.")

# Set reminder next time washer becomes available
@run_async
def washer(update, context):

    if (qr_washer.get_next_available_time() < coin_washer.get_next_available_time()):
        schedule_washer = qr_washer.get_name()
        schedule_min = qr_washer.get_next_available_time()
    elif (coin_washer.get_next_available_time() < qr_washer.get_next_available_time()):
        schedule_washer = coin_washer.get_name()
        schedule_min = coin_washer.get_next_available_time()
    else:
        schedule_washer = both_washers.get_name()
        schedule_min = qr_washer.get_next_available_time()

    if (schedule_min != 0):
        context.bot.send_message(chat_id = update.effective_chat.id,
                             text = schedule_washer + " will be available in " + str(schedule_min) + " min. Setting a reminder.")
        set_reminder(schedule_min, appliance = schedule_washer, update = update, context = context)
    else:
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = schedule_washer + " available. No reminder will be set.")

# Set reminder next time dryer becomes available
@run_async
def dryer(update, context):

    if (qr_dryer.get_next_available_time() < coin_dryer.get_next_available_time()):
        schedule_dryer = qr_dryer.get_name()
        schedule_min = qr_dryer.get_next_available_time()
    elif (coin_dryer.get_next_available_time() < qr_dryer.get_next_available_time()):
        schedule_dryer = coin_dryer.get_name()
        schedule_min = coin_dryer.get_next_available_time()
    else:
        schedule_dryer = both_dryers.get_name()
        schedule_min = qr_dryer.get_next_available_time()

    if (schedule_min != 0):
        context.bot.send_message(chat_id = update.effective_chat.id,
                             text = schedule_dryer + " will be available in " + str(schedule_min) + " min. Setting a reminder.")
        set_reminder(schedule_min, appliance = schedule_dryer, update = update, context = context)
    else:
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = schedule_dryer + " available. No reminder will be set.")

# Create and add command handlers
start_handler = CommandHandler("start", start)
dispatcher.add_handler(start_handler)

check_handler = CommandHandler("check", check)
dispatcher.add_handler(check_handler)

washer_handler = CommandHandler("washer", washer)
dispatcher.add_handler(washer_handler)

dryer_handler = CommandHandler("dryer", dryer)
dispatcher.add_handler(dryer_handler)

# Start!
updater.start_polling()
updater.idle()