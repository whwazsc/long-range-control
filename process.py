import psutil
import tkinter as tk
import time
import _thread
import threading


class MyThread(threading.Thread):
    def __init__(self,func,server,name=''):
        threading.Thread.__init__(self)
        self.name=name
        self.func=func
        self.server=server
        self.flag = threading.Event() 
        self.flag.set()       
    def run(self):
        self.func(self.server, self.flag)
    def stop(self):
        self.flag.clear() 
 

def send_info(server,flag):
       while flag.isSet():
              PID = psutil.pids()
              for eachid in PID:
                  try:
                     p = psutil.Process(eachid)
                     name = p.name()
                     status = p.status()
                     proinfo = name + "+" + str(eachid) + "+" + status
                     server.send(("process-" + proinfo).encode())
                  except:
                     pass
                  time.sleep(0.005)
              server.send(("processend").encode())
              PID.clear()
              time.sleep(5)

def rec_info(prodic, nextprodic, listbox_process):
        if listbox_process.get(0) == "正在获取进程信息...":
            listbox_process.delete(0)
        maxid = -1
        k = 0
        prolist = list(prodic.values())
        for info in nextprodic.values():
            i = 0
            if len(prodic) == 0:
                listbox_process.insert(tk.END, info[0])
                maxid = int(info[1])
                continue
            proid = int(info[1])
            for eachpro in prolist:
                eachid = int(eachpro[1])
                if proid > eachid:
                    if eachid > maxid:
                        listbox_process.delete(i + k)
                        k -= 1
                    i += 1
                    if len(prolist) == i:
                        listbox_process.insert(tk.END, info[0])
                        maxid = int(info[1])                       
                    continue
                elif proid == eachid:
                    if info != eachpro:
                        listbox_process.delete(i + k)
                        listbox_process.insert(i + k, info[0])
                    maxid = proid
                    i += 1
                    break
                elif proid < eachid:
                    listbox_process.insert(i + k, info[0])
                    maxid = proid
                    k += 1
                    break
        if i < len(prodic):
            for k in range(0, len(prodic) - i):
                listbox_process.delete(tk.END)
        prodic.clear()
        for keys, values in nextprodic.items():
            prodic[keys] = values
        nextprodic.clear()
    
def begin_key(clientlist, listbox_process):
       if len(clientlist) > 0 and "process" not in clientlist:
              listbox_process.insert(0, "正在获取进程信息...")
              clientlist.append("process")
              clientlist[0].send("process".encode())

def end_key(clientlist, nextprodic):
       if len(clientlist) > 0 and "process" in clientlist:
              clientlist.remove("process")
              clientlist[0].send("processend".encode())
              nextprodic.clear()

def thread_rec_info(prodic, nextprodic, listbox_process):
       _thread.start_new_thread(rec_info, (prodic, nextprodic, listbox_process))

def thread_send_info(serverlist, threaddic):
       if len(serverlist) > 1 and "process" not in threaddic:
              process_thread = MyThread(send_info, serverlist[1], send_info.__name__)
              process_thread.start()
              threaddic["process"] = process_thread

def close_pro(thread):
       thread.stop()
       del thread

def thread_close_pro(threaddic):
       if "process" in threaddic:
              _thread.start_new_thread(close_pro, (threaddic["process"], ))
              threaddic.pop("process")

def clear_lb(listbox_process, prodic, nextprodic):
    while nextprodic != {}:
        continue
    listbox_process.delete(0, tk.END)
    prodic.clear()
    

def show_proinfo(procdic, listbox_process):
    if len(procdic) == 0:
        return False
    try:
        item = listbox_process.curselection()
    except:
        return False
    infolist = list(procdic.values())
    info = infolist[item[0]]
    top = tk.Toplevel(height = 200, width = 400)
    top.title("进程信息")
    w_process_show = tk.Canvas(top, width = 300, height = 150)
    w_process_show.grid(row = 0, column = 0, rowspan = 10, columnspan = 10)
    w_process_show.create_rectangle(0, 0, 650, 400)
    label_name = tk.Label(top, text = ("进程名称:  " + info[0]))
    label_name.grid(row = 0, column = 0, rowspan = 4, sticky = tk.W)
    label_PID = tk.Label(top, text = ("PID:   " + info[1]))
    label_PID.grid(row = 2, column = 0, rowspan = 4, sticky = tk.W)
    label_status = tk.Label(top, text = ("进程状态:  " + info[2]))
    label_status.grid(row = 4, column = 0, rowspan = 4, sticky = tk.W)

def thread_client_end_process(clientlist, procdic, listbox_process, nextprodic):
    if len(clientlist) > 0 and len(procdic) > 0:
        try:
            item = listbox_process.curselection()[0]
        except:
            return False
        if listbox_process.get(item) == "正在获取进程信息..." or listbox_process.get(item) == "正在删除...":
            return False
        _thread.start_new_thread(client_end_process, (clientlist, procdic, item, nextprodic, listbox_process))
        listbox_process.delete(tk.ACTIVE)
        listbox_process.insert(item, "正在删除...")

        
def thread_server_end_process(threaddic, pid):
    if "process" in threaddic:
        _thread.start_new_thread(server_end_process, (pid, ))

def server_end_process(pid):
    pid = int(pid)
    try:
        p = psutil.Process(pid)
        p.terminate()
    except:
        pass

def client_end_process(clientlist, prodic, item, nextprodic, listbox_process):
    prolist = list(prodic.values())
    pid = prolist[item][1]
    while nextprodic != {}:
        continue
    clientlist[0].send(("processdele-" + pid).encode())
    listbox_process.delete(item)
    prodic.pop(pid)
    
    
       

