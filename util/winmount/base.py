import os, sys
from subprocess import Popen, PIPE

class MountBase():
    mount_cmd = None
    umount_cmd = None
    win_server = None
    mount_point = None
    share_folder = None
    user_name = None
    options = {'network_folder':'', 'mount_point':'','user':''}
    success = []
    error = []

    def _prepare(self):
        if sys.platform == "win32":
            pass
        else:
            if not os.path.exists(self.mount_point):
                print('creating %s folder for mounting' % self.mount_point)
                os.makedirs(self.mount_point)

    def mount(self):
        self._prepare()

        p1 = Popen(self.mount_cmd.split(" "), stdout=PIPE, stderr=PIPE)
        out, err = [x.decode(sys.stdout.encoding) for x in  p1.communicate()]
        if out:
            print('----------------------------------------------')
            print('Windows network folder success mounted to %s' %(self.options['mount_point']))
            print(out)
            #print('Mounted with options %s' %(self.options))
            self.success.append(out)
        elif err:
            print('----------------------------------------------')
            print('Network folder did not connect:')
            print(err)
            #print('Mount command: ', self.mount_cmd)
            #print('Check connection options and retry again')
            #print('Error mounted with options %s' %(self.options))
            self.error.append(err)

    def umount(self):
        Popen(self.umount_cmd, stdout=PIPE, shell=True)

    def options(self):
        return self.options

    def error(self):
        return self.error

    def success(self):
        return self.success