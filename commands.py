from settings import *
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


