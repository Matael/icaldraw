#! /usr/bin/env python
# -*- coding:utf8 -*-
#
# icaldraw.py
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
Class Drawing an EDT
"""

from __future__ import print_function

from fetcher import IcalFetcher
from svgutils import SVGwriter

class IcalDraw:

    def __init__(self, url=None, file=None, utc_offset=1, stroke_color="rgb(5%, 32%, 65%)"):
            self.url = url
            self.file = file
            self.utc_offset = utc_offset
            self.stroke_color = stroke_color

            # space to be left as a header
            self.blank_header = 45

            self.cal = IcalFetcher()
            if self.url: self.cal.from_url(self.url)
            elif self.file: self.cal.from_file(self.file)
            else: raise ValueError("Give me a source !")

            self.cal.get_events()

            self.img = SVGwriter(1360, 410)

    def draw(self):
        self._grid()
        self._header()
        self._place_events()

    def save(self,filename):
        self.img.save(filename)

    def _header(self):
        middle = self.img.width/2
        self.img.add_text(
            "Semaine du {0}/{1}".format(self.cal.events[0].dtstart.day,self.cal.events[0].dtstart.month),
            middle,
            self.blank_header*2/3,
            style="text-anchor: middle; font-size: 30; alignment-baseline: middle; letter-spacing: 2pt; stroke: {};".format(self.stroke_color)
        )

    def _grid(self):
        """ Draw a hours&days grid """

        style = "stroke: black; stroke-opacity: 0.4;"

        # vertical
        for n in xrange(12):
            if (n+8) in [8,12,14,18]:
                self.img.add_line(20+n*120,self.blank_header+10,20+n*120,self.img.height-10, style=style+"stroke-width: 3;")
            else:
                self.img.add_line(20+n*120,self.blank_header+10,20+n*120,self.img.height-10, style=style)

        # horizontal
        for n in xrange(7):
            self.img.add_line(10,self.blank_header+30+n*50,self.img.width-10,self.blank_header+30+n*50, style=style)

        # n+... on each line
        for n in range(7):
            if n == 0: str = "n"
            else: str = "n+{}"

            self.img.add_text(
                str.format(n),
                self.img.width-50,
                self.blank_header+20+n*50,
                style="text-anchor: middle; letter-spacing: 2pt; stroke: black; stroke-opacity: 0.4;")

    def _place_events(self):
        """ Places events on timelines """

        previous_d = self.cal.events[0].dtstart.day
        nb_days = 0
        for e in self.cal:
            if previous_d != e.dtstart.day:
                nb_days += e.dtstart.day - previous_d
                previous_d = e.dtstart.day

            if nb_days < 7:

                start_px = 20+(e.dtstart.hour+self.utc_offset-8)*120+(e.dtstart.minute/5)*10
                end_px = 20+(e.dtend.hour+self.utc_offset-8)*120+(e.dtend.minute/5)*10
                middle_px = start_px + (end_px-start_px)/2
                height = self.blank_header+30+50*nb_days


                self.img.add_line(
                    start_px,
                    height,
                    end_px,
                    height,
                    style = "stroke: {}; stroke-width: 10;".format(self.stroke_color)
                )
                self.img.add_circle(
                    start_px,
                    height,
                    10,
                    style = "fill: {};".format(self.stroke_color)
                )
                self.img.add_circle(
                    end_px,
                    height,
                    10,
                    style = "fill: {};".format(self.stroke_color)
                )
                self.img.add_text(
                    e.summary,
                    middle_px,
                    height-15,
                    style="text-anchor: middle; font-size: 0.8em; letter-spacing: 2pt; stroke: {};".format(self.stroke_color)
                )
                self.img.add_text(
                    e.location,
                    middle_px,
                    height+25,
                    style="text-anchor: middle; font-size: 0.8em; letter-spacing: 2pt; stroke: {};".format(self.stroke_color)
                )
