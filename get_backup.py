#!/usr/bin/env python3
import argparse
import os.path
import configparser
import sys
from termcolor import cprint

from settings import *
from commands import *
from util import execute

def download_backup(cloud_provider, rclone_dir):
    cprint(f"Let's download the cloud backup of {cloud_provider} to {rclone_dir}", 'green')
    execute(cmd_rclone_syn_to_disk.format(cloud_provider=cloud_provider,
                                          rclone_dir=rclone_dir))
    execute(cmd_rclone_check.format(dir_to_check=rclone_dir,
                                    cloud_provider=cloud_provider))


def init():
    parser = argparse.ArgumentParser("Get the backup out of the cloud")
    parser.add_argument("--target-dir", "-t", help="Where should I put the borg file into?", required=True)
    parser.add_argument("--cloud-provider", "-c", help="Which cloud provider should I take", required=True)
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read(location_rclone_config)
    list_cloud_provider = config.sections()
    if args.cloud_provider not in list_cloud_provider:
        cprint(f"ERROR: Cloud provider not found. Available: {list_cloud_provider}", "red")
        sys.exit(1)
    if not os.path.exists(args.target_dir):
        cprint(f"ERROR: Target dir '{args.target_dir} does not exist", "red")
        sys.exit(1)
    os.environ['RCLONE_CONFIG'] = location_rclone_config
    download_backup(args.cloud_provider, args.target_dir)


if __name__ == '__main__':
    init()
