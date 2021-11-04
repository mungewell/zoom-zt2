#!/usr/bin/python
#
# Script decode drum table/patterns from Zoom F/W
# (c) Simon Wood, 10 May 2020
#

from argparse import ArgumentParser
from construct import *

#--------------------------------------------------
# Define drum table/patterns using Construct (v2.9)
# requires:
# https://github.com/construct/construct

Item = Struct(
    "name" / PaddedString(9, "ascii"),
    "sample1" / PaddedString(12, "ascii"),
    "sample2" / PaddedString(12, "ascii"),
    "sample3" / PaddedString(12, "ascii"),
    "sample4" / PaddedString(12, "ascii"),
    "sample5" / PaddedString(12, "ascii"),
    "sample6" / PaddedString(12, "ascii"),
    "sample7" / PaddedString(12, "ascii"),
    "sample8" / PaddedString(12, "ascii"),
    "sample9" / PaddedString(12, "ascii"), # Should be 'Click.raw'
    "tsig_top" / Byte,
    "tsig_bot" / Byte,
    "bars" / Byte,
    "pointer" / Int24ul,
    Const(b"\xC0"),
)

Table = Struct(
    "items" / GreedyRange(Item),
)

Sample = Struct(
    "end" / Peek(Byte),
    Check(this.end != 0xF0),
    "element" / BitStruct(
        "sample" / Default(BitsInteger(4), 0),
        "volume" / Default(BitsInteger(4), 0),
    ),
    "skiptime" / Byte,
)

Pattern = Struct(
    "config1" / Byte,
    "config2" / Byte,
    Const(b"\x00"),
    "elements" / GreedyRange(Sample),
    Const(b"\xF0"),
)

#-------------------------------------------

parser = ArgumentParser(prog="decode_patterns")
parser.add_argument('files', metavar='FILE', nargs=1,
    help='File to process')

parser.add_argument("-d", "--dump", help="dump configuration to text",
    action="store_true", dest="dump")

parser.add_argument("-T", "--table",
    help="offset to pattern table within '129' file (G1Four V2.00 use 407304)",
    dest="table")
parser.add_argument("-D", "--drums",
    help="offset to drum data within '129' file (G1Four V2.00 use 457078)",
    dest="drums")

parser.add_argument("-P", "--pointer",
    help="print out the pointers to drum data as a sorted list",
    action="store_true", dest="pointer")

parser.add_argument("-p", "--pattern",
    help="print drum data representation for a pattern", dest="pattern")

options = parser.parse_args()

if not len(options.files):
    parser.error("FILE not specified")


# Read data from file
infile = open(options.files[0], "rb")
if not infile and not options.test:
    sys.exit("Unable to open config FILE for reading")
else:
    data = infile.read()
    infile.close()

table = []
if options.table:
    table = Table.parse(data[int(options.table):])

if options.dump:
    print(table)

if options.drums:
    pointers = []
    for item in table['items']:
        new = [item['name'], int(item['pointer'])]
        pointers.append(new)

    # sort them for future use    
    pointers = sorted(pointers, key=lambda tup: tup[1])

    if options.pointer:
        first = pointers[0][1]
        for item in pointers:
            print("%s %s " % (item[0].ljust(10, ' '), str.format('0x{:08X}', item[1] - first + int(options.drums))))

    if options.pattern and int(options.pattern) <= len(pointers):
        first = pointers[0][1]
        item = table['items'][int(options.pattern)-1]
        pointer = int(item['pointer']) - first + int(options.drums)

        count = 0
        ascii = [list(" " * 200) for i in range(9)]
        graphic = "0123456789ABCDEF"
        graphic = "..,,ooxxOOXX$$##"

        pattern = Pattern.parse(data[pointer:])
        if options.dump:
            print(pattern)

        for element in pattern['elements']:
            ascii[element['element']['sample'] - 1][count] = graphic[element['element']['volume']]
            if element['skiptime']:
                #count += 1
                count += element['skiptime']

        print("Pattern %s : %s (%s)" % (options.pattern, item['name'], str.format('0x{:08X}', pointer)))
        print("Bars %d (%d/%d)" % (item['bars'], item['tsig_top'], item['tsig_bot']))
        print("---")
        for key in range(9):
            print("%s :%s:" % (item['sample'+str(key+1)].ljust(12, ' '), "".join(ascii[key][:count])))
