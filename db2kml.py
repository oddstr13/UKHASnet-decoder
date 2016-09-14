#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import arrow
from logger_lib import *


import re
from datetime import timedelta

GROUPDELTA = timedelta(minutes=5)

_delta_r = re.compile(r'((?P<weeks>\d+?)w)?((?P<days>\d+?)d)?((?P<hours>\d+?)hr?)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')
def parse_td(time_str):
    # http://stackoverflow.com/a/4628148/1035647
    parts = _delta_r.match(time_str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for (name, param) in parts.items():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)

def write_kml(packets, fh=sys.stdout):
    fh.write("""<kml xmlns="http://www.opengis.net/kml/2.2"
 xmlns:gx="http://www.google.com/kml/ext/2.2">
<Document>
<name>{node}, {start} - {end}</name>
""".format(node=packets[0].node.name, start=packets[0].received, end=packets[-1].received))

    entrypoints = {}
    for packet in packets:
        entrypoint = packet.hops[0] if packet.hops else packet.gateway
        if entrypoint not in entrypoints:
            entrypoints[entrypoint] = []

        if (not entrypoints[entrypoint]) or (packet.received - entrypoints[entrypoint][-1][-1].received > GROUPDELTA):
            entrypoints[entrypoint].append([packet])
            continue
        entrypoints[entrypoint][-1].append(packet)
    pnum = 0
    avglat = Decimal(0)
    avglon = Decimal(0)

    for entrypoint in entrypoints:
      packetgroups = entrypoints[entrypoint]
      fh.write("""<Folder>
  <name>{entrypoint}</name>

""".format(entrypoint=entrypoint.name))
      for group in packetgroups:
        fh.write("""<Folder>
  <name>{start} - {end}</name>

""".format(node=group[0].node.name, start=group[0].received, end=group[-1].received))
        for packet in group:
            parsed = parsePacket(packet.data)
            if parsed['sensordata'].get('L', None) is None or len(parsed['sensordata'].get('L',[])) < 2:
                continue # Skip packets without location
            latitude = parsed['sensordata'].get('L')[0]
            longitude = parsed['sensordata'].get('L')[1]
            try:
                altitude = parsed['sensordata'].get('L')[2]
            except:
                altitude = 0

            pnum += 1
            avglat += latitude
            avglon += longitude


            fh.write("""<Placemark id="{id}">
  <name>{rssi}</name>
  <visibility>1</visibility>
  <description>{node}: {time}
RSSI: <em>{rssi}</em></description>
  <TimeStamp><when>{time}</when></TimeStamp>
  <StyleSelector>...</StyleSelector>
  <Point>
    <coordinates>{longitude},{latitude},{altitude}</coordinates>
  </Point>
  <ListStyle>
    <bgColor>ff{color:02x}{color:02x}ff</bgColor>
  </ListStyle>
</Placemark>
""".format(
    id=packet.id,
    node=packet.node.name,
    gateway=packet.gateway.name,
    rssi=parsed['sensordata'].get('R', [''])[0],
    time=packet.received,
    longitude=longitude,
    latitude=latitude,
    altitude=altitude,
    color=int(0xff-parsed['sensordata'].get('R', [0])[0])
))
        fh.write("""</Folder>
""")
      fh.write("""</Folder>
""")

    fh.write("""<LookAt>
  <heading>0</heading>
  <tilt>0</tilt>
  <range>5000</range>
  <longitude>{longitude}</longitude>
  <latitude>{latitude}</latitude>
  <altitude>0</altitude>
  <altitudeMode>relativeToGround</altitudeMode>
</LookAt>
</Document>
</kml>
""".format(
    longitude=avglon/pnum,
    latitude=avglat/pnum
))

def main(name, delta=None):
    node = session.query(Node).filter(Node.name == name).one_or_none()

    if delta is not None:
        delta = parse_td(delta)
        start = arrow.now() - delta

        packets = session.query(Packet).filter(Packet.node == node, Packet.received > start.datetime).order_by(Packet.received).all()
    else:
        packets = session.query(Packet).filter(Packet.node == node).order_by(Packet.received).all()
#    print(packets)
    write_kml(packets)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        print("""Usage: {0} <node> [delta]
    node: Node name, case sensitive. Required.
    time: How far back? 1w2d5h20m15s. Optional.
""".format(sys.argv[0]))
