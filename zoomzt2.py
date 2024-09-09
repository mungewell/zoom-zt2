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
    "id" / Int32ul,
    "group" / Computed((this.id & 0xFF000000) >> 24),
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
	AG_MODEL = 20,
	ACOUSTIC = 29,
	RHYTHM = 30,
	LOOPER = 31,
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
'''
ZT2 = Sequence(
    "header" / Header,
    "groups" / GreedyRange(Group),
)

'''
#--------------------------------------------------

ICON = Struct(
    Const(b"ICON"),
    "length" / Int32ul,
    "data" / Bytes(this.length),
)

TXJ1 = Struct(
    Const(b"TXJ1"),
    "length" / Int32ul,
    "data" / Bytes(this.length),
)

TXE1 = Struct(
    Const(b"TXE1"),
    "length" / Int32ul,
    "description" / PaddedString(this.length, "ascii"),
)

INFO = Struct(
    Const(b"INFO"),
    "length" / Int32ul,
    "data" / Bytes(this.length - 4),
    "dspload" / Float32l,
)

DATA = Struct(
    Const(b"DATA"),
    "length" / Int32ul,
    "data" / Bytes(this.length),
)

PRMJ = Struct(
    Const(b"PRMJ"),
    "length" / Int32ul,
    "data" / Bytes(this.length),
)

PRME = Struct(
    Const(b"PRME"),
    "length" / Int32ul,
    "xml" / PaddedString(this.length, "ascii"),
)

ZD2 = Struct(
    Const(b"ZDLF"),
    "length" / Int32ul,
    "checksum" / Int32ul,

    "hex1" / HexDump(Peek(Bytes(77))),
    "unknown" / Bytes(77),

    "version" / PaddedString(4, "ascii"),
    Const(b"\x00\x00"),
    "group" / Byte,
    "id" / Int32ul,

    "aname" / Peek(CString("ascii")),
    "bname" / Bytes(11),                # figure out how to write as PaddedString on rebuild
    "name" / IfThenElse(lambda ctx: ctx.aname.__len__() < 11,
        "name" / Computed(this.aname),
        "name" / Computed(this.bname),
    ),
    "groupname" / PaddedString(11, "ascii"),

    "unknown3" / Bytes(2),
    "unknown4" / BitStruct("unknown4" / Array(8, BitsInteger(1))),
    Const(b"\x00\x00\x00"),

    "ICON" / ICON,
    "TXJ1" / TXJ1,
    "TXE1" / TXE1,
    "INFO" / INFO,
    "DATA" / DATA,

    # these do not appear in the effects from AC-2 and AC-3
    "PRMJ" / Optional(PRMJ),
    "PRME" / Optional(PRME),

    "hex5" / HexDump(Peek(Bytes(16))),
    "unknown5" / Bytes(16),
)

#--------------------------------------------------
import os
import sys
import mido
import binascii
from time import sleep


midinames = ["ZOOM G", "ZOOM MS Plus Series"]

