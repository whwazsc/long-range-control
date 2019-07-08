from win32 import win32gui
import win32ui
import win32con
import win32api
import threading
from PIL import Image
import os
import socket
import _thread
import time
import shutil
from tkinter import messagebox
from tkinter import filedialog as fd
import base64


class MyThread(threading.Thread):
    def __init__(self,func,server,sleep_time,lasting_time,name=''):
        threading.Thread.__init__(self)
        self.name=name
        self.func=func
        self.server=server
        self.sleep_time=sleep_time
        self.lasting_time=lasting_time
        self.running = threading.Event()     # 用于终止线程的标识
        self.running.set()       # 设置为True
    def run(self):
        self.func(self.server,self.sleep_time,self.lasting_time, self.running)
    def stop(self):
        self.running.clear()       # 将线程终止 

def screen_shot(server,sleep_time,lasting_time, running):
    path_i="D:\\new"
    timedic = {"屏幕变化":"屏幕变化","不限":"不限","1s":1, "2s":2, "5s":5, "10s":10, "30s":30, "1min":60, "5min":300, "10min":600, "30min":1800, "1h":3600, "12h":43200, "24h":86400}
    start = time.time()
    # 获取桌面
    desktop = win32gui.GetDesktopWindow()

    # 分辨率适应
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    # 创建设备描述表
    desktop_dc = win32gui.GetWindowDC(desktop)
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)

    # 创建一个内存设备描述表
    mem_dc = img_dc.CreateCompatibleDC()

    # 创建位图对象
    screenshot = win32ui.CreateBitmap()
    screenshot.CreateCompatibleBitmap(img_dc, width, height)
    mem_dc.SelectObject(screenshot)

    window = win32gui.GetForegroundWindow()
    pre_window = win32gui.GetWindowText(window)
    filename = ''
    while running.isSet():
        # 将截图保存到文件中
        turn_start = time.time()
        window = win32gui.GetForegroundWindow()
        current_window = win32gui.GetWindowText(window)
        end = time.time()
        if current_window != pre_window and timedic[sleep_time] == "屏幕变化":
            pre_window = current_window
        # 截图至内存设备描述表
            mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)
            isExists = os.path.exists(path_i)
            if not isExists:
                os.makedirs(path_i)
            filename_new = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
            if filename_new != filename :
                filename = filename_new
            else:
                continue
            path_r = path_i+'\\'+filename+'.bmp'
            path_c = path_i+'\\'+filename+'.jpg'
            try:
                screenshot.SaveBitmapFile(mem_dc, path_r)
                compress_image(path_r,path_c,mb=100,step=20,quality=80)
                os.remove(path_r)
            except:
                continue
            end = time.time()
            if int(end-start) >= timedic[lasting_time]:
                flag = 1
            else:
                flag = 0
            shot_send_thread = threading.Thread(target = shot_send, args = (server,path_c,flag,path_i,filename))
            shot_send_thread.start()
            time.sleep(0.2)
        elif timedic[sleep_time] != "屏幕变化":
            pre_window = current_window
        # 截图至内存设备描述表
            mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)
            isExists = os.path.exists(path_i)
            if not isExists:
                os.makedirs(path_i)
            filename = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
            path_r = path_i+'\\'+filename+'.bmp'
            path_c = path_i+'\\'+filename+'.jpg'
            screenshot.SaveBitmapFile(mem_dc, path_r)
            compress_image(path_r,path_c,mb=100,step=20,quality=80)
            os.remove(path_r)
            end = time.time()
            if int(end-start) >= timedic[lasting_time]:
                flag = 1
            else:
                flag = 0
            shot_send_thread = threading.Thread(target = shot_send, args = (server,path_c,flag,path_i,filename))
            shot_send_thread.start()
            turn_end = time.time()
            time.sleep(timedic[sleep_time]+turn_start-turn_end)
        if timedic[lasting_time] != "不限":
            if int(end-start) >= timedic[lasting_time]:
                break
    # 内存释放
    mem_dc.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())
    if os.path.exists(path_i) == True:
        try:
            os.chdir(path_i)
            for fileima in os.listdir():
                os.remove(fileima)
            os.chdir("../")
            os.rmdir(path_i)
        except:
            pass
    server.send("screenend".encode())

def get_size(file):
    # 获取文件大小:KB
    size = os.path.getsize(file)
    return size / 1024

def compress_image(infile, outfile, mb=100, step=20, quality=80):
    """不改变图片尺寸压缩到指定大小
    :param infile: 压缩源文件
    :param outfile: 压缩文件保存地址
    :param mb: 压缩目标，KB
    :param step: 每次调整的压缩比率
    :param quality: 初始压缩比率
    """
    o_size = get_size(infile)
    if o_size <= mb:
        return infile
    while o_size > mb:
        im = Image.open(infile)
        im.save(outfile, quality=quality)
        if quality - step < 0:
            break
        quality -= step
        o_size = get_size(outfile)

def shot_send(server,path_r,flag,path_i,filename):
    file_size = os.stat(path_r).st_size
    f = open(path_r,'rb')
    has_sent=0  
    while has_sent < file_size:  
        data = f.read(3000)
        data_base = base64.b64encode(data)
        data_o = str(data_base,encoding='utf8')
        has_sent+=len(data)
        data = 'screen-'+filename+str(len(data_o)).zfill(5)+data_o
        server.send(data.encode())
        time.sleep(0.001)
    #time.sleep(0.015)
    server.send('screen_end'.encode())
    f.close()
    if(flag):
        shutil.rmtree(path_i)
    
def thread_screen_press(serverlist,sleep_time,lasting_time,threaddic):
    if len(serverlist) > 1 and "screen" not in threaddic:
        #创建线程
        screen_thread = MyThread(screen_shot,serverlist[1],sleep_time,lasting_time,screen_shot.__name__)
        #启动线程
        screen_thread.start()
        threaddic["screen"] = screen_thread
        

def begin_screen(clientlist, sleep_time,lasting_time):
      if len(clientlist) > 0 and "screen" not in clientlist:
            clientlist.append("screen")
            clientlist[0].send(("screenbegin-" + sleep_time + "-" + lasting_time).encode())
      elif "screen" in clientlist:
            message = messagebox.showinfo(title = "出错", message = "正在监控")

def screen_save(data,path):
      f= open(path,'ab')
      f.write(data)
      f.close()

def thread_screen_save(filename,data,path_save,clientlist):  #path_save是用户在控制端指定的图片保存地址，save_name是图片名字
        posi = -2
        while path_save.find("\\", posi + 2) != -1:
            posi = path_save.find("\\", posi + 2)
            path_save = path_save[:posi] + "\\" + path_save[posi:]
        if os.path.isabs(path_save) == False:
            clientlist[0].send("screenend".encode())
            clientlist.pop("screen")
            message = messagebox.showinfo(tltle = "路径出错", message = "请输入正确绝对路径")
            return False
        path = path_save + '\\' + filename + '.bmp'
        _thread.start_new_thread(screen_save, (data,path))
        

def end_key(clientlist):
      if len(clientlist) > 0 and "screen" in clientlist:
            clientlist.remove("screen")
            clientlist[0].send("screenend".encode())

def close_screen_shot(thread,server):
    thread.stop()
    del thread
    server.send("screen_end".encode())

def thread_close_listener(threaddic, serverlist, screen):
    if "screen" in threaddic:
        _thread.start_new_thread(close_screen_shot, (threaddic[screen], serverlist[1]))
        threaddic.pop(screen)

def save_path(entry_screen_shot_str):
       path = fd.askdirectory()
       entry_screen_shot_str.set(path)
