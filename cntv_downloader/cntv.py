# -*- coding: utf-8 -*-

'''
Created on Aug 26, 2012

@author: coolcute
'''

import argparse
import os
import errno
import urllib
import subprocess
import sys
import concurrent.futures
from urllib.request import urlopen
from html.parser import HTMLParser

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
tester : http://www.pythonregex.com/
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
    wget_opts = ['/opt/local/bin/wget', download_url, '-O', filename, '-q']
    if os.path.exists(download_url):
        wget_opts.append('-c')
    exit_code = subprocess.call(wget_opts)
    if exit_code != 0:
        raise Exception(filename + ' : wget exited abnormaly')

def downloadUrlToFile(url, saveFilePath):
    print('Saving ' + url + ' to ' + saveFilePath)
    wgetDownload(url, saveFilePath)
    print('Done ' + saveFilePath)
    '''
    print('Saving ' + url + ' to ' + saveFilePath)
    retryCount = 0
    while retryCount < 3:
        try:
            urllib.request.urlretrieve(url, saveFilePath)
        except Exception as exp:
            print('Exception : ' + str(exp))
            retryCount += 1
        
    print('Done ' + saveFilePath)
    '''

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
    
    with open(inputFilePath) as file:
        content = file.readlines()
    
    # Read file with cntv video link inside
    future_to_url = dict()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        for cntvUrl in content :
            print( 'Getting ' + cntvUrl)
            titleToUrls = getCNTVDownloadLinksWithTitle(cntvUrl);
            
            saveFileDirPath = outputFolderPath + '/' + titleToUrls['Title']
            mkdir_p(saveFileDirPath)
            
            for mp4url in titleToUrls['Urls']:
                mp4urlPath = urllib.parse.urlparse(mp4url)[2] # 2 for path
                fileName = saveFileDirPath + mp4urlPath[mp4urlPath.rindex(r'/'):] # file the file name
                future_to_url[executor.submit(downloadUrlToFile, mp4url, fileName)] = mp4url

    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        if future.exception() is not None:
            print('%r generated an exception: %s' % (url, future.exception()))
#        else:
#            print('Succeed')
    
    '''
        # Generate download urls file with title
        fileName = outputFolderPath + '/' + titleToUrls['Title'] + '.txt'
        with open(fileName, 'w') as outputFile:
            mp4Urls = titleToUrls['Urls']
            
            print( 'Wrting ' + fileName + ' with ' + str(len(mp4Urls)) + ' urls')
            for mp4Url in mp4Urls:
                outputFile.write(mp4Url + '\n')
            
            outputFile.close()
    '''
    
# Main file
if __name__ == '__main__':
    main()
