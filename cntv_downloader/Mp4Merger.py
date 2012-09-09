# -*- coding: utf-8 -*-

'''
Created on Sep 9, 2012

@author: coolcute
'''
import subprocess

# ls | sort -t- -k2 -n | sed -e 's/^/-cat /g' | tr "\n" " " | xargs MP4Box new.mp4

class Mp4Merger(object):
    '''
    classdocs
    '''
    mergeCmd = "ls | sort -t- -k2 -n | sed -e 's/^/-cat /g' | tr \"\\n\" \" \" | xargs MP4Box "
    def __init__( self, workingDir, fileName):
      self.workingDir = workingDir
      self.fileName = fileName
      
    def merge(self):
        completeMergeCmd = self.mergeCmd + self.fileName
        exit_code = subprocess.call(completeMergeCmd, cwd=self.workingDir, shell=True)
        # TODO move logger into a class
        exit_code = -1;

# Tester
def main():
    mp4Merger = Mp4Merger(r"/Volumes/video/百家讲坛/王立群读宋史/tmp", r"123.mp4")
    mp4Merger.merge()

# Main method
if __name__ == '__main__':
    main()