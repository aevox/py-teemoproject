#!/bin/env python

import os
import base64
import subprocess
import hashlib

from celery import Celery

RESULT_DIR = os.environ.get('RESULT_DIR') or '/var/py-teemoproject'
REDIS_ADDRESS = os.environ.get('REDIS_ADDRESS') or 'localhost'
REDIS_PORT = os.environ.get('REDIS_PORT') or 6379
WKHTMLTODPF_PATH = os.environ.get('WKHTMLTODPF_PATH') or 'wkhtmltopdf'
WKHTMLTOPDF_ARGS = os.environ.get('WKHTMLTOPDF_ARGS') or '--quiet,--enable-external-links,--print-media-type,--javascript-delay,300'
WKHTMLTOPDF_FOOTERURL = os.environ.get('WKHTMLTOPDF_FOOTERURL') or ''

redis_url = 'redis://' + REDIS_ADDRESS + ':' + str(REDIS_PORT) + '/0'

app = Celery('htmltopdf', backend=redis_url, broker=redis_url)


@app.task
def convertHtmlToPdf(url, footer_url=''):
    result_path = RESULT_DIR + '/' + md5sum([url, footer_url]) + '.pdf'
    wkhtmlpdf_args = WKHTMLTOPDF_ARGS.split(',')
    args = [WKHTMLTODPF_PATH] + wkhtmlpdf_args
    if WKHTMLTOPDF_FOOTERURL!= '':
        args += ['--footer-html', WKHTMLTOPDF_FOOTERURL]
    args += [url] + [result_path]
    process = subprocess.Popen(args,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    output = process.communicate()[0]
    ret = process.wait()
    if ret != 0:
        return ret, url, args, output
    else:
        return ret, url, args

def md5sum(stringList):
    string = ''
    for s in stringList:
        string += s
    return hashlib.md5(string).hexdigest()

def convertUrl(urlList):
    for url in urlList:
        convertHtmlToPdf.delay(url)


if __name__ == '__main__':
    import sys
    convertUrl(sys.argv[1:])
