#! /usr/bin/env python
# -*- coding:utf8 -*-
#
# fetcher.py
#
# Copyright © 2013 Mathieu Gaborit (matael) <mathieu@matael.org>
#
#
# Distributed under WTFPL terms
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                    Version 2, December 2004
#
# Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>
#
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#  0. You just DO WHAT THE FUCK YOU WANT TO.
#

"""
Fetcher Ical
"""

from icalendar import Calendar
from collections import namedtuple
from urllib import urlopen

# Structure de donnée pour les évènements
Vevent = namedtuple('Vevent', ['dtstart', 'dtend', 'summary', 'location'])

class IcalFetcher:
    """
    Fetcher for Ical data.
    Provides a wrapper to get clean, sorted list of events

    """

    def __init__(self):

        # init. all to None, this way we can infer which source to use
        # if user doesn't specify it
        self.filename = None
        self.url = None
        self.mode = None

    def from_url(self, url):
        """ Add URL source and change mode to URL """

        self.mode = "URL"
        self.url = url

    def from_file(self, filename):
        """ Add file source and change mode to FILE """

        self.mode = "FILE"
        self.filename = filename

    def __iter__(self):
        """ Add __iter__ special method so we can iterate directly over the object """

        for ev in self.events:
            yield ev


    def get_events(self, mode=None):
        """ Grab list of events and sort them. Source is selected through mode """

        # find which source to use (if no mode's specified on call, use self.mode)
        if mode==None: mode = self.mode

        if mode == "FILE" and self.filename!=None:
            # read data from file
            with open(self.filename, 'r') as f:
                gcal = Calendar.from_ical(f.read())
        elif mode == "URL" and self.url!=None:
            # open url and read data from it
            gcal = Calendar.from_ical(urlopen(self.url).read())
        else:
            # if mode's unknown, just raise an Exception
            raise ValueError("Supplied mode is not correct. Accepted modes are : FILE, URL")

        # clean and sort events
        events = []
        for component in gcal.walk():
            if component.name == "VEVENT":
                e = Vevent(dtstart=component.get('dtstart').dt,
                           dtend=component.get('dtend').dt,
                           summary=component.get('summary').encode('utf8'),
                           location=component.get('location').encode('utf8')
                          )
                events.append(e)
        events.sort(key = lambda ev: ev.dtstart)
        self.events =  events
