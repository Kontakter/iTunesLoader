import os
import subprocess

def run(command, return_stdout=False):
    print "RUNNING:", command
    pipe = subprocess.PIPE if return_stdout else None
    proc = subprocess.Popen(command, shell=True, stdout=pipe)
    stdout = proc.communicate()[0]
    if proc.returncode != 0:
        raise Exception("suprocess interrupted with error: %d" % proc.returncode)
    return stdout

def remove_file(filename):
    print "Removing file", filename
    os.remove(filename)
