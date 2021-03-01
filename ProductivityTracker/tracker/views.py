from itertools import count
from ctypes.wintypes import DWORD
from ctypes import byref, create_unicode_buffer, windll
from collections import namedtuple
import pandas as pd
import threading
from django.shortcuts import render, HttpResponse, redirect

import pythoncom
from .activity import *
import json
import datetime
import win32gui
import win32process
import psutil
import winreg
import time
import schedule
import re
import wmi
import pickle
from datetime import datetime as d
import sys
import ctypes
import psutil
import os

val = ""
fmval = ""


def about_page(request):
    return render(request, "about_page.html")


def home(request):
    name = []
    time1 = []
    table = []

    idx = 0

    noActivity = False

    try:
        myjsondata = open("activities.json", "r")
        jsondata = myjsondata.read()
        obj = json.loads(jsondata)
    except:
        noActivity = True

    if noActivity == False:
        for l in obj["activities"]:
            t = 0
            name.append(l["name"][:65])
            for k in l["time_entries"]:
                time = (
                    int(k["days"]) * 24 * 60
                    + int(k["minutes"])
                    + int(k["hours"]) * 60
                    + (int(k["seconds"]) / 60)
                )
                t = t + time

            s = str(t)
            time1.append(s[:5])

            if len(l["name"][:65]) > 0:
                n = []
                n.append(idx + 1)
                n.append(l["name"][:65])
                n.append(s[:5])
                table.append(n)
                idx = idx + 1

            t = 0
    context = {"name": name, "time": time1, "table": table}

    val = "off"
    fmval = "off"
    if request.method == "POST":
        v = request.POST.get("start")
        fmv = request.POST.get("focusmode")

        settings = {"tracking": v, "focus": fmv}

        with open("settings.pkl", "wb") as file:
            pickle.dump(settings, file)

        if v == "on" and fmv == "on":
            val = "on"
            fmval = "on"
            final(val, fmval)
        elif v == "on" and fmv == "off":
            val = "on"
            fmval = "off"
            final(val, fmval)
        elif v == "off" and fmv == "on":
            val = "off"
            fmval = "on"
            final(val, fmval)
        else:
            val = "off"
            fmval = "off"
            final(val, fmval)

        context["setting"] = settings
        return render(request, "home.html", context=context)

    settings = []
    try:
        pythoncom.CoInitialize()
        with open("settings.pkl", "rb") as file:
            settings = pickle.load(file)
    except:
        print("\nsomething went wrong\n")

    context["setting"] = settings
    return render(request, "home.html", context=context)


def get_active_window():
    _active_window_name = None
    try:
        if sys.platform in ["Windows", "win32", "cygwin"]:
            window = win32gui.GetForegroundWindow()
            pid = win32process.GetWindowThreadProcessId(
                win32gui.GetForegroundWindow())
            _active_window_name = psutil.Process(pid[-1]).name()
        else:
            print(
                "sys.platform={platform} is not supported.".format(
                    platform=sys.platform
                )
            )
            print(sys.version)
    except:
        _active_window_name = "Unknown"
        return _active_window_name
    return _active_window_name[0:-4]


# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------


def final(val, fmval):
    if val == "on":
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
        print("No json")
    m = 0
    try:
        while True:
            new_window_name = get_active_window()
            focusMode(fmval)
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
                    with open("activities.json", "w") as json_file:
                        json.dump(
                            activeList.serialize(), json_file, indent=4, sort_keys=True
                        )
                        start_time = datetime.datetime.now()
                first_time = False
                active_window_name = new_window_name

            time.sleep(1)

    except KeyboardInterrupt:
        with open("activities.json", "w") as json_file:
            json.dump(activeList.serialize(), json_file,
                      indent=4, sort_keys=True)


# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------


def focusMode(val):
    pythoncom.CoInitialize()
    data = []
    with open("focusModeApps.pkl", "rb") as file:
        data = pickle.load(file)
    f = wmi.WMI()
    app_proccess_names = []
    for process in f.Win32_Process():
        for i in data:
            if re.search(process.Name[:-4].lower(), i.lower()):
                app_proccess_names.append(process.Name)
    # print(app_proccess_names)
    if val == "on":
        for application in app_proccess_names:
            if application in (p.name() for p in psutil.process_iter()):
                # select process by its name
                os.system("taskkill /im " + application)


# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------


