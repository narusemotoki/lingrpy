#!/usr/bin/env python
# -*- coding: utf-8 -*-

import simplejson
import urllib
import urllib2


class Lingr(object):

    __URL_BASE__ = 'http://lingr.com/api/'
    __URL_BASE_OBSERVE__ = "http://lingr.com:8080/api/"

    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.counter = 0

    def create_session(self):
        data = self.post('session/create', {
            'user': self.user,
            'password': self.password
        })
        if data:
            self.session = data['session']
            self.nickname = data['nickname']
        return data

    def get_rooms(self):
        data = self.get("user/get_rooms", {
            'session': self.session
        })
        if data:
            self.rooms = data['rooms']
        return data

    def subscribe(self, room=None, reset='true'):
        if not room:
            room = ','.join(self.rooms)
        data = self.post("room/subscribe", {
            'session': self.session,
            'room': room,
            'reset': reset
        })
        if data:
            self.counter = data['counter']
        return data

    def observe(self):
        data = self.get("event/observe", {
            'session': self.session,
            'counter': self.counter
        })
        if 'counter' in data:
            self.counter = data['counter']
        return data

    def say(self, room, text):
        data = self.post('room/say', {
            'session': self.session,
            'room': room,
            'nickname': self.nickname,
            'text': text
        })
        return data

    def post(self, path, params):
        r = self.get_opener().open(self.get_url(path),
                                   urllib.urlencode(params))
        return self.loads(r.read())

    def get(self, path, params):
        full_url = self.get_url(path) + '?' + urllib.urlencode(params)
        r = self.get_opener().open(full_url)
        return self.loads(r.read())

    def loads(self, json):
        data = simplejson.loads(json)
        if data['status'] == 'ok':
            return data
        else:
            print 'error'
            print data
        return None

    def get_url(self, path):
        url = self.__URL_BASE__
        if path == 'event/observe':
            url = self.__URL_BASE_OBSERVE__
        return url + path

    def get_opener(self):
        opener = urllib2.build_opener()
        opener.addheaders = [
            ('User-agent', 'python lingr(http://d.hatena.ne.jp/jYoshiori/)')
        ]
        return opener

    def stream(self):
        self.create_session()
        self.get_rooms()
        self.subscribe()
        while True:
            obj = self.observe()
            if 'events' in obj:
                for event in obj['events']:
                    yield event

# こっから Ubuntu 用の実装
import os
import pynotify
from pit import Pit


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
        pynotify.init("lingr")
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
