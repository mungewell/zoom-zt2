
This repo contains a Python script and associated files for uploading effects to 
the ZOOM G Series pedals (G1Four and possibly others), and the new 'MS-plus' pedals.

Inspired by another project, which allows for the re-packing of effects into the
ZOOM F/W Installer binary. Unfortunately that technique proved unsuccessful on the 
G1Four.
https://github.com/Barsik-Barbosik/Zoom-Firmware-Editor

The script has been tested with G1Four, it is expected/hoped that it will also 
work on the G1XFour, B1Four, B1XFour, G3n, G3Xn, B3n and G5n. It is also at least partially compatible with the MS-50G+, MS-60B+, MS-70CDR+ and MS-80IR+.

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

Note: For MS-Plus pedals ensure the tick boxes for 'include-ZIC' (ICON) and 
'include-ZIR' (IR) are selected, where appropriate. If the icon file is missing
you will find a blank space in the library and you will not be able to identify
which effect it represents.

The 'zoomzt2.py' script can alternatively be used from the command line to modify
a 'FLST_SEQ.ZT2' file and/or to install/remove effects from a pedal.

__WARNING__: There is no online resource for MS-plus effects (zd2/icon/ir) files, a factory 
reset __WILL NOT RESTORE__ removed/deleted files! Please take back-ups of anything
you indend to remove/delete from the pedal.

## Effects

The effects used by the G1Four are '.ZD2' format, these are also used on the G3n and G5n 
pedals. They are not compatible with the '.ZDL' effects used on the 'MultiStomp' pedals.

Each effect is identified by a 32bit ID, the upper 8bits are a group ID. The ID/Group for
the MS-plus pedals use a different ID/Group schema to the G1Four/etc.

Note: it is not yet know whether MS-plus ZD2 are compatible with G1Four/etc, or vice-versa.

Mostly effect binaries are common between the G1Four and the G3n/G5n, although it would appear 
that some effects are imcompatible due to hardware differences - these appear to be denoted with
'1U' (only one screen on G1Four) and '3S' suffixes on the filenames.

Regarding the nomenclature `{effect-name-tag}{suffix}.ZD2`:

|suffix|meaning|details
|------|-------|-----------
| 1U   | single unit (screen)| on one-screen units the wide-effects, which have 8 parameters (controlled by 4 knobs), need to be paged over 3pages: (3params + Dummy), (3params+Dummy), (2params + Dummy); the Dummy parameters are used for paging.
| 3S | 3000ms (delay)| the big-boy units in G Series are able to process 4000ms delays/reverb effects but the G1/B1/A1 FOUR units are able to handle only up to 3000ms (3sec). This is likely due to memory or processing power limits. Asking these units to produce over 3sec delay results in kinda noisy whoosh.

For these reasons, Zoom engineers created the respective 1U, 3S versions of _most_ but not all corresponding modules and put the respective names of the "unrestricted" modules into `GUARDZDL.ZT2` to avoid possible problems if anyone tried to load such modules on the restricted hardware. 

The AC-2 and AC-3 use a similar '.ZD2' effects, but they do not have a LCD display
and all effects are in a special 'group 29'.



## Command Line Options

The 'zoomzt2.py' script is controlled via command line options. Primarily it used for editing
the contents of '.zt2' files, but it also allows for upload/download to the pedal.

If you want to install the required dependencies from PIP, you can do: `python3 -m venv ../zt2-venv && source ../zt2-venv/bin/activate && pip install -r requirements.txt`.

