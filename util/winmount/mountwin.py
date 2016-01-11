#!/usr/bin/python
try:
    import winmount
except ImportError:
    import sys
    from os.path import abspath, dirname, split
    parent_dir = split(dirname(abspath(__file__)))[0]
    sys.path.append(parent_dir)
    import winmount

if __name__ == '__main__':
    
    if len (sys.argv) == 6:
        win_server = sys.argv[1]
        share_folder = sys.argv[2]
        mount_point = sys.argv[3]
        user_name = sys.argv[4]
        user_password = sys.argv[5]
        new_share = winmount.share(win_server, share_folder, mount_point, user_name, user_password)
        new_share.mount()
    else:
        print ("Windows share mount in linux required cifs-util installed")
        print ("Enter mandatory options: win_server, share_folder, mount_point, user_name, user_password")
        print ("Example usage:")
        print ("python mountwin.py 192.168.1.1 share_folder_name /mnt/winshare winusername winuserpass")