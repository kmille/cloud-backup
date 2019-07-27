import configparser
from termcolor import cprint
import subprocess
import os.path
from settings import *

def check_dir(dir):
    if not os.path.exists(dir):
        print(f"Directory '{dir}' not found")
        sys.exit(1)

def execute(cmd, hide_output=False):
    cprint(f"Executing: '{cmd}'", 'magenta')
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    stdout, stderr = p.communicate()
    stdout = stdout.decode().strip()
    stderr = stderr.decode().strip()
    if p.returncode != 0:
        cprint(f"The following command failed:\n{cmd}\nStderr: {stdout}\nStderr: {stderr}", 'red')
        sys.exit(1)
    if not hide_output:
        if len(stdout) > 0:
            print(stdout)
        if len(stderr) > 0:
            print(stderr)
    return stdout



