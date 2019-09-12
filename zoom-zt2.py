#!/usr/bin/python
#
# Script decode/encode ZT2 file from Zoom F/W
# (c) Simon Wood, 11 July 2019
#

from construct import *

#--------------------------------------------------
# Define ZT2/ZD2 file format using Construct (v2.9)
# requires:
# https://github.com/construct/construct

Header = Struct(
    Const(b"\x3e\x3e\x3e\x00"),
    Padding(22),
    "name" / PaddedString(12, "ascii"),
    Padding(6),
    Const(b"\x01"),
    Padding(7),
    Const(b"\x3c\x3c\x3c\x00"),
    Padding(22),
)

Effect = Struct(
    "effect" / PaddedString(12, "ascii"),
    Const(b"\x00"),
    "version" / PaddedString(4, "ascii"),
    Const(b"\x00"),
    "installed" / Default(Byte, 1),     # "Guitar Lab additional effects" = 0
    "id" / Int16ul,
    "unknown" / Byte,                   # seems to be connected with ID 
    "group" / Byte,
    Check(this.group == this._.group),
    Const(b"\x00\x00\x00"),
)

Group = Struct(
    Const(b"\x3e\x3e\x3e\x00"),
    "group" / Byte,
    "groupname" / Enum(Computed(this.group),
        DYNAMICS = 1,
	FILTER = 2,
	DRIVE = 3,
	AMP = 4,
	CABINET = 5,
	MODULATION = 6,
	SFX = 7,
	DELAY = 8,
	REVERB = 9,
	PEDAL = 11,
	ACOUSTIC = 29,
    ),
    Padding(21),
    "effects" / GreedyRange(Effect),
    Const(b"\x3c\x3c\x3c\x00"),
    "group_end" / Rebuild(Byte, this.group),
    Check(this.group_end == this.group),
    Padding(21),
)

ZT2 = Padded(8502, Sequence(
    "header" / Header,
    "groups" / GreedyRange(Group),
))

ZD2 = Struct(
    Const(b"\x5a\x44\x4c\x46\x78"),
    Padding(83),
    Const(b"\x01"),
    "version" / PaddedString(4, "ascii"),
    Const(b"\x00\x00"),
    "group" / Byte,
    "groupname" / Enum(Computed(this.group),
        DYNAMICS = 1,
	FILTER = 2,
	DRIVE = 3,
	AMP = 4,
	CABINET = 5,
	MODULATION = 6,
	SFX = 7,
	DELAY = 8,
	REVERB = 9,
	PEDAL = 11,
	ACOUSTIC = 29,
    ),
    "type" / Int32ul,
    "name" / CString("ascii"),
)

#--------------------------------------------------

import sys
import os
from optparse import OptionParser
import mido
import binascii
from time import sleep

inport = None
outport = None
data = bytearray(b"")

if sys.platform == 'win32':
    mido.set_backend('mido.backends.rtmidi_python')
    midiname = b"ZOOM G"
else:
    midiname = "ZOOM G"

usage = "usage: %prog [options] FILENAME"
parser = OptionParser(usage)
parser.add_option("-d", "--dump",
    help="dump configuration to text",
    action="store_true", dest="dump")
parser.add_option("-s", "--summary",
    help="summarized configuration in human readable form",
    action="store_true", dest="summary")
parser.add_option("-b", "--build",
    help="output commands required to build this FLTS_SEQ",
    dest="build")

parser.add_option("-A", "--add",
    help="add an effect to group ADD", dest="add")
parser.add_option("-n", "--name",
    help="effect name (use with --add)", dest="name")
parser.add_option("-v", "--ver",
    help="effect version (use with --add)", dest="ver")
parser.add_option("-i", "--id",
    help="effect id (use with --add)", dest="id")
parser.add_option("-u", "--unknown",
    help="effect unknown (use with --add)", dest="unknown")

parser.add_option("-t", "--toggle",
    help="toggle install/uninstall state of effect NAME in FLST_SEQ", dest="toggle")
parser.add_option("-D", "--delete",
    help="delete last effect in group DEL", dest="delete")

parser.add_option("-w", "--write", dest="write",
    help="write config back to same file", action="store_true")

# interaction with attached device
parser.add_option("-R", "--receive",
    help="Receive FLST_SEQ from attached device",
    action="store_true", dest="receive")