```
$ python3 zoomzt2.py --help
usage: zoomzt2 [-h] [-d] [-s] [-b BUILD] [-A ADD] [-v VER] [-i ID] [-D DELETE] [-N] [-t TOGGLE] [-w] [-R] [-S] [-I] [-U]
               [--install-only] [--uninstall-only] [-e] [--include-zic] [--include-zir] [--download-all] [-a]
               [-p PATCHDOWN | -P PATCHUP | -c] [--old-patch] [-M MIDISKIP]
               FILE [FILE ...]

positional arguments:
  FILE                  File(s) to process

options:
  -h, --help            show this help message and exit
  -d, --dump            dump configuration to text
  -s, --summary         summarized configuration in human readable form
  -b BUILD, --build BUILD
                        output commands required to build this FLTS_SEQ
  -A ADD, --add ADD     add effect to FLST_SEQ
  -v VER, --ver VER     effect version (use with --add)
  -i ID, --id ID        effect id (use with --add)
  -D DELETE, --delete DELETE
                        delete effect from FLST_SEQ
  -N, --not-add         add effect to FLST_SEQ, but as uninstalled
  -t TOGGLE, --toggle TOGGLE
                        toggle install/uninstall state of effect NAME in FLST_SEQ
  -w, --write           write config back to same file
  -R, --receive         Receive FLST_SEQ from attached device
  -S, --send            Send FLST_SEQ to attached device
  --include-zic         When downloading or uploading effect binary, include the corrsponding .ZIC icon file
  --include-zir         When downloading or uploading effect binary, include the corrsponding .ZIR impulse response file
  --old-patch           Use the 'old' method for reading patches
  -M MIDISKIP, --midiskip MIDISKIP
                        Skip devices when connecting, ie when you have multiple pedals

ZD2:
  Process ZDL2 effect file(s)

  -I, --install         Install effect binary to attached device, updating FLST_SEQ
  -U, --uninstall       Remove effect binary from attached device, updating FLST_SEQ
  --install-only        Install effect binary to attached device without affecting FLST_SEQ
  --uninstall-only      Remove effect binary from attached device without affecting FLST_SEQ
  -e, --effectdown      Download effect binary with name FILE
  --download-all        Download all files on pedal to directory FILE
  -a, --available       Print out the available diskspace after action

ZPTC:
  Process ZPTC patch file

  -p PATCHDOWN, --patchdown PATCHDOWN
                        download specific zptc
  -P PATCHUP, --patchup PATCHUP
                        upload specific zptc
  -c, --curdown         download current zptc
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

Turn tuner on/off
```
$ amidi -p hw:1,0,0 -S 'F0 52 00 6e 64 0b F7'
or
$ amidi -p hw:1,0,0 -S 'F0 52 00 6e 64 0c F7'
```

When in 'Editor mode' the pedal will continuously send note information
```
3427328 + 0: 0xf052006e640bf7
3427328 + 0: 0xb0620c <- note A=1, A#=2, .. G#=b, no_note/"_"=c
3427328 + 0: 0xb06300 <- degree 1=flat, 8=perfect, f=sharp
```

And tuning information (440Hz = 0x05)
```
52855808 + 0: 0xf052006e6403000a0c0600000000f7
52886528 + 0: 0xf052006e6403000a0c0700000000f7
52913152 + 0: 0xf052006e6403000a0c0800000000f7
                                  ^^ Tuning
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

Note: in PC mode the only function on pedal is to change Lo/Mid/Hi tone, and Volume.

### Effects settings

Configure Current Patch Effect(s)
```
$ amidi -p hw:1,0,0 -S 'f0 52 00 6e 64 03 00 01  02 3d 17 00 00 00 f7'
                                                    ^^ ^^ ^^ ^^ ^^ value
                                                    (7bit little endian)
                                                 ^^ param
                                             ^^ config effect in slot (0..8)
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

Note: The parameter value is converted to 7bit to allow sending over midi,
this means values need to be adjusted. For example setting slot 0 to an effect
of 0x01000010 (COMP.ZD2) would be sent as:

`amidi -p hw:1,0,0 -S 'f0 52 00 6e 64 03 00 00 01 10 00 00 08 00 f7'`

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
                                                 ^^ n-th position (0..9)
                                             09 = Patch ASCII name
```

Change Current Patch Volume Level (seen under 'Settings'/'Patch')
```
$ amidi -p hw:1,0,0 -S 'f0 52 00 6e 64 03 00 0a  00 3d 00 00 00 00 f7'
                                                    ^^ Value
                                                 00 = Patch volume level
                                             0a = System setting
```

### Other Settings

Change Tempo (for Rythm/Looper)
```
$ amidi -p hw:1,0,0 -S 'f0 52 00 6e 64 03 00 0a  02 3d 00 00 00 00 f7'
                                                    ^^ ^^ Value
                                                 02 = Tempo
                                             0a = System setting
```

Change Autosave
```
$ amidi -p hw:1,0,0 -S 'f0 52 00 6e 64 03 00 0a  0f 01 00 00 00 00 f7'
                                                    ^^ Off/On (0..1)
                                                 0f = Autosave
                                             0a = System setting
```

### Patch Files

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
