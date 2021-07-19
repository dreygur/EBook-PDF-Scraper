import csv
import ast
import json

"""
    This script is for converting my previously saved json data
    to csv format.
    May be not helpful for anyone else!
"""

def main():
  # Keys to get exact info from NASA-Dict
  data_locations = ["uri", "download link", "filename"]

  with open('db.csv', 'w') as nasa:
    with open('db.json', 'r') as json_data:
      data = json.load(json_data)
      print(type(data))
      d_data = csv.DictWriter(nasa, restval="-", fieldnames=data_locations)
      d_data.writeheader()
      d_data.writerows(data)

if __name__ == "__main__":
  main()