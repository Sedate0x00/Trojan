#!/usr/bin/env python
# coding=utf-8

import os

#获取环境变量
def run(**args):
    print '[*] Inenvironment module.'
    return str(os.environ)
