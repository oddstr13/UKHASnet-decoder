#!/usr/bin/env python
# -*- coding: utf8 -*-
# 
# Dependencies:
#  * requests
#  * arrow

import sys
import requests
import arrow

NAME = "OS0"
LOCATION = "62.68,10.03,620"

UKHASNET_API_UPLOAD = "https://ukhas.net/api/upload"

def isValid(data):
    if len(data) <= 4:
        return False
    if data[0] not in "0123456789":
        return False
    if data[1] not in "abcdefghijklmnopqrstuvwxyz":
        return False
    if '[' not in data:
        return False
    if not data.endswith(']'):
        return False
    return True

def upload(data):
    if isValid(data):
         res = requests.post(UKHASNET_API_UPLOAD, {
             'origin': NAME,
             'data': data,
         }, timeout=15)
         return res.json()

    return False

def tryUpload(line):
    try:
        sys.stdout.write(arrow.now().format("YYYY-MM-DD HH:mm:ss.SSS"))
        sys.stdout.write('\t')
        sys.stdout.write(line)
        sys.stdout.write(' ')
        sys.stdout.write(str(upload(line)))
        sys.stdout.write('\n')
    except Exception as e:
        print(e)

if __name__ == "__main__":

    tryUpload("0aV-1L{location}:rtl-sdr listen-only node started[{name}]".format(name=NAME, location=LOCATION))

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
        except Exception as e:
            print(e)
            continue


        line = line.strip()
        if line:
            tryUpload(line)


