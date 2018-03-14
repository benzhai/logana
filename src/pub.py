#!/usr/bin/python

from __future__ import division

import sys
import re
import threading
import time
from optparse import OptionParser
import shutil
from datetime import datetime
from urlparse import *
import urllib

VERSION = "LOGANA V1.03, 2017/12/01; copyright by less (less@beescast.com)"

CNT = 0
HIT = 0
ERR = 0
END = 0
STM = 0


def stat_dump(ofile):
    global CNT, HIT, STM

    ntime = datetime.now()

    sspend = (ntime - STM).seconds

    mspend = (ntime - STM).microseconds

    spend = sspend * 1000000 + mspend

    # print "sspend=%d , mspend=%d" % (sspend, mspend)
    # print "spend=%d" %(spend)

    if spend < 1:
        spend = 1

    speed = (CNT * 1000000) / spend

    if CNT == 0:
        rate = 0
    else:
        rate = (HIT * 100) / CNT

    secs = spend / 1000000

    print "\r CNT %-10d  HIT %-10d  ERR %-10d  RATE %.4f%%          %-5.2f seconds  %4d/s; " % (CNT, HIT, ERR, rate, secs, speed),
    sys.stdout.flush()

    if ofile != None:
        print >> ofile, " ----------------------------------------------------------------------------------------"
        print >> ofile, " CNT %-10d  HIT %-10d  ERR %-10d RATE %.4f%%          %-5.2f seconds  %4d/s; " % (
        CNT, HIT, ERR, rate, secs, speed)


def stat_thread(period, ofile):
    global END, STM
    stop = 0
    print "\n"

    STM = datetime.now()
    time.sleep(period)
    while stop == 0:
        stat_dump(None)

        if END == 0:
            time.sleep(period)
        else:
            stat_dump(ofile)
            stop = 1


def dump_base_info(ofile):
    global VERSION, STM
    print >> ofile, "\n ----------------------------------------------------------------------------------------"
    print >> ofile, " %s" % (VERSION)
    print >> ofile, " %s" % (STM.strftime('%Y-%m-%d %H:%M:%S'))
    print >> ofile, " %s" % (' '.join(sys.argv))

    print "\n ----------------------------------------------------------------------------------------"
    print " %s" % (VERSION)
    print " %s  <->  %s" % (STM.strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print " %s" % (' '.join(sys.argv))


# End of file