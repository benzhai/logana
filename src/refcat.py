#!/usr/bin/python

#!/usr/bin/python

from __future__ import division

import sys
import re
import threading
import time
from optparse import OptionParser
import shutil
from datetime import datetime

VERSION="LOGANA V1.01, 2017/10/24; copyright by less (less@beescast.com)"

CNT = 0
HIT = 0
END = 0
STIME = 0

def stat_dump(ofile):
    global CNT, HIT, STIME

    ntime = datetime.now()

    sspend = (ntime - STIME).seconds

    mspend = (ntime - STIME).microseconds

    spend = sspend * 1000000 + mspend

    #print "sspend=%d , mspend=%d" % (sspend, mspend)
    #print "spend=%d" %(spend)

    if spend < 1:
        spend = 1

    speed = (CNT * 1000000) / spend

    if CNT == 0:
        rate = 0
    else:
        rate = (HIT * 100) / CNT

    secs = spend / 1000000

    print "\r CNT %-10d  HIT %-10d  RATE %.4f%%  %-5.2f seconds  %4d/s; " % (CNT, HIT, rate, secs, speed),
    sys.stdout.flush()

    if ofile != None:
        print >> ofile, "----------------------------------------------------------------------------------------"
        print >> ofile, "CNT %-10d  HIT %-10d  RATE %.4f%%  %-5.2f seconds  %4d/s; " % (CNT, HIT, rate, secs, speed)

def stat_thread(period, ofile):
    global END, STIME
    stop = 0
    print "\n"

    STIME = datetime.now()
    time.sleep(period)
    while stop == 0:
        stat_dump(None)

        if END == 0:
            time.sleep(period)
        else:
            stat_dump(ofile)
            stop = 1

def field_compare(pstr, vstr):
    pattern = re.compile(pstr)
    match = pattern.match(vstr)

    if match:
        return True

    return False


def log_filter(ifile, ofile, kdict):
    global CNT, HIT, END
    for LINE in ifile.readlines():
        LINE = LINE.strip('\n')
        FIELD = LINE.split('|')

        if len(FIELD) < 5:
            continue

        SIF = FIELD[0]
        DIF = FIELD[1]
        OUF = FIELD[2]
        RUF = FIELD[3]
        UAF = FIELD[4]

        SIV = SIF.split(' ')

        TIME = SIV[0]
        SIP  = SIV[4]

        CNT += 1

        if kdict.has_key('ou'):
            if field_compare(kdict['ou'], OUF) == False:
                continue

        if kdict.has_key('ru'):
            if field_compare(kdict['ru'], RUF) == False:
                continue

        if kdict.has_key('ua'):
            if field_compare(kdict['ua'], UAF) == False:
                continue

        print >> ofile, LINE
        HIT += 1

    END = 1

def kstr_parser(kstr):
    kdict = {}

    pairs = kstr.split(",")

    for pair in pairs:
        ep = pair.find('=')

        if ep < 0:
            return None
        key = pair[0:ep]
        val = pair[ep+1:]
        #print "key=%s, val=%s" % (key, val)

        kdict[key] = val


    return kdict

def main():
    global END
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-i", "--ipath", dest="ipath", help="read log from FILENAME")
    parser.add_option("-o", "--opath", dest="opath", help="write result to FILENAME")
    parser.add_option("-k", "--key", dest="kstr",help="match key & value")
    parser.add_option("-v", "--verbose", action="store_true", dest="version")

    (options, args) = parser.parse_args()

    #print "options", options

    if options.version:
        print "%s." % VERSION
        exit(1)

    if options.ipath == None or options.opath == None or options.kstr == None:
        parser.error("Invaild param")

    ipath = options.ipath

    opath = options.opath

    kstr  = options.kstr

    kdict = kstr_parser(kstr)

    if kdict == None:
        parser.error("Invaild key string")

    ifile = open(ipath, "r")

    ofile = open(opath, "w")

    t = threading.Thread(target=log_filter, args=(ifile, ofile, kdict, ))
    t.start()

    stat_thread(0.25, ofile)

    ifile.close()
    ofile.close()

if __name__ == "__main__":
    main()