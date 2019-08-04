

# What do we want?
- We want an encrypted cloud backup
- We use several free cloud storages for redundancy
- automated
- tested

# What do we do technically?
- We have a bunch of files
- We use borg backup (https://borgbackup.readthedocs.io). We make a backup to a local directory
- We put the local directory of borg in da cloud
    - therefore we use rclone which is easy to use and supports a lot of cloud providers (https://rclone.org/)
- We want a check? Was the backup successfully?
    - before the backup: create a file with the current time stamp
    - after the backup: mount it and compare the time stamp


# how to make a cloud backup
## Setup
```bash
pwgen 32 1
export BORG_PASSPHRASE=aiXo9Igh9phai0oow7Foomeeci9ziePh
borg init --encryption=repokey-blake2 /home/kmille/tmp/rclone/borg-files
checkout settings.py

create rclone.conf (or use rclone config)
[dropbox]
type = dropbox
token = {"access_token":"token","token_type":"bearer","expiry":"0001-01-01T00:00:00Z"}
```

## Let's make a backup
```bash
source venv/bin/activate
set borg key as environment variable
pyton make_backup.py
```


# how to get the backups locally (from a different client)
```bash
(venv) kmille@homebox cloud-backup master % python get_backup.py -t /home/kmille/tmp/cloud-backup-tmp/manual-test -c onedrive
Let's download the cloud backup of onedrive to /home/kmille/tmp/cloud-backup-tmp/manual-test
Executing: 'rclone sync onedrive: /home/kmille/tmp/cloud-backup-tmp/manual-test --progress'
Transferred:      279.756M / 279.756 MBytes, 100%, 22.776 MBytes/s, ETA 0s
Errors:                 0
Checks:                 0 / 0, -
Transferred:           17 / 17, 100%
Elapsed time:       12.2s
Executing: 'rclone check /home/kmille/tmp/cloud-backup-tmp/manual-test onedrive:'
2019/08/04 09:59:08 NOTICE: One drive root '': 0 differences found
2019/08/04 09:59:08 NOTICE: One drive root '': 17 matching files

(venv) kmille@homebox cloud-backup master % export BORG_PASSPHRASE=yolo123
(venv) kmille@homebox cloud-backup master % borg mount /home/kmille/tmp/cloud-backup-tmp/manual-test::cloud-backup-2019-08-04T09:45:11 /home/kmille/mnt 
```


# commands I use (it's basically a python wrapper around bash commands
```bash

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
```
