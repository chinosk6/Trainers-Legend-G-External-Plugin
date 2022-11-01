# Trainers-Legend-G-Plugin
- [Trainers-Legend-G](https://github.com/MinamiChiwa/Trainers-Legend-G)的外部插件, 用于增强插件本体功能



## 目前有的功能

- 快捷编辑`config.json`, 并附带注释
- Discord Rich Presence, 向您的列表展示游戏状态
- 插件自动更新
- 快速重启游戏, 无需DMM



# 运行

您可以前往[Release](https://github.com/chinosk114514/Trainers-Legend-G-External-Plugin/releases)下载exe文件, 若您不喜欢使用exe, 请：

- 安装`Python 3`环境
- 安装以下包: `pip install -r requirements.txt`

```
PyQt5>=5.15.4
requests>=2.26.0
pypresence>=4.2.0
jsonschema>=4.6.0
```

- 运行`main.py`

```shell
python main.py
```



## 自行编译pyd

- 由于 Python 自带的 `zipfile` 库有文件名编码问题, 故更改为  `c++ minizip` 库, 使用 [pybind11](https://github.com/pybind/pybind11) 编译, 编译文件放置于 `./gui/umauitools.pyd`。此二进制文件基于 `Python 3.8`, 若您的Python版本不一致, 请自行编译, 源码位于: `./unzip_cpp`

### 编译配置

**以下路径配置仅为例子, 请自行修改为自己的`python` 和 `pybind11` 的安装目录**

- 配置属性 - VC++目录 - 包含目录:

```
C:\Users\Administrator\AppData\Local\Programs\Python\Python38\include
C:\Users\Administrator\Downloads\pybind11\include
```

- 配置属性 - VC++目录 - 库目录:

```
C:\Users\Administrator\AppData\Local\Programs\Python\Python38\libs
```





# 打包

- 建议使用[Nuitka](https://github.com/Nuitka/Nuitka)进行打包。Nuitka可以将Python代码转换为C++后编译, 极大提高了运行速度

```shell
nuitka --standalone --windows-icon-from-ico=jio.ico --onefile --plugin-enable=pyqt5 --include-qt-plugins=sensible,styles main.py
```



- 您也可以使用[pyinstaller](https://github.com/pyinstaller/pyinstaller)进行打包

