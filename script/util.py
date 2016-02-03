import os
import sys
import subprocess
import urllib
import tarfile
import zipfile
import shutil
import errno
import platform

SOURCE_ROOT = os.path.split(os.path.realpath(__file__))[0]
SOURCE_DOWNLOAD = os.path.abspath(os.path.join(SOURCE_ROOT, '../vendor/download'))

# if dst path exists, use command 'git pull', otherwise, use command 'git clone url'
def git_update(dst, url):
    if os.path.exists(dst):
        old = os.getcwd()
        os.chdir(dst)
        try:
            execute_stdout(['git', 'pull'])
        except Exception as e:
            pass
        os.chdir(old)
    else:
        execute_stdout(['git', 'clone', url])

def targz_update(dst, url):
    safe_mkdir(dst)
    execute_stdout(['git', 'clone', url])


def rm_rf(path):
  try:
    shutil.rmtree(path)
  except OSError:
    pass

def safe_mkdir(path):
  try:
    os.makedirs(path)
  except OSError as e:
    if e.errno != errno.EEXIST:
      raise

def execute(argv, env=os.environ):
  print ' '.join(argv)
  try:
    output = subprocess.check_output(argv, stderr=subprocess.STDOUT, env=env)
    print output
    return output
  except subprocess.CalledProcessError as e:
    print e.output
    raise e

def execute_stdout(argv, env=os.environ):
    print ' '.join(argv)
    try:
      subprocess.check_call(argv, env=env)
    except subprocess.CalledProcessError as e:
      print e.output
      raise e

def extract_zip(zip_path, dst):
  if sys.platform == 'darwin':
    # Use unzip command on Mac to keep symbol links in zip file work.
    execute(['unzip', zip_path, '-d', dst])
  else:
    with zipfile.ZipFile(zip_path) as z:
      z.extractall(dst)

def extract_tar_gz(tar_gz_path, dst):
    if sys.platform == 'darwin':
        # Use gunzip command on Mac to keep symbol links in zip file work.
        old = os.getcwd()
        safe_mkdir(dst)
        os.chdir(dst)
        gunzip = subprocess.Popen(('gunzip', '-c', tar_gz_path), stdout=subprocess.PIPE)
        output = subprocess.check_output(('tar', 'xopf', '-'), stdin=gunzip.stdout)
        gunzip.wait()
        os.chdir(old)
    else:
        tar = tarfile.open(tar_gz_path, 'r')
        for item in tar:
            tar.extract(item, dst)

def download_http_package(url, path):
    module_context = urllib.URLopener()
    module_context.retrieve(url, path, download_hook)

def download_hook(count, blocksize, totalsize):
    if totalsize != -1:
        percent = int(count * blocksize * 100 / totalsize);
        sys.stdout.write("\r%2d%%" % percent)
    else:
        sys.stdout.write('.')
    sys.stdout.flush()

def download_path(name):
    safe_mkdir(SOURCE_DOWNLOAD)
    return SOURCE_DOWNLOAD + '/' + name
