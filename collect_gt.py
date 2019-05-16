import os
import shutil

gt_dir = './gt'

ALL_file = os.path.join(gt_dir, 'ALL')
BACKUP_file = os.path.join(gt_dir, 'ALL_bak')
if os.path.isfile(ALL_file):
    shutil.copyfile(ALL_file, BACKUP_file)

with open(ALL_file, 'w') as all:
    for gt_f in os.listdir(gt_dir):
        gt_f = os.path.join(gt_dir, gt_f)
        if not os.path.isfile(gt_f):
            continue
        if not os.path.splitext(gt_f)[-1].endswith('txt'):
            continue
        with open(gt_f) as f:
            for l in f:
                all.write(l)
