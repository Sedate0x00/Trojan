#!/usr/bin/env python
# coding=utf-8

import os

#列举当前目录下所有文件
def run (**args):
    print '[*] Indirlister module.'
    files = os.listdir('.')
    return str(files)
