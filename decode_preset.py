#!/usr/bin/python
#
# Script decode/encode 'ZPTC' patch files from Zoom F/W
# (c) Simon Wood, 13 May 2020
#

from construct import *

#--------------------------------------------------
# Define ZPTC file format using Construct (v2.9)
# requires:
# https://github.com/construct/construct

TXJ1 = Struct(
    Const(b"TXJ1"),
    "length" / Rebuild(Int32ul, len_(this.data)),
    "data" / Bytes(this.length),
)

TXE1 = Struct(
    Const(b"TXE1"),
    "length" / Rebuild(Int32ul, len_(this.desc)),
    "desc" / PaddedString(this.length, "ascii"),
)

EDTB2 = Struct( # Working with a Byte-reversed copy of data
    #"dump" / Peek(HexDump(Bytes(24))),
    "unknown" / Bytes(9),
    "control" / Bitwise(Struct(
        "unknown" / BitsInteger(6),
        "param8" / BitsInteger(8),
        "param7" / BitsInteger(8),
        "param6" / BitsInteger(8),
        "param5" / BitsInteger(12),
        "param4" / BitsInteger(12),
        "param3" / BitsInteger(12),
        "param2" / BitsInteger(12),
        "param1" / BitsInteger(12),
        "id" / BitsInteger(29),
        "enabled" / Flag,
    )),
)

EDTB1 = Struct(
    #"dump" / Peek(HexDump(Bytes(24))),
    "autorev" / ByteSwapped(Bytes(24)),
    "reversed" / RestreamData(this.autorev, EDTB2), # this does not allow re-build of data :-(
)

EDTB = Struct(
    Const(b"EDTB"),
    "length" / Rebuild(Int32ul, 24 * len_(this.effects)),
    "effects" / Array(this._.fx_count, EDTB1),
)

PPRM12 = Struct(
    #"dump" / Peek(HexDump(Bytes(12))),
    "control" / Bitwise(Struct(
        "punknown" / BitsInteger(23),
        "editslot" / BitsInteger(3), # active/editing slot 0..4 on G1Four/etc
        "volume" / BitsInteger(7),
        "pad" / BitsInteger(7),
    )),
    "unknown" / Bytes(7),
)

PPRM = Struct(
    Const(b"PPRM"),
    "length" / Rebuild(Int32ul, len_(this.autorev)),
    #"dump" / Peek(HexDump(Bytes(this.length))),

    "autorev" / ByteSwapped(Bytes(12)),                 # not sure all are 12bytes, but needs fixed len
    "reversed" / RestreamData(this.autorev, PPRM12),    # this does not allow re-build of data :-(
)

PPRM_v2 = Struct(
    Const(b"PRM2"),
    "length" / Rebuild(Int32ul, len_(this.unknown)),
    "dump" / Peek(HexDump(Bytes(this.length))),

    "unknown" / Bytes(this.length),
)

NAME = Struct(
    Const(b"NAME"),
    "length" / Rebuild(Int32ul, len_(this.name)),
    #"dump" / Peek(HexDump(Bytes(this.length))),

    "name" / PaddedString(this.length, "ascii"),
)

PEEK = Struct(
    "l" / Int32ul,
    "v" / Int32ul,
)

ZPTC = Struct(
    Const(b"PTCF"),

    "p" / Peek(PEEK),           # need to peek ahead for the version

    "length" / IfThenElse(this.p.v> 1,
            Rebuild(Int32ul, 68 + (this.fx_count * 4) + \
                this.TXJ1.length + this.TXE1.length + \
                this.EDTB.length + this.PPRM.length + this.NAME.length),    # V2
            Rebuild(Int32ul, 68 + (this.fx_count * 4) + \
                this.TXJ1.length + this.TXE1.length + \
                this.EDTB.length + this.PPRM.length),                       # V1
            ),
    "version" / Int32ul,
    "fx_count" / Rebuild(Int32ul, len_(this.EDTB.effects)),

    "targets" / Peek(BitsSwapped(Bitwise(Struct(    # Informational, does not rebuild
        "g5n"       / BitsInteger(1),   # 0x01
        "g3n"       / BitsInteger(1),   # 0x02
        "g3xn"      / BitsInteger(1),   # 0x04
        "b3n"       / BitsInteger(1),   # 0x08
        "g1four"    / BitsInteger(1),   # 0x10
        "g1xfour"   / BitsInteger(1),   # 0x20
        "b1four"    / BitsInteger(1),   # 0x40
        "b1xfour"   / BitsInteger(1),   # 0x80
        "a1four"    / BitsInteger(1),   # 0x100
        "a1xfour"   / BitsInteger(1),   # 0x200
        "g11"       / BitsInteger(1),   # 0x400
        Padding(5),
        "b2four"    / BitsInteger(1),   # 0x10000
        Padding(15),
    )))),
    "target" / Int32ul, # pedal that patch is for
    "data" / Bytes(6),

    "name" / PaddedString(10, "ascii"),
    "ids" / Array(this.fx_count, Int32ul),

    "TXJ1" / TXJ1,
    "TXE1" / TXE1,
    "EDTB" / EDTB,

    "PPRM" / IfThenElse(this.version > 1,
        PPRM_v2,
        PPRM
    ),
    "NAME" / If(this.version > 1, Optional(NAME)),
)

