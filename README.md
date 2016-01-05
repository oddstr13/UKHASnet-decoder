Decode UKHASnet packets with a RTL SDR dongle
==================

This is a simple UKHASnet decoder for RTL SDR dongles. Other similar decoder might already exist but this was a way for me to understand the protocol and get used to it.

You need to have a working dongle and rtl_fm running.

Before starting
-------
`rtl_test`

`rtl_test -p 10` to get ppm error or use kalibrate but it did not work for me on OSX.

Get started
-------
`make`

`./UKHASnet-decoder -h`

`rtl_fm -f 869500000 -s 64k -g 48 -p 38 -r 8000 | ./UKHASnet-decoder.exe -qs 8000 | ./UKHASnet-upload.py`

TODO (see code for details)
-------
- Synchronisation:
	- Add tolerance bit option (and possibly use the preamble for more robustness)
	- Support inverted bits
- Confirm that RFM CRC computation is weird (has someone had some experience with that ?)
- Find better threshold formula to account for packet with no sufficient bit transitions
