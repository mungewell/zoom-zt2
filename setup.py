from cx_Freeze import setup, Executable

base = None    

executables = [Executable("zoom-zt2.py", base=base)]

packages = ["construct", "os", "optparse", "sys", "binascii", "mido", "rtmidi_python"]
options = {
    'build_exe': {    
        'packages':packages,
        'excludes':["pygame", "numpy"],
    },    
}

setup(
    name = "zoom-zt2.py",
    options = options,
    version = "0.1.0.0",
    description = 'Script for Upload Effects/Configuration to ZOOM G Series Pedals',
    executables = executables
)
