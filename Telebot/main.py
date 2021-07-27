# Unused for now
# import requests - for API calls
# from telegram_menu import BaseMessage, TelegramMenuSession, NavigationHandler - other types of handlers

import config
import time, math
from datetime import datetime, timedelta
from telegram.ext import Updater, CommandHandler, MessageHandler, run_async, Filters
import paho.mqtt.client as mqtt

# Configuring Logger
import logging
logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',level = logging.INFO)

TOKEN = config.TOKEN

# Setting up polling
updater = Updater(token = TOKEN, use_context = True)
dispatcher = updater.dispatcher

# Superclass of Dryer and Washer
class Appliance():

    def __init__(self, name, last_close_time = datetime.now() - timedelta(minutes = 40), last_open_time = datetime.now()):
        self.name = name
        self.last_close_time = last_close_time
        self.last_open_time = last_open_time

    def get_name(self):
        return self.name

    def get_last_close_time(self):
        return self.last_close_time

    def get_last_open_time(self):
        return self.last_open_time

# A subclass of appliance
class Dryer(Appliance):
    DRY_CYCLE = timedelta(minutes = 3)

    def __init__(self, name, last_close_time = datetime.now() - timedelta(minutes = 40), last_open_time = datetime.now()):
        super(Dryer, self).__init__(name, last_close_time, last_open_time)

    def status(self, query_time):
        if (self.last_close_time < self.last_open_time) and (self.last_open_time < query_time):
            return "available"
        elif (self.last_open_time < self.last_close_time) and (self.last_close_time + self.DRY_CYCLE > query_time):
            return "cycle"
        elif (self.last_open_time < self.last_close_time) and (self.last_close_time + self.DRY_CYCLE < query_time):
            return "waiting"

    def get_cycle_complete_time(self):
        return self.last_close_time + self.DRY_CYCLE

# A subclass of appliance
class Washer(Appliance):
    WASH_CYCLE = timedelta(minutes = 2)

    def __init__(self, name, last_close_time = datetime.now() - timedelta(minutes = 30), last_open_time = datetime.now()):
        super(Washer, self).__init__(name, last_close_time, last_open_time)

    def status(self, query_time):
        if (self.last_close_time < self.last_open_time) and (self.last_open_time < query_time):
            return "available"
        elif (self.last_open_time < self.last_close_time) and (self.last_close_time + self.WASH_CYCLE > query_time):
            return "cycle"
        elif (self.last_open_time < self.last_close_time) and (self.last_close_time + self.WASH_CYCLE < query_time):
            return "waiting"

    def get_cycle_complete_time(self):
        return self.last_close_time + self.WASH_CYCLE

# Creating dryer and washer objects
coin_dryer = Dryer("Coin Dryer")
qr_dryer = Dryer("QR Dryer")
qr_washer = Washer("QR Washer")
coin_washer = Washer("Coin Washer")

appliance_arr = [coin_dryer, qr_dryer, qr_washer, coin_washer]

coin_dryer_notifications_queue = []
qr_dryer_notifications_queue = []
qr_washer_notifications_queue = []
coin_washer_notifications_queue = []

