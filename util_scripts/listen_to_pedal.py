#!/usr/bin/python
#
# Script to listen for messages from the Zoom pedals
# (c) Simon Wood, 13 May 2020
#

import zoomzt2

import sys
import hexdump
from argparse import ArgumentParser

parser = ArgumentParser(prog="listen_to_pedal")

parser.add_argument("-p", "--pc",
    help="switch into PC mode",
    action="store_true", dest="pc")
parser.add_argument("-t", "--tuner",
    help="switch into tuner mode",
    action="store_true", dest="tuner")
parser.add_argument("-M", "--midiskip",
    type=int, default=0, dest="midiskip",
    help="Skip devices when connecting, ie when you have multiple pedals")

options = parser.parse_args()

pedal = zoomzt2.zoomzt2()
if not pedal.connect(options.midiskip):
    sys.exit("Unable to find Pedal")
else:
    print("Connected")
    pedal.editor_on()

    if options.pc:
            pedal.pcmode_on()

    if options.tuner:
            pedal.tuner_on_off()

while(True):
    msg = pedal.inport.receive()
    if hasattr(msg, 'data'):
        print(hexdump.hexdump(bytes(msg.data)))

