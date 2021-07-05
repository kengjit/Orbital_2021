# Unused for now
# import requests - for API calls
# from telegram_menu import BaseMessage, TelegramMenuSession, NavigationHandler - other types of handlers

import time, math
from datetime import datetime, timedelta
from telegram.ext import Updater, CommandHandler, MessageHandler, run_async, Filters
import paho.mqtt.client as mqtt

# Configuring Logger
import logging
logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',level = logging.INFO)

TOKEN = "1840357751:AAFe-yBkxyMjh1-qF6PaSxsjV2LWooFpjnU"

# Setting up polling
updater = Updater(token = TOKEN, use_context = True)
dispatcher = updater.dispatcher

# Superclass of Dryer and Washer
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
    DRY_CYCLE = timedelta(minutes = 4)

    def __init__(self, name, start_time = datetime(2021, 1, 1, 0, 0, 0)):
        super(Dryer, self).__init__(name, start_time)

    def get_next_available_time(self):
        return self.start_time + self.DRY_CYCLE

    def is_available(self, query_time):
        return self.get_next_available_time() < query_time

# A subclass of appliance
class Washer(Appliance):
    WASH_CYCLE = timedelta(minutes = 3)

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

# Convenient way of naming
both_dryers = Dryer("Both dryers")
both_washers = Washer("Both washers")

# Placing dryers and washers in an array
appliance_arr = [coin_dryer, qr_dryer, qr_washer, coin_washer]

# Specifying availability
# ESP32 will perform this in the future
# coin_washer.start_time = datetime.now() - timedelta(minutes = 1)
# qr_washer.start_time = datetime.now() - timedelta(minutes = 2)

# New Code
# What happens when a message is received
def on_message(client, userdata, message):
    # print("Topic:", message.topic)
    msg = "Message Received: " + str(message.payload.decode("utf-8"))
    print(datetime.now(), msg)

    updater.bot.send_message(chat_id = 109550488, text = msg)

    # Splitting message for each appliance
    if len(str(msg)) == 4:
        coin_dryer_status = int(msg[0])
        qr_dryer_status = int(msg[1])
        qr_washer_status = int(msg[2])
        coin_washer_status = int(msg[3])

        if coin_dryer_status == 1:
            coin_dryer.start_time = datetime.now()
        if qr_dryer_status == 1:
            qr_dryer.start_time = datetime.now()
        if qr_washer_status == 1:
            qr_washer.start_time = datetime.now()
        if coin_washer_status == 1:
            coin_washer.start_time = datetime.now()

# Logging connection status
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True
        print("Log:", "Connection successful")
    else:
        print("Log:", "Bad connection. Returned code:", rc)

broker_address = "broker.emqx.io"
topic = "laundrobot"
client_id = "sub"

client = mqtt.Client(client_id)
client.on_message = on_message
client.on_connect = on_connect

@run_async
def start_client():
    print("Log:", "Connecting to broker")
    client.connected_flag = False
    client.connect(broker_address)
    while client.connected_flag:
        print("Log:", "waiting")
        time.sleep(1)

    client.loop_start()
    topic = "laundrobot"
    print("Log:", "Subscribing to topic", topic)
    client.subscribe(topic)

start_client()

# Functions to handle each commands
# Additional features: method to cancel reminder queue? option to set reminder X min in advance
# Booking feature. Take down telegram handle?
# /stats to see when's a good time?

# Display start message
def start(update, context):
    print(str(update.effective_chat.id,))
    context.bot.send_message(chat_id = update.effective_chat.id,
                             text = "Hey, I'm LaundroBot! How can I help you? Here are the commands to interact with me: "
                             + "\n" + "\n"
                             + "To check washer/dryer availability status: /check"
                             + "\n" + "\n"
                             + "To remind when 💦 becomes available:"
                             + "\n" + "Any washer: /washer"
                             + "\n" + "QR washer: /qrwasher"
                             + "\n" + "Coin washer: /coinwasher"
                             + "\n" + "\n"
                             + "To remind when 🔥 becomes available:"
                             + "\n" + "Any dryer: /dryer"
                             + "\n" + "QR dryer: /qrdryer"
                             + "\n" + "Coin dryer: /coindryer")

