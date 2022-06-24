import gui
import win32file
import sys
import os
import psutil

sys.stdout = open("legend_g_plugin_log.log", "a", encoding="utf8")

def check_runs(name: str):
    selfid = os.getpid()
    for i in psutil.process_iter():
        if i.name() == name:
            if i.pid != selfid:
                print(f"检测到重复运行程序: {name} ({i.pid}), 将尝试关闭")
                os.system(f"taskkill /F /pid {i.pid}")
                os.system(f"taskkill /pid {i.pid}")


def is_open(filename):
    try:
        if not os.path.isfile(filename):
            return False
        vHandle = win32file.CreateFile(filename, win32file.GENERIC_READ, 0, None,
                                       win32file.OPEN_EXISTING,
                                       win32file.FILE_ATTRIBUTE_NORMAL, None)
        if int(vHandle) == win32file.INVALID_HANDLE_VALUE:
            return True
        win32file.CloseHandle(vHandle)
        return False
    except Exception as e:
        # print(e)
        return True


if __name__ == '__main__':
    # if is_open("legend_g_plugin_log.log"):
    #     # print("由于文件 legend_g_plugin_log.log 被占用, 程序退出")
    #     sys.exit(0)
    # self_name = os.path.split(sys.argv[0])[1]
    # check_runs(self_name)

    uic = gui.GuiMain()
    uic.ui_run_main()
