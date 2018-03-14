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

VERSION="LOGSTAT V1.00, 2018/3/9; copyright by ben (ben@fstrings.com)"

CNT   = 0
HIT   = 0
END   = 0
STIME = 0

DUPAT = []

def str_hit(tab, str):
    if str == '':
        str = "None"
    tab[str] = tab.get(str, 0) + 1

def tab_dump(ofile, TAB, TAB_NAME, TOPX):
    UIDX = 0

    print "\n    ................................................................................"
    print >> ofile, "\n    ................................................................................"
    print "    %s: %d items" % (TAB_NAME, len(TAB))
    print >> ofile, "    %s: %d items" % (TAB_NAME, len(TAB))

    UITEMS = sorted(TAB.items(), key=lambda TU: TU[1], reverse=True)
    
    for STR, UNUM in UITEMS:
        print "      %-3d      %-10d      %-80s" % (UIDX, UNUM, STR)
        print >> ofile, "      %-3d      %-10d       %-80s" % (UIDX, UNUM,STR)
            
        UIDX += 1
        if UIDX >= TOPX:
            break

def fdicts_dump(fdicts, ofile, verbose, topx):
    if fdicts == None or len(fdicts) < 0:
        return

    print >> ofile, "\n----------------------------------------------------------------------------------------"
    print "\n ----------------------------------------------------------------------------------------"

    print >> ofile, "FDICTS:"
    print " FDICTS:"
    FCNT = 0

    for fdict in fdicts:
        print >> ofile, " filter [%.3d]: len %d hit %-8d " % (fdict['id'], fdict['len'], fdict['hit']),
        print " filter [%.3d]: len %d hit %-8d " % (fdict['id'], fdict['len'], fdict['hit']),

        if fdict.has_key('url'):
            print >> ofile, "url=%s" % (fdict['url']),
            print ", url=%s" % (fdict['url']),

        if fdict.has_key('ref'):
            print >> ofile, ", ref=%s" % (fdict['ref']),
            print ", ref=%s" % (fdict['ref']),

        if fdict.has_key('ua'):
            print >> ofile, ", ua=%s" % (fdict['ua']),
            print ", ua=%s" % (fdict['ua']),

        print >> ofile, ""
        print ""

        if verbose > 1:
            if len(fdict['du_tab']) > 0:
                tab_dump(ofile, fdict['du_tab'], "DU", topx)

        if verbose > 0:
            if len(fdict['rh_tab']) > 0:
                tab_dump(ofile, fdict['rh_tab'], "RH", topx)

        if verbose > 2:
            if len(fdict['ru_tab']) > 0:
                tab_dump(ofile, fdict['ru_tab'], "RU", topx)


