#!/usr/bin/env python
# -*- coding: utf8 -*-

import arrow
import sys
from decimal import Decimal
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey, Table, Text
from sqlalchemy.types import DateTime
try: # wtf Python3
    from functools import reduce
except: pass

engine = sqlalchemy.create_engine('sqlite:///db.sqlite')

Base = declarative_base()

session = sessionmaker()(bind=engine)
#session = Session(bind

packet_hops = Table('packet_hops', Base.metadata,
    Column('node_id', ForeignKey('nodes.id'), primary_key=True),
    Column('packet_id', ForeignKey('packets.id'), primary_key=True)
)


class Packet(Base):
    __tablename__ = "packets"

    id = Column(Integer, Sequence("packet_id_seq"), primary_key=True)
    node_id = Column(Integer, ForeignKey('nodes.id'))
    data = Column(String(256))
    gateway_id = Column(Integer, ForeignKey('nodes.id'))
    received = Column(DateTime(timezone=True))

    node = relationship("Node", back_populates="packets", foreign_keys=[node_id])
    gateway = relationship("Node", back_populates="uploaded_packets", foreign_keys=[gateway_id])
    hops = relationship("Node", secondary=packet_hops, back_populates='routed_packets')

    def __repr__(self):
        return "<Packet(id='{id}', node='{node}', gateway='{gateway}', received='{received}', data='{data}'".format(
            id=self.id,
            node=self.node.name,
            gateway=self.gateway.name,
            received=self.received,
            data=self.data
        )

class Node(Base):
    __tablename__ = 'nodes'

    id = Column(Integer, Sequence("node_id_seq"), primary_key=True)
    name = Column(String(16), unique=True)
    description = Column(String(256))

    routed_packets = relationship('Packet', secondary=packet_hops, back_populates='hops')
    packets = relationship('Packet', foreign_keys=[Packet.node_id])
    uploaded_packets = relationship('Packet', foreign_keys=[Packet.gateway_id])

    def __repr__(self):
        return "<Node(name='{0}', description='{1}')>".format(self.name, self.description)


Base.metadata.create_all(engine)

def getNodeByName(name):
    node = session.query(Node).filter(Node.name == name).one_or_none()
    if node is None:
        node = Node(name=name, description='')
        session.add(node)
        session.commit()
    return node

all = lambda *l: reduce(lambda a, b: a and b, l, True)

class InvalidPacket(Exception): pass

def parsePacket(data):
    assert all(
        data[0].isdigit(),
        data[1].islower(),
        '[' in data,
        data[-1] == ']',
        data[-2] != '['
    ), InvalidPacket("Basic packet structure not matching 3a[n]: '{data}'".format(data=data))

    hops_left = int(data[0])
    sequence = data[1]
    hops = data.split('[')[1].split(']')[0].split(',')

    if ':' in data:
        readings, comment = data[2:].split('[')[0].split(':')
    else:
        readings = data[2:].split('[')[0]
        comment = None
    _spl = []
    for c in readings:
        if c.isupper():
            _spl.append([c, ''])
        else:
            _spl[-1][1] += c

    sensordata = {}
    for k,v in _spl:
        vl = []
        for val in v.split(','):
            try:
                vl.append(Decimal(val))
            except:
                try:
                    vl.append(float(val))
                except:
                    vl.append(val)
        if k == 'Z':
            vl = bool(int(v))
        sensordata[k] = vl

    return dict(
        hops_left = hops_left,
        sequence = sequence,
        node = hops[0],
        hops = hops[1:],
        comment = comment,
        sensordata = sensordata
    )

def addPacket(data):
    if '\t' in data:
        try:
            ts, pdata, gw, res = data.split('\t')
            dt = arrow.get(ts).datetime
            gateway = getNodeByName(gw)
            _hops = [getNodeByName(x) for x in pdata.split('[')[1].split(']')[0].split(',')]
            node = _hops[0]
            hops = _hops[1:]

            packet = Packet(data=pdata, received=dt, node=node, gateway=gateway)
            session.add(packet)
            for hop in hops:
                packet.hops.append(hop)
            session.commit()

        except Exception as e:
            sys.stderr.write(str(e))
            sys.stderr.write('\n')
            sys.stderr.flush()
            return None

