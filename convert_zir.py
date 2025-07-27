# Convert ZIR files between known formats

from PIL import Image, ImageOps
from construct import *

#--------------------------------------------------
# For wav file output (optional)
# https://github.com/WarrenWeckesser/wavio

try:
   import wavio
   _hasWavIO = True
except ImportError:
   _hasWavIO = False
'''
_hasWavIO = False
'''

#--------------------------------------------------
# Define ZIR file format using Construct (v2.9)
# requires:
# https://github.com/construct/construct

ZIR_1U = Struct(
    "type" / Computed("1U"),

    "low" / Array(512, Float32l),
    "mid" / Array(512, Float32l),
    "high" / Array(512, Float32l),
)

ZIR_ST = Struct(
    "type" / Computed("ST"),

    "left" / Array(768, Float32l),
    "right" / Array(768, Float32l),
)

ZIR_LT = Padded(12288, 
    Struct(
    "type" / Computed("LT"),

    "low" / Array(256, Float32l),
    "mid" / Array(256, Float32l),
    "high" / Array(256, Float32l),
))

#--------------------------------------------------

def upscale_1U_to_ST(a):
    o = []
    for i in range(0, len(a), 2):
        c = a[i]
        try:
            n = a[i+1]
        except:
            n = 0
        try:
            m = a[i+2]
        except:
            m = 0
        o.append(c)
        o.append((c+n+n)/3)
        o.append((n+n+m)/3)
    return o

def downscale_1U_to_LT(a):
    o = []
    for i in range(0, len(a), 2):
        c = a[i]
        try:
            n = a[i+1]
        except:
            n = 0
        o.append((c+n)/2)
    return o

def downscale_ST_to_1U(a):
    o = []
    for i in range(0, len(a), 3):
        c = a[i]
        try:
            n = a[i+1]
        except:
            n = 0
        try:
            m = a[i+2]
        except:
            m = 0
        o.append((c+c+n)/3)
        o.append((n+m+m)/3)
    return o

def downscale_ST_to_LT(a):
    o = []
    for i in range(0, len(a), 3):
        c = a[i]
        try:
            n = a[i+1]
        except:
            n = 0
        try:
            m = a[i+2]
        except:
            m = 0
        o.append((c+n+m)/3)
    return o

def upscale_LT_to_1U(a):
    o = []
    for i in range(len(a)):
        c = a[i]
        try:
            n = a[i+1]
        except:
            n = 0
        o.append(c)
        o.append((c+n)/2)
    return o

def upscale_LT_to_ST(a):
    o = []
    for i in range(len(a)):
        c = a[i]
        try:
            n = a[i+1]
        except:
            n = 0
        o.append(c)
        o.append((c+c+n)/3)
        o.append((c+n+n)/3)
    return o

#--------------------------------------------------

