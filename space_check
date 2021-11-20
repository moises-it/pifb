#!/usr/bin/python3
#Place this in /usr/local/bin/ on the remote server that you wish to backup to
#This allows the script to run this using ssh and instantly know the freespace and compare it to the drive size
import os
#Change this to target directory when using network backup
backup_directory = "/home/pibackup/backup"
path = os.path.join(backup_directory,"")
path_stat = os.statvfs(path)
path_space_available = (path_stat.f_frsize * path_stat.f_bfree)
print(path_space_available)