#--------------------------------------------------
# Allow for decoding of SysEx Packets

# Midi is 7bit stuffed - each byte max 0x7F
class Midi2u(Adapter):
    def _decode(self, obj, context, path):
        return((obj & 0x7f) + ((obj & 0x7f00) >> 1))
    def _encode(self, obj, context, path):
        return((obj & 0x7f) + ((obj & 0x3f80) << 1))

# Current patch, ie starts...
# 00000000  f0 52 00 6e 64 12 01 40  06 04 50 54 43 46 3c 01  |.R.nd..@..PTCF<.|
#                                       [<- start of packed data
#                                ^^  ^^ length

Midi_64 = Struct(
    "header" / Const(b"\xf0\x52\x00\x6e\x64\x12\x01"),
    "length" / Midi2u(Int16ul),
    "data" / Bytes(this.length),
    #"footer" / Const(b"\xf7"),
    )

# Specific/Numbered patch, ie starts...
# 00000000  f0 52 00 6e 45 00 00 00  00 00 00 40 06 04 50 54  |.R.nE......@..PT|
#                                                   [<- start of packed data
#                                             ^^ ^^ length

Midi_45 = Struct(
    "header" / Const(b"\xf0\x52\x00\x6e\x45\x00\x00"),
    "patch" / Bytes(4),
    "length" / Midi2u(Int16ul),
    "data" / Bytes(this.length),
    #"footer" / Const(b"\xf7"),
    )


def unpack(packet):
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

#--------------------------------------------------
# Convert Patches between Effects with 1 or 2screen versions
convert = [ # 2screen -> 1screen
        [0x02000050, 0x02000051], # Gt GEQ
        [0x02000053, 0x02000054], # Gt GEQ 7
        [0x02000060, 0x02000061], # St Gt GEQ
        [0x02800050, 0x02800051], # BassGEQ
        [0x02800060, 0x02800061], # St Ba GEQ
        [0x03800010, 0x03800011], # Bass DRV
        [0x03800030, 0x03800031], # Dark Pre
        [0x04000010, 0x04000011], # MS 800
        [0x04000018, 0x04000019], # MS 1959
        [0x0400001a, 0x0400001b], # MS 45os
        [0x04000020, 0x04000021], # FD TWNR
        [0x04000027, 0x04000028], # FD B-MAN
        [0x0400002a, 0x0400002c], # FD DLXR
        [0x0400002b, 0x0400002d], # FD MASTER
        [0x04000030, 0x04000031], # UK 30A
        [0x04000040, 0x04000041], # BG MK1
        [0x04000042, 0x04000043], # BG MK3
        [0x04000050, 0x04000051], # XtasyBlue
        [0x04000060, 0x04000061], # HW 100
        [0x04000070, 0x04000071], # Recti ORG
        [0x04000080, 0x04000081], # ORG120
        [0x04000090, 0x04000091], # DZ DRV
        [0x040000a0, 0x040000a1], # MATCH30
        [0x04800010, 0x04800011], # AMPG SVT
        [0x04800020, 0x04800021], # BMAN100
        [0x04800030, 0x04800031], # SMR400
        [0x04800040, 0x04800041], # AG 750
        [0x04800050, 0x04800051], # TE400SMX
        [0x04800060, 0x04800061], # AC 370
        [0x04800090, 0x04800091], # FlipTop
        [0x06000130, 0x06000131], # CoronaTri
        [0x06000170, 0x06000171], # Duo Phase
        [0x07000040, 0x07000041], # LoopRoll
        [0x07800030, 0x07800031], # Z-Syn
        [0x08000010, 0x08000011], # Delay
        [0x08000020, 0x08000021], # AnalogDly
        [0x08000040, 0x08000041], # ReverseDL
        [0x08000080, 0x08000081], # P-P Delay
        [0x080000a0, 0x080000a1], # Dual DLY
        [0x080000b0, 0x080000b1], # Pitch DLY
        [0x080000c0, 0x080000c1], # SlapBackD
        [0x080000d0, 0x080000d1], # A-Pan DLY
        [0x080000e0, 0x080000e1], # PhaseDly
        [0x080000f0, 0x080000f1], # TapeEcho3
        [0x08000100, 0x08000101], # ICE Delay
        [0x08000110, 0x08000111], # SlwAtkDly
        [0x08000120, 0x08000121], # SoftEcho
        [0x0b0000a0, 0x0b0000a1], # PDL Delay
        [0x0b0000c0, 0x0b0000c1], # OSC Echo
        [0x0b0000e0, 0x0b0000e1], # PDL Roto
        ]

