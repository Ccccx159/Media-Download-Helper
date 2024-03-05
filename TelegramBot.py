#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import requests, json, os
import log

# 填充电报机器人的token
TG_BOT_URL = 'https://api.telegram.org/bot%s/' % os.getenv('BOT_TOKEN')
# 填充电报频道 chat_id
# TG_CHAT_ID = os.getenv('CHAT_ID')

class POST_ERR(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)



def send_message(chat_id, text):
    payload = {
        'method': 'sendMessage',
        'chat_id': chat_id,
        'text': text,
        # 'parse_mode': 'Markdown',
    }
    log.logger.debug(log.SensitiveData(json.dumps(payload, ensure_ascii=False)))
    try:
      res = requests.post(TG_BOT_URL, json=payload)
      res.raise_for_status()
      # print(res)
    except:
       raise POST_ERR('ERR!!! post caption failed!!!!\n%s' % text)
    log.logger.debug('send message successfully!')

def send_photo(chat_id, caption, photo):
    payload = {
        'method': 'sendPhoto',
        'chat_id': chat_id,
        'photo': photo,
        'caption': caption,
        'parse_mode': 'Markdown',
    }
    res = requests.post(TG_BOT_URL, json=payload)
    res.raise_for_status()
