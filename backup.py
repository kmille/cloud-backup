#!/usr/bin/env python3
import subprocess
import os.path
import os
import sys
from termcolor import cprint

from ipdb import set_trace

location_files_to_backup = "/home/kmille/tmp/files-to-backup"
location_borg_files = "/home/kmille/tmp/borg-files"
location_tmp = "/home/kmille/tmp/tmp"
prefix_backup_name = "cloud-backup"

# BEGIN COMMANDS
# BEGIN make backup
cmd_create_backup = f"borg create -C zlib,6 --verbose --stats {location_borg_files}::{prefix_backup_name}-{{now}} {location_files_to_backup}"
cmd_check_backup = "borg check --verbose {location_borg_files}"
# END make backup

# BEGIN push backups in da cloud
cmd_rclone_sync_to_cloud = "rclone sync {location_borg_files} {cloud_provider}: --progress"
cmd_rclone_check = "rclone check {dir_to_check} {cloud_provider}:"
cmd_rclone_size = "rclone size {cloud_provider}:"
# END push backups in da cloud

cmd_rclone_syn_to_disk = "rclone sync {cloud_provider}: {rclone_dir} --progress"
#export RCLONE_CONFIG=/home/kmille/tmp/rclone/rclone.conf

cmd_borg_list_last_backup_name = "borg list {rclone_dir} --json | jq '.archives[-1].name'"
cmd_borg_mount_backup = "borg mount {rclone_dir}::{backup_name} {mount_dir}"

cmd_borg_umount = "borg umount {mount_dir}"
# END COMMANDS

os.environ['BORG_RELOCATED_REPO_ACCESS_IS_OK'] = 'YES'


def check_dir(dir):
    if not os.path.exists(dir):
        print(f"Directory '{dir}' not found")
        sys.exit(1)


def check_directories():
    check_dir(location_files_to_backup)
    check_dir(location_borg_files)
    check_dir(location_tmp)


def execute(cmd):
    cprint(f"Executing: '{cmd}'", 'magenta')
    #return
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    stdout, stderr = p.communicate()
    stdout = stdout.decode().strip()
    stderr = stderr.decode().strip()
    if p.returncode != 0:
        cprint(f"The following command failed:\n{cmd}\nStderr: {stdout}\nStderr: {stderr}", 'red')
        sys.exit(1)
    if len(stdout) > 0:
        print(stdout)
    if len(stderr) > 0:
        print(stderr)
    return stdout


def do_backup():
    cprint("Let's make a backup", 'green')
    execute(cmd_create_backup)
    execute(cmd_check_backup.format(location_borg_files=location_borg_files))

def put_backup_in_da_cloud(cloud_provider):
    cprint("Let's put the backup in da cloud", 'green')
    execute(cmd_rclone_sync_to_cloud.format(location_borg_files=location_borg_files,
                                            cloud_provider=cloud_provider))
    execute(cmd_rclone_check.format(dir_to_check=location_borg_files,
                                    cloud_provider=cloud_provider))
    execute(cmd_rclone_size.format(cloud_provider=cloud_provider))


def download_backup(cloud_provider, rclone_dir):
    execute(cmd_rclone_syn_to_disk.format(cloud_provider=cloud_provider,
                                          rclone_dir=rclone_dir))
    execute(cmd_rclone_check.format(dir_to_check=rclone_dir,
                                    cloud_provider=cloud_provider))
def test_backup(cloud_provider):
    cprint(f"Let's test the cloud backup of {cloud_provider}", 'green')
    rclone_dir = os.path.join(location_tmp, cloud_provider + "-files")
    print(f"Clearing {rclone_dir}")
    execute(f"rm -rf {rclone_dir}")
    execute(f"mkdir {rclone_dir}")
    download_backup(cloud_provider, rclone_dir)
    mount_backup(cloud_provider, rclone_dir)
    print(f"Done with testing the {cloud_provider} backup. Clearing {rclone_dir}")
    execute(f"rm -rf {rclone_dir}")



def mount_backup(cloud_provider, rclone_dir):
    cprint(f"Let's test the cloud backup of {cloud_provider}", 'green')
    mount_dir = os.path.join(location_tmp, cloud_provider + "-mnt")
    print(f"Clearing {mount_dir}")
    execute(f"rm -rf {mount_dir}")
    execute(f"mkdir {mount_dir}")
    execute(cmd_check_backup.format(location_borg_files=rclone_dir))
    last_backup_name = execute(cmd_borg_list_last_backup_name.format(rclone_dir=rclone_dir))
    print("this is the backup_name: {}".format(last_backup_name))
    execute(cmd_borg_mount_backup.format(rclone_dir=rclone_dir,
                                         backup_name=last_backup_name,
                                         mount_dir=mount_dir))
    execute(cmd_borg_umount.format(mount_dir=mount_dir))
    execute(f"rm -rf {mount_dir}")


check_directories()
do_backup()
put_backup_in_da_cloud("dropbox")
test_backup("dropbox")