def main():
    import os
    import sys
    from argparse import ArgumentParser

    parser = ArgumentParser(prog="convert-zir")
    parser.add_argument('files', metavar='FILE', nargs='+',
        help='File(s) to process')

    parser.add_argument("-d", "--dump",
        help="dump configuration to text",
        action="store_true", dest="dump")

    tpx = parser.add_mutually_exclusive_group()
    tpx.add_argument("-1", "--1U",
        help="ZIR Type 1 '_1U' = 6144 bytes, low/mid/high",
        action="store_true", dest="type_1u")
    tpx.add_argument("-2", "--ST",
        help="ZIR Type 2 '_ST' = 6144 bytes, left/right",
        action="store_true", dest="type_st")
    tpx.add_argument("-3", "--LT",
        help="ZIR Type 3 '_LT' = 12288 bytes, low/mid/high",
        action="store_true", dest="type_lt")

    opx = parser.add_mutually_exclusive_group()
    opx.add_argument("-O", "--writeback",
        help="write output back to same file",
        action="store_true", dest="writeback")
    opx.add_argument("-o", "--output",
        help="write output to FILE",
        dest="output")

    if _hasWavIO:
        parser.add_argument("-w", "--wav",
            help="write spectrum to a wav file, for easy inspection",
            dest="wav")
        parser.add_argument("-s", "--scale",
            help="wav file scale, set '0.0' for auto-scale",
            type=float, default=1.0, dest="scale")

    options = parser.parse_args()

    zir = None
    data = None
    guess = False

    if not len(options.files):
        parser.error("FILE not specified")
    else:
        print("Inspecting:", options.files[0])
        infile = open(options.files[0], "rb")
        if not infile:
            sys.exit("Unable to open FILE for reading")

        data = infile.read()
        infile.close()

        #print("length:", len(data))

    if options.output or options.writeback:
        # type specifies wanted output, so we guess at input type
        guess = True

    if not guess:
        if options.type_1u:
            zir = ZIR_1U.parse(data)
        elif options.type_st:
            zir = ZIR_ST.parse(data)
        elif options.type_lt:
            zir = ZIR_LT.parse(data)
        else:
            guess = True

    if guess:
        if len(data) == 12288:
            print("Guessing 'LT'")
            zir = ZIR_LT.parse(data)
        else:
            filename, extension = os.path.splitext(options.files[0])
            if filename[-2:] == "ST":
                print("Guessing 'ST'")
                zir = ZIR_ST.parse(data)
            elif filename[-2:] == "1U":
                print("Guessing '1U'")
                zir = ZIR_1U.parse(data)

        if not zir:
            sys.exit("unable to guess....")


    if options.dump:
        print(zir)


    if options.output or options.writeback:
        # up/down-sample data to change type
        if zir['type'] == "1U":
            if options.type_st:
                zir['left'] = upscale_1U_to_ST(zir['mid'])
                zir['right'] = upscale_1U_to_ST(zir['mid'])
                zir['type'] = "ST"
            if options.type_lt:
                zir['low'] = downscale_1U_to_LT(zir['low'])
                zir['mid'] = downscale_1U_to_LT(zir['mid'])
                zir['high'] = downscale_1U_to_LT(zir['high'])
                zir['type'] = "LT"
        if zir['type'] == "LT":
            if options.type_1u:
                zir['low'] = upscale_LT_to_1U(zir['low'])
                zir['mid'] = upscale_LT_to_1U(zir['mid'])
                zir['high'] = upscale_LT_to_1U(zir['high'])
                zir['type'] = "1U"
            if options.type_st:
                zir['left'] = upscale_LT_to_ST(zir['mid'])
                zir['right'] = upscale_LT_to_ST(zir['mid'])
                zir['type'] = "ST"
        if zir['type'] == "ST":
            if options.type_1u:
                zir['low'] = downscale_ST_to_1U(zir['left'])
                zir['mid'] = downscale_ST_to_1U(zir['left'])
                zir['high'] = downscale_ST_to_1U(zir['left'])
                zir['type'] = "1U"
            if options.type_lt:
                zir['low'] = downscale_ST_to_LT(zir['left'])
                zir['mid'] = downscale_ST_to_LT(zir['left'])
                zir['high'] = downscale_ST_to_LT(zir['left'])
                zir['type'] = "LT"

        if options.writeback:
            outfile = open(options.files[0], "wb")
            if not outfile:
               sys.exit("Unable to open FILE for writing")
        if options.output:
            outfile = open(options.output, "wb")
            if not outfile:
               sys.exit("Unable to open FILE for writing")

        if zir['type'] == "1U":
            data = ZIR_1U.build(zir)
        elif zir['type'] == "ST":
            data = ZIR_ST.build(zir)
        elif zir['type'] == "LT":
            data = ZIR_LT.build(zir)

        outfile.write(data)
        outfile.close()


    if _hasWavIO:
        if options.wav:
            if options.scale == 0:
                options.scale = "auto"

            if zir['type'] == "ST":
                wavio.write(options.wav, zir['left'], 48000, sampwidth=3, scale=options.scale)
            else:
                wavio.write(options.wav, zir['mid'], 48000, sampwidth=3, scale=options.scale)


if __name__ == "__main__":
    main()
