import os

import telebot
from telebot.apihelper import ApiException


class TelegramSender:
    """Notification service by telegram bot. """
    def __init__(self, parse_mode=None):
        BOT_TOKEN = os.getenv("BOT_TOKEN")
        CHAT_ID = os.getenv("CHAT_ID")

        self.tb = telebot.TeleBot(token=BOT_TOKEN, parse_mode=parse_mode)
        self.chat_id = CHAT_ID

    def send_message(self, message):
        try:
            mess = self.tb.send_message(chat_id=self.chat_id, text=message)
            return mess
        except ApiException as e:
            return e


bot = TelegramSender()
