echo off
REM script to run the GUI version of ZoomZT2

if exist build\exe.win-amd64-3.12\zoomzt2-gui.exe (
	echo Found 'pre-built/py2exe' file
	build\exe.win-amd64-3.12\zoomzt2-gui.exe %*
) else (
	echo Trying to run Python script directly
	echo (note: system may be missing some required modules)
	py.exe zoomzt2-gui.py
)

