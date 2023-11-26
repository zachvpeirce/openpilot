# PFEIFER - MAPD
import os
import subprocess
import urllib.request

from openpilot.common.realtime import Ratekeeper
import stat

from openpilot.selfdrive.mapd_manager import COMMON_DIR, MAPD_PATH, VERSION_PATH

VERSION = 'v1.7.0'
URL = f"https://github.com/pfeiferj/openpilot-mapd/releases/download/{VERSION}/mapd"


def download():
  if not os.path.exists(COMMON_DIR):
    os.makedirs(COMMON_DIR)
  with urllib.request.urlopen(URL) as f:
    with open(MAPD_PATH, 'wb') as output:
      output.write(f.read())
      os.fsync(output)
      current_permissions = stat.S_IMODE(os.lstat(MAPD_PATH).st_mode)
      os.chmod(MAPD_PATH, current_permissions | stat.S_IEXEC)
    with open(VERSION_PATH, 'w') as output:
      output.write(VERSION)
      os.fsync(output)


def mapd_thread():
  rk = Ratekeeper(0.05, print_delay_threshold=None)

  while True:
    try:
      if not os.path.exists(MAPD_PATH):
        download()
        continue
      if not os.path.exists(VERSION_PATH):
        download()
        continue
      with open(VERSION_PATH) as f:
        content = f.read()
        if content != VERSION:
          download()
          continue

      process = subprocess.Popen(MAPD_PATH)
      process.wait()
    except Exception as e:
      print(e)

    rk.keep_time()


def main():
  mapd_thread()


if __name__ == "__main__":
  main()
