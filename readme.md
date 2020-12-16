
This repo contains a Python script and associated files for uploading effects to 
the ZOOM G Series pedals (G1Four and possibly others).

Inspired by another project, which allows for the re-packing of effects into the
ZOOM F/W Installer binary. Unfortunately that technique proved unsuccessful on the 
G1Four.
https://github.com/Barsik-Barbosik/Zoom-Firmware-Editor

The script has been tested with G1Four, it is expected/hoped that it will also 
work on the G1XFour, B1Four, B1XFour, G3n, G3Xn, B3n and G5n.

This project is not supported/authorized by ZOOM, use at your own risk.

## Operation.

![Screen Shot](/pictures/ZoomZT2-GUI.png)

The 'zoomzt2-gui.py' script uses MIDI SysEx to control the pedal, and functions
on Linux and Windows. A pre-built Windows binary is provided in releases for
convience for those who down have/want Python install.

In order to install a new effect, the binary for the effect must first be located - 
which can be extracted from the F/W Installer binary via 'Zoom-Firmware-Editor'.

Once the script is started it will attempt to connect with the pedal, if not found
check the connection and press 'Connect'. Click 'Select Effect' and navigate to 
where you have stored the binary for the desired effect.

The 'Info' window will show some basic parameters for the effect. Click 'Install'
and the effect will be uploaded to the pedal. The 'Effects' and 'Files' tabs allow
you to see what is already present on the pedal.

The 'zoomzt2.py' script can alternatively be used from the command line to modify
a 'FLST_SEQ.ZT2' file and/or to install/remove effects from a pedal.

## Effects

The effects used by the G1Four are '.ZD2' format, these are also used on the G3n and G5n 
pedals. They are not compatible with the '.ZDL' effects used on the 'MultiStomp' pedals.

Mostly effect binaries are common between the G1Four and the G3n/G5n, although it would appear 
that some effects are imcompatible due to hardware differences - these appear to be denoted with
'1U' (only one screen on G1Four) and '3S' suffixes on the filenames.

The is also a 'GUARDZDL.ZT2' file within the F/W which blacklists some effects from the
G3/G5.

The AC-2 and AC-3 use a similar '.ZD2' effects, but they do not have a LCD display
and all effects are in a special 'group 29'.

## Command Line Options

The 'zoomzt2.py' script is controlled via command line options. Primarily it used for editing
the contents of '.zt2' files, but it also allows for upload/download to the pedal.

```
$ python3 zoomzt2.py -h
Usage: zoomzt2.py [options] FILENAME

Options:
  -h, --help            show this help message and exit
  -d, --dump            dump configuration to text
  -s, --summary         summarized configuration in human readable form
  -b BUILD, --build=BUILD
                        output commands required to build this FLTS_SEQ
  -A ADD, --add=ADD     add effect to FLST_SEQ
  -v VER, --ver=VER     effect version (use with --add)
  -i ID, --id=ID        effect id (use with --add)
  -D DELETE, --delete=DELETE
                        delete effect from FLST_SEQ
  -t TOGGLE, --toggle=TOGGLE
                        toggle install/uninstall state of effect NAME in
                        FLST_SEQ
  -w, --write           write config back to same file
  -R, --receive         Receive FLST_SEQ from attached device
  -S, --send            Send FLST_SEQ to attached device
  -I INSTALL, --install=INSTALL
                        Install effect binary to attached device
  -U UNINSTALL, --uninstall=UNINSTALL
                        Remove effect binary from attached device
  -p PATCH, --patch=PATCH
                        download specific patch (10..59)
  -P UPLOAD, --upload=UPLOAD
                        upload specific patch (10..59)
```

## MIDI Operation

The two scripts (above) use MIDI to communicate with the pedal(s), the
following is my attempt to document those packets - more for interest than
any real purpose.

Unless you are trying to do something funky, or are just nerdy, you don't 
need to know this....

### MIDI structure; address + command + parameters

Most actions are triggered by SysEx packets, and the G1Four responds on 
'Address' `52 00 6e`. This may be different for other pedals in the family.

One exception is 'Select Bank/Program', which used PC/CC messages
```
$ amidi -p hw:1,0,0 -S 'b0 20 00 c0 03'
                               ^     ^
                               |     +--- Program (0..9)
                               +--------- Bank (0..4)
```

