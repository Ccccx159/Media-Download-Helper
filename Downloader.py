#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from qbittorrent import Client as QbClient
from queue import Queue
import urllib.parse
import time, os

# qbittorrent login info
QBIT_HOST = os.getenv('QBIT_HOST')
QBIT_USER = os.getenv('QBIT_USER')
QBIT_PASS = os.getenv('QBIT_PASS')

class MyQbittorrent:
  def __init__(self, host, user, password):
    self.qb = QbClient(host)
    self.qb.login(user, password)
    self.perferences = self.qb.preferences()
    print('Login successfully')

  def __del__(self):
    print('Logout successfully')
  
  def __extract_hash_from_magnet(self, magnet_url):
    magnet_params = urllib.parse.urlparse(magnet_url)
    magnet_args = urllib.parse.parse_qs(magnet_params.query)
    if 'xt' in magnet_args:
      xt_values = magnet_args['xt']
      for value in xt_values:
        if value.startswith('urn:btih:'):
          return value[9:]
    return None

  def query_torrent(self, magnet_url):
    tr_lists = self.qb.torrents(sorted='added_on')
    for tr in tr_lists:
      # print(tr['magnet_uri'])
      if self.__extract_hash_from_magnet(tr['magnet_uri']) == self.__extract_hash_from_magnet(magnet_url):
        return tr
    return None
  
  def download(self, magnet_url, save_path='/downloads'):
    tr = self.query_torrent(magnet_url)
    if tr is not None:
      content = 'Torrent {} already exists, please do not download again'.format(tr['name'])
      # print(content)
      return 'Error', None, content
    else:
      self.qb.download_from_link(magnet_url, save_path=save_path)
      start_time = time.time()
      while True:
        tr = self.query_torrent(magnet_url)
        if tr is None:
          time.sleep(5)
          if time.time() - start_time > 60:
            content = 'Add download task failed! Qbittorrent not response, please check the host is working normally'
            return 'Error', None, content
          continue
        return 'Success', tr, '{} now has started downloading'.format(tr['name'])
