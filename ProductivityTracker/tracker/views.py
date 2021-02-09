from itertools import count
from ctypes.wintypes import DWORD
from ctypes import byref, create_unicode_buffer, windll
from collections import namedtuple
import pandas as pd
import threading
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

    val = 'off'
    try:
        myjsondata = open('activities.json', 'r')
        jsondata = myjsondata.read()
        obj = json.loads(jsondata)
    except:
        return render(request, 'home.html')

    name = []
    time1 = []
    table = []

    idx = 0

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

        return render(request, 'home.html', context)

    return render(request, 'home.html', context)

# ----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------


def about(request):

    # defined at http://msdn.microsoft.com/en-us/library/aa370101(v=VS.85).aspx
    UID_BUFFER_SIZE = 39
    PROPERTY_BUFFER_SIZE = 256
    ERROR_MORE_DATA = 234
    ERROR_INVALID_PARAMETER = 87
    ERROR_SUCCESS = 0
    ERROR_NO_MORE_ITEMS = 259
    ERROR_UNKNOWN_PRODUCT = 1605

# diff propoerties of a product, not all products have all properties
    PRODUCT_PROPERTIES = [u'Language',
                          u'ProductName',
                          u'PackageCode',
                          u'Transforms',
                          u'AssignmentType',
                          u'PackageName',
                          u'InstalledProductName',
                          u'VersionString',
                          u'RegCompany',
                          u'RegOwner',
                          u'ProductID',
                          u'ProductIcon',
                          u'InstallLocation',
                          u'InstallSource',
                          u'InstallDate',
                          u'Publisher',
                          u'LocalPackage',
                          u'HelpLink',
                          u'HelpTelephone',
                          u'URLInfoAbout',
                          u'URLUpdateInfo', ]

# class to be used for python users :)
    Product = namedtuple('Product', PRODUCT_PROPERTIES)

    def get_property_for_product(product, property, buf_size=PROPERTY_BUFFER_SIZE):
        """Retruns the value of a fiven property from a product."""
        property_buffer = create_unicode_buffer(buf_size)
        size = DWORD(buf_size)
        result = windll.msi.MsiGetProductInfoW(product, property, property_buffer,
                                               byref(size))
        if result == ERROR_MORE_DATA:
            return get_property_for_product(product, property,
                                            2 * buf_size)
        elif result == ERROR_SUCCESS:
            return property_buffer.value
        else:
            return None

    def populate_product(uid):
        """Return a Product with the different present data."""
        properties = []
        for property in PRODUCT_PROPERTIES:
            properties.append(get_property_for_product(uid, property))
        return Product(*properties)

    def get_installed_products_uids():
        """Returns a list with all the different uid of the installed apps."""
        # enum will return an error code according to the result of the app
        products = []
        for i in count(0):
            uid_buffer = create_unicode_buffer(UID_BUFFER_SIZE)
            result = windll.msi.MsiEnumProductsW(i, uid_buffer)
            if result == ERROR_NO_MORE_ITEMS:
                # done interating over the collection
                break
            products.append(uid_buffer.value)
        return products

    def get_installed_products():
        """Returns a collection of products that are installed in the system."""
        products = []
        for puid in get_installed_products_uids():
            products.append(populate_product(puid))
        return products

    def is_product_installed_uid(uid):
        """Return if a product with the given id is installed.

        uid Most be a unicode object with the uid of the product using
        the following format {uid}
        """
        # we try to get the VersisonString for the uid, if we get an error it means
        # that the product is not installed in the system.
        buf_size = 256
        uid_buffer = create_unicode_buffer(uid)
        property = u'VersionString'
        property_buffer = create_unicode_buffer(buf_size)
        size = DWORD(buf_size)
        result = windll.msi.MsiGetProductInfoW(uid_buffer, property, property_buffer,
                                               byref(size))
        if result == ERROR_UNKNOWN_PRODUCT:
            return False
        else:
            return True

    apps = get_installed_products()
    context = {'apps': apps}
# for app in apps:
    # print app.InstalledProductName
    # apps[0].InstalledProductName
    return render(request, 'about.html', context)


def activity_tracks(request):
    return render(request, 'tracker.html')
