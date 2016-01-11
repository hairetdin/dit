from winmount.base import MountBase

from winmount import win_drive_letter

class Mount(MountBase):
    def __init__(self, win_server, share_folder, mount_point, user, password):
        
        """ Windows share folder mount prepare """
        
        share_folder = share_folder.replace("/", "\\")
        mount_point = mount_point.replace(':','')
        network_folder = r'\\%s\%s' %(win_server, share_folder)
        drive_letter = win_drive_letter.get()
        if len(mount_point) > 1:
            mount_point = drive_letter['free'][-1]
        elif mount_point in drive_letter['use']:
            mount_point = drive_letter['free'][-1]
            print('Drive letter %s used, changed mount_point drive letter to %s' %(drive_letter['use'], drive_letter['free'][-1]))
        mount_point+=':'
        print('Mount_point - %s' %(mount_point))
        print('In the python code next use mount() function - to mount windows share folder, and use umount() function - to unmount')
        
        self.options = {'network_folder':network_folder, 'mount_point':mount_point,'user':user}
        self.success = []
        self.error = []
        mount_cmd = "net use {mount_point} {network_folder} /user:{user} {password}"
        self.mount_cmd = mount_cmd.format(network_folder=network_folder,
                                            mount_point=mount_point,
                                            user=user,
                                            password=password)
        self.umount_cmd = "net use {mount_point} /delete /y".format(mount_point=mount_point)