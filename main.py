#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import os
import pynotify
from pit import Pit
from lingr import Lingr


def get_img(url):
    BASE_DIR = os.path.expanduser('~/.lingr')
    if not os.path.exists(BASE_DIR):
        os.mkdir(BASE_DIR)
        os.chmod(BASE_DIR, 0700)
    path = os.path.join(BASE_DIR, os.path.basename(url))
    if os.path.exists(path):
        return path
    file = open(path, 'wb')
    file.write(urllib.urlopen(url).read())
    file.close()
    return path


def main():
    config = Pit.get('lingr.com', {
        'require': {
            'user': 'Your lingr user name',
            'password': 'Your lingr password'
        }
    })
    lingr = Lingr(config['user'], config['password'])

    for event in lingr.stream():
        pynotify.init('lingr')
        title = None
        text = None
        img = None
        if 'message' in event:
            message = event['message']
            title = '%s@%s' % (message['nickname'], message['room'])
            text = message['text']
            img = get_img(message['icon_url'])
        elif 'presence' in event:
            presence = event['presence']
            title = '%s@%s' % (presence['nickname'], presence['room'])
            text = presence['status']
            img = get_img(presence['icon_url'])
        n = pynotify.Notification(title, text, img)
        n.show()

if __name__ == '__main__':
    main()
