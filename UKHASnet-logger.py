#!/usr/bin/env python
# -*- coding: utf8 -*-

import arrow
import sys
from logger_lib import addPacket

if __name__ == "__main__":
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
        except Exception as e:
            sys.stderr.write(str(e))
            sys.stderr.write('\n')
            sys.stderr.flush()
            continue


        line = line.strip()
        if line:
            sys.stdout.write(line)
            sys.stdout.write('\n')
            sys.stdout.flush()
            addPacket(line)

