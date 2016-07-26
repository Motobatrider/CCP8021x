#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Cisco log check -- 802.1x enable or not v1.1
# Created by Randy Chen
# Jun 24 2016

# v1.0 update
# Log file should under ./Export/
# py file should under ./
# Report in ./list.txt
# July 04 2016: add output window

# v1.1 update
# Create catch router running config model
# no router list read
# no password encrypt

import sys
import os
import time
from Tkinter import *
from tratto import *
from tratto.systems import *
from tratto.connectivity import *

routerlist = open('./config/routers.txt','r')
routerlist_line = routerlist.readlines()
today_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))

class Notice(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        log =  'Please wait till running finished'
        self.helloLabel = Label(self, text=log)
        self.helloLabel.pack()
        self.quitButton = Button(self, text='Go', command=self.quit)
        self.quitButton.pack()

Notice = Notice()
Notice.master.title('Cisco Counting is running')
Notice.mainloop()


def mkdir(path):
    # 去除首位空格
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists=os.path.exists(path)

    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        print path+'created'
        # 创建目录操作函数
        os.makedirs(path)
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        return True

def craw_cisco(x):
    # Create Export Files
    routerconfig = open('./config/password.txt')
    routerconfig_line = routerconfig.readlines()
    router_name = routerconfig_line[0].replace('\n','')
    router_password = routerconfig_line[1].replace('\n','')
    router_enable_password = routerconfig_line[2].replace('\n','')
    today_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))

    m = SystemProfiles['IOS']
    #change 23 for 22 and telnet for ssh for ssh enabled devices
    s = Session(x,22,"ssh",m)
#    s.login("cisco", "Valmet123!@#..")
    try:
        s.login(router_name, router_password)
        # if your need to issue an "enable" command
        s.escalateprivileges(router_enable_password)
        show_running_config = s.sendcommand("show run")
        s.logout()
        path = "./Export/%s"%today_date
        mkdir(path)
        e = open('./Export/%s/%s.txt'%(today_date,x),'w')
        e.write(show_running_config)
        e.close()

    except:
        try:
            s = Session(x,23,"telnet",m)
            s.login(router_name,router_password)
            s.escalateprivileges(router_enable_password)
            show_running_config = s.sendcommand("show run")
            s.logout()
            path = "./Export/%s"%today_date
            mkdir(path)
            e = open('./Export/%s/%s.txt'%(today_date,x),'w')
            e.write(show_running_config)
            e.close()
        except:
            connect_error = open('./error.txt','a')
            connect_error.write('%s, login error, '%x+time.strftime('%Y-%m-%d_%H:%M:%S',time.localtime(time.time()))+'\n')
            connect_error.close()
            print "%s connect error"%x

    # Create Export Files
#    m = SystemProfiles['IOS']
#    #change 23 for 22 and telnet for ssh for ssh enabled devices
#    s = Session(x,22,"ssh",m)
#    s.login("cisco", "Valmet123!@#..")
#    s.escalateprivileges('abc123!')
#    show_running_config = s.sendcommand("show run")
#    s.logout()
#    e = open('./Export/%s.txt'%x,'w')
#    e.write(show_running_config)
#    e.close()

# Ping check
for r in routerlist_line:
    r = r.replace('\n','')
    return1=os.system('ping -n -c 2 -i 1 %s'%r) # ping twice waiting for 2 seconds
    if return1:
        connect_error = open('./Error/error%s.txt'%today_date,'a')
        connect_error.write('%s, connect error, '%r+time.strftime('%Y-%m-%d_%H:%M:%S',time.localtime(time.time()))+'\n')
#        print "can't open"
    else:
        craw_cisco(r)

def count():
    # Count 8021x
    today_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    flist = os.listdir('./Export/%s/'%today_date)
    countp = 0

    for j in flist:
        a2 = open('./Export/%s/'%today_date+j)
        line = a2.readlines()
        n = 0
        interface = []
        for i in line:
            if 'hostname' in i:
                router_host_name = i[-20:-2]
            if 'interface GigabitEthernet' in i:
                interface.append(n)
            n = n + 1
            if 'Invalid input detected' in i:
                connect_error = open('./Error/error%s.txt'%today_date,'a')
                connect_error.write('%s, enable error, '%r+time.strftime('%Y-%m-%d_%H:%M:%S',time.localtime(time.time()))+'\n')
        interface.append(len(line)-1)

        x = 0
        y = len(interface)-1
        t = 0

        while x < y:
            o = interface[x]
            p = interface[x+1]
            n = o
            z = ' '
            while n < p:
                if 'authentication port-control auto' in line[n]:
            	    t = t + 1
                if 'description' in line[n]:
                    z = line[n]
                n = n + 1
            if t == 0:
                f = open('./Report/repot%s.txt'%today_date, 'a') #a 为增量写文件
    # Windows Version
    #            f.write(line[14][:-8]+' , '+line[o][-5:-1]+' , '+z[:-1]+'\n') # 去除字符串最后换行，最后手工添加换行
                f.write(router_host_name + ' , ' + line[o].replace('\n','')[:-1] + ' , '+z.replace('\n','')+'\n') # 去除字符串最后换行，最后手工添加换行
    # There is no ^M in linux so should be [-6:-2]
    #            f.write(j[:-4]+' , '+line[o][-5:-1]+' , '+z[:-1]+'\n') # 去除字符串最后换行，最后手工添加换行
                f.close()
                countp = countp + 1
            t = 0
            x = x +1
    f = open('./Report/repot%s.txt'%today_date, 'a')
    f.write('-== Report on '+time.strftime('%Y-%m-%d_%H:%M:%S',time.localtime(time.time()))+' ==- \n')
    f.close()
    return countp

countp = count()

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        today_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        flist = os.listdir('./Export/%s/'%today_date)
        log =  '      Read ' + str(len(flist)) + ' Cisco log files       '+ '\n'+ '\n' + '      ' + str(countp) + ' ports turned-off 802.1x      ' + '\n' + '\n'+ '      Report in list.txt      '
        self.helloLabel = Label(self, text=log)
        self.helloLabel.pack()
        self.quitButton = Button(self, text='Quit', command=self.quit)
        self.quitButton.pack()

app = Application()
app.master.title('C-Log')
app.mainloop()
