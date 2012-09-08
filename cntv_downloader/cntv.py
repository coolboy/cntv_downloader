# -*- coding: utf-8 -*-

'''
Created on Aug 26, 2012

@author: coolcute

Require: wget MP4Box 
'''

import argparse
import os
import errno
import urllib
import logging
import subprocess
import concurrent.futures
from urllib.request import urlopen
from html.parser import HTMLParser

# Init logging
def getLogger():
    return logging.getLogger(__name__)

def initLogging(logFilePath):
    logging.disable(logging.NOTSET)
    
    logger = getLogger()
    logger.setLevel(logging.INFO)
    
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # create console handler
    sh = logging.StreamHandler()
    sh.setLevel(logging.WARN)
    sh.setFormatter(formatter)
    
    # create file handler
    fh = logging.FileHandler(logFilePath, mode='a', encoding='utf-8')
#    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    
    # append handlers
    logger.addHandler(sh)
    logger.addHandler(fh)

# create a subclass and override the handler methods
class FlvcdHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag != 'input' :
            return
        
        attrsDict = dict() 
        for key, value in attrs:
            attrsDict[key] = value
        
        if 'name' not in attrsDict or 'value' not in attrsDict:
            return
        
        if attrsDict['name'] == 'inf':
            value = attrsDict['value']
            if r'<$>' in value :
                return
            
            self.urls = attrsDict['value'].splitlines()
        elif attrsDict['name'] == 'filename':
            self.title = attrsDict['value']
        else:
            return
        
    def getTitle(self):
        return self.title
    def getUrls(self):
        return self.urls

'''
http://kejiao.cntv.cn/bjjt/classpage/video/20120824/100886.shtml
http://www.flvcd.com/parse.php?kw=http%3A%2F%2Fkejiao.cntv.cn%2Fbjjt%2Fclasspage%2Fvideo%2F20120824%2F100886.shtml&format=high&flag=one
'''

def getCNTVDownloadLinksWithTitle(cntvUrl):
    cntvUrlEncoded = urllib.parse.quote(cntvUrl, safe='');
    flvcdPrefix = 'http://www.flvcd.com/parse.php?kw='
    flvcdSuffix = '&format=high&flag=one'
    
    flvcdQuery = flvcdPrefix + cntvUrlEncoded + flvcdSuffix

    with urlopen(flvcdQuery) as webFile:
        text = webFile.read().decode ('gb2312');

    flvcdParser = FlvcdHTMLParser()
    flvcdParser.feed(text);
    
    return {'Title' : flvcdParser.getTitle(), 'Urls' : flvcdParser.getUrls()}

def wgetDownload(download_url, filename):
    wget_opts = 'wget ' + download_url + ' -O "' + filename + '" -q'
    if os.path.exists(download_url):
        wget_opts.append('-c')
    # When shell is true, we should not use list
    exit_code = subprocess.call(wget_opts, shell=True)
    if exit_code != 0:
        raise Exception(filename + ' : wget exited abnormaly')

def downloadUrlToFile(url, saveFilePath):
    logger = getLogger()
    logger.info('Saving ' + url + ' to ' + saveFilePath)
    wgetDownload(url, saveFilePath)
    logger.info('Done ' + saveFilePath)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else: raise

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-urls-path', help='urls as txt file location')
    parser.add_argument('-o', '--output-folder', help='output folder')
    args = parser.parse_args()
    
    inputFilePath = args.input_urls_path
    outputFolderPath = args.output_folder
    
    initLogging('cntv.log')
    logger = getLogger()
    
    with open(inputFilePath) as file:
        content = file.readlines()
    
    # Download cntv mp4s with the urls and titles as the folder name
    # TODO : refactor to merge when everything is fine
    future_to_url = dict()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # for each cntv url ( one video ) 
        for cntvUrl in content :
            logger.info( 'Getting ' + cntvUrl)
            titleToUrls = getCNTVDownloadLinksWithTitle(cntvUrl);
            
            saveFileDirPath = outputFolderPath + '/' + titleToUrls['Title']
            mkdir_p(saveFileDirPath)
            
            for mp4url in titleToUrls['Urls']:
                mp4urlPath = urllib.parse.urlparse(mp4url)[2] # 2 is the index for path
                fileName = saveFileDirPath + mp4urlPath[mp4urlPath.rindex(r'/'):] # find the file name
                future_to_url[executor.submit(downloadUrlToFile, mp4url, fileName)] = mp4url

    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        if future.exception() is not None:
            logger.warning('%r generated an exception: %s' % (url, future.exception()))
            
    # TODO : Merge the parted mp4
            
# Main method
if __name__ == '__main__':
    main()
