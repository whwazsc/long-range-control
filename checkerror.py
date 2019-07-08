from tkinter import messagebox

def link_ip_error():
       message = messagebox.showerror(title = "error", message = "ip error")

def link_ip_check(ip_link):
       num = ip_link.count(".")
       if num != 3:
              return False
       else:
              tup = ip_link.split(".")
              for each in tup:
                     if each.isdigit() == False:
                            return False
                     elif int(each) < 0 or int(each) > 255:
                            return False
              return True
              
def link_port_check(port_link):
       if port_link.isdigit():
              return True
       elif len(port_link) == 0:
              return True
       else:
              return False
       
def link_port_error():
       message = messagebox.showerror(title = "error", message = "port error")



