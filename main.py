#!/usr/bin/pytho
import subprocess
import socket
import os
from this import s
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import font

#Config/Default stuff
config = []
#Please add / at the end of directories
mount_path = "/media/redux/"
sshalias = "fileserver"
remotescript = "space_check"
remotepath = "~/nas/pi-transfer/"
logpath = "/tmp/pifb.log"
#Functions

#Test internet
netipaddress = socket.gethostbyname(socket.gethostname())
def test_net():
    if netipaddress=="127.0.0.1":
        return  False
    else:
        return True

#Test internet and display messagebox
def test_net_gui():
    if test_net():
        tk.messagebox.showinfo(title="Success!",message="Connected to the network")
    else:
        tk.messagebox.showerror(title="No Network",message="Not connected to the internet")
    return

root = tk.Tk()
root.attributes("-fullscreen", True)
root.geometry("480x320")

tabControl = ttk.Notebook(root)
tab1 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)
tab3 = ttk.Frame(tabControl)
tab4 = ttk.Frame(tabControl)

#tabControl.add(tab1, text ='Test')
tabControl.add(tab1, text ='Drive')
tabControl.add(tab2, text ='Network')
tabControl.add(tab3, text ='Optical')
tabControl.add(tab4, text ='Config')

tabControl.pack(expand = 1, fill="both")

#Exit button function
def close_form():
    root.destroy()
    return

#Exit button
tab1_btn_exit = tk.Button(tab1, text="Exit", command=close_form)

#Drive Tab
lbl_drive = tk.Label(tab1, text="Select Drives To Transfer", font=('Modern', '20'))


drives = os.listdir(os.path.join("", mount_path))
drive_path = []

for x in drives:
    drive_path.append(os.path.join(mount_path, x))

from_groupbox = tk.LabelFrame(tab1, text="From")
to_groupbox = tk.LabelFrame(tab1, text="To")

drive_lb = tk.Listbox(from_groupbox, selectmode=tk.SINGLE, exportselection=0)
drive_lb2 = tk.Listbox(to_groupbox, selectmode=tk.SINGLE, exportselection=0)

def refresh_drives(listboxlb):
    listboxlb.delete('0', 'end')
    drives = os.listdir(os.path.join("", mount_path))
    for x in drives:
        drive_path.append(os.path.join(mount_path, x))
    for x in drives:
        listboxlb.insert(tk.END, x)
    return

#refresh both drives from & to
def ref_from_to():
    refresh_drives(drive_lb)
    refresh_drives(drive_lb2)
    return

    #Initial refresh
refresh_drives(drive_lb)
refresh_drives(drive_lb2)

    #Copy from drive to drive
def copy_drive():
    try:
        drive_from = drive_lb.get(drive_lb.curselection())
        drive_to = drive_lb2.get(drive_lb2.curselection())
    except:
        tk.messagebox.showerror(title="Error!", message="Please select drives to copy files")
    else:
        #Check if user selected same drive on both listbox
        if drive_from == drive_to:
            tk.messagebox.showerror(title="Error",message="Can't copy to the same drive!")
        else:
            #Contuine if drives are selected properly
            #Check if space available
            from_path = os.path.join(mount_path, drive_from)
            to_path = os.path.join(mount_path, drive_to)
            from_stat = os.statvfs(from_path)
            to_stat = os.statvfs(to_path)

            from_space_size = (from_stat.f_frsize * from_stat.f_blocks) - (from_stat.f_frsize * from_stat.f_bfree)
            from_space_size_gib = from_space_size / 1073741824
            to_space_available = (to_stat.f_frsize * to_stat.f_bfree)

            continue_yn = True
            if from_space_size > to_space_available:
                msgbox_space = tk.messagebox.askquestion(title='Continue?', message="There is not enough space \
                on the destination media, try anyways?", icon="warning")
                if msgbox_space == 'no':
                    continue_yn = False

            if continue_yn:
                copy_yn_message = "Copy " + str(round(from_space_size_gib, 2)) + " GiB from " + drive_from  + " to " + drive_to + "?"
                copy_yn = tk.messagebox.askquestion(title="Continue?", message=copy_yn_message)

                if copy_yn == 'no':
                    tk.messagebox.showinfo(message="Copy aborted.")
                if copy_yn == 'yes':
                    #update label
                    lbl_drive.config(text="Do not remove/move media!", fg="RED")
                    tk.messagebox.showwarning(message="Do not remove/move media!")
                    def rsync_copy():
                        #Create new window with verbose
                        copy_verbose = tk.Tk()
                        copy_verbose.attributes("-fullscreen", True)
                        copy_verbose.geometry("480x320")

                        #add exit button
                        def verbose_exit():
                            copy_verbose.destroy()
                            return

                        btn_verbose_exit = tk.Button(copy_verbose, text="Exit", command=verbose_exit)

                        rsync_log_txt = tk.Text(copy_verbose)
                        rsync_log_txt.pack(side=tk.TOP)
                        rsync_log_txt.place(height=200,width=480)

                        scrollbar = tk.Scrollbar(rsync_log_txt, orient="vertical", command=rsync_log_txt.yview)
                        scrollbar.pack(side=tk.RIGHT, fill="y")

                        rsync_log_txt.config(yscrollcommand=scrollbar.set)

                        #Rsync section
                        try:
                            cmd = "rsync -r -v -t" + " " + os.path.join(mount_path,drive_from) + " " + os.path.join(mount_path,drive_to)
                            rsync_cmd = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            universal_newlines=True)
                            out,err = rsync_cmd.communicate()
                            stdout = open(logpath, 'w')
                            stdout.writelines(out)
                            stdout.close()
                        except:
                            tk.messagebox.showerror(title="Error!", message="Something went wrong while copying, please check log")

                        #Start rsync on seperate thread to allow output to log while user waits
                        #thread1 = thread.start_new_thread(rsync, ())

                        verbose = open(logpath, 'r')
                        Lines = verbose.readlines()
                        for line in Lines:
                            rsync_log_txt.insert(tk.END, line)
                            rsync_log_txt.see(tk.END)
                        #Add exit button when finished copying
                        btn_verbose_exit.pack(side=tk.BOTTOM)

                        lbl_drive.config(text="Copied!", fg="GREEN")
                        return
                    rsync_copy()
            else:
                tk.messagebox.showinfo(message="Copy aborted.")
    return

