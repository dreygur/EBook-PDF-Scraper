#!/usr/bin/env python

import os
import re
import sys
import math
import enlighten
import requests as rq
from urllib.parse import unquote

def get_all_urls() -> list:
  # WP-JSON api to get all the pages
  uri = "https://bdebooks.com/wp-json/wp/v2/genres?_fields=link&per_page=100&page="
  urls = []
  page = 1

  # Loop through the pages of WP-JSON api
  while True:
    res = rq.get(f'{uri}{page}')
    if len(res.json()) == 0:
      return urls
    for url in res.json():
      urls.append(url.get('link'))
    page += 1

  return urls

def get_books(uri: str) -> list:
  """Get Book Link

  Args:
    str (uri): Page link where books are listed

  Returns:
    list: Individual book's page link
  """
  res = rq.get(uri)

  if res.status_code != 200: return

  # Find all books page
  links = re.findall(r'bdebooks\.com\/books\/[a-zA-Z0-9-]*', res.text)
  links = ['https://' + link for link in links]

  return links

def download(uri: str) -> None:
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

    # Filename
    d = res.headers['content-disposition']
    fname = unquote(re.findall("filename=(.+)", d)[0]).replace('"', '')
    fname = re.sub(r'\s?-?\s\([A-z.].*\)', '', fname)

    # Author's Name
    author = ''
    try:
      author = re.search(r'\s?\s?by\s?\s([A-z\s]{1,})', fname, flags=re.IGNORECASE).group(1)
    except AttributeError:
      pass

    # Download Location for Different Authors
    location = os.path.join(download_location, author)
    if not os.path.isdir(location):
      os.mkdir(location)

    dlen = int(res.headers.get('Content-Length', '0')) or None
    print(f"[+] {fname}")

    # Status Bar and File Saver
    with MANAGER.counter(
      color = 'green',
      total = dlen and math.ceil(dlen / 2 ** 20),
      unit = 'MiB',
      leave = False
    ) as ctr, open(os.path.join(location, fname), 'wb', buffering=2**24) as f:
      for chunk in res.iter_content(chunk_size = 2 ** 20):
        f.write(chunk)
        ctr.update()

def main():
  urls = set(get_all_urls())

  for uri in urls:
    books = set(get_books(uri))
    for book in books:
      download(book)

if __name__ == '__main__':
  MANAGER = enlighten.get_manager()
  try:
    download_location = os.path.join(os.getcwd(), 'books')
    if not os.path.exists(download_location):
      os.mkdir(download_location)

    if len(sys.argv) == 2:
      download(sys.argv[1])
    else:
      main()
  except KeyboardInterrupt:
    sys.exit()
