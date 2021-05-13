#!/usr/bin/python3
# -*- coding=utf-8 -*-
# author:   RedLeaves
# date:     2021/05/13
# version:  0.1


import requests
import json
import sys
import os
import re

from bs4 import BeautifulSoup
from json import JSONEncoder
from urllib.parse import urlparse


################################################################
# Custom Config
BASE_URL = "https://guangzhou.8684.cn"
HEADER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0"}

# Debug Config
TEST = False

################################################################
class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class BusInfo:
    def __init__(self, bus_name, stations):
        self.bus_name = bus_name
        self.stations = stations


def main(argv):
    bus_hrefs = []

    print("start find bus href...")

    print("find %s" % (BASE_URL))
    index_page = requests.get(BASE_URL, headers=HEADER)
    Soup = BeautifulSoup(index_page.text, "lxml")

    bus_layers = Soup.find("div", class_="bus-layer").find_all("a")
    # print(bus_layers)

    for bus_layer in bus_layers:
        if TEST == True:
            break

        # print(bus_layer)
        href = bus_layer["href"]
        basename = os.path.basename(href)
        bus_layer_href = os.path.join(BASE_URL, basename)
        # print(bus_layer_href)

        if "x_" in basename:
            if bus_layer_href not in bus_hrefs:
                bus_hrefs.append(bus_layer_href)
            continue

        print("find %s" % (bus_layer_href))
        bus_layer_page = requests.get(bus_layer_href, headers=HEADER)
        Soup = BeautifulSoup(bus_layer_page.text, "lxml")

        buses = Soup.find("div", class_="list").find_all("a")
        # print(buses)

        for bus in buses:
            # print(bus)
            href = bus["href"]
            basename = os.path.basename(href)
            bus_href = os.path.join(BASE_URL, basename)
            # print(bus_href)

            if "x_" in basename:
                if bus_href not in bus_hrefs:
                    bus_hrefs.append(bus_href)
                continue

    print("")

    if TEST == True:
        bus_hrefs = [
            "https://guangzhou.8684.cn/x_7e645093",
            "https://guangzhou.8684.cn/x_be6283cb",
        ]

    f = open("bus-infos.json", "w")

    print("start fetch bus info...")

    for i, bus_href in enumerate(bus_hrefs):
        # print(bus_href)
        print("[%3d%%] fetch %s" % ((i + 1) * 100 / len(bus_hrefs), bus_href))
        bus_page = requests.get(bus_href, headers=HEADER)
        Soup = BeautifulSoup(bus_page.text, "lxml")

        bus_lz_info = Soup.find("div", class_="bus-lzinfo")
        bus_name = bus_lz_info.find("h1", class_="title").get_text()

        bus_lz_list = Soup.find("div", class_="bus-lzlist")
        stations = bus_lz_list.find_all("a")
        s = []
        for i, station in enumerate(stations):
            station_name = station.get_text()
            s.append({i + 1: station_name})

        line = json.dumps(BusInfo(bus_name, s), ensure_ascii=False, cls=MyEncoder) + "\n"
        f.write(line)
        # print(line)

    f.flush()
    f.close()


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt as e:
        print("")
        quit()
