#!/usr/bin/python
# -*- coding: utf-8 -*-
import simplejson as json
from twisted.internet import task
import urllib2


class reddit_checker(object):

    def __init__(self, irc):
        self.registered_events = {}
        self.irc = irc
        self.subreddit = irc.factory.server_config['plugin_config']['reddit_subreddit']
        self.last_id = self.get_latest_post_id()
        looper = task.LoopingCall(self.redditcheck)
        looper.start(30)

    def get_events(self):
        return self.registered_events

    def get_subreddit_new(self):
        user_agent = 'slutbot for polling ' + self.subreddit
        url = 'http://www.reddit.com/r/' + self.subreddit \
            + '/new.json?sort=new'
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', user_agent)]
        response = opener.open(url)
        data = response.read()
        parsed = json.loads(data)
        return parsed['data']['children']

    def get_latest_post_id(self):
        data = self.get_subreddit_new()
        return data[0]['data']['id']

    def redditcheck(self):
        send_channel = self.irc.factory.server_config['plugin_config']['reddit_channel']

#    ....self.irc.msg(send_channel, 'getting data for ' + self.subreddit)

        data = self.get_subreddit_new()
        next_last_id = data[0]['data']['id']

#        self.irc.msg(send_channel, 'top id for subreddit is ' + next_last_id)

        for child in data:
            id = child['data']['id']
            if id == self.last_id:
                break
            self.irc.msg(send_channel, 'New r/' + self.subreddit + ' submission: ' + child['data']['title'])
            self.irc.msg(send_channel, 'link: http://www.reddit.com' + child['data']['permalink'])
        self.last_id = next_last_id
