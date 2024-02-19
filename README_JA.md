# Trainers-Legend-G-Plugin
- Trainers-Legend-Gを拡張するためのExternal Plugin(外部プラグイン)です。

## 現在使用可能な機能

- コメント付きの`config.json`を高速で編集
- Discordのアクティビティステータス、ゲーム状況をリストに表示
- プラグインの自動アップデート
- DMMを要しない迅速なゲームプレイ
- 設定のホットリロード (設定によってはゲームの再起動が必要)
- 翻訳項目の切り替え
- ゲームウィンドウの位置と比率の調整
- ......


## ファイルのアップデート機能

- プラグインの更新は、GitHub APIをベースにしており国内の逆生成サーバーを使用して速度を最適化しています
- 翻訳ファイルのホットアップデートプロジェクトは、以下から使用できます: [**Trainers-Legend-Barbecue**](https://github.com/chinosk6/Trainers-Legend-Barbecue)



# 実行

exeファイルは、[Release](https://github.com/chinosk114514/Trainers-Legend-G-External-Plugin/releases) からダウンロードできます:

- `Python 3`の環境をインストール
- 以下のパッケージをインストール: `pip install -r requirements.txt`

```
PyQt5>=5.15.4
requests>=2.26.0
pypresence==4.2.0
jsonschema>=4.6.0
```

- `main.py`を実行

```shell
python main.py
```



## pydを自分でコンパイルする

- Pythonの`zipfile`ライブラリは、ファイル名のエンコーディングに問題があるため[bit7z](https://github.com/rikyoz/bit7z)の[7-Zip](https://www.7-zip.org/)に変更できます。ライブラリは[pybind11](https://github.com/pybind/pybind11) でコンパイルされ、コンパイルされたファイルは`. /gui/umauitools.pyd`に配置されます。このバイナリは、`Python 3.8`に基づいています。もし違うバージョンのPythonを使用している場合は、自分でコンパイルをしてください。ソースコードは以下にあります: `./unzip_cpp`

### コンパイルの設定

**以下のパスはあくまでも例であり、自分で`python`と`pybind11`のインストールディレクトリに変更してください。**

- 設定のプロパティ - VC++のディレクトリ - 以下のディレクトリ:

```
C:\Users\Administrator\AppData\Local\Programs\Python\Python38\include
C:\Users\Administrator\Downloads\pybind11\include
```

- 設定のプロパティ - VC++のディレクトリ - ライブラリのディレクトリ:

```
C:\Users\Administrator\AppData\Local\Programs\Python\Python38\libs
```

- 設定のプロパティ - リンク - 追加依存関係

```
python3.lib
python38.lib
```

# パッケージ化

- [Nuitka](https://github.com/Nuitka/Nuitka)はPythonのコードをC++に変換してからコンパイルができるので作業効率が大幅に向上します


```shell
nuitka --standalone --windows-icon-from-ico=jio.ico --onefile --plugin-enable=pyqt5 --include-qt-plugins=sensible,styles main.py
```

- [pyinstaller](https://github.com/pyinstaller/pyinstaller)を使ってパッケージ化もできます
