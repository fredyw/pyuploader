#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2014 Fredy Wijaya
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#  
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys, os, urllib2, base64, logging, argparse, exceptions

logger = None

class PyUploaderException(Exception):
    def __init__(self, msg):
        self.msg = msg

def upload(url_path, path, username=None, password=None):
    if not os.path.exists(path):
        raise exceptions.Exception(path + ' does not exist')
    for (file_path, full_url_path) in build_urls(url_path, path):
        logger.info('%s -> %s' % (file_path, full_url_path))
        request = urllib2.Request(full_url_path, data=open(file_path, 'rb'))
        request.add_header('Content-Type', 'application/octet-stream')
        request.add_header('Content-Length', os.path.getsize(file_path))
        if username is not None and password is not None:
            base64string = base64.encodestring('%s:%s' % (username,
                                                          password)).replace('\n', '')
            request.add_header('Authorization', 'Basic %s' % base64string)
        request.get_method = lambda: 'PUT'
        url = urllib2.urlopen(request)
        if url.getcode() < 200 or url.getcode() >= 300:
            raise PyUploaderException('Got a non-2XX HTTP status code')

def build_urls(url_path, path):
    urls = []
    if not url_path.endswith('/'):
        url_path = url_path + '/'
    if os.path.isfile(path):
        full_url_path = url_path + os.path.basename(path)
        urls.append((path, full_url_path.replace('\\', '/')))
    else:
        if path.endswith('/'):
            path = path[:len(path)-1]
        base_path = os.path.basename(path)
        for (dirpath, dirnames, filenames) in os.walk(path):
            for filename in sorted(filenames):
                file_path = os.path.join(dirpath, filename)
                p = file_path[len(path)+1:]
                full_url_path = url_path + base_path + '/' + p
                urls.append((file_path, full_url_path.replace('\\', '/')))
    return urls
  
def configure_logger():
    global logger
    FORMAT = '%(asctime)s [%(levelname)-5s] %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.INFO)
    logger = logging.getLogger('pyuploader')

def validate_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str, required=True)
    parser.add_argument('--path', type=str, required=True)
    parser.add_argument('--username', type=str)
    parser.add_argument('--password', type=str)
    return parser.parse_args()
    
if __name__ == '__main__':
    configure_logger()
    args = validate_args()
    try:
        upload(args.url, args.path, args.username, args.password)
    except Exception as e:
        logger.error(str(e))
        sys.exit(1)
