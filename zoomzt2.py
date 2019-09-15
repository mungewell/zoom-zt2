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
import os
import sys
import mido
import binascii
from time import sleep

if sys.platform == 'win32':
    mido.set_backend('mido.backends.rtmidi_python')
    midiname = b"ZOOM G"
else:
    midiname = "ZOOM G"

class zoomzt2(object):
    inport = None
    outport = None

    def is_connected(self):
        if self.inport == None or self.outport == None:
            return(False)
        else:
            return(True)

    def connect(self):
        for port in mido.get_input_names():
            if port[:len(midiname)]==midiname:
                self.inport = mido.open_input(port)
                #print("Using Input:", port)
                break
        for port in mido.get_output_names():
            if port[:len(midiname)]==midiname:
                self.outport = mido.open_output(port)
                #print("Using Output:", port)
                break

        if self.inport == None or self.outport == None:
            #print("Unable to find Pedal")
            return(False)

        # Enable PC Mode
        msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x52])
        self.outport.send(msg); sleep(0); msg = self.inport.receive()
        return(True)

    def disconnect(self):
        # Disable PC Mode
        msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x53])
        self.outport.send(msg); sleep(0); msg = self.inport.receive()

        self.inport = None
        self.outport = None

    def pack(self, data):
        # Pack 8bit data into 7bit, MSB's in first byte followed
        # by 7 bytes (bits 6..0).
        packet = bytearray(b"")
        encode = bytearray(b"\x00")

        for byte in data:
            encode[0] = encode[0] + ((byte & 0x80) >> len(encode))
            encode.append(byte & 0x7f)

            if len(encode) > 7:
                packet = packet + encode
                encode = bytearray(b"\x00")

        # don't forget to add last few bytes
        if len(encode) > 1:
            packet = packet + encode

        return(packet)

    def unpack(self, packet):
        # Unpack data 7bit to 8bit, MSBs in first byte
        data = bytearray(b"")
        loop = -1
        hibits = 0

        for byte in packet:
            if loop !=-1:
                if (hibits & (2**loop)):
                    data.append(128 + byte)
                else:
                    data.append(byte)
                loop = loop - 1
            else:
                hibits = byte
                # do we need to acount for short sets (at end of block block)?
                loop = 6

        return(data)

    def filename(self, packet, name):
        # send filename (with different packet headers)
        head, tail = os.path.split(name)
        for x in range(len(tail)):
            packet.append(ord(tail[x]))
        packet.append(0x00)

        msg = mido.Message("sysex", data = packet)
        self.outport.send(msg); sleep(0); msg = self.inport.receive()
        return(msg)

    def file_check(self, name):
        # check file is present on device
        packet = bytearray(b"\x52\x00\x6e\x60\x25\x00\x00")
        head, tail = os.path.split(name)
        self.filename(packet, tail)

        msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x05, 0x00])
        self.outport.send(msg); sleep(0); msg = self.inport.receive()
        
        msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x27])
        self.outport.send(msg); sleep(0); msg = self.inport.receive()
        return(True)
    
    def file_download(self, name):
        # download file from pedal to PC
        packet = bytearray(b"\x52\x00\x6e\x60\x20\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        head, tail = os.path.split(name)
        self.filename(packet, tail)

        msg = mido.Message("sysex", data = packet)
        self.outport.send(msg); sleep(0); msg = self.inport.receive()
        
        # Read parts 1 through 17 - refers to FLST_SEQ, possibly larger
        data = bytearray(b"")
        for part in range(17):
            msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x05, 0x00])
            self.outport.send(msg); sleep(0); msg = self.inport.receive()

            msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x22, 0x14, 0x2f, 0x60, 0x00, 0x0c, 0x00, 0x04, 0x00, 0x00, 0x00])
            self.outport.send(msg); sleep(0); msg = self.inport.receive()

            msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x05, 0x00])
            self.outport.send(msg); sleep(0); msg = self.inport.receive()

            #decode received data
            packet = msg.data
            length = int(packet[9]) * 128 + int(packet[8])
            block = self.unpack(packet[10:10 + length + int(length/7) + 1])

            # confirm checksum (last 5 bytes of packet)
            checksum = packet[-5] + (packet[-4] << 7) + (packet[-3] << 14) \
                    + (packet[-2] << 21) + ((packet[-1] & 0x0F) << 28) 
            if (checksum ^ 0xFFFFFFFF) == binascii.crc32(block):
                data = data + block
            else:
                print("Checksum error", hex(checksum))
        return(data)

    def file_upload(self, name, data):
        packet = bytearray(b"\x52\x00\x6e\x60\x24")
        head, tail = os.path.split(name)
        self.filename(packet, tail)

        packet = bytearray(b"\x52\x00\x6e\x60\x20\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        head, tail = os.path.split(name)
        self.filename(packet, tail)

        msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x05, 0x00])
        self.outport.send(msg); sleep(0); msg = self.inport.receive()

        while len(data):
            packet = bytearray(b"\x52\x00\x6e\x60\x23\x40\x00\x00\x00\x00")
            if len(data) > 512:
                length = 512
            else:
                length = len(data)
            packet.append(length & 0x7f)
            packet.append((length >> 7) & 0x7f)
            packet = packet + bytearray(b"\x00\x00\x00")

            packet = packet + self.pack(data[:length])

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
            self.outport.send(msg); sleep(0); msg = self.inport.receive()

            msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x05, 0x00])
            self.outport.send(msg); sleep(0); msg = self.inport.receive()

    def file_delete(self, name):
        packet = bytearray(b"\x52\x00\x6e\x60\x24")
        head, tail = os.path.split(name)
        self.filename(packet, tail)

    def file_close(self):
        msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x21, 0x40, 0x00, 0x00, 0x00, 0x00])
        self.outport.send(msg); sleep(0); msg = self.inport.receive()
        
        msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x09])
        self.outport.send(msg); sleep(0); msg = self.inport.receive()

#--------------------------------------------------
def main():
    from optparse import OptionParser

    data = bytearray(b"")
    pedal = zoom()

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

    parser.add_option("-T", "--test", dest="test",
        help="test", action="store_true")
    
    (options, args) = parser.parse_args()
    
    if len(args) != 1:
        parser.error("FILE not specified")

    if options.install and options.uninstall:
        sys.exit("Cannot use 'install' and 'uninstall' at same time")
    
    if options.receive or options.send or options.install:
        if not pedal.connect():
            sys.exit("Unable to find Pedal")
    
    if options.receive:
        pedal.file_check("FLST_SEQ.ZT2")
        data = pedal.file_download("FLST_SEQ.ZT2")
        pedal.file_close()
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

            pedal.file_check(options.install)
            pedal.file_upload(options.install)

    if options.uninstall:
        pedal.file_check(options.uninstall)
        pedal.file_delete(options.uninstall)

    if options.send:
        pedal.file_check("FLST_SEQ.ZT2")
        pedal.file_upload("FLST_SEQ.ZT2", data)
    
    if options.send or options.install or options.uninstall:
        pedal.file_close()
    
    if pedal.is_connected():
        pedal.disconnect()
    
if __name__ == "__main__":
    main()
