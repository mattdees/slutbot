#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import BeautifulSoup


class weather_check:

    def __init__(self, irc):
        self.registered_events = {'.w': self.wunderground,
                                  '.pws': self.wu_pws}
        self.irc = irc

    def get_events(self):
        return self.registered_events

    def wunderground(
        self,
        channel,
        arguments,
        user,
        ):
        res_xml = \
            self.http_get_query('http://api.wunderground.com/auto/wui/geo/WXCurrentObXML/index.xml'
                                , {'query': arguments})
        parsed_res = BeautifulSoup.BeautifulStoneSoup(res_xml)
        res = \
            parsed_res.current_observation.display_location.full.string \
            + ' '
        res = self.parse_wunderground_respone(parsed_res, res)
        self.irc.msg(channel, res.encode('latin-1'))

    def wu_pws(
        self,
        channel,
        arguments,
        user,
        ):
        stations = \
            self.http_get_query('http://api.wunderground.com/auto/wui/geo/GeoLookupXML/index.xml'
                                , {'query': arguments})
        stations_parsed = BeautifulSoup.BeautifulStoneSoup(stations)
        station_id = \
            stations_parsed.location.nearby_weather_stations.pws.station.id.string
        station_id = station_id.replace('<![CDATA[', '')
        station_id = station_id.replace(']]>', '')
        res_xml = \
            self.http_get_query('http://api.wunderground.com/weatherstation/WXCurrentObXML.asp'
                                , {'ID': station_id})
        parsed_res = BeautifulSoup.BeautifulStoneSoup(res_xml)
        res = parsed_res.current_observation.location.full.string + ' '
        res = self.parse_wunderground_respone(parsed_res, res)
        self.irc.msg(channel, res.encode('latin-1'))

    def parse_wunderground_respone(self, data, response):
        if len(data.current_observation.temperature_string.contents) \
            != 0:
            response += ' temp: ' \
                + data.current_observation.temperature_string.string

        if len(data.current_observation.relative_humidity.contents) \
            != 0:
            response += ' humidity: ' \
                + data.current_observation.relative_humidity.string

        if len(data.current_observation.wind_string.contents) != 0:
            response += ' wind: ' \
                + data.current_observation.wind_string.string

        if len(data.current_observation.windchill_string.contents) != 0:
            response += ' windchill: ' \
                + data.current_observation.windchill_string.string

        if len(data.current_observation.pressure_string.contents) != 0:
            response += ' pressure: ' \
                + data.current_observation.pressure_string.string

        if len(data.current_observation.dewpoint_string.contents) != 0:
            response += ' dewpoint: ' \
                + data.current_observation.dewpoint_string.string

        if len(data.current_observation.station_id.contents) != 0:
            response += ' station: ' \
                + data.current_observation.station_id.string

        return response

    def http_get_query(self, url, arguments):

        # Build our query

        http_query = url + '?' + urllib.urlencode(arguments)

        # perform our query

        try:
            response = urllib2.urlopen(http_query)
        except (URLError, HTTPError):

            # error if our query has issues

            print 'Error while retrieving http data for ' + http_query
            return False

        # return the data contained within the http query

        return response.read()


