import os

def get():
    drive_letter = {'free':[], 'use':[]}
    for drive in (list("abcdefghijklmnopqrstuvwxyz")):
        if os.path.exists("%s:\\" % (drive)):
            #print("Drive letter '%s' is in use." % (drive))
            drive_letter['use'].append(drive)
        else:
            #print("Drive letter '%s' is not in use." % (drive))
            drive_letter['free'].append(drive)
    return drive_letter