def net_backup_drive():
    try:
        drive_from = net_lb.get(net_lb.curselection())
    except:
        tk.messagebox.showerror(title="Error!", message="Please select drives to copy files")
    else:
        #Check if space available
        from_path = os.path.join(mount_path, drive_from)
        from_stat = os.statvfs(from_path)
        from_space_size = (from_stat.f_frsize * from_stat.f_blocks) - (from_stat.f_frsize * from_stat.f_bfree)
        from_space_size_gib = from_space_size / 1073741824

        #retrieve space available on remote server
        try:
            cmd = "ssh " + sshalias + " " + remotescript
            rsync_cmd = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            out = rsync_cmd.communicate()
            to_space_available = out
        #If there is a failure contacting server, abort since you can't copy anyways
        except:
            tk.messagebox.showerror(title="Error!", message="Something went wrong contacting server...")
        #continue rest of code if all is well
        else:

            continue_yn = True
            if from_space_size > int((to_space_available[0])):
                msgbox_space = tk.messagebox.askquestion(title='Continue?', message="There is not enough space on\
                the destination media, try anyways?", icon="warning")
                if msgbox_space == 'no':
                    continue_yn = False

            if continue_yn:
                copy_yn_message = "Copy " + str(round(from_space_size_gib, 2)) + " GiB from " + drive_from  + " to Server?"
                copy_yn = tk.messagebox.askquestion(title="Continue?", message=copy_yn_message)

                if copy_yn == 'no':
                    tk.messagebox.showinfo(message="Copy aborted.")
                if copy_yn == 'yes':
                    #update label
                    lbl_network.config(text="Do not remove/move media!", fg="RED")
                    tk.messagebox.showwarning(message="Do not remove/move media!")
                    def rsync_copy():
                        #Create new window with verbose
                        copy_verbose = tk.Tk()
                        copy_verbose.attributes("-fullscreen", True)
                        copy_verbose.geometry("480x320")

                        #add exit button
                        def verbose_exit():
                            copy_verbose.destroy()
                            return

                        btn_verbose_exit = tk.Button(copy_verbose, text="Exit", command=verbose_exit)

                        rsync_log_txt = tk.Text(copy_verbose)
                        rsync_log_txt.pack(side=tk.TOP)
                        rsync_log_txt.place(height=200,width=480)

                        scrollbar = tk.Scrollbar(rsync_log_txt, orient="vertical", command=rsync_log_txt.yview)
                        scrollbar.pack(side=tk.RIGHT, fill="y")
                        rsync_log_txt.config(yscrollcommand=scrollbar.set)

                        #Rsync section
                        #try:
                        remote_target = "%s:%s"%(sshalias,remotepath)
                        
                        from_target = os.path.join(mount_path,drive_from)
                        from_target = "'" + str(from_target) + "'"
                        cmd = "rsync -rvt %s %s > %s"%(from_target,remote_target,logpath)
                        print(cmd)
                        print("\n")
                        print(cmd)
                        subprocess.call(cmd,shell=True)
                            #subprocess.call("rsync -r -v -t" + " " + "/media/redux/ISOs\ -\ Driver/" + " " + "fileserver:~/nas/pi-transfer/", shell=True)
                            #os.system(str("rsync -r -v -t" + " " + os.path.join(mount_path,drive_from) + " " + sshalias + ":" + os.path.join(remotepath,"") + " > logpath"))
                            #cmd = "rsync -r -v -t" + " " + os.path.join(mount_path,drive_from) + " " + sshalias + ":" + os.path.join(remotepath,"")
                            #rsync_cmd = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                            #stderr=subprocess.PIPE, universal_newlines=True)
                            #out,err = rsync_cmd.communicate()
                            #stdout = open('logpath', 'w')
                            #stdout.writelines(out)
                            #stdout.close()
                            #stderr = open('/tmp/pifb.error', 'w')
                            #stderr.writelines(err)
                            #stderr.close()
                        #except:
                            #tk.messagebox.showerror(title="Error!", message="Something went wrong while copying, please check log")
                        verbose = open(logpath, 'r')
                        Lines = verbose.readlines()
                        for line in Lines:
                            rsync_log_txt.insert(tk.END, line)
                            rsync_log_txt.see(tk.END)
                            #Add exit button when finished copying
                        btn_verbose_exit.pack(side=tk.BOTTOM)

                        lbl_network.config(text="Copied!", fg="GREEN")
                        return
                    rsync_copy()
            else:
                tk.messagebox.showinfo(message="Copy aborted.")
    return