# When a message is received
@run_async
def on_message(client, userdata, message):
    # print("Topic:", message.topic)
    msg = str(message.payload.decode("utf-8"))
    logging.info("MQTT Message Received: " + msg)

    # Debugging purpose
    # james_chat_id = 109550488
    # updater.bot.send_message(chat_id = james_chat_id, text = msg)

    # Splitting message for each appliance
    if len(str(msg)) == 2:
        appliance_num = int(msg[0])
        status = int(msg[1])

        if appliance_num == 1:
            if status == 1:
                coin_dryer.last_close_time = datetime.now()
            elif status == 0:
                coin_dryer.last_open_time = datetime.now()
                # Trigger reminder if needed
                for i in coin_dryer_notifications_queue:
                    msg = "Reminder: " + coin_dryer.get_name() + " is available."
                    updater.bot.send_message(chat_id = i, text = msg)
                coin_dryer_notifications_queue.clear()

        elif appliance_num == 2:
            if status == 1:
                qr_dryer.last_close_time = datetime.now()
            elif status == 0:
                qr_dryer.last_open_time = datetime.now()
                # Trigger reminder if needed
                for i in qr_dryer_notifications_queue:
                    msg = "Reminder: " + qr_dryer.get_name() + " is available."
                    updater.bot.send_message(chat_id = i, text = msg)
                qr_dryer_notifications_queue.clear()

        elif appliance_num == 3:
            if status == 1:
                qr_washer.last_close_time = datetime.now()
            elif status == 0:
                qr_washer.last_open_time = datetime.now()
                # Trigger reminder if needed
                for i in qr_washer_notifications_queue:
                    msg = "Reminder: " + qr_washer.get_name() + " is available."
                    updater.bot.send_message(chat_id = i, text = msg)
                qr_washer_notifications_queue.clear()

        elif appliance_num == 4:
            if status == 1:
                coin_washer.last_close_time = datetime.now()
            elif status == 0:
                coin_washer.last_open_time = datetime.now()
                # Trigger reminder if needed
                for i in coin_washer_notifications_queue:
                    msg = "Reminder: " + coin_washer.get_name() + " is available."
                    updater.bot.send_message(chat_id = i, text = msg)
                coin_washer_notifications_queue.clear()

# Logging connection status
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True
        logging.info("Connection successful")
    else:
        logging.info("Bad connection. Returned code: " + rc)

broker_address = "broker.emqx.io"
topic = "laundrobot"
client_id = "sub"

client = mqtt.Client(client_id)
client.on_message = on_message
client.on_connect = on_connect

@run_async
def start_client():
    logging.info("Connecting to broker")
    client.connected_flag = False
    client.connect(broker_address)
    while client.connected_flag:
        logging.info("Waiting for broker")
        time.sleep(1)

    client.loop_start()
    topic = "laundrobot"
    logging.info("Subscribing to topic " + topic)
    client.subscribe(topic)
start_client()

# Functions to handle each commands
# Additional features: method to cancel reminder queue? option to set reminder X min in advance
# Booking feature. Take down telegram handle?
# /stats to see when's a good time?

# Display start message
def start(update, context):
    logging.info("Chat ID " + str(update.effective_chat.id) + " started")
    context.bot.send_message(chat_id = update.effective_chat.id,
                             text = "Hey, I'm LaundroBot! How can I help you? Here are the commands to interact with me: "
                             + "\n" + "\n"
                             + "To check washer/dryer status: /check"
                             + "\n" + "\n"
                             + "To remind when 💦 cycle is completed:"
                             + "\n" + "Any washer: /washercycle"
                             + "\n" + "QR washer: /qrwashercycle"
                             + "\n" + "Coin washer: /coinwashercycle"
                             + "\n" + "\n"
                             + "To remind when 💦 is available:"
                             + "\n" + "Any washer: /washer"
                             + "\n" + "QR washer: /qrwasher"
                             + "\n" + "Coin washer: /coinwasher"
                             + "\n" + "\n"
                             + "To remind when 🔥 cycle is completed:"
                             + "\n" + "Any dryer: /dryercycle"
                             + "\n" + "QR dryer: /qrdryercycle"
                             + "\n" + "Coin dryer: /coindryercycle"
                             + "\n" + "\n"
                             + "To remind when 🔥 cycle is available:"
                             + "\n" + "Any dryer: /dryer"
                             + "\n" + "QR dryer: /qrdryer"
                             + "\n" + "Coin dryer: /coindryer")

