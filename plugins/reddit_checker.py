#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2

from sb_plugins import plugin_base

import simplejson as json

from twisted.internet import task


class reddit_checker(plugin_base):
    def __init__(self, irc):
        self.registered_events = {}
        self.irc = irc
        self.reddit_config = irc.factory.server_config['plugin_config']['reddit']

        looper = task.LoopingCall(self.redditcheck)
        looper.start(30)

    def get_subreddit_new(self, subreddit):
        user_agent = 'slutbot for polling ' + subreddit
        url = 'http://www.reddit.com/r/' + subreddit + '/new.json?sort=new'
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', user_agent)]
        response = opener.open(url)
        data = response.read()
        parsed = json.loads(data)
        return parsed['data']['children']

    def get_latest_post_id(self, subreddit):
        data = self.get_subreddit_new(subreddit)
        return data[0]['data']['id']

    def redditcheck(self):
        print("tick")
        print(self.reddit_config)
        for subscribe in self.reddit_config:
            subreddit = subscribe['subreddit']
            channel = subscribe['channel']
            if 'next_last_id' not in subscribe.keys():
                subscribe['next_last_id'] = self.get_latest_post_id(subreddit)
            else:
                data = self.get_subreddit_new(subreddit)

                for child in data:
                    id = child['data']['id']
                    if id == subscribe['next_last_id']:
                        break

                    title = child['data']['title']
                    link = child['data']['permalink']
                    print(title)
                    print(link)

                    self.irc.msg(
                        channel,
                        'New r/' + self.subreddit + ' submission: ' + title
                    )
                    self.irc.msg(
                        channel,
                        'link: http://www.reddit.com' + link
                    )

                subscribe['next_last_id'] = data[0]['data']['id']
