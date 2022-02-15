#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   m3u8-checker.py --- Description
#
#   Copyright (C) 2022, Schspa, all rights reserved.
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import m3u8
from ffprobe import FFProbe
import tempfile
from urllib import *
from urllib.request import urlretrieve
import urllib
import sys

def get_iptv_info(url):
    print(url)
    m = m3u8.load(url)
    if len(m.playlists) == 0:
        return
    pl = m.playlists[0]
    m2 = m3u8.load(pl.absolute_uri)
    for sm in m2.segments:
        url2 = sm.absolute_uri
        print(url2)
        try:
            (filename, headers) = urlretrieve(url2)
            metadata = FFProbe(filename)
            print(metadata.metadata)
            print(metadata.video[0].frame_size())
            break;
        except URLError as e:
            raise RuntimeError("Failed to download '{}'. '{}'".format(url2, e.reason))

        pass
    pass

if __name__ == '__main__':
    urls = [
        "http://112.17.40.145/PLTV/88888888/224/3221226154/index.m3u8",
        "http://112.17.40.145/PLTV/88888888/224/3221226138/index.m3u8",
        "http://liveop.cctv.cn/hls/4KHD/playlist.m3u8"
    ]

    for url in urls:
        try:
            get_iptv_info(url)
        except urllib.error.HTTPError as e:
            pass
    for i in range(3221226154, 3221226254):
        try:
            get_iptv_info("http://112.17.40.145/PLTV/88888888/224/%d/index.m3u8" % (i))
        except urllib.error.HTTPError as e:
            pass
