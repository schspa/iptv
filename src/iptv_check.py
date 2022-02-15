#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   iptv_check.py --- Description
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

from utils import m3u8_info
import os
import sys
from pprint import pprint
import click
import m3u8

import re
from m3u8 import protocol
from m3u8.parser import save_segment_custom_value
from utils import m3u8_info

# https://en.wikipedia.org/wiki/M3U
# #EXTINF:
## track information: runtime in seconds and display title of the following resource
## additional properties as key-value pairs
## #EXTINF:123 logo="cover.jpg",Track Title
## #EXTINF:-1 group-title="== 未分组 ==",CCTV1

def parse_iptv_attributes(line, lineno, data, state):
    # Customize parsing #EXTINF
    if line.startswith(protocol.extinf):
        title = ''
        chunks = line.replace(protocol.extinf + ':', '').split(',')
        if len(chunks) == 3:
            duration_and_props = chunks[0] + ' ' + chunks[1]
            title = chunks[2]
        elif len(chunks) == 2:
            duration_and_props, title = chunks
        elif len(chunks) == 1:
            duration_and_props = chunks[0]

        additional_props = {}
        chunks = duration_and_props.strip().split(' ', 1)
        if len(chunks) == 2:
            duration, raw_props = chunks
            matched_props = re.finditer(r'([\w\-]+)="([^"]*)"', raw_props)
            for match in matched_props:
                additional_props[match.group(1)] = match.group(2)
        else:
            duration = duration_and_props

        if 'segment' not in state:
            state['segment'] = {}
        state['segment']['duration'] = float(duration)
        state['segment']['title'] = title

        # Helper function for saving custom values
        save_segment_custom_value(state, 'extinf_props', additional_props)

        # Tell 'main parser' that we expect an URL on next lines
        state['expect_segment'] = True

        # Tell 'main parser' that it can go to next line, we've parsed current fully.
        return True

def parse_m3u_list():
    iptvlist = []
    for root, dirs, files in os.walk("sources", topdown=False):
        for fname in files:
            print('-' * 80)
            print(os.path.join(root, fname))
            parsed = m3u8.load(os.path.join(root, fname), custom_tags_parser=parse_iptv_attributes)
            for seg in parsed.segments:
                first_segment_props = seg.custom_parser_values['extinf_props']
                iptvlist.append({'title':seg.title, 'uri': seg.uri, 'props': first_segment_props})

    return iptvlist

@click.group()
@click.option('--debug/--no-debug', default=False)
@click.option('-c', '--channel', type=str)
@click.pass_context
def cli(ctx, debug, channel):
    ctx.ensure_object(dict)

    ctx.obj['channel'] = channel
    ctx.obj['list'] = parse_m3u_list()

def iptv_name_match(channel, title):
    return channel in title

def stream_compare(e):
    return e['stream_info']['linkspeed']

@cli.command()
@click.pass_context
def find_uri(ctx):
    active = []
    possible_stream = list(filter(lambda x: iptv_name_match(ctx.obj['channel'], x['title']), ctx.obj['list']))
    pprint(possible_stream)
    for channel in possible_stream:
        try:
            click.secho('Trying: %s' % (channel['uri']),
                bg='black',
                fg='green')
            stream_info = m3u8_info.get_iptv_info(channel['uri'])
            channel['stream_info'] = stream_info
            pprint(channel)
            active.append(channel)
        except Exception as e:
            print(e)
            continue

    active.sort(key = stream_compare)
    pprint(active)

PLAYLIST = """#EXTM3U
    #EXTINF:-1 timeshift="0" catchup-days="7" catchup-type="flussonic" tvg-id="channel1" group-title="Group1",Channel1
    http://str00.iptv.domain/7331/mpegts?token=longtokenhere
    #EXTINF:-1 group-title="== 未分组 ==",CCTV-1综合
    http://117.148.179.155/PLTV/88888888/224/3221231468/index.m3u8
    #EXTINF:-1 ,道
    http://112.74.200.9:88/tv000000/m3u8.php?/migu/625774640
    #EXTINF:-1,tvg-id="欢笑剧场" tvg-name="欢笑剧场" tvg-logo="https://epg.112114.xyz/logo/欢笑剧场.png" group-title="4K频道",欢笑剧场4K
    http://baidu.live.cqccn.com/__cl/cg:live/__c/hxjc_4K/__op/default/__f//index.m3u8
    """

if __name__ == '__main__':
    cli(obj={})