# Run through array and display availability
def check(update, context):
    logging.info("Chat ID " + str(update.effective_chat.id) + " checked")
    results = "✅: Available\n💦: Washing Cycle\n🔥: Drying Cycle\n❌: Uncollected Laundry\n\n"
    for appliance in range(4):
        results += appliance_arr[appliance].get_name() + ": "
        if (appliance_arr[appliance].status(datetime.now()) == "available"):
            results += "✅" + "\n"
        elif (appliance_arr[appliance].status(datetime.now()) == "cycle"):
            time_remaining_seconds = (appliance_arr[appliance].get_cycle_complete_time() - datetime.now()).total_seconds()
            time_remaining_minutes = math.ceil(time_remaining_seconds / 60)

            if appliance == 0 or appliance == 1:
                results += "🔥 "
            elif appliance == 2 or appliance == 3:
                results += "💦 "
            results += "Cycle: " + str(time_remaining_minutes) + " min left." + "\n"
        elif (appliance_arr[appliance].status(datetime.now()) == "waiting"):
            results += "❌" + "\n"

    context.bot.send_message(chat_id = update.effective_chat.id, text = results)

# Schedule reminder for specified appliance when laundry cycle is completed
def reminder_cycle(schedule_sec, appliance, update, context):
    time.sleep(schedule_sec)
    logging.info("Chat ID " + str(update.effective_chat.id) + " reminded for completed " + appliance + " laundry cycle")
    context.bot.send_message(chat_id = update.effective_chat.id,
                         text = "Reminder: " + appliance + " laundry cycle completed.")

# Schedule reminder for specified appliance when it is available
def reminder_available(chat_id, appliance, update, context):
    logging.info("Chat ID " + str(update.effective_chat.id) + " reminded for available " + appliance)
    context.bot.send_message(chat_id = chat_id,
                         text = "Reminder: " + appliance + " is available.")

# Set reminder next time ANY washer cycle is completed
@run_async
def remind_washer_cycle(update, context):
    logging.info("Chat ID " + str(update.effective_chat.id) + " remind washer cycle")
    if (qr_washer.get_cycle_complete_time() < coin_washer.get_cycle_complete_time()):
        schedule_washer = qr_washer.get_name()
        schedule_sec = (qr_washer.get_cycle_complete_time() - datetime.now()).total_seconds()
        schedule_min = math.ceil(schedule_sec / 60)
    elif (coin_washer.get_cycle_complete_time() < qr_washer.get_cycle_complete_time()):
        schedule_washer = coin_washer.get_name()
        schedule_sec = (coin_washer.get_cycle_complete_time() - datetime.now()).total_seconds()
        schedule_min = math.ceil(schedule_sec / 60)
    else:
        schedule_washer = "Both washers"
        schedule_sec = (coin_washer.get_cycle_complete_time() - datetime.now()).total_seconds()
        schedule_min = math.ceil(schedule_sec / 60)

    if (schedule_min > 0):
        context.bot.send_message(chat_id = update.effective_chat.id,
                             text = schedule_washer + " laundry cycle will be completed in " + str(schedule_min) + " min. Setting a reminder.")
        reminder_cycle(schedule_sec, appliance = schedule_washer, update = update, context = context)
    else:
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = schedule_washer + " laundry cycles completed. No reminder will be set.")

# Set reminder next time QR Washer cycle is completed
@run_async
def remind_qr_washer_cycle(update, context):
    logging.info("Chat ID " + str(update.effective_chat.id) + " remind QR washer cycle")
    schedule_washer = qr_washer.get_name()
    schedule_sec = (qr_washer.get_cycle_complete_time() - datetime.now()).total_seconds()
    schedule_min = math.ceil(schedule_sec / 60)

    if (schedule_min > 0):
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = schedule_washer + " laundry cycle will be completed in " + str(schedule_min) + " min. Setting a reminder.")
        reminder_cycle(schedule_sec, appliance = schedule_washer, update = update, context = context)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text = schedule_washer + " laundry cycle completed. No reminder will be set.")

# Set reminder next time Coin Washer cycle is completed
@run_async
def remind_coin_washer_cycle(update, context):
    logging.info("Chat ID " + str(update.effective_chat.id) + " remind coin washer cycle")
    schedule_washer = coin_washer.get_name()
    schedule_sec = (coin_washer.get_cycle_complete_time() - datetime.now()).total_seconds()
    schedule_min = math.ceil(schedule_sec / 60)

    if (schedule_min > 0):
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = schedule_washer + " cycle will be completed in " + str(schedule_min) + " min. Setting a reminder.")
        reminder_cycle(schedule_sec, appliance = schedule_washer, update = update, context = context)
    else:
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = schedule_washer + " cycle completed. No reminder will be set.")

