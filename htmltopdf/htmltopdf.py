#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2018 Marc Fouché
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''Wrapper around wkhtmltopdf to send pdfs to owncloud.
'''

import os
import subprocess
import hashlib
import owncloud

from celery import Celery

REDIS_ADDRESS = os.environ.get('REDIS_ADDRESS') or 'localhost'
REDIS_PORT = os.environ.get('REDIS_PORT') or '6379'
REDIS_DB = os.environ.get('REDIS_DB') or '0'

WKHTMLTODPF_PATH = os.environ.get('WKHTMLTODPF_PATH') or \
        '/usr/local/bin/wkhtmltopdf'
WKHTMLTOPDF_ARGS = os.environ.get('WKHTMLTOPDF_ARGS') or \
        ('--quiet '
         '--enable-external-links '
         '--print-media-type '
         '--javascript-delay '
         '300')

OWNCLOUD_URL = os.environ.get('OWNCLOUD_URL') or 'http://localhost'
OWNCLOUD_USER = os.environ.get('OWNCLOUD_USER') or 'admin'
OWNCLOUD_PASSWORD = os.environ.get('OWNCLOUD_PASSWORD') or 'admin'
OWNCLOUD_BASEDIR = os.environ.get('OWNCLOUD_BASEDIR') or 'py-teemoproject'

REDIS_URL = 'redis://' + REDIS_ADDRESS + ':' + REDIS_PORT + '/' + REDIS_DB

APP = Celery('htmltopdf', backend=REDIS_URL, broker=REDIS_URL)


class WkhtmltopdfError(Exception):
    '''Error raised when whtmltopdf returns an error
    '''
    pass


class OwncloudError(Exception):
    '''Error raised when owncloud returns an error
    '''
    pass


@APP.task
def html_to_owncloud(url, pdf_path=None):
    '''Convert an html page to pdf and puts it into a file on owncloud

    :param url: URL of the target html page
    :param pdf_path: path to the pdf in owncloud
    :returns: tuple containing the url and the pdf_path if successful
    :rtype: (string, string)
    '''
    if pdf_path is None or pdf_path == '':
        pdf_path = hashlib.md5(url).hexdigest() + '.pdf'

    wkhtmltopdf_args = WKHTMLTOPDF_ARGS.split(' ')
    data = convert_html_to_pdf(url, WKHTMLTODPF_PATH, *wkhtmltopdf_args)

    pdf_path = OWNCLOUD_BASEDIR.strip('/') + '/' + pdf_path.strip('/')
    send_data_to_owncloud(OWNCLOUD_URL, OWNCLOUD_USER, OWNCLOUD_PASSWORD,
                          pdf_path, data)
    return (url, pdf_path)


def convert_html_to_pdf(url, wkhtmltopdf_path, *args):
    '''Convert an html page to pdf

    :param url: URL of the target html page
    :param wkhtmlpath_path: path to the wkhtmltopdf binary
    :*args: args passed to wkhtmldopdf before the url
    :returns: output from wkhtmltopdf binary
    :rtype: binary data
    :raises: WkhtmltopdfError if wkhtmltopdf encounters an error
    '''
    cmd = [wkhtmltopdf_path] + list(args) + [url] + ['-']
    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    output, err = process.communicate()
    if process.returncode != 0:
        raise WkhtmltopdfError('%s: %s' % (err, url))
    return output


def send_data_to_owncloud(owncloud_url, user, password, file_path,
                          data):
    '''Write data into a remote file on owncloud

    :param owncloud_url: path of the remote file
    :param user: user used to authenticate against owncloud
    :param password: user password
    :param file_path: name of the remote file
    :param data: data to write into the remote file
    :returns: True if the operation succeeded, False otherwise
    :rtype: bool
    :raises: OwncloudError in case the basedir cannot be created
    '''
    oclient = owncloud.Client(owncloud_url)
    oclient.login(user, password)
    remote_path = file_path.strip('/')
    create_oc_dir_tree(oclient, remote_path)
    return oclient.put_file_contents(remote_path, data)


def create_oc_dir_tree(oclient, remote_path):
    '''Create parent directories needed for the given path in owncloud

    :param oclient: owncloud.Client logged in
    :param remote_path: path to file we want to create a dir tree to
    :returns: parent directory if it exists
    :rtype: string
    :raises: OwncloudError in case one of the directory of the path is a file
    '''
    parent_dir = ('/').join(remote_path.strip('/').split('/')[:-1])

    # Check if directory exists, if it does retun directory path
    try:
        if oclient.file_info(parent_dir).is_dir():
            return parent_dir
        else:
            raise OwncloudError('Cannot create directory: %s exists and is not'
                                ' a directory' % parent_dir)
    except owncloud.HTTPResponseError as err:
        if err.status_code == 404:
            pass

    # Try to create the full path. If it fails, recursively call
    # create_oc_dir_tree to create the parent directory
    try:
        oclient.mkdir(parent_dir)
    except owncloud.HTTPResponseError as err:
        if err.status_code == 409:
            create_oc_dir_tree(oclient, parent_dir)

    return create_oc_dir_tree(oclient, remote_path)


def convert_urls(urls):
    '''Push URLs to be converted in HTML in celery's queue

    :param urls: list of url
    '''
    for url in urls:
        html_to_owncloud.delay(url)


if __name__ == '__main__':
    import sys
#    convert_urls(sys.argv[1:])
    html_to_owncloud.delay(sys.argv[1], sys.argv[2])
