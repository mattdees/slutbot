#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

import urllib
import urllib2

import BeautifulSoup

from sb_plugins import plugin_base


class weather_check(plugin_base):
    def __init__(self, irc):
        self.registered_events = {
            '.w': self.wunderground,
            '.pws': self.wu_pws,
            '.pwsid': self.wu_pwsid
        }

        baseurl = 'http://api.wunderground.com/'
        self.endpoints = {
            'GeoCurrent': baseurl + 'auto/wui/geo/WXCurrentObXML/index.xml',
            'GeoLookup': baseurl + 'auto/wui/geo/GeoLookupXML/index.xml',
            'WsCurrent': baseurl + 'weatherstation/WXCurrentObXML.asp',
        }
        self.irc = irc

    def wunderground(self, sbmessage):
        res_xml = self.http_get_query(
            self.endpoints['GeoCurrent'],
            {'query': sbmessage.arguments}
        )

        parsed_res = BeautifulSoup.BeautifulStoneSoup(res_xml)
        res = \
            parsed_res.current_observation.display_location.full.string \
            + ' '
        res = self.parse_wunderground_respone(parsed_res, res)
        sbmessage.respond(res.encode('latin-1'))

    def wu_pws(self, sbmessage):
        stations = self.http_get_query(
            self.endpoints['GeoLookup'],
            {'query': sbmessage.arguments}
        )

        stations_parsed = BeautifulSoup.BeautifulStoneSoup(stations)

        nearby_stations = stations_parsed.location.nearby_weather_stations
        station_id = nearby_stations.pws.station.id.string
        station_id = station_id.replace('<![CDATA[', '')
        station_id = station_id.replace(']]>', '')

        self.return_pwsid(sbmessage, station_id)

    def wu_pwsid(self, sbmessage):
        station_id = "KTXHOUST890"
        self.return_pwsid(sbmessage, station_id)

    def return_pwsid(self, sbmessage, stationid):
        res_xml = self.http_get_query(
            self.endpoints['WsCurrent'],
            {'ID': stationid}
        )

        parsed_res = BeautifulSoup.BeautifulStoneSoup(res_xml)
        res = parsed_res.current_observation.location.full.string + ' '
        res = self.parse_wunderground_respone(parsed_res, res)
        sbmessage.respond(res.encode('latin-1'))

    def parse_wunderground_respone(self, data, response):
        obs = data.current_observation

        if len(obs.temperature_string.contents) != 0:
            response += ' temp: ' + obs.temperature_string.string

        if len(obs.relative_humidity.contents) != 0:
            response += ' humidity: ' + obs.relative_humidity.string

        if len(obs.wind_string.contents) != 0:
            response += ' wind: ' + obs.wind_string.string

        if len(obs.windchill_string.contents) != 0:
            response += ' windchill: ' + obs.windchill_string.string

        if len(obs.pressure_string.contents) != 0:
            response += ' pressure: ' + obs.pressure_string.string

        if len(obs.dewpoint_string.contents) != 0:
            response += ' dewpoint: ' + obs.dewpoint_string.string

        if len(obs.station_id.contents) != 0:
            response += ' station: ' + obs.station_id.string

        return response

    def http_get_query(self, url, arguments):

        # Build our query

        http_query = url + '?' + urllib.urlencode(arguments)

        # perform our query

        try:
            response = urllib2.urlopen(http_query)
        except (urllib2.URLError, urllib2.HTTPError):

            # error if our query has issues

            print('Error while retrieving http data for ' + http_query)
            return False

        # return the data contained within the http query

        return response.read()
