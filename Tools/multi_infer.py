import infer
import concurrent.futures as cf
import os

in_dir = '/home/thebeast/Desktop/repos/KNOX-preprocessing/Tools/output'

for file in os.listdir(in_dir,):
    if file.endswith(".png"):
        infer.main(os.path.join(in_dir,file))