def remote_space_btn():
    try:
        cmd = "ssh " + sshalias + " " + remotescript
        cmd_run = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        space_available = cmd_run.communicate()
        space_gib = (round(float(space_available[0])/1073742000, 2))
        tk.messagebox.showinfo(title="Space",message="There is " + str(space_gib) + "G available on the remote server.")
    except:
        print("Error with connection to remote server")
        tk.messagebox.showerror(message="Error connecting to remote server")

#Optical Media Functions
def opt_format():
    return
def opt_backup():
    return
def opt_space():
    return

#Network copying
lbl_network = tk.Label(tab2, text="Select Drive to Backup", font=('Modern', '20'))
net_groupbox = tk.LabelFrame(tab2, text="Drives")
netbtn_groupbox = tk.LabelFrame(tab2)
net_lb = tk.Listbox(net_groupbox, selectmode=tk.SINGLE, exportselection=0)
#initial drive refresh for net_lb (listbox)
refresh_drives(net_lb)
btn_net_test_internet = tk.Button(netbtn_groupbox, text="Test Wifi", command=test_net_gui)
btn_net_copy = tk.Button(netbtn_groupbox, text="Backup", command=net_backup_drive)
btn_net_refresh = tk.Button(netbtn_groupbox, text="Refresh", command=lambda: refresh_drives(net_lb))
btn_net_exit = tk.Button(netbtn_groupbox, text="Exit", command=close_form)
btn_net_space = tk.Button(netbtn_groupbox, text="Server Space", command=remote_space_btn)
btn_drive_refresh = tk.Button(tab1, text="Refresh Devices", fg="BLUE", command=ref_from_to)
btn_drive_start = tk.Button(tab1, text="Transfer Files", fg="GREEN", command=copy_drive)


#Optical Drive stuff
lbl_optical = tk.Label(tab3, text="Select Drive to Archive", font=('Modern', '20'))
opt_groupbox = tk.LabelFrame(tab3, text="Drives")
optbtn_groupbox = tk.LabelFrame(tab3)
opt_lb = tk.Listbox(opt_groupbox, selectmode=tk.SINGLE,exportselection=0)
opt_lb.pack()
refresh_drives(opt_lb)

btn_opt_copy = tk.Button(optbtn_groupbox, text="Backup", command=opt_backup)
btn_opt_space = tk.Button(optbtn_groupbox, text="Media Space", command=opt_space)
btn_opt_format = tk.Button(optbtn_groupbox, text="Format Media", command=opt_format)
btn_opt_exit = tk.Button(optbtn_groupbox, text="Exit", command=close_form)
#packing
lbl_drive.pack()
btn_drive_refresh.pack()
btn_drive_start.pack(side=tk.BOTTOM)
from_groupbox.pack(side=tk.LEFT, padx=5, pady=5)
to_groupbox.pack(side=tk.RIGHT, padx=5, pady=5)
drive_lb2.pack()
drive_lb.pack()

lbl_optical.pack()
opt_groupbox.pack(side=tk.LEFT, padx=5, pady=5)
optbtn_groupbox.pack(side=tk.RIGHT, padx=5, pady=5)
btn_opt_space.pack()
btn_opt_copy.pack()
btn_opt_format.pack()
btn_opt_exit.pack()

lbl_network.pack()
net_groupbox.pack(side=tk.LEFT, padx=5, pady=5)
netbtn_groupbox.pack(side=tk.RIGHT, padx=5, pady=5)
net_lb.pack()
#btn_net_test_internet.pack()
btn_net_copy.pack()
btn_net_refresh.pack()
btn_net_space.pack()
btn_net_exit.pack()
#btn_2.pack()
root.mainloop()
