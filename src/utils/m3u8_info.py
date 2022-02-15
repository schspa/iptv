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
import urllib
from urllib.request import urlretrieve
import urllib
import os
import sys
import time

def get_iptv_info(url, verbose = True):
    m = m3u8.load(url)

    if len(m.playlists) > 0:
        pl = m.playlists[0]
        return get_iptv_info(pl.absolute_uri)

    for sm in m.segments:
        url2 = sm.absolute_uri
        try:
            start_time = time.time()
            (filename, headers) = urlretrieve(url2)
            end_time = time.time()
            size = os.path.getsize(filename)
            speed = size / (end_time - start_time)
            metadata = FFProbe(filename)
            return {
                "url" : url,
                "linkspeed": speed,
                "frame_size" : metadata.video[0].frame_size(),
                "metadata" : metadata.metadata
            }
            break;
        except URLError as e:
            raise RuntimeError("Failed to download '{}'. '{}'".format(url2, e.reason))

        pass
    pass

if __name__ == '__main__':
    urls = [
        "http://112.17.40.145/PLTV/88888888/224/3221226154/index.m3u8",
        "http://183.207.248.71:80/cntv/live1/cctv-13/cctv-13",
        "http://117.148.179.182/PLTV/88888888/224/3221231648/index.m3u8",
        "http://39.134.115.163:8080/PLTV/88888910/224/3221225635/index.m3u8",
        "http://liveop.cctv.cn/hls/4KHD/playlist.m3u8"
    ]

    for url in urls:
        try:
            print(get_iptv_info(url))
        except urllib.error.HTTPError as e:
            pass
