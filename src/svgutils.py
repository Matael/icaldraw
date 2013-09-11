#! /usr/bin/env python
# -*- coding:utf8 -*-
#
# svgutils.py
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
Tools to output SVG from python
"""

class SVGwriter:


    def __init__(self, w, h, title="", desc=""):
        """
        We do not remember title and desc 'cause we won't need them anymore after header

        """
        self.width = w
        self.height = h

        # output buffer
        self.lines = []

        self._out([
            '<?xml version="1.0" encoding="utf-8"?>',
            '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{0}" height="{1}">'.format(w, h),
            '<title>{0}</title>'.format(title),
            '<desc>{0}</desc>'.format(desc)
        ])

    def _out(self, l):
        """ Append a line or a list of lines to the output buffer """

        if type(l) == list:
            for i in l: self._out(i)
        else:
            self.lines.append(l)

    def save(self, filename):
        """ Save self.lines to filename """

        self._out("</svg>")
        with open(filename, "w") as f:
            for l in self.lines:
                f.write(l)
                f.write('\n')

    def add_rect(self, w, h, x, y, style=""):
        """ Rectangle """

        if style == "":
            self._out('<rect width="{0}" height="{1}" x="{2}" y="{3}" />'.format(w, h, x, y))
        else:
            self._out('<rect width="{0}" height="{1}" x="{2}" y="{3}" style="{4}" />'.format(w, h, x, y, style))

    def add_circle(self, x, y, r, style=""):
        """ Circle """

        if style == "":
            self._out('<circle cx="{0}" cy="{1}" r="{2}" />'.format(x, y, r))
        else:
            self._out('<circle cx="{0}" cy="{1}" r="{2}" style="{3}" />'.format(x, y, r, style))

    def add_line(self, x1, y1, x2, y2, style=""):
        """ Line """

        if style == "":
            self._out('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" />'.format(x1, y1, x2, y2))
        else:
            self._out('<line x1="{0}" y1="{1}" x2="{2}" y2="{3}" style="{4}" />'.format(x1, y1, x2, y2, style))

    def add_text(self, text, x, y, style=""):
        """ Text """

        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        if style == "":
            self._out('<text x="{0}" y="{1}">{2}</text>'.format(x, y, text))

        else:
            self._out('<text x="{0}" y="{1}" style="{2}">{3}</text>'.format(x, y, style, text))
