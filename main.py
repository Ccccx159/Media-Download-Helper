#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import Downloader as dl
import time, re
import simple_http_server as http_srv
from queue import Queue
from threading import Thread
import TelegramBot as tgbot
import TMDBQuery as tmdb

def task_processor(msg_queue, qb):
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



if __name__ == '__main__':
  msg_queue = Queue()
  thread_httpd = Thread(target=http_srv.simple_http_server, args=(msg_queue,))
  thread_httpd.start()

  # 开启任务处理线程
  my_qb = dl.MyQbittorrent(dl.QBIT_HOST, dl.QBIT_USER, dl.QBIT_PASS)
  for i in range(3 if my_qb.perferences.get('max_active_downloads') == 99 else my_qb.perferences.get('max_active_downloads')):
    t = Thread(target=task_processor, args=(msg_queue, my_qb))
    t.setDaemon(True)
    t.start()

  while True:
    if not msg_queue.empty():
      msg = msg_queue.get()
      print('chat_id: {}'.format(msg.get('chat_id')))
      print('magnet_url:{}'.format(msg.get('magnet_url')))
      time.sleep(5)
      
    else:
      time.sleep(10 * 1 / 1000)
      
  thread_httpd.join()
