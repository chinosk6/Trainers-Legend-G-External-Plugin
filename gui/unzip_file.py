import os

try:
    from . import umauitools
    unz_stat = 0
except:
    import zipfile
    unz_stat = 1


def config_update(config_before: dict, new_config: dict):
    # keepList = {
    #     "enableConsole",
    #     "enableLogger",
    #     "dumpStaticEntries",
    #     "maxFps",
    #     "unlockSize",
    #     "uiScale",
    #     "replaceFont",
    #     "autoFullscreen",
    #     "externalPlugin",
    #     "openExternalPluginOnLoad",
    #     "autoChangeLineBreakMode",
    # }

    ret_cfg = new_config.copy()
    for k in config_before:
        ret_cfg[k] = config_before[k]

    # for k in ret_cfg:
    #     if k in keepList:
    #         if k in config_before:
    #             ret_cfg[k] = config_before[k]
    return ret_cfg



def unzip_file_built_in(zipfilename, unziptodir):
    if not os.path.exists(unziptodir.encode('utf-8').decode('utf-8')):
        os.mkdir(unziptodir.encode('utf-8').decode('utf-8'), 0o777)
    zfobj = zipfile.ZipFile(zipfilename)
    for name in zfobj.namelist():
        name = name.replace('\\', '/')
        if name.endswith('/'):
            _dir = os.path.join(unziptodir, name).encode('utf-8').decode('utf-8')
            if not os.path.exists(_dir):
                os.mkdir(_dir)
        else:
            ext_filename = os.path.join(unziptodir, name)
            ext_dir = os.path.dirname(ext_filename)
            if not os.path.exists(ext_dir):
                os.mkdir(ext_dir.encode('utf-8').decode('utf-8'), 0o777)
            outfile = open(ext_filename.encode('utf-8').decode('utf-8'), 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()

def unzip_file_cpp(zipfilename, unziptodir):
    unzip_stat = umauitools.Unzip.decompress_file_lib(zipfilename, unziptodir, os.path.abspath("7z.dll"))
    if unzip_stat != "ok":
        raise RuntimeError(f"Unzip failed: {unzip_stat}")


unzip_file = unzip_file_built_in if unz_stat == 1 else unzip_file_cpp
