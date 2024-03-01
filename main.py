#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import Downloader as dl
import time, re, os, requests, json, urllib3
from queue import Queue
from threading import Thread
import TelegramBot as tgbot
import TMDBQuery as tmdb

def task_customer(msg_queue, qb):
  while True:
    # 获取一个任务
    msg = msg_queue.get()
    task = {
      'chat_id': msg.get('chat_id'),
      'magnet_url': msg.get('magnet_url')
    }
    task['task_name'] = task['magnet_url'].split('&dn=')[1].split('&tr=')[0]
    task['file_name'] = task['task_name'].replace('.', ' ')
    s_match = re.search(r'\b\d{4}\b', task['file_name'])
    if s_match:
      task['type'] = 'movie'
      task['name'] = task['file_name'][:s_match.start()].strip()
      task['year'] = s_match.group()
    else:
      s_match = re.search(r'\bS\d{2}(E\d{2})?\b', task['file_name'])
      task['type'] = 'tv'
      task['name'] = task['file_name'][:s_match.start()].strip()
      task['series'] = s_match.group()

    res, tr, content = qb.download(task['magnet_url'])
    print(content)
    tgbot.send_message(task['chat_id'], content)
    if res =='Success':
      while True:
        tr = qb.query_torrent(task['magnet_url'])
        # print('time:{}, {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tr['added_on']))))
        # print('name: {}\nhash: {}\nstate: {}'.format(tr['name'], tr['hash'], tr['state']))
        # print('*' * 30)
        if tr['state'] == 'stalledUP' or tr['state'] == 'uploading' or tr['state'] == 'pausedUP':
          print('{} download Finished!'.format(tr['name']))
          break
        time.sleep(10)
      content = ('{} download Finished!'.format(task['task_name']))
      tgbot.send_message(chat_id=task['chat_id'], text=content)

      # get detail info from tmdb and send to user
      res, caption, poster_url = tmdb.get_detail_by_tmdb(task)
      if res == 'Success':
        tgbot.send_photo(chat_id=task['chat_id'], caption=caption, photo=poster_url)
      else:
        tgbot.send_message(chat_id=task['chat_id'], text=poster_url)
    msg_queue.task_done()

def task_producer(msg_queue):
  google_apps_script_url = os.getenv('GOOGLE_APPS_SCRIPT_URL')
  while True:
    try:
      res = requests.get(google_apps_script_url, timeout=10, verify=False)
      res.raise_for_status()
      if res.json()['status'] == 'OK':
        magnet_list = res.json()['magnet_urls']
        for magnet in magnet_list:
          print(json.loads(magnet['magnet'])['chat_id'])
          print(json.loads(magnet['magnet'])['url'])
          msg = {
            'chat_id': json.loads(magnet['magnet'])['chat_id'],
            'magnet_url': json.loads(magnet['magnet'])['url']
          }
          msg_queue.put(msg)
    except Exception as e:
      print(e)
      time.sleep(60)
      continue
    time.sleep(60)
  return

if __name__ == '__main__':
  urllib3.disable_warnings()
  msg_queue = Queue()
  thread_producer = Thread(target=task_producer, args=(msg_queue,))
  thread_producer.start()

  # 开启任务处理线程
  my_qb = dl.MyQbittorrent(dl.QBIT_HOST, dl.QBIT_USER, dl.QBIT_PASS)
  for i in range(3 if my_qb.perferences.get('max_active_downloads') == 99 else my_qb.perferences.get('max_active_downloads')):
    t = Thread(target=task_customer, args=(msg_queue, my_qb))
    t.setDaemon(True)
    t.start()
  thread_producer.join()