parser.add_option("-S", "--send",
    help="Send FLST_SEQ to attached device",
    action="store_true", dest="send")
parser.add_option("-I", "--install",
    help="Install effect binary to attached device", dest="install")
parser.add_option("-U", "--uninstall",
    help="Remove effect binary from attached device", dest="uninstall")

(options, args) = parser.parse_args()
if len(args) != 1:
    parser.error("FILE not specified")

if options.install and options.uninstall:
    sys.exit("Cannot use 'install' and 'uninstall' at same tiime")

if options.receive or options.send or options.install:
    for port in mido.get_input_names():
        if port[:len(midiname)]==midiname:
            inport = mido.open_input(port)
            #print("Using Input:", port)
            break
    for port in mido.get_output_names():
        if port[:len(midiname)]==midiname:
            outport = mido.open_output(port)
            #print("Using Output:", port)
            break

    if inport == None or outport == None:
        sys.exit("Unable to find Pedal")

    # Enable PC Mode
    msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x52])
    outport.send(msg); sleep(0); msg = inport.receive()

if options.receive:
    # Set up read
    msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x25, 0x00, 0x00, 0x46, 0x4c, 0x53, 0x54, 0x5f, 0x53, 0x45, 0x51, 0x2e, 0x5a, 0x54, 0x32, 0x00, 0x05])
    outport.send(msg); sleep(0); msg = inport.receive()

    msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x05, 0x00])
    outport.send(msg); sleep(0); msg = inport.receive()
    
    msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x27])
    outport.send(msg); sleep(0); msg = inport.receive()
    
    msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x20, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46, 0x4c, 0x53, 0x54, 0x5f, 0x53, 0x45, 0x51, 0x2e, 0x5a, 0x54, 0x32, 0x00])
    outport.send(msg); sleep(0); msg = inport.receive()
    
    # Read parts 1 through 17
    for part in range(17):
        msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x05, 0x00])
        outport.send(msg); sleep(0); msg = inport.receive()

        msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x22, 0x14, 0x2f, 0x60, 0x00, 0x0c, 0x00, 0x04, 0x00, 0x00, 0x00])
        outport.send(msg); sleep(0); msg = inport.receive()

        msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x05, 0x00])
        outport.send(msg); sleep(0); msg = inport.receive()

        #decode received data
        packet = msg.data
        block = bytearray(b"")
        offset = 10
        loop = -1 # start by reading hibits value
        hibits = 0

        length = int(packet[offset-1]) * 128 + int(packet[offset-2])
        for byte in range(length + int(length/7) + 1):
            if loop !=-1:
                if (hibits & (2**loop)):
                    block.append(128 + packet[offset+byte])
                else:
                    block.append(packet[offset+byte])
                loop = loop - 1
            else:
                hibits = packet[offset+byte]
                # do we need to acount for short sets (at end of block block)?
                loop = 6

        # confirm checksum (last 5 bytes of packet)
        checksum = packet[-5] + (packet[-4] << 7) + (packet[-3] << 14) \
                + (packet[-2] << 21) + ((packet[-1] & 0x0F) << 28) 
        if (checksum ^ 0xFFFFFFFF) == binascii.crc32(block):
            data = data + block
        else:
            print("Checksum error", hex(checksum))
else:
    # Read data from file
    infile = open(args[0], "rb")
    if not infile and not options.test:
        sys.exit("Unable to open config FILE for reading")
    else:
        data = infile.read()
        infile.close()

if options.add and options.name and options.ver and options.id and options.unknown:
    config = ZT2.parse(data)

    group = config[1][int(options.add)-1]
    number = group['group']
    effects = group['effects']

    print("Group %s:" % number)
    for effect in effects:
        print("    %s" % effect["effect"])

    # create record for new effect
    print("Add:%s" % options.name)
    new = dict(effect=options.name, version=options.ver, id=int(options.id), \
            unknown=int(options.unknown), group=number)

    effects.append(new)
    data = ZT2.build(config)

if options.delete:
    config = ZT2.parse(data)

    group = config[1][int(options.delete)-1]
    number = group['group']
    effects = group['effects']

    print("Group %s:" % number)
    last = len(effects)-1
    for effect in effects[:-1]:
        print("    %s" % effect["effect"])

    print("Del:%s" % effects[last]['effect'])

    del effects[last]
    data = ZT2.build(config)

