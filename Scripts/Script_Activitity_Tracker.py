from django.shortcuts import render, HttpResponse
import sys
import win32gui
import time
from .activity import *
import json
import datetime


def get_active_window():
    _active_window_name = None
    if sys.platform in ['Windows', 'win32', 'cygwin']:
        window = win32gui.GetForegroundWindow()
        _active_window_name = win32gui.GetWindowText(window)
    
    else:
        print("sys.platform={platform} is not supported."
              .format(platform=sys.platform))
        print(sys.version)
    return _active_window_name   

val=''
def check():
 if val=='on':
     return True
 else:
     return False
    

def final(val):
 if val=='on':
  t=True
 else:
     t=False
 active_window_name = ""
 activity_name = ""
 start_time = datetime.datetime.now()
 activeList = AcitivyList([])
 first_time = True

 try:
    activeList.initialize_me()
 except Exception:
    print('No json')
 m=0
 try:
    while m<5:
        m=m+1
        previous_site = ""
        new_window_name = get_active_window()        
        if m==4 and val=='on':
            m=0
        if val=='off':
            m=5
        
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
        json.dump(activeList.serialize(), json_file, indent=4, sort_keys=True)
 

import threading

# -------------------------------------------------------------------------------------
def home(request):
    

 val='off'
 if request.method == 'POST':
   v=request.POST.get('start')
   t = threading.Thread(target = final, args =(val, )) 
   
   if v=='on':
       val='on'
       final(val)
       
       
       t.start() 
   else:
       
       val='off'
       final(val)
       
   
       
       return render(request, 'home.html')

    
   
 return render(request, 'home.html'
