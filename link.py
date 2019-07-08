import socket
from tkinter import messagebox
import checkerror
import _thread
import key
import shot
import tkinter as tk
import process
import base64
import information

threaddic = {}

def client_link_button(server_ip, server_port, clientlist, text_key, entry_screen_shot_str, listbox_process, nextprodic, prodic, hostvarlist):
       save_path = ""
       if len(clientlist) > 0:
              if isinstance(clientlist[0], socket.socket) == True:
                     message = messagebox.showwarning(title = "warning", message = "已连接")
                     return False
       client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
       try:
              client.connect((server_ip, int(server_port)))
              clientlist.append(client)
              while True:
                     data = client.recv(4096).decode()
                     if data == "exit":
                            client.send("exit".encode())
                            clientlist.clear()
                            nextprodic.clear()
                            prodic.clear()
                            i = 0
                            while i < 11:
                                    hostvarlist[i].set("")
                                    i += 1
                            hostvarlist[-1].clear()
                     elif data[:5] == "shot-":
                            key.thread_key_show(data, text_key)
                     elif data[:7] == "screen-":
                            filename = data[7:21]
                            length = data[21:26]
                            data = data[26:26+int(length)]
                            if len(data):
                                   data_b = bytes(data.encode('utf-8'))
                                   if len(data_b)%4 > 0 :
                                          data_b = data_b+b'='*(4-len(data_b)%4)
                                   data_o = base64.b64decode(data_b)
                                   if save_path == "":
                                          save_path = entry_screen_shot_str.get()
                                   shot.thread_screen_save(filename,data_o,save_path,clientlist)
                     elif data == "screen_end":
                            save_path = ""
                     elif data == "screenend":
                            if "screen" in clientlist:
                                   clientlist.remove("screen")
                            if "screen" in threaddic:
                                   threaddic.pop("screen")
                     elif data == "processend":
                            process.thread_rec_info(prodic, nextprodic, listbox_process)
                     elif data[:8] == "process-":
                            info = data[8:].split("+")
                            nextprodic[info[1]] = info
                     elif data[:15] == "informa-static-":
                            information.thread_show_static(hostvarlist, data)
                     elif data[:12] == "informa-dyn-":
                            information.thread_show_dyn(hostvarlist, data)                     
       except Exception as a:
              message = messagebox.showerror(title = "错误", message = str(a))
              return False
       client.close()
              

              
       

def server_link_button(server_port, link_state, server_ip, server_port_label, client_ip, client_port, serverlist):
       if len(serverlist) > 0:
              if isinstance(serverlist[0], socket.socket) == True:
                     message = messagebox.showwarning(title = "warning", message = "已打开端口")
                     return False
       try:
              server_ip_local = socket.gethostbyname(socket.gethostname())
              server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
              server.bind((server_ip_local, int(server_port)))
              serverlist.append(server)
              link_state.set("等待连接")
              server.listen(1)
              while True:
                     (conn, (addr, port)) = server.accept()
                     message = messagebox.askokcancel(title = "正在连接", message = "确认连接")
                     if message == False:
                            continue
                     else:
                            serverlist.append(conn)
                            link_state.set("已连接")
                            server_ip.set(addr)
                            server_port_label.set(port)
                            client_ip.set(server_ip_local)
                            client_port.set(server_port)
                            while True:
                                   data = conn.recv(1024).decode()
                                   if data == "exit":
                                          serverlist.clear()
                                          for thread in threaddic.values():
                                                 thread.stop()
                                                 del thread
                                          threaddic.clear()
                                          break
                                   elif data == "shot":
                                          key.thread_key_press(serverlist, threaddic)
                                   elif data == "shotend":
                                          key.thread_close_listener(threaddic, "key")
                                   elif data[0:12] == "screenbegin-":
                                          (s, sleep_time, lasting_time) = data.split("-")
                                          shot.thread_screen_press(serverlist,sleep_time,lasting_time,threaddic)
                                   elif data == "screenend":
                                          shot.thread_close_listener(threaddic, serverlist, "screen")
                                   elif data == "process":
                                          process.thread_send_info(serverlist, threaddic)
                                   elif data == "processend":
                                          process.thread_close_pro(threaddic)
                                   elif data[:12] == "processdele-":
                                          process.thread_server_end_process(threaddic, data[12:])
                                   elif data == "informa":
                                          information.thread_get_info(serverlist, threaddic)
                                   elif data == "informaend":
                                          information.thread_close_get_info(threaddic)                                          
                     break
              conn.close()
       except OSError:
              pass
       except Exception as reason:
              message = messagebox.showerror(title = "错误", message = str(reason))
       finally:
              link_state.set("未连接")
              server_port_label.set("")
              server_ip.set("")
              client_ip.set("")
              client_port.set("")

              

def close_link_client(client, nextprodic, prodic, hostvarlist):
       client.send("exit".encode())
       screen_save_name.clear()
       nextprodic.clear()
       prodic.clear()
       i = 0
       while i < 11:
           hostvarlist[i].set("")
           i += 1
       hostvarlist[-1].clear()

def close_link_server(conn):
       conn.send("exit".encode())
                     
def thread_client_link(server_ip, server_port, clientlist, text_key, entry_screen_shot_str, listbox_process, nextprodic, prodic, hostvarlist):
       if checkerror.link_ip_check(server_ip) == False:
              checkerror.link_ip_error()
              return False
       if checkerror.link_port_check(server_port) == False:
              checkerror.link_port_error()
              return False
       _thread.start_new_thread(client_link_button, (server_ip, server_port, clientlist, text_key, entry_screen_shot_str, listbox_process, nextprodic, prodic, hostvarlist))

def thread_server_link(server_port, link_state, server_ip, server_port_label, client_ip, client_port, serverlist):
       if checkerror.link_port_check(server_port) == False:
              checkerror.link_ip_error()
              return False
       _thread.start_new_thread(server_link_button, (server_port, link_state, server_ip, server_port_label, client_ip, client_port, serverlist))

def thread_close_link_client(clientlist, nextprodic, prodic, hostvarlist):
       if len(clientlist) > 0:
              _thread.start_new_thread(close_link_client, (clientlist[0], nextprodic, prodic, hostvarlist))
              clientlist.clear()

def thread_close_link_server(serverlist):
       if len(serverlist) > 1:
              _thread.start_new_thread(close_link_server, (serverlist[1],))
       elif len(serverlist) == 1:
              serverlist[0].close()
              serverlist.clear()
              
       
