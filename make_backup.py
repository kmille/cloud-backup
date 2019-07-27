#!/usr/bin/env python3
import configparser
import arrow
import os.path
import os
import sys
from termcolor import cprint

from ipdb import set_trace

from settings import *
from util import *

list_cloud_provider = []

# BEGIN COMMANDS
# BEGIN make backup
cmd_borg_create_backup = f"borg create -C zlib,6 --verbose --stats {location_borg_files}::{prefix_backup_name}-{{now}} {location_files_to_backup}"
cmd_borg_check_backup = "borg check --verbose {location_borg_files}"
# END make backup

# BEGIN push backups in da cloud
cmd_rclone_sync_to_cloud = "rclone sync {location_borg_files} {cloud_provider}: --progress"
cmd_rclone_check = "rclone check {dir_to_check} {cloud_provider}:"
cmd_rclone_size = "rclone size {cloud_provider}:"
# END push backups in da cloud

cmd_rclone_syn_to_disk = "rclone sync {cloud_provider}: {rclone_dir} --progress"

cmd_borg_list_last_backup_name = "borg list {rclone_dir} --json | jq -r '.archives[-1].name'"
cmd_borg_mount_backup = "borg mount {rclone_dir}::{backup_name} {mount_dir}"

cmd_borg_umount = "borg umount {mount_dir}"
# END COMMANDS


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


def create_backup_test_file():
    cprint("Let's create the file to test the backup", 'green')
    file_abs = os.path.join(location_files_to_backup, test_backup_filename)
    with open(file_abs, "w") as f:
        f.write(str(arrow.now()))


def check_backup_test_file(mountpoint):
    for dir_name, __, files in os.walk(mountpoint):
        for file in files:
            if file == test_backup_filename:
                file_abs = os.path.join(dir_name, file)
                break
    with open(file_abs, "r") as f:
        backup_creation_time = arrow.get(f.read())
    now = arrow.now()
    diff = now - backup_creation_time
    cprint(f"Let's check if the backup work", "green")
    print(f"Time backup created: {backup_creation_time}")
    print(f"Time now:            {now}")
    print(f"Time diff: {diff}")
    if diff.days == 0:
        cprint(f"Checked the backup. Looks good \o/", "green")
    else:
        cprint(f"Error: Seems like the backup does not work. diff.days={diff.days}", "red")
        sys.exit(1)


def do_backup():
    cprint("Let's make a borg backup", 'green')
    create_backup_test_file()
    execute(cmd_borg_create_backup)
    execute(cmd_borg_check_backup.format(location_borg_files=location_borg_files))
    cprint("Done making a brog backup", 'green')


def put_backup_in_da_cloud(cloud_provider):
    cprint(f"Let's put the borg files in da {cloud_provider} cloud", 'green')
    execute(cmd_rclone_sync_to_cloud.format(location_borg_files=location_borg_files,
                                            cloud_provider=cloud_provider))
    execute(cmd_rclone_check.format(dir_to_check=location_borg_files,
                                    cloud_provider=cloud_provider))
    cprint("Done putting the borg files in da cloud", 'green')


def download_backup(cloud_provider, rclone_dir):
    cprint(f"Let's download the cloud backup of {cloud_provider} to {rclone_dir}", 'green')
    execute(cmd_rclone_syn_to_disk.format(cloud_provider=cloud_provider,
                                          rclone_dir=rclone_dir))
    execute(cmd_rclone_check.format(dir_to_check=rclone_dir,
                                    cloud_provider=cloud_provider))

def test_backup(cloud_provider):
    cprint(f"Let's test the cloud backup of {cloud_provider}", 'green')
    rclone_dir = os.path.join(location_tmp, cloud_provider + "-files")
    print(f"Clearing {rclone_dir}")
    execute(f"rm -rf {rclone_dir}; mkdir {rclone_dir}")
    download_backup(cloud_provider, rclone_dir)
    mount_test_umount_backup(cloud_provider, rclone_dir)
    print(f"Clearing {rclone_dir}")
    execute(f"rm -rf {rclone_dir}")



def mount_test_umount_backup(cloud_provider, rclone_dir):
    cprint(f"Let's mount the last the cloud backup of {cloud_provider}", 'green')
    mount_dir = os.path.join(location_tmp, cloud_provider + "-mnt")
    print(f"Clearing {mount_dir}")
    execute(f"rm -rf {mount_dir}; mkdir {mount_dir}")
    execute(cmd_borg_check_backup.format(location_borg_files=rclone_dir))
    last_backup_name = execute(cmd_borg_list_last_backup_name.format(rclone_dir=rclone_dir))
    print(f"Last backup name: {last_backup_name}")
    execute(cmd_borg_mount_backup.format(rclone_dir=rclone_dir,
                                         backup_name=last_backup_name,
                                         mount_dir=mount_dir))
    check_backup_test_file(mount_dir)
    execute(cmd_borg_umount.format(mount_dir=mount_dir))
    execute(f"rm -rf {mount_dir}")


def print_used_storage_for_provider(cloud_provider):
    cprint(f"Used storage for {cloud_provider}", 'green')
    execute(cmd_rclone_size.format(cloud_provider=cloud_provider))


if __name__ == '__main__':
    init()
    do_backup()
#    cloud_provider = "google-drive"
#    put_backup_in_da_cloud(cloud_provider)
#    test_backup(cloud_provider)
#    exit()

    for cloud_provider in list_cloud_provider:
        put_backup_in_da_cloud(cloud_provider)
        test_backup(cloud_provider)
    #for cloud_provider in list_cloud_provider:
        #print_used_storage_for_provider(cloud_provider)
