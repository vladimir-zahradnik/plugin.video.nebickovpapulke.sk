# -*- coding: UTF-8 -*-
# *
# *      Copyright (C) 2015 Vladimir Zahradnik
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */

import sys
import re
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import urllib, urllib2, urlparse

web_base_url = 'http://www.nebickovpapulke.sk'
addon = xbmcaddon.Addon()
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')

MODE_PLAY_EPISODE = 'play_episode'

def build_url(query):
    addon_base_url = sys.argv[0]
    return addon_base_url + '?' + urllib.urlencode(query)

def get_http_data_from_url(url):
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20120101 Firefox/33.0'
    request = urllib2.Request(url)
    request.add_header('User-Agent', user_agent)
    response = urllib2.urlopen(request)
    httpdata = response.read()
    response.close()
    return httpdata

def notify(msg, timeout = 5000):
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(addon.getAddonInfo('name'), msg,
                                                        timeout, addon.getAddonInfo('icon')))

def add_item(name, url, mode, isFolder=False):
    plugin_url = build_url({'url': url, 'mode': mode, 'name': name})
    li = xbmcgui.ListItem(name, iconImage="DefaultFolder.png")

    result = xbmcplugin.addDirectoryItem(handle=addon_handle, url=plugin_url,
                                         listitem=li, isFolder=isFolder)
    return result


def add_directory(name, url, mode=None):
    return add_item(name, url, mode, isFolder=True)


def translation(id):
    return addon.getLocalizedString(id).encode('utf-8')

def list_archived_shows():
    url = args.get('url', None)

    if url is None:
        url = web_base_url + '/epizody'
    else:
        url = url[0]

    content = get_http_data_from_url(url)

    # Limit result to only Epizode Archive part
    content = content[content.find('Archív Epizód') : content.find('<aside class="second">')]

    # Regexp to match aired date and epizode name
    pattern = 'class="date-display-single">(\d{2}.\d{2}.\d{4})<\/span>.*?<a href="(.*?)">Epizóda (\d{2}\/\d{4})\s*:*\s*(.*?)<\/a>'
    match = re.compile(pattern, re.DOTALL).findall(content)

    for aired, url, episode, name in match:
        add_directory(translation(30000) + " " + episode + ": " + name, web_base_url + url, MODE_PLAY_EPISODE)

    # Check if there is more episodes
    pattern = 'class="pager-next.*?<a href="(.*?)"'
    match = re.compile(pattern, re.DOTALL).findall(content)

    if match:
        url = match[0]
        add_directory("[B]" + translation(30001) +"[/B]", web_base_url + url)

    xbmcplugin.endOfDirectory(addon_handle)

mode = args.get('mode', None)

#if mode is None:
list_archived_shows()