if options.dump and data:
    config = ZT2.parse(data)
    print(config)

if options.toggle and data:
    config = ZT2.parse(data)
    groupnum=0

    for group in config[1]:
        for effect in dict(group)["effects"]:
            if dict(effect)["effect"] == options.toggle:
                if dict(effect)["installed"] == 1:
                    config[1][groupnum]["effects"][0]["installed"] = 0
                else:
                    config[1][groupnum]["effects"][0]["installed"] = 1

        groupnum = groupnum + 1
    data = ZT2.build(config)

if options.summary and data:
    config = ZT2.parse(data)
    for group in config[1]:
        print("Group", dict(group)["group"], ":", dict(group)["groupname"])

        for effect in dict(group)["effects"]:
            print("   ", dict(effect)["effect"], "(ver=", dict(effect)["version"], \
                "), group=", dict(effect)["group"], ", id=", dict(effect)["id"], \
                "unknown=", dict(effect)["unknown"], \
                ", installed=", dict(effect)["installed"])

if options.build and data:
    config = ZT2.parse(data)
    for group in config[1]:
        for effect in dict(group)["effects"]:
            print("python3 zoom-zt2.py -A ", dict(effect)["group"], \
                "-u", dict(effect)["unknown"], "-i", dict(effect)["id"], \
                "-n", dict(effect)["effect"], "-v", dict(effect)["version"], \
                "-w", options.build)

if options.write and data:
   outfile = open(args[0], "wb")
   if not outfile:
       sys.exit("Unable to open FILE for writing")

   outfile.write(data)
   outfile.close()

binfile = None
if options.install:
    # Read data from file
    binfile = open(options.install, "rb")
    if infile:
        bindata = binfile.read()
        binfile.close()

if options.install or options.uninstall:
    # I "f0 52 00 6e 60 25 00 00 42 4c 41 43 4b 4f 50 54 2e 5a 44 32 00 f7"
    # U "f0 52 00 6e 60 25 00 00 42 4c 41 43 4b 4f 50 54 2e 5a 44 32 00 f7"
    packet = bytearray(b"\x52\x00\x6e\x60\x25\x00\x00")
    if options.install:
        head, tail = os.path.split(options.install)
    else:
        head, tail = os.path.split(options.uninstall)

    for x in range(len(tail)):
        packet.append(ord(tail[x]))
    packet.append(0x00)
    msg = mido.Message("sysex", data = packet)
    outport.send(msg); sleep(0); msg = inport.receive()

    # U "f0 52 00 6e 60 05 00 f7"

    # I/U "f0 52 00 6e 60 27 f7"
    msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x27])
    outport.send(msg); sleep(0); msg = inport.receive()

    # I "f0 52 00 6e 60 20 01 00 00 00 00 00 00 00 00 00 42 4c 41 43 4b 4f 50 54 2e 5a 44 32 00 f7"
    # U "f0 52 00 6e 60 24 42 4c 41 43 4b 4f 50 54 2e 5a 44 32 00 f7 00"
    if options.install:
        packet = bytearray(b"\x52\x00\x6e\x60\x20\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00")
    else:
        packet = bytearray(b"\x52\x00\x6e\x60\x24")
    for x in range(len(tail)):
        packet.append(ord(tail[x]))
    packet.append(0x00)
    msg = mido.Message("sysex", data = packet)
    outport.send(msg); sleep(0); msg = inport.receive()

    # getting hung during uninstall....
    if options.install:
        # "f0 52 00 6e 60 05 00 f7"
        msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x05, 0x00])
        outport.send(msg); sleep(0); msg = inport.receive()

    # data sent same way as FLST
    while options.install and len(bindata):
        # header (without 0xF0)
        packet = bytearray(b"\x52\x00\x6e\x60\x23\x40\x00\x00\x00\x00")

        if len(bindata) > 512:
            length = 512
        else:
            length = len(bindata)
        packet.append(length & 0x7f)
        packet.append((length >> 7) & 0x7f)
        packet = packet + bytearray(b"\x00\x00\x00")

        # Encode/Pack high bits
        encode = bytearray(b"\x00")
        for z in range(length):
            # into [0] bits 7..0
            encode[0] = encode[0] + ((bindata[z] & 0x80) >> len(encode))
            encode.append(bindata[z] & 0x7f)

            if len(encode) > 7:
                #print(binascii.hexlify(encode))
                packet = packet + encode
                encode = bytearray(b"\x00")

        # don't forget to add last few bytes
        if len(encode) > 1:
            packet = packet + encode

        # Compute CRC32
        crc = binascii.crc32(bindata[:length]) ^ 0xFFFFFFFF
        packet.append(crc & 0x7f)
        packet.append((crc >> 7) & 0x7f)
        packet.append((crc >> 14) & 0x7f)
        packet.append((crc >> 21) & 0x7f)
        packet.append((crc >> 28) & 0x0f)

        bindata = bindata[length:]
        #print(hex(len(packet)), binascii.hexlify(packet))

        msg = mido.Message("sysex", data = packet)
        outport.send(msg); sleep(0); msg = inport.receive()
        #print(msg)

        msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x05, 0x00])
        outport.send(msg); sleep(0); msg = inport.receive()
        #print(msg)
    