Request bank/program ID, response is in 'normal' MIDI CC/PC messages.
```
$ amidi -p hw:1,0,0 -S 'f0 52 00 6e 33 f7'
control_change channel=0 control=0 value=0 time=0
control_change channel=0 control=32 value=4 time=0
program_change channel=0 program=4 time=0
```

Configure Tempo, for drum machine/looper
```
$ amidi -p hw:1,0,0 -S 'f0 52 00 6e 64 03 00 0a 02 75 00 00 00 00 f7'
                                                   ^^ ^^
                                                   ++-++---- Tempo lo/hi (ie. set to 117 BPM)
```

Set Master Volume
```
$ amidi -p hw:1,0,0 -S 'f0 52 00 6e 64 03 00 0a 00 20 00 00 00 00 f7'
                                                   ^^
                                                   ++---- Volume
```

Turn tuner on, when in 'Editor mode' the pedal will continuously send note information
```
$ amidi -p hw:1,0,0 -S 'F0 52 00 6e 64 0b F7'

3427328 + 0: 0xf052006e640bf7
3427328 + 0: 0xb0620c <- note A=1, A#=2, .. G#=b, no_note/"_"=c
3427328 + 0: 0xb06300 <- degree 1=flat, 8=perfect, f=sharp
```

Turn tuner off
```
$ amidi -p hw:1,0,0 -S 'F0 52 00 6e 64 0c F7'
```

### Modes

Some actions can only be performed when the pedal is switch to a particular
mode.

Editor Mode - sends CC's/SysEx on configuration change
```
$ amidi -p hw:1,0,0 -S 'F0 52 00 6e 50 F7'
```

Exit Editor Mode
```
$ amidi -p hw:1,0,0 -S 'F0 52 00 6e 51 F7'
```

Enter PC mode
```
$ amidi -p hw:1,0,0 -S 'F0 52 00 6e 52 F7'
```

Exit PC Mode
```
$ amidi -p hw:1,0,0 -S 'F0 52 00 6e 53 F7'
```

### Effects settings

Configure Current Patch Effect(s)
```
$ amidi -p hw:1,0,0 -S 'f0 52 00 6e 64 03 00 01  02 3d 17 00 00 00 f7'
                                                    ^^ ^^ value lo/hi
                                                 ^^ param
                                             ^^ display slot (0..8)
param 0: effect on/off (0,1)
param 1: effect type
param 2: dial 1 (left most)
param 3: dial 2
param 4: dial 3
param 5: dial 4 (right most)
param 6: dial 5 (pg 2, if applicable)
param 7: dial 6
param 8: dial 7
param 9: dial 8
```

The 'display slot' is nominally 0 through 4. However if the patch includes
'large effects' (with more that 4 active parameters) they will consume 2 slots
each, meaning that the next effect will skip a slot (be higher by 1).

For G1Four if slot is larger than allowable (ie more than 5 effects in use, but 
upto 8), the first slot will be affected. I assume this is to allow more effects
on the G5n and G11.

Note: G1Four/similar pages the dials (on screen) in groups of 3 if more than 
4 dials are active, the right most dial is used to change which are displayed.

Change Current Patch Name (character by character)
```
$ amidi -p hw:1,0,0 -S 'f0 52 00 6e 64 03 00 09  02 3d 00 00 00 00 f7'
                                                    ^^ ASCII character
                                                 ^^ nth position (0..9)
```

Change Current Patch Level (seen under 'Settings'/'Patch')
```
$ amidi -p hw:1,0,0 -S 'f0 52 00 6e 64 03 00 0a  00 3d 00 00 00 00 f7'
                                                    ^^ Patch Level
```

### Patches

Request Current Patch Info (need to be in 'Editor Mode')
```
$ amidi -p hw:1,0,0 -S 'f0 52 00 6e 29 f7'
```

Request Specific Patch Info (note: slightly longer reply).
```
$ amidi -p hw:1,0,0 -S 'F0 52 00 6e 09 00 04 09 F7'
                                           ^  ^
                                           |  +-- Program (0..9)
                                           +----- Bank (0..4)
```

Read display information of current patch, which is mostly text based.
(can be saved to a file and processed with 'decode_screens.py')
```
$ amidi -p hw:2,0,0 -S 'F0 52 00 6e 64 02 00 00 00 F7'
                                           ^  ^
                                           |  +-- End Screen
                                           +----- Start Screen
```