# Set reminder next time ANY dryer cycle is completed
@run_async
def remind_dryer_cycle(update, context):
    logging.info("Chat ID " + str(update.effective_chat.id) + " remind dryer cycle")
    if (qr_dryer.get_cycle_complete_time() < coin_dryer.get_cycle_complete_time()):
        schedule_dryer = qr_dryer.get_name()
        schedule_sec = (qr_dryer.get_cycle_complete_time() - datetime.now()).total_seconds()
        schedule_min = math.ceil(schedule_sec / 60)
    elif (coin_dryer.get_cycle_complete_time() < qr_dryer.get_cycle_complete_time()):
        schedule_dryer = coin_dryer.get_name()
        schedule_sec = (coin_dryer.get_cycle_complete_time() - datetime.now()).total_seconds()
        schedule_min = math.ceil(schedule_sec / 60)
    else:
        schedule_dryer = "Both dryers"
        schedule_sec = (coin_dryer.get_cycle_complete_time() - datetime.now()).total_seconds()
        schedule_min = math.ceil(schedule_sec / 60)

    if (schedule_min > 0):
        context.bot.send_message(chat_id = update.effective_chat.id,
                             text = schedule_dryer + " laundry cycle will be completed in " + str(schedule_min) + " min. Setting a reminder.")
        reminder_cycle(schedule_sec, appliance = schedule_dryer, update = update, context = context)
    else:
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = schedule_dryer + " laundry cycles completed. No reminder will be set.")

# Set reminder next time QR Dryer cycle is completed
@run_async
def remind_qr_dryer_cycle(update, context):
    logging.info("Chat ID " + str(update.effective_chat.id) + " remind QR dryer cycle")
    schedule_dryer = qr_dryer.get_name()
    schedule_sec = (qr_dryer.get_cycle_complete_time() - datetime.now()).total_seconds()
    schedule_min = math.ceil(schedule_sec / 60)

    if (schedule_min > 0):
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = schedule_dryer + " laundry cycle will be completed in " + str(schedule_min) + " min. Setting a reminder.")
        reminder_cycle(schedule_sec, appliance = schedule_dryer, update = update, context = context)
    else:
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = schedule_dryer + " laundry cycle completed. No reminder will be set.")

# Set reminder next time Coin Dryer cycle is completed
@run_async
def remind_coin_dryer_cycle(update, context):
    logging.info("Chat ID " + str(update.effective_chat.id) + " remind coin dryer cycle")
    schedule_dryer = coin_dryer.get_name()
    schedule_sec = (coin_dryer.get_cycle_complete_time() - datetime.now()).total_seconds()
    schedule_min = math.ceil(schedule_sec / 60)

    if (schedule_min > 0):
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = schedule_dryer + " laundry cycle will be completed in " + str(schedule_min) + " min. Setting a reminder.")
        reminder_cycle(schedule_sec, appliance = schedule_dryer, update = update, context = context)
    else:
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = schedule_dryer + " laundry cycle completed. No reminder will be set.")

# Set reminder next time ANY washer is available
def remind_washer(update, context):
    logging.info("Chat ID " + str(update.effective_chat.id) + " remind washer availability")
    if qr_washer.status(datetime.now()) == "available" or coin_washer.status(datetime.now()) == "available":
        schedule_washer = "Washer(s)"
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = schedule_washer + " available. No reminder will be set.")
    else:
        if qr_washer_notifications_queue.count(update.effective_chat.id) < 1:
            qr_washer_notifications_queue.append(update.effective_chat.id)
        if coin_washer_notifications_queue.count(update.effective_chat.id) < 1:
            coin_washer_notifications_queue.append(update.effective_chat.id)
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = "Laundrobot will alert you when any washer is available.")

