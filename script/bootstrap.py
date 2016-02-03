#!/usr/bin/env python

import sys
import os
import util
import shutil

SOURCE_ROOT = os.path.split(os.path.realpath(__file__))[0]
SOURCE_VENDOR = os.path.abspath(os.path.join(SOURCE_ROOT, '../vendor'))

def main():
    if not os.path.exists(SOURCE_VENDOR):
        os.makedirs(SOURCE_VENDOR)

    os.chdir(SOURCE_VENDOR)
    download_node()
    download_chromium()
    platform_specific()

def download_node():
    node_path = os.path.join(SOURCE_VENDOR, 'node')
    update_module(node_path, 'node', 'git', 'https://github.com/silkedit/node.git')
    old_path = os.getcwd()
    os.chdir(node_path)
    util.execute_stdout(['git', 'checkout', 'origin/silkedit'])
    os.chdir(old_path)

def download_chromium():
    SOURCE_CHROMIUM = os.path.join(SOURCE_VENDOR, 'chromium')
    module_list = build_list()
    for module in module_list :
        module_root = os.path.join(SOURCE_CHROMIUM, module['dir'])
        util.safe_mkdir(module_root)
        os.chdir(module_root)
        for submodule_key, submodule_url in module['modules'].iteritems():
            name_and_type = submodule_key.split(':')
            path = os.path.join(module_root, name_and_type[0])
            update_module(path, name_and_type[0], name_and_type[1], submodule_url)


    # download http file chromium/VERSION  chromium/src/base/basictypes.h
    print '3 copy missed file chromium/VERSION  chromium/src/base/basictypes.h'
    # https://chromium.googlesource.com/chromium/src/+/master/chrome/VERSION
    print '3.1 copy script/VERSION to vendor/chromium/'
    shutil.copyfile(SOURCE_ROOT + '/VERSION', os.path.join(SOURCE_CHROMIUM, 'src', 'chrome') + '/VERSION')
    # https://chromium.googlesource.com/chromium/chromium/+/master/base/basictypes.h
    print '3.2 copy script/basictypes.h to vendor/chromium/src/base/'
    shutil.copyfile(SOURCE_ROOT + '/basictypes.h', os.path.join(SOURCE_CHROMIUM, 'src', 'base') + '/basictypes.h')

def platform_specific():
    print 'apply platform dependent operation...'
    if sys.platform == 'win32':
        winsdk_dir = os.environ['WindowsSdkDir']
        if not winsdk_dir or winsdk_dir.isspace():
            print 'windows sdk not installed'
            sys.exit(-1)

        setenv_cmd_path = os.path.join(winsdk_dir, 'bin')
        setenv_cmd_path += '/SetEnv.Cmd'
        setenv_cmd_path = os.path.normpath(setenv_cmd_path)
        if not os.path.isfile(setenv_cmd_path):
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                sys.exit('need admin privilege on Windows')
            open(setenv_cmd_path, 'a').close()
    elif sys.platform == 'darwin':
        util.execute_stdout([os.path.join(SOURCE_ROOT, 'update-clang.sh')])

def build_list():
    src_url_map = {
        'dir': 'src',
        'modules': {
            'base:git': 'https://chromium.googlesource.com/chromium/src/base',
            'testing:git': 'https://chromium.googlesource.com/chromium/src/testing',
            'build:git': 'https://chromium.googlesource.com/chromium/src/build'
        }
    }
    tools_url_map = {
        'dir': 'src/tools',
        'modules': {
            'gyp:git': 'https://chromium.googlesource.com/external/gyp',
            'clang:git': 'https://chromium.googlesource.com/chromium/src/tools/clang',
            'depot_tools:zip': 'https://src.chromium.org/svn/trunk/tools/depot_tools.zip'
        }
    }
    third_party_url_map = {
        'dir': 'src/third_party',
        'modules': {
            'zlib:git': 'https://chromium.googlesource.com/chromium/src/third_party/zlib',
            'icu:git': 'https://chromium.googlesource.com/chromium/deps/icu',
            'modp_b64:git': 'https://chromium.googlesource.com/chromium/src/third_party/modp_b64',
            'libxml:tar.gz': 'https://chromium.googlesource.com/chromium/chromium/+archive/master/third_party/libxml.tar.gz'
        }
    }
    gtest_url_map = {
        'dir': 'src/testing',
        'modules': {
            'gtest:git': 'https://chromium.googlesource.com/chromium/testing/gtest'
        }
    }
    chrome_url_map = {
        'dir': 'src/chrome',
        'modules': {}
    }
    apple_apsl_url_map = {
        'dir': 'src/third_party',
        'modules': {
            'apple_apsl:tar.gz': 'https://chromium.googlesource.com/chromium/chromium/+archive/master/third_party/apple_apsl.tar.gz'
        }
    }
    url_list = [src_url_map, tools_url_map, third_party_url_map, gtest_url_map, chrome_url_map]
    if sys.platform == 'darwin':
        url_list.append(apple_apsl_url_map)
    return url_list

def update_module(path, name, type, url):
    print 'update ' + path + "---" + type + '---' + url
    if type == 'git':
        util.git_update(path, url)
    else:
        if os.path.exists(path):
            pass
        else:
            util.safe_mkdir(path)
            download_file = util.download_path(name)
            if not os.path.exists(download_file):
                util.download_http_package(url, download_file)
            if type == 'tar.gz':
                util.extract_tar_gz(download_file, path)
            elif type == 'zip':
                util.extract_zip(download_file, os.path.normpath(path + '/../'))

if __name__ == '__main__':
    sys.exit(main())
