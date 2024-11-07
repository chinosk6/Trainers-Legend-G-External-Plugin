import sys
import os
import ctypes

system_dir = os.path.expandvars(r'%SystemRoot%\System32')
os.environ['PATH'] = system_dir + os.pathsep + os.environ['PATH']

ctypes.CDLL(os.path.join(system_dir, 'dxgi.dll'))

for i in sys.argv:
    if i.startswith("--resource_path="):
        work_path = i[len("--resource_path="):]
        os.chdir(work_path)
        break

import gui

# sys.stdout = open("legend_g_plugin_log.log", "a", encoding="utf8")


if __name__ == '__main__':
    uic = gui.GuiMain()
    uic.ui_run_main()