# Set reminder next time qr washer is available
def remind_qr_washer(update, context):
    logging.info("Chat ID " + str(update.effective_chat.id) + " remind QR washer availability")
    if qr_washer.status(datetime.now()) == "available":
        schedule_washer = qr_washer.get_name()
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = schedule_washer + " available. No reminder will be set.")
    else:
        if qr_washer_notifications_queue.count(update.effective_chat.id) < 1:
            qr_washer_notifications_queue.append(update.effective_chat.id)
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = "Laundrobot will alert you when QR Washer is available.")

# Set reminder next time coin washer is available
def remind_coin_washer(update, context):
    logging.info("Chat ID " + str(update.effective_chat.id) + " remind coin washer availability")
    if  coin_washer.status(datetime.now()) == "available":
        schedule_washer = coin_washer.get_name()
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = schedule_washer + " available. No reminder will be set.")
    else:
        if coin_washer_notifications_queue.count(update.effective_chat.id) < 1:
            coin_washer_notifications_queue.append(update.effective_chat.id)
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = "Laundrobot will alert you when Coin Washer is available.")

# Set reminder next time ANY dryer is available
def remind_dryer(update, context):
    logging.info("Chat ID " + str(update.effective_chat.id) + " remind dryer availability")
    if qr_dryer.status(datetime.now()) == "available" or coin_dryer.status(datetime.now()) == "available":
        schedule_dryer = "Dryer(s)"
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = schedule_dryer + " available. No reminder will be set.")
    else:
        if qr_dryer_notifications_queue.count(update.effective_chat.id) < 1:
            qr_dryer_notifications_queue.append(update.effective_chat.id)
        if coin_dryer_notifications_queue.count(update.effective_chat.id) < 1:
            coin_dryer_notifications_queue.append(update.effective_chat.id)
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = "Laundrobot will alert you when any dryer is available.")

# Set reminder next time qr dryer is available
def remind_qr_dryer(update, context):
    logging.info("Chat ID " + str(update.effective_chat.id) + " remind QR dryer availability")
    if qr_dryer.status(datetime.now()) == "available":
        schedule_dryer = qr_dryer.get_name()
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = schedule_dryer + " available. No reminder will be set.")
    else:
        if qr_dryer_notifications_queue.count(update.effective_chat.id) < 1:
            qr_dryer_notifications_queue.append(update.effective_chat.id)
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = "Laundrobot will alert you when QR Dryer is available.")

# Set reminder next time coin dryer is available
def remind_coin_dryer(update, context):
    logging.info("Chat ID " + str(update.effective_chat.id) + " remind coin dryer availability")
    if coin_dryer.status(datetime.now()) == "available":
        schedule_dryer = coin_dryer.get_name()
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = schedule_dryer + " available. No reminder will be set.")
    else:
        if coin_dryer_notifications_queue.count(update.effective_chat.id) < 1:
            coin_dryer_notifications_queue.append(update.effective_chat.id)
        context.bot.send_message(chat_id = update.effective_chat.id,
                                 text = "Laundrobot will alert you when Coin Dryer is available.")

