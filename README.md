This program written in mostly python, gives the user a GUI in order to easily backup files on the press of a button via drive to drive or drive to network copy.
It utilizes rsync for the bulk of its functions.

Network feature needs private key setup to the destination server with .ssh/config alias setup, this way rsync can work without a password.
  Also, it needs space_check to be on the remote server, preferrably placed in /usr/local/bin or as a bash alias. 
  This is how pifb determines there is enough space on the remote server
