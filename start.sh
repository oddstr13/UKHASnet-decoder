#!/usr/bin/bash

cd $(dirname $0)

rtl_fm -f 869500000 -s 64k -g 48 -p 38 -r 8000 \
| ./UKHASnet-decoder -qs 8000 \
| ./UKHASnet-upload.py \
| ./UKHASnet-logger.py \
2>> ./error.log
