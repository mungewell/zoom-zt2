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
    "length" / Int32ul,
    "data" / Bytes(this.length),
)

TXE1 = Struct(
    Const(b"TXE1"),
    "length" / Int32ul,
    "desc" / PaddedString(this.length, "ascii"),
)

EDTB2 = Struct( # Working with a Byte-reversed copy of data
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
    "length" / Int32ul,
    "effects" / Array(this._.fx_count, EDTB1),
)

PPRM = Struct(
    Const(b"PPRM"),
    "length" / Int32ul,
    #"pprm_dump" / Peek(HexDump(Bytes(this.length))),
    # does this contain patch volume?
    "pdata" / Bytes(this.length),
)

ZPTC = Struct(
    Const(b"PTCF"),
    "length" / Int32ul,
    "version" / Int32ul, # ???
    "fx_count" / Int32ul,

    "target" / Int32ul, # pedal that patch is for???
    "data" / Bytes(6),

    "name" / PaddedString(10, "ascii"),
    "ids" / Array(this.fx_count, Int32ul),

    "TXJ1" / TXJ1,
    "TXE1" / TXE1,
    "EDTB" / EDTB,
    "PPRM" / PPRM,
)

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

    parser.add_argument("-o", "--output", dest="outfile",
        help="write data to OUTFILE")
    parser.add_argument("-p", "--pad", type=int,
        help="pad output size to PAD bytes", dest="pad")
    parser.add_argument("-t", "--target", type=int,
        help="set the target pedal value", dest="target")

    parser.add_argument("-1", "--convert1",
        help="convert patch to use '1 screen' effects",
        action="store_true", dest="convert1")
    parser.add_argument("-2", "--convert2",
        help="convert patch to use '2 screen' effects",
        action="store_true", dest="convert2")

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

    if data:
        config = ZPTC.parse(data)

        if options.dump:
            print(config)

        if options.summary:
            print("Name: %s" % config['name'])
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
                config['target'] = options.target

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

            # need to rebuild EDTB's reversed data
            for id in range(config['fx_count']):
                #config['EDTB']['effect'][id]['reversed']['control']['enabled'] = False
                blob = EDTB2.build(config['EDTB']['effects'][id]['reversed'])
                config['EDTB']['effects'][id]['autorev'] = blob

            data = ZPTC.build(config)

            if options.pad and options.pad > len(data):
                data = data + (b"\x00" * (options.pad - len(data)))

            if outfile:
                outfile.write(data)
                outfile.close

if __name__ == "__main__":
    main()