# Can add more stuff if needed
# To change the status of appliance by messaging the bot
def status(update, context):
    msg = update.message.text
    logging.info("Chat ID " + str(update.effective_chat.id) + " Message Received: " + msg)

    # check 4 digit number
    if (len(msg) == 2 and int(msg) <= 41):

        # Applies to coin dryer
        if int(msg[0]) == 1:
            if int(msg[1]) == 1:
                coin_dryer.last_close_time = datetime.now()
            elif int(msg[1]) == 0:
                coin_dryer.last_open_time = datetime.now()
                # Trigger reminder if needed
                for i in coin_dryer_notifications_queue:
                    msg = "Reminder: " + coin_dryer.get_name() + " is available."
                    updater.bot.send_message(chat_id = i, text = msg)
                coin_dryer_notifications_queue.clear()

        # Applies to qr dryer
        elif int(msg[0]) == 2:
            if int(msg[1]) == 1:
                qr_dryer.last_close_time = datetime.now()
            elif int(msg[1]) == 0:
                qr_dryer.last_open_time = datetime.now()
                # Trigger reminder if needed
                for i in qr_dryer_notifications_queue:
                    msg = "Reminder: " + qr_dryer.get_name() + " is available."
                    updater.bot.send_message(chat_id = i, text = msg)
                qr_dryer_notifications_queue.clear()

        # Applies to qr washer
        elif int(msg[0]) == 3:
            if int(msg[1]) == 1:
                qr_washer.last_close_time = datetime.now()
            elif int(msg[1]) == 0:
                qr_washer.last_open_time = datetime.now()
                # Trigger reminder if needed
                for i in qr_washer_notifications_queue:
                    msg = "Reminder: " + qr_washer.get_name() + " is available."
                    updater.bot.send_message(chat_id = i, text = msg)
                qr_washer_notifications_queue.clear()

        # Applies to coin washer
        elif int(msg[0]) == 4:
            if int(msg[1]) == 1:
                coin_washer.last_close_time = datetime.now()
            elif int(msg[1]) == 0:
                coin_washer.last_open_time = datetime.now()
                # Trigger reminder if needed
                for i in coin_washer_notifications_queue:
                    msg = "Reminder: " + coin_washer.get_name() + " is available."
                    updater.bot.send_message(chat_id = i, text = msg)
                coin_washer_notifications_queue.clear()

    # reset timers
    if msg == "reset status":
        logging.info("Chat ID " + str(update.effective_chat.id) + " resetted status")
        coin_dryer.last_close_time = datetime.now() - coin_dryer.DRY_CYCLE
        coin_dryer.last_open_time = datetime.now()
        qr_dryer.last_close_time = datetime.now() - qr_dryer.DRY_CYCLE
        qr_dryer.last_open_time = datetime.now()
        qr_washer.last_close_time = datetime.now() - qr_washer.WASH_CYCLE
        qr_washer.last_open_time = datetime.now()
        coin_washer.last_close_time = datetime.now() - coin_washer.WASH_CYCLE
        coin_washer.last_open_time = datetime.now()

# Create and add command handlers
start_handler = CommandHandler("start", start)
dispatcher.add_handler(start_handler)

check_handler = CommandHandler("check", check)
dispatcher.add_handler(check_handler)

washer_cycle_handler = CommandHandler("washercycle", remind_washer_cycle)
dispatcher.add_handler(washer_cycle_handler)
qr_washer_cycle_handler = CommandHandler("qrwashercycle", remind_qr_washer_cycle)
dispatcher.add_handler(qr_washer_cycle_handler)
coin_washer_cycle_handler = CommandHandler("coinwashercycle", remind_coin_washer_cycle)
dispatcher.add_handler(coin_washer_cycle_handler)
dryer_cycle_handler = CommandHandler("dryercycle", remind_dryer_cycle)
dispatcher.add_handler(dryer_cycle_handler)
qr_dryer_cycle_handler = CommandHandler("qrdryercycle", remind_qr_dryer_cycle)
dispatcher.add_handler(qr_dryer_cycle_handler)
coin_dryer_cycle_handler = CommandHandler("coindryercycle", remind_coin_dryer_cycle)
dispatcher.add_handler(coin_dryer_cycle_handler)

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
coin_dryer_handler = CommandHandler("coindryer", remind_coin_dryer)
dispatcher.add_handler(coin_dryer_handler)

status_handler = MessageHandler(Filters.text & ~(Filters.command), status)
dispatcher.add_handler(status_handler)

# Start!
updater.start_polling()
updater.idle()

# Bot List of Commands:
# start - To view all commands
# check - To check washer/dryer status
# washercycle - To remind when any washer cycle is completed
# qrwashercycle - To remind when QR washer cycle is completed
# coinwashercycle - To remind when coin washer cycle is completed
# washer - To remind when any washer is available
# qrwasher - To remind when QR washer is available
# coinwasher - To remind when coin washer is available
# dryercycle - To remind when any dryer cycle is completed
# qrdryercycle - To remind when QR dryer cycle is completed
# coindryercycle - To remind when coin dryer cycle is completed
# dryer - To remind when any dryer is available
# qrdryer - To remind when QR dryer is available
# coindryer - To remind when coin dryer is available
