from cx_Freeze import setup, Executable

base = None    

executables = [Executable("zoomzt2-gui.py", base=base)]

packages = ["construct", "os", "argparse", "sys", "binascii", "mido", "rtmidi"]
options = {
    'build_exe': {    
        'packages':packages,
        'excludes':["pygame", "numpy"],
    },    
}

setup(
    name = "zoomzt2-gui.py",
    options = options,
    version = "0.4.0.0",
    description = 'Script for Upload Effects/Configuration to ZOOM G Series Pedals',
    executables = executables
)
