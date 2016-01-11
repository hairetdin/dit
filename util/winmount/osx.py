from winmount.base import MountBase

class Mount(MountBase):
    def __init__(self, win_server, share_folder, mount_point, user, password):
        """ Mac osx share folder mount prepare """
        
        share_folder = share_folder.replace("/", "\\")
        network_folder = r'//%s/%s' %(win_server, share_folder)

        print('Mount_point - %s' %(mount_point))
        print('In the python code next use mount() function - to mount windows share folder, and use umount() function - to unmount')
        self.mount_point = mount_point
        self.options = {'network_folder':network_folder, 'mount_point':mount_point,'user':user}
        self.success = []
        self.error = []

        mount_cmd = "mount_smbfs //{user}:{password}@{network_folder} {mount_point}"
        self.mount_cmd = mount_cmd.format(network_folder=network_folder,
                                            mount_point=mount_point,
                                            user=user,
                                            password=password)
        self.umount_cmd = "umount {mount_point}".format(mount_point=mount_point)