# -*- coding: utf-8 -*-

'''
Created on Sep 9, 2012

@author: coolcute
'''
import argparse
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
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-mp4-directory', help='the directory contains mp4s')
    parser.add_argument('-o', '--output-file-name', help='final merged mp4 file name')
    args = parser.parse_args()
    
    inputMp4DirectoryPath = args.input_mp4_directory
    outputFileName = args.output_file_name
    # mp4Merger = Mp4Merger(r"/Volumes/video/百家讲坛/王立群读宋史/tmp", r"123.mp4")
    mp4Merger = Mp4Merger(inputMp4DirectoryPath, outputFileName)
    mp4Merger.merge()

# Main method
if __name__ == '__main__':
    main()