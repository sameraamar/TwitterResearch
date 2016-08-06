# -*- coding: utf-8 -*-
"""
Created on Sat Jun 18 07:17:41 2016

@author: SAMERA
"""

import time

SLEEP_INTERVAL = 1.0

def follow(fin):
    "Iterate through lines and then tail for further lines."
    while True:
        line = fin.readline()
        if line:
            yield line
        else:
            tail(fin)

def tail(fin):
    "Listen for new lines added to file."
    while True:
        where = fin.tell()
        line = fin.readline()
        if not line:
            time.sleep(SLEEP_INTERVAL)
            fin.seek(where)
        else:
            yield line

def main():

    with open('tweets.json', 'r') as fin:
        for line in follow(fin):
            print (line.strip())

if __name__ == '__main__':
    main()