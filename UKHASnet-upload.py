#!/usr/bin/env python
import sys
import requests

NAME = "OS0"

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
         })
         return res.json()

    return False

if __name__ == "__main__":
    while True:
        line = sys.stdin.readline()
        if not line:
            break

        line = line.strip()
        if line:
            try:
                print(line)
                print(upload(line))
            except Exception as e:
                print(e)


