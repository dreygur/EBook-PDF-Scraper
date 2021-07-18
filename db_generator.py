#!/usr/bin/env python

import os
import re
import sys
import json
import math
import enlighten
import requests as rq
from urllib.parse import unquote

# Internal Import
from app import get_all_urls, get_books

def db(uri: str) -> None:
  """Download the Book

  Args:
    uri (str): Download Link
  """
  if not uri.startswith('http'): 'https://' + uri
  
  res = rq.get(uri)
  if res.status_code != 200: return

  # Find all dl* links
  link = re.findall(r'dl\.bdebooks\.com\/index\.php\/s\/[a-zA-Z0-9]*\/download', res.text)

  if len(link) != 0:
    res = rq.get('https://' + link[0], stream=True)

    d = res.headers['content-disposition']
    fname = unquote(re.findall("filename=(.+)", d)[0]).replace('"', '')

    dlen = int(res.headers.get('Content-Length', '0')) or None
    print(f"[+] {fname}")

    # Status Bar and File Saver
    with MANAGER.counter(
      color = 'green',
      total = dlen and math.ceil(dlen / 2 ** 20),
      unit = 'MiB',
      leave = False
    ) as ctr:
      db_obj = {
        "uri": uri,
        "download link": link[0],
        "filename": fname
      }
      ctr.update()
      return db_obj

def main():
  urls = set(get_all_urls())

  database = []
  
  try:
    for uri in urls:
      books = set(get_books(uri))
      for book in books:
        database.append(db(book))

    with MANAGER.counter(
      color = 'green',
      total = len(database) and math.ceil(database / 2 ** 20),
      unit = 'MiB',
      leave = False
    ) as ctr, open(os.path.join(db_location), 'a', buffering=2**24) as f:
      json.dump(database, f, indent=4)
      ctr.update()

  except:
    with MANAGER.counter(
      color = 'green',
      total = len(database) and math.ceil(len(database) / 2 ** 20),
      unit = 'MiB',
      leave = False
    ) as ctr, open(os.path.join(db_location), 'a', buffering=2**24) as f:
      json.dump(database, f, indent=2)
      ctr.update()

if __name__ == '__main__':
  MANAGER = enlighten.get_manager()
  db_location = os.path.join(os.getcwd(), 'db.json')
  main()