class zoomzt2(object):
    inport = None
    outport = None
    editor = False
    pcmode = False

    def is_connected(self):
        if self.inport == None or self.outport == None:
            return(False)
        else:
            return(True)

    def connect(self, midiskip = 0):
        self.inport = None
        skip = midiskip
        for port in mido.get_input_names():
            for midiname in midinames:
                if port[:len(midiname)]==midiname:
                    if not skip:
                        self.inport = mido.open_input(port)
                        break
                    else:
                        skip = skip - 1
            if self.inport != None:
                break

        self.outport = None
        skip = midiskip
        for port in mido.get_output_names():
            for midiname in midinames:
                if port[:len(midiname)]==midiname:
                    if not skip:
                        self.outport = mido.open_output(port)
                        break
                    else:
                        skip = skip - 1
            if self.outport != None:
                break

        if self.inport == None or self.outport == None:
            #print("Unable to find Pedal")
            return(False)
        return(True)

    def disconnect(self):
        if self.pcmode:
            self.pcmode_off()

        self.inport = None
        self.outport = None

    def pcmode_on(self):
        # Enable PC Mode
        msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x52])
        self.outport.send(msg); sleep(0); msg = self.inport.receive()
        self.pcmode = True

    def pcmode_off(self):
        # Disable PC Mode
        msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x53])
        self.outport.send(msg); sleep(0); msg = self.inport.receive()
        self.pcmode = False

    def editor_on(self):
        # Enable Editor Mode
        msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x50])
        self.outport.send(msg); sleep(0); msg = self.inport.receive()
        self.editor = True

    def editor_off(self):
        # Disable Editor Mode
        msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x51])
        self.outport.send(msg); sleep(0); msg = self.inport.receive()
        self.editor = False

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

    def add_effect(self, data, name, version, id, installed=True):
        config = ZT2.parse(data)
        head, tail = os.path.split(name)
        
        group_new = (id & 0xFF000000) >> 24
        group_found = False

        for group in config[1]:
            if group['group'] == group_new:
                group_found = True
                effects = group['effects']
                slice = 0
                for effect in effects:
                    if effect['effect'] == tail:
                        del effects[slice]
                    slice = slice + 1

                new = dict(effect=tail, version=version, id=id, installed=installed)
                effects.append(new)

        if not group_found:
            effects = []
            new = dict(effect=tail, version=version, id=id, installed=installed, group=group_new)
            effects.append(new)
            new = dict(group=group_new, groupname=group_new, effects=effects, groupend=group_new)
            config[1].append(new)

        return ZT2.build(config)

    def add_effect_from_filename(self, data, name):
        binfile = open(name, "rb")
        if binfile:
            bindata = binfile.read()
            binfile.close()

            binconfig = ZD2.parse(bindata)
            head, tail = os.path.split(name)

            return self.add_effect(data, tail, binconfig['version'], binconfig['id'])
        return data


    def remove_effect(self, data, name):
        config = ZT2.parse(data)
        head, tail = os.path.split(name)
        
        for group in config[1]:
            effects = group['effects']
            slice = 0
            for effect in effects:
                if effect['effect'] == tail:
                    del effects[slice]
                slice = slice + 1

        return ZT2.build(config)

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
        self.outport.send(msg); sleep(0); resp = self.inport.receive()
        
        msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x27])
        self.outport.send(msg); sleep(0); msg = self.inport.receive()

        if bytes(resp.data[-5:]) == b'\x00\x00\x00\x00\x00':
            return(True)
        return(False)
    
    def file_wild(self, first):
        if first:
            packet = bytearray(b"\x52\x00\x6e\x60\x25\x00\x00")
        else:
            packet = bytearray(b"\x52\x00\x6e\x60\x26\x00\x00")
        msg = self.filename(packet, "*")

        if msg.data[4] == 4:
            for x in range(14,27):
                if msg.data[x] == 0:
                    return bytes(msg.data[14:x]).decode("utf-8")
        else:
            return ""

    def file_download(self, name):
        # download file from pedal to PC
        packet = bytearray(b"\x52\x00\x6e\x60\x20\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        head, tail = os.path.split(name)
        self.filename(packet, tail)

        msg = mido.Message("sysex", data = packet)
        self.outport.send(msg); sleep(0); msg = self.inport.receive()
        
        # Read parts 1 through 17 - refers to FLST_SEQ, possibly larger
        data = bytearray(b"")
        while True:
            msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x05, 0x00])
            self.outport.send(msg); sleep(0); msg = self.inport.receive()

            msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x22, 0x14, 0x2f, 0x60, 0x00, 0x0c, 0x00, 0x04, 0x00, 0x00, 0x00])
            self.outport.send(msg); sleep(0); msg = self.inport.receive()

            msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x05, 0x00])
            self.outport.send(msg); sleep(0); msg = self.inport.receive()

            #decode received data
            packet = msg.data
            length = int(packet[9]) * 128 + int(packet[8])
            if packet[4] != 4 or length == 0:
                break
            block = self.unpack(packet[10:10 + length + int(length/7) + 1])

            # confirm checksum (last 5 bytes of packet)
            # note: mido packet does not have SysEx prefix/postfix
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

    def disk_usage(self):
        msg = mido.Message("sysex", data = [0x52, 0x00, 0x6e, 0x60, 0x29, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.outport.send(msg); sleep(0); msg = self.inport.receive()

        packet = bytes(msg.data)
        #print(binascii.hexlify(packet))
        #b'52 00 6e 60 04 29 01 00 08 00 34 16 07 07 00 26 7c 12 04 00 00 0000000'
        #                          Max = XX XX XX XX XX,YY YY YY YY YY = Available

        maximum = int(packet[10]) + int(packet[11])*128 + int(packet[12])*128*128 +\
                    int(packet[13])*128*128*128 + int(packet[14])*128*128*128*128
        available = int(packet[15]) + int(packet[16])*128 + int(packet[17])*128*128 +\
                    int(packet[18])*128*128*128 + int(packet[19])*128*128*128*128

        if available and maximum:       # prevent div by zero
            return((1 - (float(available)/maximum)) * 100)
        else:
            return(0)

    def patch_check(self):
        packet = bytearray(b"\x52\x00\x6e\x44")

        msg = mido.Message("sysex", data = packet)
        self.outport.send(msg); sleep(0); msg = self.inport.receive()

        # decode received data
        packet = msg.data
        count = packet[5] * 128 + packet[4]
        psize = packet[7] * 128 + packet[6]
        bsize = packet[11] * 128 + packet[10]

        return(count, psize, bsize)

    def patch_download(self, location):
        (count, psize, bsize) = self.patch_check()

        packet = bytearray(b"\x52\x00\x6e\x46\x00\x00")
        bank = int((location - 1) / bsize)
        loc = location - (bank * bsize) - 1

        packet.append(bank & 0x7F)
        packet.append(bank >> 7)
        packet.append(loc & 0x7F)
        packet.append(loc >> 7)

        msg = mido.Message("sysex", data = packet)
        self.outport.send(msg); sleep(0); msg = self.inport.receive()

        # decode received data
        packet = msg.data
        length = int(packet[11]) * 128 + int(packet[10])
        if length == 0:
            return()
        data = self.unpack(packet[12:12 + length + int(length/7) + 1])

        # confirm checksum (last 5 bytes of packet)
        checksum = packet[-5] + (packet[-4] << 7) + (packet[-3] << 14) \
                + (packet[-2] << 21) + ((packet[-1] & 0x0F) << 28) 

        if (checksum ^ 0xFFFFFFFF) != binascii.crc32(data):
            print("Checksum error", hex(checksum))

        return(data)

    def patch_upload(self, location, data):
        (count, psize, bsize) = self.patch_check()

        packet = bytearray(b"\x52\x00\x6e\x45\x00\x00")
        bank = int((location - 1) / bsize)
        loc = location - (bank * bsize) - 1

        packet.append(bank & 0x7F)
        packet.append(bank >> 7)
        packet.append(loc & 0x7F)
        packet.append(loc >> 7)

        length = len(data)
        packet.append(length & 0x7f)
        packet.append((length >> 7) & 0x7f)

        packet = packet + self.pack(data[:length])

        # Compute CRC32
        crc = binascii.crc32(data[:length]) ^ 0xFFFFFFFF
        packet.append(crc & 0x7f)
        packet.append((crc >> 7) & 0x7f)
        packet.append((crc >> 14) & 0x7f)
        packet.append((crc >> 21) & 0x7f)
        packet.append((crc >> 28) & 0x0f)

        msg = mido.Message("sysex", data = packet)
        self.outport.send(msg); sleep(0); msg = self.inport.receive()

    def patch_download_old(self, location):
        (count, psize, bsize) = self.patch_check()

        packet = bytearray(b"\x52\x00\x6e\x09\x00")
        bank = int((location - 1) / bsize)
        packet.append(bank)
        packet.append(location - (bank * bsize) - 1)

        msg = mido.Message("sysex", data = packet)
        self.outport.send(msg); sleep(0); msg = self.inport.receive()

        # decode received data
        packet = msg.data
        length = int(packet[8]) * 128 + int(packet[7])
        if length == 0:
            return()
        data = self.unpack(packet[9:9 + length + int(length/7) + 1])

        # confirm checksum (last 5 bytes of packet)
        checksum = packet[-5] + (packet[-4] << 7) + (packet[-3] << 14) \
                + (packet[-2] << 21) + ((packet[-1] & 0x0F) << 28) 

        if (checksum ^ 0xFFFFFFFF) != binascii.crc32(data):
            print("Checksum error", hex(checksum))

        return(data)

    def patch_upload_old(self, location, data):
        (count, psize, bsize) = self.patch_check()

        packet = bytearray(b"\x52\x00\x6e\x08\x00")
        bank = int((location - 1) / bsize)
        packet.append(bank)
        packet.append(location - (bank * bsize) - 1)

        length = len(data)
        packet.append(length & 0x7f)
        packet.append((length >> 7) & 0x7f)

        packet = packet + self.pack(data[:length])

        # Compute CRC32
        crc = binascii.crc32(data[:length]) ^ 0xFFFFFFFF
        packet.append(crc & 0x7f)
        packet.append((crc >> 7) & 0x7f)
        packet.append((crc >> 14) & 0x7f)
        packet.append((crc >> 21) & 0x7f)
        packet.append((crc >> 28) & 0x0f)

        msg = mido.Message("sysex", data = packet)
        self.outport.send(msg); sleep(0); msg = self.inport.receive()

    def patch_download_current(self):
        packet = bytearray(b"\x52\x00\x6e\x29")

        msg = mido.Message("sysex", data = packet)
        self.outport.send(msg); sleep(0); msg = self.inport.receive()

        # decode received data
        packet = msg.data
        data = self.unpack(packet[4:])

        return(data)

    '''
    def patch_upload_current(self, data):
        packet = bytearray(b"\x52\x00\x6e\x28")
    '''

    def tuner(self, on = 0):
        packet = bytearray(b"\x52\x00\x6e\x64")

        if on:
            packet.append(0x0b)
        else:
            packet.append(0x0c)

        msg = mido.Message("sysex", data = packet)
        self.outport.send(msg); #sleep(0); msg = self.inport.receive()

    def tuner_read(self):
        note = None
        delta = 0

        notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "-"]

        for msg in self.inport.iter_pending():
            if msg.type == "control_change":
                if msg.control == 98:
                    if msg.value < 13:
                        note = notes[msg.value]
                if msg.control == 99:
                    delta = msg.value - 8

        return(note, delta)

#--------------------------------------------------

def download_and_save_file(pedal, name, outname = ""):
    data = bytearray(b"")
    if pedal.file_check(name):
        data = pedal.file_download(name)
        pedal.file_close()
    else:
        print("File \"" + name + "\" was not found on the pedal" )

    if data:
        if outname == "":
            outname = name
        outfile = open(outname, "wb")
        if outfile:
            outfile.write(data)
            outfile.close()
        else:
            print("Unable to open FILE \"" + name + "\" for writing")
    return data

def download_and_save_all_files(pedal, dirname):
    files = []
    name = pedal.file_wild(True)

    while name:
        files.append(name)
        name = pedal.file_wild(False)

    for name in files:
        fullname = os.path.join(dirname, name)
        print("Downloading file " + name.ljust(12) + " -> " + fullname)
        download_and_save_file(pedal, name, fullname)


def main():
    from argparse import ArgumentParser

    data = bytearray(b"")
    pedal = zoomzt2()

    parser = ArgumentParser(prog="zoomzt2")

    parser.add_argument('files', metavar='FILE', nargs='+',
        help='File(s) to process')

    # actions on FLST_SEQ file (local or received from pedal)
    parser.add_argument("-d", "--dump",
        help="dump configuration to text",
        action="store_true", dest="dump")
    parser.add_argument("-s", "--summary",
        help="summarized configuration in human readable form",
        action="store_true", dest="summary")
    parser.add_argument("-b", "--build",
        help="output commands required to build this FLTS_SEQ",
        dest="build")

    parser.add_argument("-A", "--add",
        help="add effect to FLST_SEQ", dest="add")
    parser.add_argument("-v", "--ver",
        help="effect version (use with --add)", dest="ver")
    parser.add_argument("-i", "--id",
        help="effect id (use with --add)", dest="id")
    parser.add_argument("-D", "--delete",
    help="delete effect from FLST_SEQ", dest="delete")
    parser.add_argument("-N", "--not-add", action="store_true",
        help="add effect to FLST_SEQ, but as uninstalled", dest="notadd")

    parser.add_argument("-t", "--toggle",
        help="toggle install/uninstall state of effect NAME in FLST_SEQ", dest="toggle")

    parser.add_argument("-w", "--write", dest="write",
        help="write config back to same file", action="store_true")

    # interaction with attached device
    parser.add_argument("-R", "--receive",
        help="Receive FLST_SEQ from attached device",
        action="store_true", dest="receive")
    parser.add_argument("-S", "--send",
        help="Send FLST_SEQ to attached device",
        action="store_true", dest="send")

    zd2 = parser.add_argument_group("ZD2", "Process ZDL2 effect file(s)").add_mutually_exclusive_group()
    zd2.add_argument("-I", "--install",
        help="Install effect binary to attached device, updating FLST_SEQ",
        action="store_true", dest="install")
    zd2.add_argument("-U", "--uninstall",
        help="Remove effect binary from attached device, updating FLST_SEQ",
        action="store_true", dest="uninstall")
    zd2.add_argument("--install-only",
        help="Install effect binary to attached device without affecting FLST_SEQ",
        action="store_true", dest="installonly")
    zd2.add_argument("--uninstall-only",
        help="Remove effect binary from attached device without affecting FLST_SEQ",
        action="store_true", dest="uninstallonly")
    zd2.add_argument("-e", "--effectdown",
        help="Download effect binary with name FILE",
        action="store_true", dest="effectdown")
    zd2.add_argument("--include-zic",
        help="When downloading or uploading effect binary, include the corrsponding .ZIC icon file",
        action="store_true", dest="includezic")
    zd2.add_argument("--include-zir",
        help="When downloading or uploading effect binary, include the corrsponding .ZIR impulse response file",
        action="store_true", dest="includezir")
    zd2.add_argument("--download-all",
        help="Download all files on pedal to directory FILE",
        action="store_true", dest="downloadall")
    zd2.add_argument("-a", "--available",
        help="Print out the available diskspace after action",
        action="store_true", dest="available")

    # attached device's effect patches
    zptc = parser.add_argument_group("ZPTC", "Process ZPTC patch file").add_mutually_exclusive_group()
    zptc.add_argument("-p", "--patchdown", type=int,
        help="download specific zptc", dest="patchdown")
    zptc.add_argument("-P", "--patchup", type=int,
        help="upload specific zptc", dest="patchup")
    zptc.add_argument("-c", "--curdown", action="store_true", 
        help="download current zptc", dest="curdown")
    zptc.add_argument("--old-patch",
        help="Use the 'old' method for reading patches",
        action="store_true", dest="oldpatch")

    parser.add_argument("-M", "--midiskip",
        type=int, default=0, dest="midiskip",
        help="Skip devices when connecting, ie when you have multiple pedals")

    options = parser.parse_args()

    if not len(options.files):
        parser.error("FILE not specified")

    if options.curdown:
        # do this first as we do not need PC mode,
        # which would cancel unsaved changes
        if not pedal.connect(options.midiskip):
            sys.exit("Unable to find Pedal")

        pedal.editor_on()
        data = pedal.patch_download_current()
        pedal.editor_off()
        pedal.disconnect()

        outfile = open(options.files[0], "wb")
        if not outfile:
            sys.exit("Unable to open FILE for writing")

        outfile.write(data)
        outfile.close()
        exit(0)

    if options.receive or options.send or \
            options.install or options.uninstall or \
            options.installonly or options.uninstallonly or \
            options.patchdown or options.patchup or \
            options.effectdown or options.downloadall:
        if not pedal.connect(options.midiskip):
            sys.exit("Unable to find Pedal")
        else:
            pedal.pcmode_on()

    if options.patchdown:
        (count, size, banks) = pedal.patch_check()
        if options.patchdown < 1 or options.patchdown > count:
            pedal.disconnect()
            sys.exit("Patch number should be between 1 and " + str(count))

        if options.oldpatch:
            data = pedal.patch_download_old(options.patchdown)
        else:
            data = pedal.patch_download(options.patchdown)
        pedal.disconnect()

        outfile = open(options.files[0], "wb")
        if not outfile:
            sys.exit("Unable to open FILE for writing")

        outfile.write(data)
        outfile.close()
        exit(0)

    if options.patchup:
        (count, size, banks) = pedal.patch_check()
        if options.patchup < 1 or options.patchup > count:
            pedal.disconnect()
            sys.exit("Patch number should be between 1 and " + str(count))

        infile = open(options.files[0], "rb")
        if not infile:
            pedal.disconnect()
            sys.exit("Unable to open FILE for reading")
        else:
            data = infile.read()
        infile.close()

        if len(data):
            if options.oldpatch:
                data = pedal.patch_upload_old(options.patchup, data)
            else:
                data = pedal.patch_upload(options.patchup, data)
        pedal.disconnect()
        exit(0)

    if options.effectdown:
        print("Downloading effect: \"" + options.files[0] + "\"" )
        download_and_save_file(pedal, options.files[0])

        filename, extension = os.path.splitext(options.files[0])

        if options.includezic:
            zicfilename = filename + ".ZIC"
            print("Downloading icon:   \"" + zicfilename + "\"" )
            download_and_save_file(pedal, zicfilename)

        if options.includezir:
            zirfilename = filename + ".ZIR"
            print("Downloading IR:     \"" + zirfilename + "\"" )
            download_and_save_file(pedal, zirfilename)

        pedal.disconnect()
        exit(0)

    if options.downloadall:
        dirname = options.files[0]
        print("Downloading all files to directory \"" + dirname + "\"" )

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        download_and_save_all_files(pedal, dirname)
        pedal.disconnect()
        exit(0)

    if options.receive or options.install or options.uninstall:
        if pedal.file_check("FLST_SEQ.ZT2"):
            data = pedal.file_download("FLST_SEQ.ZT2")
        pedal.file_close()
    elif not options.installonly and not options.uninstallonly:
        # Read data from local file
        infile = open(options.files[0], "rb")
        if not infile:
            sys.exit("Unable to open config FILE for reading")
        else:
            data = infile.read()
        infile.close()

    if data and options.add and options.ver and options.id:
        if options.id[:2] == "0x":
            data = pedal.add_effect(data, options.add, options.ver, int(options.id, 16), not options.notadd)
        else:
            data = pedal.add_effect(data, options.add, options.ver, int(options.id), not options.notadd)

    if data and options.delete:
        data = pedal.remove_effect(data, options.delete)

    if data and options.toggle:
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

    if options.install or options.installonly:
        for target in options.files:
            binfile = open(target, "rb")
            if binfile:
                bindata = binfile.read()
                binfile.close()

                print("Installing effect:", target)
                if not pedal.file_check(target):
                    print("uploading...")
                    pedal.file_upload(target, bindata)

                pedal.file_close()

                if options.available:
                    print("Percentage disk use:", pedal.disk_usage())

                if data and options.install:
                    data = pedal.add_effect_from_filename(data, target)

            filename, extension = os.path.splitext(target)

            if options.includezic:
                zicfilename = filename + ".ZIC"
                binfile = open(zicfilename, "rb")
                if binfile:
                    bindata = binfile.read()
                    binfile.close()

                    if not pedal.file_check(zicfilename):
                        print("Uploading icon:", zicfilename)
                        pedal.file_upload(zicfilename, bindata)

                    pedal.file_close()

                    if options.available:
                        print("Percentage disk use:", pedal.disk_usage())

            if options.includezir:
                zirfilename = filename + ".ZIR"
                binfile = open(zicfilename, "rb")
                if binfile:
                    bindata = binfile.read()
                    binfile.close()

                    if not pedal.file_check(zirfilename):
                        print("Uploading impulse response:", zirfilename)
                        pedal.file_upload(zirfilename, bindata)

                    pedal.file_close()

                    if options.available:
                        print("Percentage disk use:", pedal.disk_usage())

    if options.uninstall or options.uninstallonly:
        for target in options.files:
            print("Uninstalling effect:", target)
            if pedal.file_check(target):
                pedal.file_delete(target)

            pedal.file_close()

            if options.available:
                print("Percentage disk use:", pedal.disk_usage())

            if data and options.uninstall:
                data = pedal.remove_effect(data, target)

            filename, extension = os.path.splitext(target)

            if options.includezic:
                zicfilename = filename + ".ZIC"
                if pedal.file_check(zicfilename):
                    print("Uninstalling icon:", zicfilename)
                    pedal.file_delete(zicfilename)

                pedal.file_close()

                if options.available:
                    print("Percentage disk use:", pedal.disk_usage())

            if options.includezir:
                zirfilename = filename + ".ZIR"
                if pedal.file_check(zirfilename):
                    print("Uninstalling IR  :", zirfilename)
                    pedal.file_delete(zirfilename)

                pedal.file_close()

                if options.available:
                    print("Percentage disk use:", pedal.disk_usage())

    if options.send or options.install or options.uninstall:
        pedal.file_check("FLST_SEQ.ZT2")
        pedal.file_upload("FLST_SEQ.ZT2", data)
        pedal.file_close()

    if pedal.is_connected():
        pedal.disconnect()

    if options.dump and data:
        config = ZT2.parse(data)
        print(config)

    if options.summary and data:
        config = ZT2.parse(data)
        for group in config[1]:
            print("Group", dict(group)["group"], ":", dict(group)["groupname"])
    
            for effect in dict(group)["effects"]:
                print("0x%8.8x : %s, (v%s %d)" % (dict(effect)['id'], \
                    dict(effect)["effect"], dict(effect)["version"], \
                    dict(effect)["installed"]))

    if options.build and data:
        config = ZT2.parse(data)
        for group in config[1]:
            for effect in dict(group)["effects"]:
                if dict(effect)["installed"]:
                    print("python3 zoomzt2.py -i ", hex(dict(effect)["id"]), \
                        "-A", dict(effect)["effect"], "-v", dict(effect)["version"], \
                        "-w", options.build)
                else:
                    print("python3 zoomzt2.py -i ", hex(dict(effect)["id"]), \
                        "-N -A", dict(effect)["effect"], "-v", dict(effect)["version"], \
                        "-w", options.build)

    if options.write and data:
       outfile = open(options.files[0], "wb")
       if not outfile:
           sys.exit("Unable to open FILE for writing")

       outfile.write(data)
       outfile.close()

if __name__ == "__main__":
    main()

