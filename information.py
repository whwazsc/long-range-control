import socket
import os
import uuid
import platform
import psutil
import os
import threading
import _thread
import time
import tkinter as tk

class MyThread(threading.Thread):
    def __init__(self,func,server,name=''):
        threading.Thread.__init__(self)
        self.name=name
        self.func=func
        self.server=server
        self.running = threading.Event() 
        self.running.set()
    def run(self):
        self.func(self.server, self.running)
    def stop(self):
        self.running.clear()

def GetCpuInfo():  #获取CPU信息
    cpu_slv = round((psutil.cpu_percent(1)), 2)  # cpu使用率
    return str(cpu_slv)

def GetMemoryInfo():  #获取内存信息
    memory = psutil.virtual_memory()
    total_nc = round(( float(memory.total) / 1024 / 1024 / 1024), 2)  # 总内存
    used_nc = round(( float(memory.used) / 1024 / 1024 / 1024), 2)  # 已用内存
    free_nc = round(( float(memory.free) / 1024 / 1024 / 1024), 2)  # 空闲内存
    syl_nc = round((float(memory.used) / float(memory.total) * 100), 2)  # 内存使用率

    ret_list = [str(total_nc),str(used_nc),str(free_nc),str(syl_nc)]
    return ret_list

def GetDiskInfo():    #获取硬盘信息
    list = psutil.disk_partitions() #磁盘列表
    ilen = len(list) #磁盘分区个数
    i=0
    retlist1=[]
    retlist2=[]
    while i< ilen:
        diskinfo = psutil.disk_usage(list[i].device)
        total_disk = round((float(diskinfo.total)/1024/1024/1024),2) #总大小
        used_disk = round((float(diskinfo.used) / 1024 / 1024 / 1024), 2) #已用大小
        free_disk = round((float(diskinfo.free) / 1024 / 1024 / 1024), 2) #剩余大小
        syl_disk = diskinfo.percent

        retlist1=[list[i].device,str(total_disk),str(used_disk),str(free_disk),str(syl_disk)]  #序号，磁盘名称，
        strdisk = "+".join(retlist1)
        retlist2.append(strdisk)  
        i=i+1
    return retlist2

def get_info(server, running):
    infolist = []
    myname = socket.getfqdn(socket.gethostname())  #获取本机电脑名
    myaddr = socket.gethostbyname(myname)   #获取本机ip
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:]
    MAC = ":".join([mac[e:e+2] for e in range(0,11,2)])   #mac地址
    baseinfo = myname + "+" + myaddr + "+" + MAC + "+" + "-".join(platform.architecture()) + "+" + platform.system() + "-" + platform.version() + "+" + os.getlogin()
    server.send(("informa-static-" + baseinfo).encode())
    while running.isSet():
        infolist.extend(GetMemoryInfo())
        infolist.append(GetCpuInfo())
        infolist.extend(GetDiskInfo())
        info = "+".join(infolist)
        server.send(("informa-dyn-" + info).encode())
        infolist.clear()
        time.sleep(20)
        

def thread_get_info(serverlist, threaddic):
    if len(serverlist) > 1 and "informa" not in threaddic:
        informa_thread = MyThread(get_info, serverlist[1], get_info.__name__)
        informa_thread.start()
        threaddic["informa"] = informa_thread

def begin_key(clientlist):
    if len(clientlist) > 0 and "informa" not in clientlist:
        clientlist.append("informa")
        clientlist[0].send("informa".encode())

def show_static(hostvarlist, data):
    data = data[15:]
    statictup = data.split("+")
    i = 0
    for each in statictup:
        hostvarlist[i].set(each)
        i += 1

def thread_show_static(hostvarlist, data):
    _thread.start_new_thread(show_static, (hostvarlist, data))

def show_dyn(hostvarlist, data):
    data = data[12:]
    dyn = data.split("+")
    i = 6
    disk = []
    hostvarlist[-1].clear()
    for each in dyn:
        if i < 9:
            hostvarlist[i].set((each + "G"))
        elif i == 9 or i == 10:
            hostvarlist[i].set((each + "%"))
        else:
            if i % 5 == 0:
                disk.append(each)
                hostvarlist[-1].append(disk.copy())
                disk.clear()
            else:
                disk.append(each)
        i += 1

def thread_show_dyn(hostvarlist, data):
    _thread.start_new_thread(show_dyn, (hostvarlist, data))
    
def end_key(clientlist, hostvarlist):
    i = 0
    while i < 11:
        hostvarlist[i].set("")
        i += 1
    hostvarlist[-1].clear()
    if len(clientlist) > 0 and "informa" in clientlist:
        clientlist.remove("informa")
        clientlist[0].send("informaend".encode())

def close_get_info(thread):
    thread.stop()
    del thread

def thread_close_get_info(threaddic):
    if "informa" in threaddic:
        _thread.start_new_thread(close_get_info, (threaddic["informa"], ))
        threaddic.pop("informa")

def show_disk(disklist):
    num = len(disklist)
    if num == 0:
        return False
    top = tk.Toplevel(height = 600, width = 600)
    top.title("磁盘信息")
    i = 0
    while i < num:
        [name, total_disk, used_disk, free_disk, syl_disk] = disklist[i]
        tk.Label(top, text = name, justify = tk.LEFT).pack(anchor = tk.W)
        tk.Label(top, text = "总大小： " + total_disk + "G", justify = tk.LEFT).pack(anchor = tk.W)
        tk.Label(top, text = "已用大小： " + used_disk + "G", justify = tk.LEFT).pack(anchor = tk.W)
        tk.Label(top, text = "空闲大小： " + free_disk + "G", justify = tk.LEFT).pack(anchor = tk.W)
        tk.Label(top, text = "使用比率： " + syl_disk + "%", justify = tk.LEFT).pack(anchor = tk.W)  
        i += 1
        if i < num:
            w_disk_show = tk.Canvas(top, width = 600, height = 5)
            w_disk_show.pack()
            w_disk_show.create_line(0, 2, 600, 2, dash = (4, 4))
        











    
