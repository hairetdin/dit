"""
#author     :   @hairetdin https://github.com/hairetdin
#How to use:
import winmount 
win_server = '192.168.1.1' # set ip address or full domain name 
share_folder = 'example' # set windows server share folder 
mount_point = 'h:' - for windows OS or mount_point='/mnt/windows_share' for linux 
user_name = 'server_user_name' # perhaps, full domain name need - username@domain.com
user_password = 'server_user_password'
new_share = winmount.share(win_server, share_folder, mount_point, user_name, user_password) # connection share class create
new_share.mount() # mount windows share folder
new_share.options() # show connection options - 'network_folder':'', 'mount_point':'','user':''
new_share.umount() # windows share folder unmount

#Windows share mount in linux required cifs-util installed
#You can create symlink to mountwin.py (available in winmount folder) and run mountwin.py from command line to mount windows share
#Also, to run this lib ( utilizing mount.cifs) on my linux machine i append string in /etc/sudoers:
#username   ALL=(ALL)       NOPASSWD: /sbin/mount.cifs /mnt/windows_share, /bin/umount /mnt/windows_share
"""
import sys
import os

try:
    import winmount
except ImportError:
    import sys
    from os.path import abspath, dirname, split
    parent_dir = split(dirname(abspath(__file__)))[0]
    sys.path.append(parent_dir)

if sys.platform == "win32":
    from winmount.win import Mount
if sys.platform == "darwin":
    from winmount.osx import Mount
if sys.platform == "linux":
    from winmount.linux import Mount

def share(win_server, share_folder, mount_point, user, password):
    new_share = Mount(win_server, share_folder, mount_point, user, password)
    return new_share
