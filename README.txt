## Setup
pwgen 32 1
export BORG_PASSPHRASE=aiXo9Igh9phai0oow7Foomeeci9ziePh
borg init --encryption=repokey-blake2 /home/kmille/tmp/rclone/borg-files

create rclone.conf
[dropbox]
type = dropbox
token = {"access_token":"token","token_type":"bearer","expiry":"0001-01-01T00:00:00Z"}



# Create Backup
echo $(date) > /home/kmille/tmp/rclone/files-to-backup/backup_check
borg create -C zlib,6 --verbose --stats /home/kmille/tmp/rclone/borg-files/::cloud-backup-{now} /home/kmille/tmp/rclone/files-to-backup
borg check /home/kmille/tmp/rclone/borg-files --verbose



# Put the backup in da cloud
export RCLONE_CONFIG=/home/kmille/tmp/rclone/rclone.conf
rclone sync /home/kmille/tmp/rclone/borg-files/ dropbox: --dry-run --progress
rclone sync /home/kmille/tmp/rclone/borg-files/ dropbox: --progress
rclone check /home/kmille/tmp/rclone/borg-files/ dropbox: 
rclone size dropbox: 

# Test backup 
rm -rf /tmp/rclone-tmp
mkdir /tmp/rclone-tmp
rclone sync dropbox: /tmp/rclone-tmp --progress
rclone check dropbox: /tmp/rclone-tmp 

export BORG_RELOCATED_REPO_ACCESS_IS_OK=YES
borg check /tmp/rclone-tmp --verbose
borg list /tmp/rclone-tmp 
borg list /tmp/rclone-tmp --json | jq '.archives[-1].name'
export BACKUP_NAME=$(borg list /tmp/rclone-tmp --json | jq -r '.archives[-1].name')

borg mount /tmp/rclone-tmp::$BACKUP_NAME /home/kmille/mnt2
find /home/kmille/mnt2/ -name backup_check -exec cat {} \;

borg umount /home/kmille/mnt2
rm -rf /tmp/rclone-tmp




todo:
- test backup with backup_check file
- config file: yaml of backups
- python wrapper
    - log all output
    - exit if something fails
    - print summary
