import winreg
from itertools import count
from ctypes.wintypes import DWORD
from ctypes import byref, create_unicode_buffer, windll
from collections import namedtuple
import pandas as pd
import threading
from django.shortcuts import render, HttpResponse, redirect
import sys
import win32gui
import time
from .activity import *
import json
import datetime
import os
import psutil
import win32process
import win32gui
import time


def get_active_window():
    _active_window_name = None
    try:
        if sys.platform in ['Windows', 'win32', 'cygwin']:
            window = win32gui.GetForegroundWindow()
            pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow()) 
            _active_window_name = psutil.Process(pid[-1]).name()
        else:
            print("sys.platform={platform} is not supported."
              .format(platform=sys.platform))
            print(sys.version)
    except:
            _active_window_name = 'Unknown'
            return _active_window_name
    return _active_window_name[0:-4] 


val = ''


def check():
    if val == 'on':
        return True
    else:
        return False


def final(val):
    if val == 'on':
        t = True
    else:
        t = False
    active_window_name = ""
    activity_name = ""
    start_time = datetime.datetime.now()
    activeList = AcitivyList([])
    first_time = True

    try:
        activeList.initialize_me()
    except Exception:
        print('No json')
    m = 0
    try:
        while m < 5:
            m = m+1
            previous_site = ""
            new_window_name = get_active_window()
            if m == 4 and val == 'on':
                m = 0
            if val == 'off':
                m = 5

            # t=check()
            if active_window_name != new_window_name:
                print(active_window_name)
                activity_name = active_window_name

                if not first_time:
                    end_time = datetime.datetime.now()
                    time_entry = TimeEntry(start_time, end_time, 0, 0, 0, 0)
                    time_entry._get_specific_times()

                    exists = False
                    for activity in activeList.activities:
                        if activity.name == activity_name:
                            exists = True
                            activity.time_entries.append(time_entry)

                    if not exists:
                        activity = Activity(activity_name, [time_entry])
                        activeList.activities.append(activity)
                    with open('activities.json', 'w') as json_file:
                        json.dump(activeList.serialize(), json_file,
                                  indent=4, sort_keys=True)
                        start_time = datetime.datetime.now()
                first_time = False
                active_window_name = new_window_name

            time.sleep(1)

    except KeyboardInterrupt:
        with open('activities.json', 'w') as json_file:
            json.dump(activeList.serialize(), json_file,
                      indent=4, sort_keys=True)


# -------------------------------------------------------------------------------------

def home(request):
    name = []
    time1 = []
    table = []

    idx = 0

    noActivity = False

    try:
        myjsondata = open('activities.json', 'r')
        jsondata = myjsondata.read()
        obj = json.loads(jsondata)
    except:
        noActivity = True

    if noActivity == False:
        for l in obj['activities']:
            t = 0
            name.append(l['name'][:65])
            for k in l['time_entries']:
                time = int(k['days'])*24*60+int(k['minutes']) + \
                    int(k['hours'])*60+(int(k['seconds'])/60)
                t = t+time

            s = str(t)
            time1.append(s[:5])

            if len(l['name'][:65]) > 0:
                n = []
                n.append(idx+1)
                n.append(l['name'][:65])
                n.append(s[:5])
                table.append(n)
                idx = idx + 1

            t = 0
    context = {'name': name, 'time': time1, 'table': table}

    val = 'off'
    if request.method == 'POST':
        v = request.POST.get('start')
        t = threading.Thread(target=final, args=(val, ))

        if v == 'on':
            val = 'on'
            final(val)

            t.start()
        else:
            val = 'off'
            final(val)

        return render(request, 'home.html', context=context)

    return render(request, 'home.html', context=context)

# ----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------


def foo(hive, flag):
    aReg = winreg.ConnectRegistry(None, hive)
    aKey = winreg.OpenKey(aReg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                          0, winreg.KEY_READ | flag)

    count_subkey = winreg.QueryInfoKey(aKey)[0]

    software_list = []

    for i in range(count_subkey):
        software = {}
        try:
            asubkey_name = winreg.EnumKey(aKey, i)
            asubkey = winreg.OpenKey(aKey, asubkey_name)
            software['name'] = winreg.QueryValueEx(asubkey, "DisplayName")[0]

            try:
                software['version'] = winreg.QueryValueEx(
                    asubkey, "DisplayVersion")[0]
            except EnvironmentError:
                software['version'] = 'undefined'
            try:
                software['publisher'] = winreg.QueryValueEx(
                    asubkey, "Publisher")[0]
            except EnvironmentError:
                software['publisher'] = 'undefined'
            software_list.append(software)
        except EnvironmentError:
            continue

    return software_list


def about(request):
    software_list = foo(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY) + foo(
        winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY) + foo(winreg.HKEY_CURRENT_USER, 0)
    installed_apps = []
    for software in software_list:
        installed_apps.append(software['name'])

    apps = sorted(installed_apps)
    context = {'apps': apps}
    # for app in apps:
    # print app.InstalledProductName
    # apps[0].InstalledProductName
    return render(request, 'about.html', context)


def activity_tracks(request):
    if request.method == 'POST':
        try:
            if os.path.exists("activities.json"):
                os.remove("activities.json")
            else:
                print('---------------------')
        except:
            return render(request, 'tracker.html')

    try:
        myjsondata = open('activities.json', 'r')
        jsondata = myjsondata.read()
        obj = json.loads(jsondata)
    except:

        return render(request, 'tracker.html')
    name = []
    time1 = []

    for l in obj['activities']:
        t = 0
        name.append(l['name'][:65])
        for k in l['time_entries']:
            time = int(k['days'])*24*60+int(k['minutes']) + \
                int(k['hours'])*60+(int(k['seconds'])/60)
            t = t+time

        s = str(t)
        time1.append(s[:5])
        t = 0

    context = {'name': name, 'time': time1}
    return render(request, 'tracker.html', context)


def resetTracker(request):
    msg = ''
    try:
        if os.path.exists("activities.json"):
            os.remove("activities.json")
            msg = "No track activity found to reset !"
        else:
            msg = "No track activity found to reset !"
    except:
        msg = 'Something went wrong !'

    return redirect('/', msg)