# Run through array and display availability
def check(update, context):
    results = ""
    for appliance in range(4):
        results += appliance_arr[appliance].get_name() + " "
        if (appliance_arr[appliance].is_available(datetime.now())):
            results += "is available." + "\n"
        else:
            time_remaining_seconds = (appliance_arr[appliance].get_next_available_time() - datetime.now()).total_seconds()
            time_remaining_minutes = math.ceil(time_remaining_seconds / 60)
            results += "is unavailable. Available in " + str(time_remaining_minutes) + " min" + "\n"
    context.bot.send_message(chat_id = update.effective_chat.id, text = results)

# Schedule reminder for specified appliance
def set_reminder(schedule_min, appliance, update, context):
    time.sleep(schedule_min * 60)
    context.bot.send_message(chat_id = update.effective_chat.id,
                         text = "Reminder: " + appliance + " available.")

# Set reminder next time ANY washer becomes available
@run_async
def remind_washer(update, context):
    if (qr_washer.get_next_available_time() < coin_washer.get_next_available_time()):
        schedule_washer = qr_washer.get_name()
        schedule_min = math.ceil((qr_washer.get_next_available_time() - datetime.now()).total_seconds() / 60)
    elif (coin_washer.get_next_available_time() < qr_washer.get_next_available_time()):
        schedule_washer = coin_washer.get_name()
        schedule_min = math.ceil((coin_washer.get_next_available_time() - datetime.now()).total_seconds() / 60)
    else:
        schedule_washer = both_washers.get_name()
        schedule_min = math.ceil((qr_washer.get_next_available_time() - datetime.now()).total_seconds() / 60)

    if (schedule_min > 0):
        context.bot.send_message(chat_id = update.effective_chat.id,
                             text = schedule_washer + " will be available in " + str(schedule_min) + " min. Setting a reminder.")
        set_reminder(schedule_min, appliance = schedule_washer, update = update, context = context)
    else:
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = schedule_washer + " available. No reminder will be set.")

# Set reminder next time QR Washer becomes available
@run_async
def remind_qr_washer(update, context):
    schedule_washer = qr_washer.get_name()
    schedule_min = math.ceil((qr_washer.get_next_available_time() - datetime.now()).total_seconds() / 60)

    if (schedule_min > 0):
        context.bot.send_message(chat_id = update.effective_chat.id,
                             text = schedule_washer + " will be available in " + str(schedule_min) + " min. Setting a reminder.")
        set_reminder(schedule_min, appliance = schedule_washer, update = update, context = context)
    else:
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = schedule_washer + " available. No reminder will be set.")

# Set reminder next time Coin Washer becomes available
@run_async
def remind_coin_washer(update, context):
    schedule_washer = coin_washer.get_name()
    schedule_min = math.ceil((coin_washer.get_next_available_time() - datetime.now()).total_seconds() / 60)

    if (schedule_min > 0):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=schedule_washer + " will be available in " + str(
                                     schedule_min) + " min. Setting a reminder.")
        set_reminder(schedule_min, appliance=schedule_washer, update=update, context=context)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=schedule_washer + " available. No reminder will be set.")

# Set reminder next time ANY dryer becomes available
@run_async
def remind_dryer(update, context):
    if (qr_dryer.get_next_available_time() < coin_dryer.get_next_available_time()):
        schedule_dryer = qr_dryer.get_name()
        schedule_min = math.ceil((qr_dryer.get_next_available_time() - datetime.now()).total_seconds() / 60)
    elif (coin_dryer.get_next_available_time() < qr_dryer.get_next_available_time()):
        schedule_dryer = coin_dryer.get_name()
        schedule_min = math.ceil((coin_dryer.get_next_available_time() - datetime.now()).total_seconds() / 60)
    else:
        schedule_dryer = both_dryers.get_name()
        schedule_min = math.ceil((qr_dryer.get_next_available_time() - datetime.now()).total_seconds() / 60)

    if (schedule_min > 0):
        context.bot.send_message(chat_id = update.effective_chat.id,
                             text = schedule_dryer + " will be available in " + str(schedule_min) + " min. Setting a reminder.")
        set_reminder(schedule_min, appliance = schedule_dryer, update = update, context = context)
    else:
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = schedule_dryer + " available. No reminder will be set.")

