from cx_Freeze import setup, Executable

base = None    

executables = [
        Executable("zoomzt2.py", base=base),
        Executable("zoomzt2-gui.py", base=base),
        Executable("decode_effect.py", base=base),
        Executable("decode_preset.py", base=base),
        ]

packages = ["construct", "os", "argparse", "sys", "binascii", "mido", "rtmidi"]
options = {
    'build_exe': {    
        'packages':packages,
        'excludes':["pygame", "numpy"],
    },    
}

setup(
    name = "zoomzt2.py",
    options = options,
    version = "1.2.0.0",
    description = 'Script for Upload Effects/Configuration to ZOOM G Series Pedals',
    executables = executables
)
