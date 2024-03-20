nuitka --standalone --windows-disable-console --windows-icon-from-ico=jio.ico --onefile -o legend_g_plugin.exe --plugin-enable=pyqt5 --include-qt-plugins=sensible,styles main.py
pyinstaller -F --noconsole -i jio.ico -n legend_g_plugin.exe main.py --upx-dir "E:\upx" --clean
E:\python\python311\Scripts\pyinstaller -F --noconsole -i jio.ico -n legend_g_plugin.exe main.py --upx-dir "E:\upx" --clean

pyinstaller legend_g_plugin.exe.spec --upx-dir "E:\upx"

pyinstaller -F --noconsole -i jio.ico -n legend_g_plugin.exe main.py --upx-dir "E:\upx" --clean --add-data uncompressed.tpk;./UnityPy/resources/
pause
pause