# Set reminder next time QR Dryer becomes available
@run_async
def remind_qr_dryer(update, context):
    schedule_dryer = qr_dryer.get_name()
    schedule_min = math.ceil((qr_dryer.get_next_available_time() - datetime.now()).total_seconds() / 60)

    if (schedule_min > 0):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=schedule_dryer + " will be available in " + str(
                                     schedule_min) + " min. Setting a reminder.")
        set_reminder(schedule_min, appliance=schedule_dryer, update=update, context=context)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=schedule_dryer + " available. No reminder will be set.")

# Set reminder next time Coin Dryer becomes available
@run_async
def remind_coin_dryer(update, context):
    schedule_dryer = coin_dryer.get_name()
    schedule_min = math.ceil((coin_dryer.get_next_available_time() - datetime.now()).total_seconds() / 60)

    if (schedule_min > 0):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=schedule_dryer + " will be available in " + str(
                                     schedule_min) + " min. Setting a reminder.")
        set_reminder(schedule_min, appliance=schedule_dryer, update=update, context=context)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=schedule_dryer + " available. No reminder will be set.")


# Can add more stuff if needed
# To change the status of appliance by messaging the bot
def status(update, context):
    msg = update.message.text

    # check 4 digit number
    if (len(msg) == 4 and int(msg) <= 1111):
        coin_dryer_status = int(msg[0])
        qr_dryer_status = int(msg[1])
        qr_washer_status = int(msg[2])
        coin_washer_status = int(msg[3])

        if coin_dryer_status == 1:
            coin_dryer.start_time = datetime.now()
        if qr_dryer_status == 1:
            qr_dryer.start_time = datetime.now()
        if qr_washer_status == 1:
            qr_washer.start_time = datetime.now()
        if coin_washer_status == 1:
            coin_washer.start_time = datetime.now()

    # reset timers
    if msg == "reset status":
        coin_dryer.start_time = datetime.now() - coin_dryer.DRY_CYCLE
        qr_dryer.start_time = datetime.now() - qr_dryer.DRY_CYCLE
        qr_washer.start_time = datetime.now() - qr_washer.WASH_CYCLE
        coin_washer.start_time = datetime.now() - coin_washer.WASH_CYCLE

# Create and add command handlers
start_handler = CommandHandler("start", start)
dispatcher.add_handler(start_handler)

check_handler = CommandHandler("check", check)
dispatcher.add_handler(check_handler)

washer_handler = CommandHandler("washer", remind_washer)
dispatcher.add_handler(washer_handler)

qr_washer_handler = CommandHandler("qrwasher", remind_qr_washer)
dispatcher.add_handler(qr_washer_handler)

coin_washer_handler = CommandHandler("coinwasher", remind_coin_washer)
dispatcher.add_handler(coin_washer_handler)

dryer_handler = CommandHandler("dryer", remind_dryer)
dispatcher.add_handler(dryer_handler)

qr_dryer_handler = CommandHandler("qrdryer", remind_qr_dryer)
dispatcher.add_handler(qr_dryer_handler)

coin_dryer_handler = CommandHandler("coindryer", remind_coin_washer)
dispatcher.add_handler(coin_dryer_handler)

status_handler = MessageHandler(Filters.text & ~(Filters.command), status)
dispatcher.add_handler(status_handler)

# Start!
updater.start_polling()
updater.idle()

# Bot List of Commands:
# check - To check washer/dryer availability
# washer - To remind when any washer becomes available
# qrwasher - To remind when QR washer becomes available
# coinwasher - To remind when coin washer becomes available
# dryer - To remind when any dryer becomes available
# qrdryer - To remind when QR dryer becomes available
# coindryer - To remind when coin dryer comes available
