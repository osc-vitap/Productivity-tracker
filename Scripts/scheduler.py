import schedule
import time
from datetime import datetime as d
import os
import ctypes
import psutil    

# Hosts path of Windows. change hosts path according to your OS
hosts_path = "C:/Windows/System32/drivers/etc/hosts"
# localhost's IP
redirect = "127.0.0.1"
# add website to websites list to block
websites = ["www.facebook.com","www.instagram.com", "www.gmail.com"]
applications = ["notepad.exe","firefox.exe"]

def focus(startH,startM,endH,endM):
    while True:
        # time of your work
        if d(d.now().year, d.now().month, d.now().day, startH, startM) < d.now() < d(d.now().year, d.now().month, d.now().day,endH,endM):
            print("Working hour...", d.now())
            with open(hosts_path, 'r+') as file:
                content = file.read()
                for website in websites:
                    if website in content:
                        pass
                    else:
                        # mapping hostnames to your localhost IP address
                        file.write(redirect + " " + website + "\n")
            for application in applications:
                if(application in (p.name() for p in psutil.process_iter())):
                    os.system('taskkill /im '+application) # select process by its name
        else:
            with open(hosts_path, 'r+') as file:
                content = file.readlines()
                file.seek(0)
                for line in content:
                    if not any(website in line for website in websites):
                        file.write(line)
                # removing hostnmes from host file
                file.truncate()
            print("Chill time", d.now())
            
        time.sleep(2)
def job():
    print("Work mode on...")
    print("TO ENABLE THE FOCUS MODE\n___________________________")
    startH = int(input("Enter the starting hour: "))
    startM = int(input("Enter the starting minute: "))
    endH = int(input("Enter the ending hour: "))
    endM = int(input("Enter the ending minute: "))
    focus(startH, startM, endH, endM)


#schedule.every(1).to(2).seconds.do(job)
schedule.every().day.at("01:01").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)