def foo(hive, flag):
    aReg = winreg.ConnectRegistry(None, hive)
    aKey = winreg.OpenKey(
        aReg,
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        0,
        winreg.KEY_READ | flag,
    )

    count_subkey = winreg.QueryInfoKey(aKey)[0]

    software_list = []

    for i in range(count_subkey):
        software = {}
        try:
            asubkey_name = winreg.EnumKey(aKey, i)
            asubkey = winreg.OpenKey(aKey, asubkey_name)
            software["name"] = winreg.QueryValueEx(asubkey, "DisplayName")[0]

            try:
                software["version"] = winreg.QueryValueEx(
                    asubkey, "DisplayVersion")[0]
            except EnvironmentError:
                software["version"] = "undefined"
            try:
                software["publisher"] = winreg.QueryValueEx(
                    asubkey, "Publisher")[0]
            except EnvironmentError:
                software["publisher"] = "undefined"
            software_list.append(software)
        except EnvironmentError:
            continue

    return software_list


def about(request):

    if request.method == "POST":
        # use filters var here to process
        data = request.POST.getlist("filters")
        # print(data)
        with open("focusModeApps.pkl", "wb") as file:
            pickle.dump(data, file)

        # print(data)

    software_list = (
        foo(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY)
        + foo(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY)
        + foo(winreg.HKEY_CURRENT_USER, 0)
    )
    installed_apps = []
    for software in software_list:
        installed_apps.append(software["name"])

    apps = sorted(installed_apps)
    data = []
    try:
        pythoncom.CoInitialize()
        with open("focusModeApps.pkl", "rb") as file:
            data = pickle.load(file)
    except:
        print("\nsomething went wrong\n")

    schedulertime = ""
    try:
        with open("schedulerTiming.pkl", "rb") as file:
            schedulertime = pickle.load(file)
    except:
        print("\nSchedule Time not found.\n")

    context = {"apps": apps, "selectedApp": data, 'start_time': '', 'end_time': ''}

    if len(schedulertime) > 0:
        startH = schedulertime[0:2]
        startM = schedulertime[3:5]
        endH = schedulertime[5:7]
        endM = schedulertime[8:]

        start_time = startH + ":" + startM
        end_time = endH + ":" + endM

        context['start_time'] = start_time
        context['end_time'] = end_time
    # for app in apps:
    # print app.InstalledProductName
    # apps[0].InstalledProductName
    return render(request, "about.html", context)


def activity_tracks(request):
    if request.method == "POST":
        try:
            if os.path.exists("activities.json"):
                os.remove("activities.json")
            else:
                print("---------------------")
        except:
            return render(request, "tracker.html")

    try:
        myjsondata = open("activities.json", "r")
        jsondata = myjsondata.read()
        obj = json.loads(jsondata)
    except:

        return render(request, "tracker.html")
    name = []
    time1 = []

    for l in obj["activities"]:
        t = 0
        name.append(l["name"][:65])
        for k in l["time_entries"]:
            time = (
                int(k["days"]) * 24 * 60
                + int(k["minutes"])
                + int(k["hours"]) * 60
                + (int(k["seconds"]) / 60)
            )
            t = t + time

        s = str(t)
        time1.append(s[:5])
        t = 0

    context = {"name": name, "time": time1}
    return render(request, "tracker.html", context)


def resetTracker(request):
    msg = ""
    try:
        if os.path.exists("activities.json"):
            os.remove("activities.json")
            msg = "No track activity found to reset !"
        else:
            msg = "No track activity found to reset !"
    except:
        msg = "Something went wrong !"

    return redirect("/", msg)


def setTime(request):
    schedulertime = ""  # 10:1214:15
    if request.method == "POST":
        start_time = request.POST.get("start_time")  # 17:20
        end_time = request.POST.get("end_time")  # 19:18
        print(start_time, end_time)
        if start_time != None and end_time != None:
            print(start_time, end_time)
            schedulertime = start_time+end_time
            with open("schedulerTiming.pkl", "wb") as file:
                pickle.dump(schedulertime, file)
    try:
        with open("schedulerTiming.pkl", "rb") as file:
            schedulertime = pickle.load(file)
    except:
        print("\nSchedule Time not found.\n")

    startH = int(schedulertime[0:2])
    startM = int(schedulertime[3:5])
    endH = int(schedulertime[5:7])
    endM = int(schedulertime[8:])

    # schedule.every().day.at('12:17').do(focusMode2(startH,startM,endH,endM))
    # schedule.every(1).to(2).seconds.do(focusMode2(startH,startM,endH,endM))

    print(startH, startM, endH, endM)
    focusMode2(startH, startM, endH, endM)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

    return redirect("/focus_mode/")


def focusMode2(startH, startM, endH, endM):
    while True:
        if (d(d.now().year, d.now().month, d.now().day, startH, startM)
                < d.now()
                < d(d.now().year, d.now().month, d.now().day, endH, endM)):
            focusMode('on')
        elif d.now() > d(d.now().year, d.now().month, d.now().day, endH, endM):
            return