#--------------------------------------------------
def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(prog="decode_effect")
    parser.add_argument('files', metavar='FILE', nargs=1,
        help='File to process')

    parser.add_argument("-d", "--dump",
        help="dump configuration to text",
        action="store_true", dest="dump")
    parser.add_argument("-s", "--summary",
        help="summarize LINE in human readable form",
        action="store_true", dest="summary")
    parser.add_argument("-m", "--midi",
        help="read file from midi SysEx packet format",
        action="store_true", dest="midi")

    parser.add_argument("-o", "--output", dest="outfile",
        help="write data to OUTFILE")
    parser.add_argument("-p", "--pad", type=int,
        help="pad output size to PAD bytes", dest="pad")
    parser.add_argument("-t", "--target",
        help="set the target pedal (value in hex)", dest="target")

    parser.add_argument("-1", "--convert1",
        help="convert patch to use '1 screen' effects",
        action="store_true", dest="convert1")
    parser.add_argument("-2", "--convert2",
        help="convert patch to use '2 screen' effects",
        action="store_true", dest="convert2")
    parser.add_argument("-b", "--bypass",
        help="move Bypass effects to end of patch",
        action="store_true", dest="bypass")
    parser.add_argument("-l", "--limit", type=int,
        help="limit the number of effects", dest="limit")
    parser.add_argument("-E", "--effect",
        help="force effects (value in hex)", dest="effect")

    options = parser.parse_args()

    if not len(options.files):
        parser.error("FILE not specified")

    # Read data from file
    infile = open(options.files[0], "rb")
    if not infile:
        sys.exit("Unable to open FILE for reading")
    else:
        data = infile.read()
    infile.close()

    if options.midi:
        midi = data

        if midi[4] == 0x45:
            packet = Midi_45.parse(data)
            data = unpack(packet['data'])
        if midi[4] == 0x64:
            packet = Midi_64.parse(data)
            data = unpack(packet['data'])

    if data:
        config = ZPTC.parse(data)

        if options.dump:
            print(config)

        if options.summary:
            print("Name: %s" % config['name'])
            print("Patch Volume: %s" % config['PPRM']['reversed']['control']['volume'])
            for id in range(config['fx_count']):
                print("Effect %d: 0x%8.8X" % (id+1, config['ids'][id]))

                print("   Enabled:", config['EDTB']['effects'][id] \
                        ['reversed']['control']['enabled'])
                for param in range(1,9):
                    print("   Param %d: %d" % (param, config['EDTB']['effects'][id] \
                        ['reversed']['control']['param'+str(param)]))

        if options.outfile:
            outfile = open(options.outfile, "wb")

            if options.target:
                config['target'] = int(options.target, 16)

            # Move Bypass to end
            if options.bypass:
                for c in range(config['fx_count']-1):
                    if config['ids'][c] == 1:       # Bypass effect
                        e = config['EDTB']['effects'][c]
                        for m in range(c+1, config['fx_count']):
                            config['ids'][m-1] = config['ids'][m]
                            config['EDTB']['effects'][m-1] = config['EDTB']['effects'][m]
                        config['ids'][m] = 1
                        config['EDTB']['effects'][m] = e

            # Limit the number of effects
            if options.limit and options.limit < config['fx_count']:
                config['fx_count'] = options.limit
                config['ids'] = config['ids'][:options.limit]
                config['EDTB']['effects'] = config['EDTB']['effects'][:options.limit]

            # Convert between 1 and 2 screen versions of effects
            if options.convert1 or options.convert2:
                for id in range(config['fx_count']):
                    for item in convert:
                        if options.convert1 and config['ids'][id] == item[0]:
                            print("Converting Effect %d : 0x%8.8X -> 0x%8.8X" \
                                   % (id + 1, config['ids'][id], item[1]))
                            config['ids'][id] = item[1]
                            config['EDTB']['effects'][id]['reversed']['control']['id'] \
                                    = item[1] & 0x1FFFFFFF

                        if options.convert2 and config['ids'][id] == item[1]:
                            print("Converting Effect %d : 0x%8.8X -> 0x%8.8X" \
                                   % (id + 1, config['ids'][id], item[0]))
                            config['ids'][id] = item[0]
                            config['EDTB']['effects'][id]['reversed']['control']['id'] \
                                    = item[0] & 0x1FFFFFFF
            # force effect
            if options.effect:
                effect = int(options.effect, 16)
                for id in range(config['fx_count']):
                    for item in convert:
                        config['ids'][id] = effect
                        config['EDTB']['effects'][id]['reversed']['control']['id'] \
                                = effect & 0x1FFFFFFF

            # need to rebuild EDTB's reversed data
            for id in range(len(config['EDTB']['effects'])):
                blob = EDTB2.build(config['EDTB']['effects'][id]['reversed'])
                config['EDTB']['effects'][id]['autorev'] = blob

            # rebuild PPRM's reverse data
            if config['version'] == 1:
                blob = PPRM12.build(config['PPRM']['reversed'])
                config['PPRM']['autorev'] = blob

            data = ZPTC.build(config)

            # double build to fix 'length' in top block
            config = ZPTC.parse(data)
            data = ZPTC.build(config)

            if options.pad and options.pad > len(data):
                data = data + (b"\x00" * (options.pad - len(data)))

            if outfile:
                outfile.write(data)
                outfile.close

if __name__ == "__main__":
    main()

