nuitka --standalone --windows-disable-console --windows-icon-from-ico=jio.ico --onefile -o legend_g_plugin.exe --plugin-enable=pyqt5 --include-qt-plugins=sensible,styles main.py
pyinstaller -F --noconsole -i jio.ico -n legend_g_plugin_windows7.exe main.py
pause
pause