#! /usr/bin/env python
# -*- coding:utf8 -*-
#
# l2spi_tc1.py
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
EDT for L3 SPI 2013 TC1/EEO2 at Maine University, Le Mans, France.
"""

from icaldraw import IcalDraw

def main():

    URL = "http://edt.univ-lemans.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources=1700,1676,1651&projectId=1&calType=ical&nbWeeks=1"


    id = IcalDraw(URL)
    id.draw()
    id.save("edt_l3spi_tc1_eeo2.svg")

if __name__=='__main__':
    main()
