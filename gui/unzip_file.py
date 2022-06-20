import zipfile
import os


def config_update(config_before: dict, new_config: dict):
    keepList = {
        "enableConsole",
        "enableLogger",
        "dumpStaticEntries",
        "maxFps",
        "unlockSize",
        "uiScale",
        "replaceFont",
        "autoFullscreen",
        "externalPlugin",
        "openExternalPluginOnLoad",
        "autoChangeLineBreakMode",
    }

    ret_cfg = new_config.copy()
    for k in ret_cfg:
        if k in keepList:
            if k in config_before:
                ret_cfg[k] = config_before[k]
    return ret_cfg

    # config_edit = config_before.copy()
    # for k in new_config:
    #     if k not in config_edit:
    #         config_edit[k] = new_config[k]
    # return config_edit



def unzip_file(zipfilename, unziptodir):
    if not os.path.exists(unziptodir.encode('cp437').decode('gbk')):
        os.mkdir(unziptodir.encode('cp437').decode('gbk'), 0o777)
    zfobj = zipfile.ZipFile(zipfilename)
    for name in zfobj.namelist():
        name = name.replace('\\', '/')
        if name.endswith('/'):
            _dir = os.path.join(unziptodir, name).encode('cp437').decode('gbk')
            if not os.path.exists(_dir):
                os.mkdir(_dir)
        else:
            ext_filename = os.path.join(unziptodir, name)
            ext_dir = os.path.dirname(ext_filename)
            if not os.path.exists(ext_dir):
                os.mkdir(ext_dir.encode('cp437').decode('gbk'), 0o777)
            outfile = open(ext_filename.encode('cp437').decode('gbk'), 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()


if __name__ == '__main__':
    unzip_file("rfe.zip", "./")
