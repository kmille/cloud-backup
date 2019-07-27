#!/usr/bin/env python3
from termcolor import cprint
import json
import sys

from settings import *
from util import *
from ipdb import set_trace

list_cloud_provider = []

cmd_rclone_lsjson = "rclone lsjson --recursive {cloud_provider}:"
cmd_rclone_delete = "rclone delete {cloud_provider}:{path}"

def init():
    global list_cloud_provider
    check_dir(location_files_to_backup)
    check_dir(location_borg_files)
    check_dir(location_tmp)
    os.environ['BORG_RELOCATED_REPO_ACCESS_IS_OK'] = 'YES'
    os.environ['RCLONE_CONFIG'] = location_rclone_config
    config = configparser.ConfigParser()
    config.read(location_rclone_config)
    list_cloud_provider = config.sections()

def purge_files_for_provider(cloud_provider):
    files_text = execute(cmd_rclone_lsjson.format(cloud_provider=cloud_provider))
    files_json = json.loads(files_text)
    for file in files_json:
        execute(cmd_rclone_delete.format(cloud_provider=cloud_provider,
                                                   path=file['Path']))
    

if __name__ == '__main__':
    init()
    for cloud_provider in list_cloud_provider:
        purge_files_for_provider(cloud_provider)
