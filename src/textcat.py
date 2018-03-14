#!/usr/bin/python
# -*- coding:utf-8 -*-

from __future__ import division

import sys
import re
import os
import shutil
from datetime import datetime

def content_search(filename):
    fcontent = open(filename, 'r').read()

    s = re.compile(FSTR)
    l = s.findall(content)

    if len(l) > 0:
        s = set(l)
        hits = ""
        for item in s:
            hits += item + "_"
        return hits
    else:
        return None

def main():


    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-i", "--idir", dest="idir", help="Dir of files")
    parser.add_option("-o", "--opath", dest="opath", help="write result to FILENAME")
    parser.add_option("-p", "--pattern", dest="pattern",help="pattern to fetch keywork to classify")
    parser.add_option("-v", "--verbose", action="store_true", dest="version")

    list = os.listdir(srcdir) #列出文件夹下所有的目录与文件

    ofile = open(opath, "r")

    for i in range(0,len(list)):
        srcpath = os.path.join(srcdir, list[i])

        rs = content_fetch(srcpath)

        if rs != None:
            HIT += 1




if __name__ == "__main__":
    main()