def dump_base_info(ofile):
    global VERSION, STIME
    print >> ofile, "\n ----------------------------------------------------------------------------------------"
    print >> ofile, " %s" % (VERSION)
    print >> ofile, " %s" % (STIME.strftime('%Y-%m-%d %H:%M:%S'))
    print >> ofile, " %s" % (' '.join(sys.argv))

    print "\n ----------------------------------------------------------------------------------------"
    print " %s" % (VERSION)
    print " %s  <->  %s" % (STIME.strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print " %s" % (' '.join(sys.argv))

def stat_dump(ofile):
    global CNT, HIT, STIME

    ntime = datetime.now()

    sspend = (ntime - STIME).seconds

    mspend = (ntime - STIME).microseconds

    spend = sspend * 1000000 + mspend

    if spend < 1:
        spend = 1

    speed = (CNT * 1000000) / spend

    if CNT == 0:
        rate = 0
    else:
        rate = (HIT * 100) / CNT

    secs = spend / 1000000

    print "\r CNT %-10d  HIT %-10d  RATE %.4f%%          %-5.2f seconds  %4d/s; " % (CNT, HIT, rate, secs, speed),
    sys.stdout.flush()

    if ofile != None:
        print >> ofile, " ----------------------------------------------------------------------------------------"
        print >> ofile, " CNT %-10d  HIT %-10d  RATE %.4f%%          %-5.2f seconds  %4d/s; " % (CNT, HIT, rate, secs, speed)

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

def str_compare(pstr, vstr):
    #print  "pstr=%s, vstr=%s" %(pstr, vstr)
    result = re.search(pstr, vstr)

    if result:
        return True

    return False

def log_filter(ifile, ofile, fdicts, options):
    global CNT, HIT, END
    #for LINE in ifile.readlines():

    #print "LOG=%s" %(options.log)
    #print "fdicts=", fdicts

    for LINE in ifile:
        LINE = LINE.strip('\n')
        FIELD = LINE.split('|')

        if len(FIELD) < 5:
            continue

        TIME = FIELD[0]
        SIP  = FIELD[3]
        DIP  = FIELD[4]
        DUF  = FIELD[9]
        RUF  = FIELD[11]
        UAF  = FIELD[10]
        DUF_HOST = ''
        RUF_HOST = ''

        DAY = TIME.split(' ')[0]

        if RUF == None or len(RUF) <= 0:
            RUF = "None"


        CNT += 1

        if fdicts == None:
            continue

        #print "options.date=%s, DAY=%s" %(options.date, DAY)
        if options.date != None:
            if str_compare(options.date, DAY) != True:
                continue

        for fdict in fdicts:
            FHIT = 0
  
            if fdict.has_key('url'):
                if str_compare(fdict['url'], DUF) == True:
                    FHIT += 1
                else:
                    continue

            if fdict.has_key('ref'):
                if str_compare(fdict['ref'], RUF) == True:
                    FHIT += 1
                else:
                    continue

            if fdict.has_key('ua'):
                if str_compare(fdict['ua'], UAF) == True:
                    FHIT += 1
                else:
                    continue
                
            #print "FHIT=%d fdict['len']=%d" %(FHIT, fdict['len'])
            if FHIT == fdict['len']:
                fdict['hit'] += 1

                if options.log:
                    print >> ofile, LINE

                HIT += 1

                str_hit(fdict['du_tab'], DUF)

                try:
                    u = urlparse(RUF)
                    u_host = u.netloc
                except:
                    u_host = "ERROR"

                str_hit(fdict['ru_tab'], RUF)
                str_hit(fdict['rh_tab'], u_host)

                break

    END = 1

def fstr_parser(fstr):
    fdict = {}

    if fstr == None:
        return None

    pairs = fstr.split(",")

    for pair in pairs:
        ep = pair.find('=')

        if ep < 0:
            return None
        key = pair[0:ep]
        val = pair[ep+1:]
        #print "key=%s, val=%s" % (key, val)

        fdict[key] = val

    return fdict



def logs_filter(ofile, fdicts, options):

    ipaths = options.ipath.split(",")

    for ipath in ipaths:
        ifile = open(ipath, "r")

        log_filter(ifile, ofile, fdicts, options)

        ifile.close()


def main():
    global END
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-I", "--ipath", type="string", dest="ipath", help="read log from FILENAME")
    parser.add_option("-O", "--opath", type="string", dest="opath", help="write result to FILENAME")
    parser.add_option("-F", "--fpath", type="string", dest="fpath", help="filter list from FILENAME")
    parser.add_option("-D", "--date", type="string", dest="date", default=None, help="filter date")
    parser.add_option("-d", "--dump", type="int", dest="dump", default=1, help="dump level")
    parser.add_option("-t", "--topx", type="int", dest="topx", default=20, help="dump top X")
    parser.add_option("-v", "--verbose", action="store_true", dest="version")
    parser.add_option("-l", "--log", action="store_true", dest="log")

    (options, args) = parser.parse_args()

    #print "options", optionsu

    if options.version:
        print "%s." % VERSION
        exit(1)

    if options.ipath == None or options.opath == None:
        parser.error("Invaild param")

    ofile = open(options.opath, "w")

    FIDX = 0
    fdicts = []
    if options.fpath != None:
        ffile = open(options.fpath, "r")

        for LINE in ffile:
            LINE = LINE.strip('\n')
            if len(LINE) <= 0:
                continue

            if LINE[0] == '#':
                continue


            fdict = fstr_parser(LINE)
            
            flen = len(fdict)

            if flen == 0:
                continue

            fdict['len'] = flen
            fdict['id'] = FIDX
            fdict['hit'] = 0
            fdict['du_tab'] = {}
            fdict['ru_tab'] = {}
            fdict['rh_tab'] = {}

            fdicts.append(fdict)
            FIDX += 1

        ffile.close()

        
    
    t = threading.Thread(target=logs_filter, args=(ofile, fdicts, options, ))
    t.start()
    
    stat_thread(0.25, ofile)

    time.sleep(3)
    fdicts_dump(fdicts, ofile, 0, 0)
    fdicts_dump(fdicts, ofile, options.dump, options.topx)
    dump_base_info(ofile)

    ofile.close()

if __name__ == "__main__":
    main()

# End of file
# Test command
# python logstat_V1.00.py -I ../log/naga.log20180306  -O ../result/naga.log20180306_result_1.log -F zimeiti.rules
# python logstat_V1.00.py -I ../log/naga.log20180306  -O ../result/naga.log20180306_toutiao.log -F toutiao.rules -d 3
# python logstat_V1.00.py -I ../log/naga.log20180306  -O ../result/naga.log20180306_test.log -F test.rules -d 3