if options.send:
    msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x25, 0x00, 0x00, 0x46, 0x4c, 0x53, 0x54, 0x5f, 0x53, 0x45, 0x51, 0x2e, 0x5a, 0x54, 0x32, 0x00])
    outport.send(msg); sleep(0); msg = inport.receive()
    #print(msg)

    msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x05, 0x00])
    outport.send(msg); sleep(0); msg = inport.receive()
    #print(msg)

    msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x27])
    outport.send(msg); sleep(0); msg = inport.receive()
    #print(msg)

    msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x24, 0x46, 0x4c, 0x53, 0x54, 0x5f, 0x53, 0x45, 0x51, 0x2e, 0x5a, 0x54, 0x32, 0x00])
    outport.send(msg); sleep(0); msg = inport.receive()
    #print(msg)

    msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x20, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46, 0x4c, 0x53, 0x54, 0x5f, 0x53, 0x45, 0x51, 0x2e, 0x5a, 0x54, 0x32, 0x00])
    outport.send(msg); sleep(0); msg = inport.receive()
    #print(msg)

    msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x05, 0x00])
    outport.send(msg); sleep(0); msg = inport.receive()
    #print(msg)
    #print("sending FLTS_SEQ next....")

    while len(data):
        # header (without 0xF0)
        packet = bytearray(b"\x52\x00\x6e\x60\x23\x40\x00\x00\x00\x00")

        if len(data) > 512:
            length = 512
        else:
            length = len(data)
        packet.append(length & 0x7f)
        packet.append((length >> 7) & 0x7f)
        packet = packet + bytearray(b"\x00\x00\x00")

        # Encode/Pack high bits
        encode = bytearray(b"\x00")
        for z in range(length):
            # into [0] bits 7..0
            encode[0] = encode[0] + ((data[z] & 0x80) >> len(encode))
            encode.append(data[z] & 0x7f)

            if len(encode) > 7:
                #print(binascii.hexlify(encode))
                packet = packet + encode
                encode = bytearray(b"\x00")

        # don't forget to add last few bytes
        if len(encode) > 1:
            packet = packet + encode

        # Compute CRC32
        crc = binascii.crc32(data[:length]) ^ 0xFFFFFFFF
        packet.append(crc & 0x7f)
        packet.append((crc >> 7) & 0x7f)
        packet.append((crc >> 14) & 0x7f)
        packet.append((crc >> 21) & 0x7f)
        packet.append((crc >> 28) & 0x0f)

        data = data[length:]
        #print(hex(len(packet)), binascii.hexlify(packet))

        msg = mido.Message("sysex", data = packet)
        outport.send(msg); sleep(0); msg = inport.receive()
        #print(msg)

        msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x05, 0x00])
        outport.send(msg); sleep(0); msg = inport.receive()
        #print(msg)
    
if options.send or options.install or options.uninstall:
    msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x21, 0x40, 0x00, 0x00, 0x00, 0x00])
    outport.send(msg); sleep(0); msg = inport.receive()
    #print(msg)
    
    msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x09])
    outport.send(msg); sleep(0); msg = inport.receive()
    #print(msg)
    
    '''
    msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x09])
    outport.send(msg); sleep(0); msg = inport.receive()
    #print(msg)

    msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x57])
    outport.send(msg); sleep(0); msg = inport.receive()
    #print(msg)
    '''


if options.receive or options.send:
    # Disable PC Mode
    msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x53])
    outport.send(msg); sleep(0); msg = inport.receive()
