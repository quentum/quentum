import sys
import os
import argparse
import util
import platform

SOURCE_ROOT = os.path.split(os.path.realpath(__file__))[0]
SOURCE_VENDOR = os.path.abspath(os.path.join(SOURCE_ROOT, '../vendor'))

def main():
    args = parse_args()
    setup_environment(args)
    build_node(args)
    build_chromium(args)

def parse_args():
    parser = argparse.ArgumentParser(description='build vendor')
    parser.add_argument('--enable_static', action='store_true', default=False, help = 'build to static library')
    parser.add_argument('--enable_debug', action='store_true', default=True, help='build with configuration debug')
    parser.add_argument('--enable_release', action='store_true', default=False, help='build with configuration release')
    return parser.parse_args()

def setup_environment(args):
    defines = 'component=shared_library'
    if args.enable_static:
        defines = 'component=static_library'

    depot_tools_path = os.path.join(SOURCE_VENDOR, 'chromium/src/tools/depot_tools')
    depot_tools_path = os.path.normpath(depot_tools_path)
    os.environ['PATH'] += os.pathsep + depot_tools_path
    os.environ['GYP_GENERATORS'] = 'ninja'
    os.environ['GYP_DEFINES'] = defines
    if sys.platform == 'win32':
        os.environ['DEPOT_TOOLS_WIN_TOOLCHAIN'] = '0'
        os.environ['GYP_MSVS_VERSION'] = '2013'

def build_node(args):
    old_path = os.getcwd()
    os.chdir(os.path.join(SOURCE_VENDOR, 'node'))
    if sys.platform == 'darwin':
        params = ['chmod', 'u+x', 'configure']
        util.execute_stdout(params)
        params = ['./configure']
        if args.enable_static:
            params.append('--enable-static')
        else:
            params.append('--enable-shared')
        if args.enable_debug:
            params.append('--debug')
        util.execute_stdout(params)
        util.execute_stdout(['make'])
    elif sys.platform == 'win32':
        params = ['vcbuild.bat']
        if not args.enable_static:
            params.append('shared')
        if args.enable_debug:
            params.append('debug')
        if args.enable_release:
            params.append('release')
        util.execute_stdout(params)
    os.chdir(old_path)

def build_chromium(args):
    old_path = os.getcwd()

    # generate ninja project files
    os.chdir(os.path.join(SOURCE_VENDOR, 'chromium'))
    params = ['python', 'src/build/gyp_chromium', 'src/base/base.gyp']
    util.execute_stdout(params)

    # build with ninja
    os.chdir(os.path.join(SOURCE_VENDOR, 'chromium', 'src'))
    config_list = []
    if args.enable_debug:
        config_list.append('Debug')
    if args.enable_release:
        config_list.append('Release')

    for config in config_list:
        build_ninja = os.path.normpath(os.path.join(os.getcwd(), 'out', config))
        params = ['ninja', '-C', build_ninja, 'base']
        util.execute_stdout(params)

    os.chdir(old_path)

if __name__ == '__main__':
    sys.exit(main())
