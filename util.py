import os
import subprocess

def run(command, return_stdout=False):
    print "RUNNING:", command
    pipe = subprocess.PIPE if return_stdout else None
    proc = subprocess.Popen(command, shell=True, stdout=pipe)
    return proc.communicate()[0]

def remove_file(filename):
    print "Removing file", filename
    os.remove(filename)
