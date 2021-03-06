#-*- coding: utf-8 -*-
#!/usr/bin/env python

import re, os, appium, time, uuid, StringIO, PIL.Image, datetime, selenium, traceback
from appium.webdriver.connectiontype import ConnectionType as Net_Android

class Phone(object):
    def __init__(self):
        #android deviceName & ios UDID
        self._identity = None
        #'android' / 'ios'
        self._platform = None
        #platform version
        self._version = None
        #app path
        self._app = None
        #app install
        self._install = False
        #android appPackage & ios BundleID
        self._package = None
        #apk Activity, android only
        self._activity = None
        #appium url
        self._executor = None
        #log path
        self._log = None
        #global delay
        self._delay = 0.7
        #private variable
        self._automation = None
        self._width = None #store phone width in private variable, in case this value varys as view changs
        self._height = None #store phone height in private variable, in case this value varys as view changs
        self._phone = None

    @property
    def identity(self):
        return self._identity
    @identity.setter
    def identity(self, identity):
        if not ((type(identity) is str) and (len(identity.strip()) > 0)):
            raise Exception('pass identity as str(len>0)!')
        self._identity = identity

    @property
    def platform(self):
        return self._platform
    @platform.setter
    def platform(self, platform):
        if not ((type(platform) is str) and (platform.strip().lower() in ['android', 'ios'])):
            raise Exception('pass platform as str(android/ios)!')
        self._platform = platform.strip().lower()

    @property
    def version(self):
        return self._version
    @version.setter
    def version(self, version):
        if not ((type(version) is str) and (len(re.findall(pattern = '^\s*[\.\d]+[\d]\s*$', string = version, flags = 0)) == 1)):
            raise Exception('pass version as str(7.7.7)!')
        self._version = version.strip()

    @property
    def app(self):
        return self._app
    @app.setter
    def app(self, app):
        if not ((type(app) is str) and (os.path.isfile(path = app.strip().decode(encoding = 'utf_8', errors = 'strict')))):
            raise Exception('pass app as str(app_path)!')
        self._app = app.strip()

    @property
    def install(self):
        return self._install is True
    @install.setter
    def install(self, install):
        self._install = install

    @property
    def package(self):
        return self._package
    @package.setter
    def package(self, package):
        if not ((type(package) is str) and (len(package.strip()) > 0)):
            raise Exception('pass package as str(len>0)!')
        self._package = package

    @property
    def activity(self):
        return self._activity
    @activity.setter
    def activity(self, activity):
        if not ((type(activity) is str) and (len(activity.strip()) > 0)):
            raise Exception('pass activity as str(len>0)!')
        self._activity = activity

    @property
    def executor(self):
        return self._executor
    @executor.setter
    def executor(self, executor):
        if not ((type(executor) is str) and (len(re.findall(pattern = '^\s*http://[a-z0-9A-Z.-_]+:\d{1,5}[/a-z]+\s*$', string = executor, flags = 0)) == 1) and (1 <= int((re.findall(pattern = '^\s*http://[a-z0-9A-Z.-_]+:(\d{1,5})[/a-z]+\s*$', string = executor, flags = 0))[0]) <= 65535)):
            raise Exception('pass executor as str(http://address:port/uri)!')
        self._executor = executor.strip()

    @property
    def log(self):
        return self._log
    @log.setter
    def log(self, path):
        self._log = Log(path = path, phone = self)

    @property
    def delay(self):
        return self._delay
    @delay.setter
    def delay(self, delay):
        if not (type(delay) is int and delay > 0):
            raise Exception('pass delay as int(>0)!')
        self._delay = delay / 1000

    def attach(self):
        if (not (self._identity is not None) and (self._platform is not None) and (self._version is not None) and (self._app is not None) and (self._executor is not None) and (self._log is not None)) or ((self._platform == 'android') and (not (self._package is not None) and (self._activity is not None))):
            raise Exception('identity/platform/version/app/executor/log/package/activity not pass!')
        elif (not (self._identity is not None) and (self._platform is not None) and (self._version is not None) and (self._app is not None) and (self._executor is not None) and (self._log is not None)) or ((self._platform == 'ios') and (self._package is None)):
            raise Exception('identity/platform/version/app/executor/log/package not pass!')

        #VERSION                       BACKEND         automationName
        #Android4.2+                   UiAutomator     Appium
        #Android2.3+                   Instrumentation Selendroid
        #iOS9.3+&Xcode7+&Appium1.6+    XCUITest        XCUITest
        #iOS9.2-&Xcode6-&Appium1.5-    Instruments     Appium
        #http://appium.io/slate/en/master/?python#android-support
        #http://appium.readthedocs.io/en/stable/en/advanced-concepts/migrating-to-xcuitest/

        #VERSION                       APILEVEL        COMPATIBILITY       INSPECTOR
        #Android4.1+                   API_Level16+    Product_Build_Ok    uiautomatorviewer
        #Android4.0-                   API_Level15-    Debug_Build_Only    hierarchyviewer
        #http://stackoverflow.com/questions/6011008/can-hierarchyviewer-be-used-with-a-real-device-other-than-the-nexus

        #VERSION                       WEBVIEW          INSPECTOR
        #Android4.4+                   Chromium         Chrome32+
        #Android4.3-                   WebKit           Selendroid
        #http://toolsqa.com/mobile-automation/appium/how-to-inspect-and-automate-webview-in-hybrid-app/

        capability = dict()
        if self._platform == 'android':
            capability['deviceName'] = self._identity
            capability['platformName'] = 'Android'
            capability['platformVersion'] = self._version
            capability['automationName'] = 'Appium'
            self._automation = 'Appium'
            if ((len(self._version.split('.')) >= 1) and (int(self._version.split('.')[0]) <= 3)) or ((len(self._version.split('.')) >= 2) and (int(self._version.split('.')[0]) == 4) and (int(self._version.split('.')[1]) <= 1)):
                capability['automationName'] = 'Selendroid'
                self._automation = 'Selendroid'
            capability['appPackage'] = self._package
            capability['appActivity'] = self._activity
            if self._app is not None:
                capability['app'] = self._app
                capability['androidInstallTimeout'] = 177000
                capability['autoLaunch'] = True
                capability['noReset'] = self._install is not True
                capability['fullReset'] = False
                capability['autoGrantPermissions'] = True
                if capability['automationName'] == 'Appium':
                    capability['noSign'] = True
            capability['deviceReadyTimeout'] = 77
            capability['androidDeviceReadyTimeout'] = 77
            capability['autoWebview'] = False
            capability['unicodeKeyboard'] = True
            capability['resetKeyboard'] = True
            capability['dontStopAppOnReset'] = False
            capability['disableAndroidWatchers'] = True
            capability['enablePerformanceLogging'] = False
            capability['nativeWebScreenshot'] = True
        else:
            capability['udid'] = self._identity
            capability['platformName'] = 'iOS'
            capability['platformVersion'] = self._version
            capability['automationName'] = 'XCUITest'
            self._automation = 'XCUITest'
            if ((len(self._version.split('.')) >= 1) and (int(self._version.split('.')[0]) <= 8)) or ((len(self._version.split('.')) >= 2) and (int(self._version.split('.')[0]) == 9) and (int(self._version.split('.')[1]) <= 2)):
                capability['automationName'] = 'Appium'
                self._automation = 'Appium'
            capability['bundleId'] = self._package
            if self._app is not None:
                capability['app'] = self._app
                capability['launchTimeout'] = 177000
                capability['autoLaunch'] = True
                capability['noReset'] = self._install is not True
                capability['fullReset'] = False
            capability['launchTimeout'] = 77000
            capability['webviewConnectRetries'] = 17
            if capability['automationName'] == 'XCUITest':
                capability['wdaLaunchTimeout'] = 77000
            capability['autoAcceptAlerts'] = False
            capability['autoDismissAlerts'] = False
            capability['autoWebview'] = False
            capability['screenshotWaitTimeout'] = 77

        self._log.ignite(ignite = 'Phone.attach()')
        try:
            self._log.clause(clause = 'identity = ' + self._identity + ', platform = ' + self._platform + ', version = ' + self._version + ', app = ' + self._app.replace('/', '\\') + ', install = ' + ('true' if self._install is True else 'false') + ', package = ' + self._package + ', activity = ' + (self._activity if self._activity is not None else 'none') + ', executor = ' + self._executor + ', log = ' + self._log._log.name.encode(encoding = 'utf_8', errors = 'strict'))

            self._phone = appium.webdriver.webdriver.WebDriver(command_executor = self._executor, desired_capabilities = capability)

            self._width = self._phone.get_window_size(windowHandle = 'current').get(u'width', None)
            self._height = self._phone.get_window_size(windowHandle = 'current').get(u'height', None)
            if not ((self._width is not None) and (self._height is not None)):
                raise Exception('phone size unknow!')

            self._log.effect(effect = 'phone attach')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def detach(self):
        self._log.ignite(ignite = 'Phone.detach()')
        try:
            self._log.clause(clause = 'none')

            self._phone.quit()

            self._log.effect(effect = 'phone detach')

            self._log._log.close()
        except Exception as e:
            self._log.error(error = e)
            self._log._log.close()
            raise e

    def applaunch(self):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.applaunch()')
        try:
            self._log.clause(clause = 'none')

            self._phone.launch_app()

            self._log.effect(effect = 'app launch')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def appclose(self):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.appclose()')
        try:
            self._log.clause(clause = 'none')

            self._phone.close_app()

            self._log.effect(effect = 'app close')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def appreset(self):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.appreset()')
        try:
            self._log.clause(clause = 'none')

            self._phone.reset()

            self._log.effect(effect = 'app reset')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def apphide(self, duration):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.apphide()')
        try:
            if not (type(duration) is int and duration > 0):
                raise Exception('pass duration as int(>0)!')

            self._log.clause(clause = 'duration = ' + str(duration))

            self._phone.background_app(seconds = duration / 1000)
            time.sleep(duration / 1000 + 0.7)

            self._log.effect(effect = 'app hide')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def find(self, attribute):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.find()')
        try:
            if ((self._platform == 'android') and (not (((type(attribute) is list) and (len(attribute) > 0)) or (isinstance(attribute, Android))))):
                raise Exception('pass attribute as Android()!')
            elif ((self._platform == 'ios') and (not (((type(attribute) is list) and (len(attribute) > 0)) or (isinstance(attribute, Ios))))):
                raise Exception('pass attribute as Ios()!')

            if type(attribute) is not list:
                attribute = [attribute]

            if self._platform == 'android':
                for i in attribute:
                    if not isinstance(i, Android):
                        raise Exception('pass attribute as list(Android())!')
            else:
                for i in attribute:
                    if not isinstance(i, Ios):
                        raise Exception('pass attribute as list(Ios())!')

            xpath = '//*'
            for i in attribute:
                if i._key in ['class', 'type']:
                    xpath = '//' + i._value
            for i in attribute:
                if i._key not in ['class', 'type']:
                    if i._strict is True:
                        xpath += '[@' + i._key + '=' + i._value + ']'
                    else:
                        xpath += '[contains(@' + i._key + ',' + i._value + ')]'

            self._log.clause(clause = 'xpath = ' + xpath)

            element = self._phone.find_elements(by = 'xpath', value = xpath.decode(encoding = 'utf_8', errors = 'strict'))
            if not ((type(element) is list) and (len(element) > 0)):
                raise Exception('find element = 0!')

            self._log.effect(effect = 'find element = ' + str(len(element)))

            array = list()
            for i in range(0, len(element), 1):
                array.append(Element(element = element[i], phone = self, xpath = xpath + '[' + str(i + 1) + ']'))

            return array
        except Exception as e:
            self._log.error(error = e)
            raise e

    def tap(self, x, y, count = 1):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.tap()')
        try:
##            if not ((type(x) is int) and (2 - self._width / 2 <= x <= self._width / 2 - 2) and (type(y) is int) and (2 - self._height / 2 <= y <= self._height / 2 - 2) and (type(count) is int) and (count > 0)):
##                raise Exception('pass x/y/count as int(within_size)/int(>0)!')
            if not ((type(x) is int) and (type(y) is int) and (type(count) is int) and (count > 0)):
                raise Exception('pass x/y/count as int()/int(>0)!')
            self._log.clause(clause = 'x = ' + str(x) + ', y = ' + str(y) + ', count = ' + str(count))

            appium.webdriver.common.touch_action.TouchAction(self._phone).tap(element = None, x = self._width / 2 + x, y = self._height / 2 - y, count = count).perform()

            self._log.effect(effect = 'phone tap = ' + str(count))
        except Exception as e:
            self._log.error(error = e)
            raise e

    def hold(self, x, y):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.hold()')
        try:
##            if not ((type(x) is int) and (2 - self._width / 2 <= x <= self._width / 2 - 2) and (type(y) is int) and (2 - self._height / 2 <= y <= self._height / 2 - 2)):
##                raise Exception('pass x/y as int(within_size)/int(>0)!')
            if not ((type(x) is int) and (type(y) is int)):
                raise Exception('pass x/y as int()/int(>0)!')
            self._log.clause(clause = 'x = ' + str(x) + ', y = ' + str(y))

            appium.webdriver.common.touch_action.TouchAction(self._phone).press(el = None, x = self._width / 2 + x, y = self._height / 2 - y).perform()

            self._log.effect(effect = 'phone hold')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def release(self, x, y):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.release()')
        try:
##            if not ((type(x) is int) and (2 - self._width / 2 <= x <= self._width / 2 - 2) and (type(y) is int) and (2 - self._height / 2 <= y <= self._height / 2 - 2)):
##                raise Exception('pass x/y as int(within_size)/int(>0)!')
            if not ((type(x) is int) and (type(y) is int)):
                raise Exception('pass x/y as int()/int(>0)!')
            self._log.clause(clause = 'x = ' + str(x) + ', y = ' + str(y))

            appium.webdriver.common.touch_action.TouchAction(self._phone).move_to(el = None, x = self._width / 2 + x, y = self._height / 2 - y).release().perform()

            self._log.effect(effect = 'phone release')
        except Exception as e:
            self._phone._log.error(error = e)
            raise e

    def press(self, duration, x, y):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.press()')
        try:
##            if not ((type(duration) is int) and (duration > 0) and (type(x) is int) and (2 - self._width / 2 <= x <= self._width / 2 - 2) and (type(y) is int) and (2 - self._height / 2 <= y <= self._height / 2 - 2)):
##                raise Exception('pass duration/x/y as int(>0)/int(within_size)!')
            if not ((type(duration) is int) and (duration > 0) and (type(x) is int) and (type(y) is int)):
                raise Exception('pass duration/x/y as int(>0)/int()!')
            self._phone._log.clause(clause = 'duration = ' + str(duration) + 'x = ' + str(x) + ', y = ' + str(y))

            appium.webdriver.common.touch_action.TouchAction(self._phone).long_press(el = None, x = self._width / 2 + x, y = self._height / 2 - y, duration = duration).perform()

            self._phone._log.effect(effect = 'phone press = ' + str(duration))
        except Exception as e:
            self._phone._log.error(error = e)
            raise e

    def shake(self, count = 1):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.shake()')
        try:
            if not ((type(count) is int) and (count > 0)):
                raise Exception('pass count as int(>0)!')

            self._log.clause(clause = 'count = ' + str(count))

            for i in range(0, count, 1):
                self._phone.shake()
                time.sleep(0.17)

            self._log.effect(effect = 'phone shake = ' + str(count))
        except Exception as e:
            self._log.error(error = e)
            raise e

    def locate(self, latitude, longitude, altitude):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.locate()')
        try:
            if not ((type(latitude) in [float, int]) and (-90 <= latitude <= 90) and (type(longitude) in [float, int]) and (-180 <= longitude <= 180) and (type(altitude) in [float, int])):
                raise Exception('pass latitude/longitude/altitude as float(latitude/longitude/altitude)/int(latitude/longitude/altitude)!')

            self._log.clause(clause = 'latitude = ' + str(latitude) + ', longitude = ' + str(longitude) + ', altitude = ' + str(altitude))

            self._phone.set_location(latitude = latitude, longitude = longitude, altitude = altitude)

            self._log.effect(effect = 'locate set')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def width(self):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.width()')
        try:
            self._log.clause(clause = 'none')

            self._log.effect(effect = 'phone width = ' + str(self._width))

            return self._width
        except Exception as e:
            self._log.error(error = e)
            raise e

    def height(self):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.height()')
        try:
            self._log.clause(clause = 'none')

            self._log.effect(effect = 'phone height = ' + str(self._height))

            return self._height
        except Exception as e:
            self._log.error(error = e)
            raise e

    def topbottom(self):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.topbottom()')
        try:
            self._log.clause(clause = 'none')

            #several android phone has soft menu button displayed at the bottom of the screen, and several android pad's notification area is on the left-top of the screen, thus we should do the operation near the screen's left edge to achive the entire flick action chain
            appium.webdriver.common.touch_action.TouchAction(driver = self._phone).press(el = None, x = self._width * 2 / 7, y = 1).move_to(el = None, x = 0, y = self._height - 2).release().perform()

            self._log.effect(effect = 'flick topbottom')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def bottomtop(self):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.bottomtop()')
        try:
            self._log.clause(clause = 'none')

            #several android phone has soft menu button displayed at the bottom of the screen, thus we should do the operation near the screen's left edge to achive the entire flick action chain
            appium.webdriver.common.touch_action.TouchAction(driver = self._phone).press(el = None, x = self._width * 2 / 7, y = self._height - 1).move_to(el = None, x = 0, y = 2 - self._height).release().perform()

            self._log.effect(effect = 'flick bottomtop')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def leftright(self):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.leftright()')
        try:
            self._log.clause(clause = 'none')

            appium.webdriver.common.touch_action.TouchAction(driver = self._phone).press(el = None, x = 1, y = self._height / 2).move_to(el = None, x = self._width - 2, y = 0).release().perform()

            self._log.effect(effect = 'flick leftright')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def rightleft(self):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.rightleft()')
        try:
            self._log.clause(clause = 'none')

            appium.webdriver.common.touch_action.TouchAction(driver = self._phone).press(el = None, x = self._width - 1, y = self._height / 2).move_to(el = None, x = 2 - self._width, y = 0).release().perform()

            self._log.effect(effect = 'flick rightleft')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def imefold(self):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.imefold()')
        try:
            self._log.clause(clause = 'none')

            if self._platform == 'android':
                self._phone.hide_keyboard(key_name = None, key = None, strategy = None)
            else:
##                #the old fashioned way
##                appium.webdriver.common.touch_action.TouchAction(driver = self._phone).press(el = None, x = self._width / 2, y = self._height / 7).move_to(el = None, x = 0, y = self._height * 6 / 7 - 2).release().perform()

                self._phone.hide_keyboard(key_name = None, key = None, strategy = 'swipeDown')

            self._log.effect(effect = 'ime fold')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def shoot(self, path):
##        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.shoot()')
        try:
            if not ((type(path) is str) and (len(re.findall(pattern = '^\s*(.+[/\\\])(.*[.]png)\s*$', string = path, flags = re.IGNORECASE)) == 1) and (len(re.findall(pattern = '^\s*(.+[/\\\])\s*(.*[.]png)\s*$', string = path, flags = re.IGNORECASE)[0][1]) > 0)):
                raise Exception('pass path as str(png_path)!')

            if not os.path.exists(path = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'utf_8', errors = 'strict')):
                os.makedirs(name = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'utf_8', errors = 'strict'), mode = 0777)

            self._log.clause(clause = 'path = ' + (re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*[.]png)\s*$', string = path, flags = re.IGNORECASE)[0][1]).replace('/', '\\'))

            for i in range(0, 7, 1):
                try:
##                    self._phone.get_screenshot_as_file(filename = (re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*[.]png)\s*$', string = path, flags = re.IGNORECASE)[0][1]).decode(encoding = 'utf_8', errors = 'strict'))
                    with open(name = (re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*[.]png)\s*$', string = path, flags = re.IGNORECASE)[0][1]).decode(encoding = 'utf_8', errors = 'strict'), mode = 'wb+', buffering = 0) as f:
                        f.write(self._phone.get_screenshot_as_base64().decode(encoding = 'base64_codec', errors = 'strict'))
                    break
                except Exception as e:
                    time.sleep(0.07)
                    if i == 6:
                        raise e

            self._log.effect(effect = 'phone shoot')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def type_Android(self, key, meta = None):
    #https://developer.android.com/reference/android/view/KeyEvent.html
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.type_Android()')
        try:
            if not ((self._platform == 'android') and (type(key) is int) and (key > 0) and ((meta is None) or ((type(meta) is int) and (meta > 0)))):
                raise Exception('android only, pass key/meta as int(>0)!')

            self._log.clause(clause = 'key = ' + str(key) + ', meta = ' + ('none' if meta is None else str(meta)))

            if self._automation == 'Appium':
                self._phone.press_keycode(keycode = key, metastate = meta)
            else:
                self._phone.keyevent(keycode = key, metastate = meta)

            self._log.effect(effect = 'key type')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def toast_Android(self, toast, strict = True, timeout = 7000):
##        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.toast_Android()')
        try:
            if not ((self._platform == 'android') and (type(toast) is str) and (len(toast) > 0) and (type(timeout) is int) and (timeout > 0)):
                raise Exception('android only, pass toast/timeout as str(len>0)/int(>0)!')

            if strict is True:
                xpath = "//*[@text='" + toast + "']"
            else:
                xpath = "//*[contains(@text,'" + toast + "')]"

            self._log.clause(clause = 'xpath = ' + xpath + ', timeout = ' + str(timeout))

            end = time.time() + timeout / 1000
            while time.time() < end:
                try:
                    if isinstance(self._phone.find_element(by = 'xpath', value = xpath.decode(encoding = 'utf_8', errors = 'strict')), appium.webdriver.webdriver.WebElement):
                        break
                except:
                    if time.time() < end:
                        time.sleep(0.07)
                    else:
                        self._log.effect(effect = 'toast miss')
                        return False

            png = self._log._log.name + '.' + uuid.uuid4().hex + '.png'
            for i in range(0, 7, 1):
                try:
##                    self._phone.get_screenshot_as_file(filename = png)
                    with open(name = png, mode = 'wb+', buffering = 0) as f:
                        f.write(self._phone.get_screenshot_as_base64().decode(encoding = 'base64_codec', errors = 'strict'))
                    self._log.effect(effect = 'toast catch = ' + png.encode(encoding = 'utf_8', errors = 'strict'))
                    break
                except:
                    time.sleep(0.07)
                    if id == 6:
                        self._log.effect(effect = 'toast catch')
            return True
        except Exception as e:
            self._log.error(error = e)
            raise e

    def net_Android(self, net):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.net_Android()')
        try:
            if not ((self._platform == 'android') and (net in appium.webdriver.connectiontype.ConnectionType.__dict__.values())):
                raise Exception('android only, pass net as AndroidNet()!')

            if net == 0:
                connection = 'NO_CONNECTION'
            elif net == 1:
                connection = 'AIRPLANE_MODE'
            elif net == 2:
                connection = 'WIFI_ONLY'
            elif net == 4:
                connection = 'DATA_ONLY'
            else:
                connection = 'ALL_NETWORK_ON'

            self._log.clause(clause = 'net = ' + connection)

            self._phone.set_network_connection(connectionType = net)

            self._log.effect(effect = connection + ' set')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def push_Android(self, local, remote):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.push_Android()')
        try:
            if not ((self._platform == 'android') and (type(local) is str) and (os.path.isfile(path = local.strip().decode(encoding = 'utf_8', errors = 'strict'))) and (type(remote) is str) and (len(re.findall(pattern = '^\s*([/\\\].*[^\s/\\\]).*$', string = remote, flags = 0)) == 1)):
                raise Exception('android only, pass local/remote as str(file_path)!')

            self._log.clause(clause = 'local = ' + local.strip().replace('/', '\\') + ', remote = ' + re.findall(pattern = '^\s*([/\\\].*[^\s/\\\]).*$', string = remote, flags = 0)[0].replace('\\', '/'))

            with open(name = local.strip().decode(encoding = 'utf_8', errors = 'strict'), mode = 'rb') as f:
                self._phone.push_file(path = re.findall(pattern = '^\s*([/\\\].*[^\s/\\\]).*$', string = remote, flags = 0)[0].replace('\\', '/').decode(encoding = 'utf_8', errors = 'strict'), base64data = f.read().encode(encoding = 'base64_codec', errors = 'strict'))

            self._log.effect(effect = 'file push')
        except Exception as e:
            self._log.error(error = e)
            raise e

    def pull_Android(self, local, remote):
        time.sleep(self._delay)
        self._log.ignite(ignite = 'Phone.pull_Android()')
        try:
            if not ((self._platform == 'android') and (type(local) is str) and (len(re.findall(pattern = '^\s*(.+[/\\\])(.*)\s*$', string = local, flags = 0)) == 1) and (len(re.findall(pattern = '^\s*(.+[/\\\])\s*(.*)\s*$', string = local, flags = 0)[0][1]) > 0) and (type(remote) is str) and (len(re.findall(pattern = '^\s*([/\\\].*[^\s/\\\]).*$', string = remote, flags = 0)) == 1)):
                raise Exception('android only, pass local/remote as str(file_path)!')

            self._log.clause(clause = 'local = ' + (re.findall(pattern = '^\s*(.+[/\\\]).*$', string = local, flags = 0)[0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*)\s*$', string = local, flags = 0)[0][1]).replace('/', '\\') + ', remote = ' + re.findall(pattern = '^\s*([/\\\].*[^\s/\\\]).*$', string = remote, flags = 0)[0].replace('\\', '/'))

            if not os.path.exists(path = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = local, flags = 0)[0].decode(encoding = 'utf_8', errors = 'strict')):
                os.makedirs(name = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = local, flags = 0)[0].decode(encoding = 'utf_8', errors = 'strict'), mode = 0777)

            try:
                with open(name = (re.findall(pattern = '^\s*(.+[/\\\]).*$', string = local, flags = 0)[0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*)\s*$', string = local, flags = 0)[0][1]).decode(encoding = 'utf_8', errors = 'strict'), mode = 'wb+', buffering = 0) as f:
                    f.write(self._phone.pull_file(path = re.findall(pattern = '^\s*([/\\\].*[^\s/\\\]).*$', string = remote, flags = 0)[0].replace('\\', '/').decode(encoding = 'utf_8', errors = 'strict')).decode(encoding = 'base64_codec', errors = 'strict'))
                pull = 'file'
            except selenium.common.exceptions.WebDriverException as e:
                try:
                    with open(name = (re.findall(pattern = '^\s*(.+[/\\\]).*$', string = local, flags = 0)[0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*)\s*$', string = local, flags = 0)[0][1]).decode(encoding = 'utf_8', errors = 'strict'), mode = 'wb+', buffering = 0) as f:
                        f.write(self._phone.pull_folder(path = re.findall(pattern = '^\s*([/\\\].*[^\s/\\\]).*$', string = remote, flags = 0)[0].replace('\\', '/').decode(encoding = 'utf_8', errors = 'strict')).decode(encoding = 'base64_codec', errors = 'strict'))
                    pull = 'folder'
                except:
                    raise e

            self._log.effect(effect = pull + ' pull')
        except Exception as e:
            self._log.error(error = e)
            raise e

##I do not think I would like to support webview
##        def context(self):
##            self._phone.contexts
##        def webin(self, web):
##            self._context = self._phone.current_context
##            self._phone._switch_to.context(context_name = web)
##            self._web = True
##        def webout(self):
##            self._phone._switch_to.context(context_name = self._context)
##            self._web = False







class Element(object):
    def __init__(self, element, phone, xpath):
        if not ((isinstance(element, appium.webdriver.webelement.WebElement)) and (isinstance(phone, Phone)) and (type(xpath) is str) and (len(xpath.strip()) > 0)):
            raise Exception('pass element/phone/xpath as WebElement()/Phone()/str(xpath)!')
        self._element = element
        self._phone = phone
        self._xpath = xpath
##        #element could be dynamic and not static, element location & size maybe change from time to time
##        self._abscissa = self._element.location_in_view.get(u'x', None) #store element x coordinate in private variable, in case this value varys as view changs
##        self._ordinate = self._element.location_in_view.get(u'y', None) #store element y coordinate in private variable, in case this value varys as view changs
##        if not ((self._abscissa is not None) and (self._ordinate is not None)):
##            raise Exception('element coordinate unknow!')

    def find(self, attribute):
        time.sleep(self._phone._delay)
        self._phone._log.ignite(ignite = 'Element.find()')
        try:
            if ((self._phone._platform == 'android') and (not (((type(attribute) is list) and (len(attribute) > 0)) or (isinstance(attribute, Android))))):
                raise Exception('pass attribute as Android()!')
            elif ((self._phone._platform == 'ios') and (not (((type(attribute) is list) and (len(attribute) > 0)) or (isinstance(attribute, Ios))))):
                raise Exception('pass attribute as Ios()!')

            if type(attribute) is not list:
                attribute = [attribute]

            if self._phone._platform == 'android':
                for i in attribute:
                    if not isinstance(i, Android):
                        raise Exception('pass attribute as list(Android())!')
            else:
                for i in attribute:
                    if not isinstance(i, Ios):
                        raise Exception('pass attribute as list(Ios())!')

            xpath = self._xpath + '//*'
            for i in attribute:
                if i._key in ['class', 'type']:
                    xpath = self._xpath + '//' + i._value
            for i in attribute:
                if i._key not in ['class', 'type']:
                    if i._strict is True:
                        xpath += '[@' + i._key + '=' + i._value + ']'
                    else:
                        xpath += '[contains(@' + i._key + ',' + i._value + ')]'

            self._phone._log.clause(clause = 'xpath = .' + xpath[len(self._xpath)::1])

            element = self._element._parent.find_elements(by = 'xpath', value = xpath.decode(encoding = 'utf_8', errors = 'strict'))
            if not ((type(element) is list) and (len(element) > 0)):
                raise Exception('find element = 0!')

            self._phone._log.effect(effect = 'find element = ' + str(len(element)))

            array = list()
            for i in range(0, len(element), 1):
                array.append(Element(element = element[i], phone = self._phone, xpath = xpath + '[' + str(i + 1) + ']'))

            return array
        except Exception as e:
            self._phone._log.error(error = e)
            raise e

    def parent(self):
        time.sleep(self._phone._delay)
        self._phone._log.ignite(ignite = 'Element.parent()')
        try:
            xpath = self._xpath + '/..'

            self._phone._log.clause(clause = 'xpath = ./..')

            element = self._element._parent.find_element(by = 'xpath', value = xpath.decode(encoding = 'utf_8', errors = 'strict'))

            self._phone._log.effect(effect = 'parent find')

            return Element(element = element, phone = self._phone, xpath = xpath)
        except Exception as e:
            self._phone._log.error(error = e)
            raise e

    def tap(self, x = 0, y = 0, count = 1):
        time.sleep(self._phone._delay)
        self._phone._log.ignite(ignite = 'Element.tap()')
        try:
##            if not ((type(x) is int) and (1 <= self._element.location_in_view[u'x'] + self._element.size['width'] / 2 + x <= self._phone._width - 1) and (type(y) is int) and (1 <= self._element.location_in_view[u'y'] + self._element.size['height'] / 2 - y <= self._phone._height - 1) and (type(count) is int) and (count > 0)):
##                raise Exception('pass x/y/count as int(within_size)/int(>0)!')
            if not ((type(x) is int) and (type(y) is int) and (type(count) is int) and (count > 0)):
                raise Exception('pass x/y/count as int()/int(>0)!')

            self._phone._log.clause(clause = 'x = ' + str(x) + ', y = ' + str(y) + ', count = ' + str(count))

            end = time.time() + 7
            while time.time() < end:
                try:
                    if self._element.is_displayed() is True:
                        break
                    else:
                        raise Exception('element not display!')
                except Exception as e:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e

            if x == 0 and y == 0:
                appium.webdriver.common.touch_action.TouchAction(self._element._parent).tap(element = self._element, x = None, y = None, count = count).perform()
            else:
                appium.webdriver.common.touch_action.TouchAction(self._element._parent).tap(element = None, x = self._element.location_in_view[u'x'] + self._element.size['width'] / 2 + x, y = self._element.location_in_view[u'y'] + self._element.size['height'] / 2 - y, count = count).perform()

            self._phone._log.effect(effect = 'element tap = ' + str(count))
        except Exception as e:
            self._phone._log.error(error = e)
            raise e

    def hold(self, x = 0, y = 0):
        time.sleep(self._phone._delay)
        self._phone._log.ignite(ignite = 'Element.hold()')
        try:
##            if not ((type(x) is int) and (1 <= self._element.location_in_view[u'x'] + self._element.size['width'] / 2 + x <= self._phone._width - 1) and (type(y) is int) and (1 <= self._element.location_in_view[u'y'] + self._element.size['height'] / 2 - y <= self._phone._height - 1)):
##                raise Exception('pass x/y as int(within_size)!')
            if not ((type(x) is int) and (type(y) is int)):
                raise Exception('pass x/y as int()!')

            self._phone._log.clause(clause = 'x = ' + str(x) + ', y = ' + str(y))

            end = time.time() + 7
            while time.time() < end:
                try:
                    if self._element.is_displayed() is True:
                        break
                    else:
                        raise Exception('element not display!')
                except Exception as e:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e

            if x == 0 and y == 0:
                appium.webdriver.common.touch_action.TouchAction(self._element._parent).press(el = self._element, x = None, y = None).perform()
            else:
                appium.webdriver.common.touch_action.TouchAction(self._element._parent).press(el = None, x = self._element.location_in_view[u'x'] + self._element.size['width'] / 2 + x, y = self._element.location_in_view[u'y'] + self._element.size['height'] / 2 - y).perform()

            self._phone._log.effect(effect = 'element hold')
        except Exception as e:
            self._phone._log.error(error = e)
            raise e

    def release(self, x = 0, y = 0):
        time.sleep(self._phone._delay)
        self._phone._log.ignite(ignite = 'Element.release()')
        try:
##            if not ((type(x) is int) and (1 <= self._element.location_in_view[u'x'] + self._element.size['width'] / 2 + x <= self._phone._width - 1) and (type(y) is int) and (1 <= self._element.location_in_view[u'y'] + self._element.size['height'] / 2 - y <= self._phone._height - 1)):
##                raise Exception('pass x/y as int(within_size)!')
            if not ((type(x) is int) and (type(y) is int)):
                raise Exception('pass x/y as int()!')

            self._phone._log.clause(clause = 'x = ' + str(x) + ', y = ' + str(y))

            end = time.time() + 7
            while time.time() < end:
                try:
                    if self._element.is_displayed() is True:
                        break
                    else:
                        raise Exception('element not display!')
                except Exception as e:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e

            if x == 0 and y == 0:
                appium.webdriver.common.touch_action.TouchAction(self._element._parent).move_to(el = self._element, x = None, y = None).release().perform()
            else:
                appium.webdriver.common.touch_action.TouchAction(self._element._parent).move_to(el = None, x = self._element.location_in_view[u'x'] + self._element.size['width'] / 2 + x, y = self._element.location_in_view[u'y'] + self._element.size['height'] / 2 - y).release().perform()

            self._phone._log.effect(effect = 'element release')
        except Exception as e:
            self._phone._log.error(error = e)
            raise e

    def press(self, duration, x = 0, y = 0):
        time.sleep(self._phone._delay)
        self._phone._log.ignite(ignite = 'Element.press()')
        try:
##            if not ((type(duration) is int) and (duration > 0) and (type(x) is int) and (1 <= self._element.location_in_view[u'x'] + self._element.size['width'] / 2 + x <= self._phone._width - 1) and (type(y) is int) and (1 <= self._element.location_in_view[u'y'] + self._element.size['height'] / 2 - y <= self._phone._height - 1)):
##                raise Exception('pass duration/x/y as int(>0)/int(within_size)!')
            if not ((type(duration) is int) and (duration > 0) and (type(x) is int) and (type(y) is int)):
                raise Exception('pass duration/x/y as int(>0)/int()!')

            self._phone._log.clause(clause = 'duration = ' + str(duration) + 'x = ' + str(x) + ', y = ' + str(y))

            end = time.time() + 7
            while time.time() < end:
                try:
                    if self._element.is_displayed() is True:
                        break
                    else:
                        raise Exception('element not display!')
                except Exception as e:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e

            if x == 0 and y == 0:
                appium.webdriver.common.touch_action.TouchAction(self._element._parent).long_press(el = self._element, x = None, y = None, duration = duration).perform()
            else:
                appium.webdriver.common.touch_action.TouchAction(self._element._parent).long_press(el = None, x = self._element.location_in_view[u'x'] + self._element.size['width'] / 2 + x, y = self._element.location_in_view[u'y'] + self._element.size['height'] / 2 - y, duration = duration).perform()

            self._phone._log.effect(effect = 'element press = ' + str(duration))
        except Exception as e:
            self._phone._log.error(error = e)
            raise e

    def clear(self):
        time.sleep(self._phone._delay)
        self._phone._log.ignite(ignite = 'Element.clear()')
        try:
            self._phone._log.clause(clause = 'none')

            end = time.time() + 7
            while time.time() < end:
                try:
                    if self._element.is_displayed() is True:
                        break
                    else:
                        raise Exception('element not display!')
                except Exception as e:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e

            if self._phone._platform == 'android':
##                #the old fashioned way
##                appium.webdriver.common.touch_action.TouchAction(self._element._parent).tap(element = self._element, x = None, y = None, count = 1).perform()
##                if self._phone._automation == 'Appium':
####                    self._element._parent.press_keycode(keycode = 29, metastate = 28672)
####                    self._element._parent.press_keycode(keycode = 112, metastate = None)
##
##                    self._element._parent.press_keycode(keycode = 122, metastate = None)
##                    self._element._parent.press_keycode(keycode = 123, metastate = 193)
##                    self._element._parent.press_keycode(keycode = 112, metastate = None)
##                else:
####                    self._element._parent.keyevent(keycode = 29, metastate = 28672)
####                    self._element._parent.keyevent(keycode = 112, metastate = None)
##
##                    self._element._parent.keyevent(keycode = 122, metastate = None)
##                    self._element._parent.keyevent(keycode = 123, metastate = 193)
##                    self._element._parent.keyevent(keycode = 112, metastate = None)
##                try:
##                    self._element._parent.hide_keyboard(key_name = None, key = None, strategy = None)
##                except:
##                    pass
                self._element.set_text(keys = '')
            else:
##                self._element.send_keys('')
##                self._element.set_value(value = '')
                self._element.clear()

            self._phone._log.effect(effect = 'content clear')
        except Exception as e:
            self._phone._log.error(error = e)
            raise e

    def send(self, send):
        time.sleep(self._phone._delay)
        self._phone._log.ignite(ignite = 'Element.send()')
        try:
            if not ((type(send) is str) and (len(send) > 0)):
                raise Exception('pass send as str(len>0)!')

            end = time.time() + 7
            while time.time() < end:
                try:
                    if self._element.is_displayed() is True:
                        break
                    else:
                        raise Exception('element not display!')
                except Exception as e:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e

            self._phone._log.clause(clause = 'send = ' + send)

            if self._phone._platform == 'android':
                appium.webdriver.common.touch_action.TouchAction(self._element._parent).tap(element = self._element, x = None, y = None, count = 1).perform()
                self._element.set_text(keys = send.decode(encoding = 'utf_8', errors = 'strict'))
                try:
                    self._element._parent.hide_keyboard(key_name = None, key = None, strategy = None)
                except:
                    pass
            else:
##                self._element.send_keys(send.decode(encoding = 'utf_8', errors = 'strict'))
                self._element.set_value(value = send.decode(encoding = 'utf_8', errors = 'strict'))

            self._phone._log.effect(effect = 'line send')
        except Exception as e:
            self._phone._log.error(exception = e)
            raise e

    def waitexist(self, attribute, timeout = 7000):
        time.sleep(self._phone._delay)
        self._phone._log.ignite(ignite = 'Element.waitexist()')
        try:
            if ((self._phone._platform == 'android') and (not (((type(attribute) is list) and (len(attribute) > 0)) or (isinstance(attribute, Android))) and (type(timeout) is int) and (timeout > 0))):
                raise Exception('pass attribute/timeout as Android()/int(>0)!')
            elif ((self._phone._platform == 'ios') and (not (((type(attribute) is list) and (len(attribute) > 0)) or (isinstance(attribute, Ios))) and (type(timeout) is int) and (timeout > 0))):
                raise Exception('pass attribute/timeout as Ios()/int(>0)!')

            if type(attribute) is not list:
                attribute = [attribute]

            if self._phone._platform == 'android':
                for i in attribute:
                    if not isinstance(i, Android):
                        raise Exception('pass attribute as list(Android())!')
            else:
                for i in attribute:
                    if not isinstance(i, Ios):
                        raise Exception('pass attribute as list(Ios())!')

            xpath = self._xpath + '//*'
            for i in attribute:
                if i._key in ['class', 'type']:
                    xpath = self._xpath + '//' + i._value
            for i in attribute:
                if i._key not in ['class', 'type']:
                    if i._strict is True:
                        xpath += '[@' + i._key + '=' + i._value + ']'
                    else:
                        xpath += '[contains(@' + i._key + ',' + i._value + ')]'

            self._phone._log.clause(clause = 'xpath = .' + xpath[len(self._xpath)::1])

            end = time.time() + timeout / 1000
            while time.time() < end:
                try:
                    if not isinstance(self._element._parent.find_element(by = 'xpath', value = xpath.decode(encoding = 'utf_8', errors = 'strict')), appium.webdriver.webdriver.WebElement):
                        raise Exception('element not exist!')
                except Exception as e:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise e
                else:
                    break

            self._phone._log.effect(effect = 'element exist')
        except Exception as e:
            self._phone._log.error(error = e)
            raise e

    def waitextinct(self, attribute, timeout = 7000):
        time.sleep(self._phone._delay)
        self._phone._log.ignite(ignite = 'Element.waitextinct()')
        try:
            if ((self._phone._platform == 'android') and (not (((type(attribute) is list) and (len(attribute) > 0)) or (isinstance(attribute, Android))) and (type(timeout) is int) and (timeout > 0))):
                raise Exception('pass attribute/timeout as Android()/int(>0)!')
            elif ((self._phone._platform == 'ios') and (not (((type(attribute) is list) and (len(attribute) > 0)) or (isinstance(attribute, Ios))) and (type(timeout) is int) and (timeout > 0))):
                raise Exception('pass attribute/timeout as Ios()/int(>0)!')

            if type(attribute) is not list:
                attribute = [attribute]

            if self._phone._platform == 'android':
                for i in attribute:
                    if not isinstance(i, Android):
                        raise Exception('pass attribute as list(Android())!')
            else:
                for i in attribute:
                    if not isinstance(i, Ios):
                        raise Exception('pass attribute as list(Ios())!')

            xpath = self._xpath + '//*'
            for i in attribute:
                if i._key in ['class', 'type']:
                    xpath = self._xpath + '//' + i._value
            for i in attribute:
                if i._key not in ['class', 'type']:
                    if i._strict is True:
                        xpath += '[@' + i._key + '=' + i._value + ']'
                    else:
                        xpath += '[contains(@' + i._key + ',' + i._value + ')]'

            self._phone._log.clause(clause = 'xpath = .' + xpath[len(self._xpath)::1])

            end = time.time() + timeout / 1000
            while time.time() < end:
                try:
                    if not isinstance(self._element._parent.find_element(by = 'xpath', value = xpath.decode(encoding = 'utf_8', errors = 'strict')), appium.webdriver.webdriver.WebElement):
                        raise
                except Exception:
                        break
                else:
                    if time.time() < end:
                        time.sleep(0.7)
                    else:
                        raise Exception('element not extinct!')

            self._phone._log.effect(effect = 'element extinct')
        except Exception as e:
            self._phone._log.error(error = e)
            raise e

    def attribute(self, key):
        time.sleep(self._phone._delay)
        self._phone._log.ignite(ignite = 'Element.attribute()')
        try:
            if not ((type(key) is str) and (len(key.strip()) > 0)):
                raise Exception('pass key as str(len>0)!')

            self._phone._log.clause(clause = 'key = ' + key.strip())

            value = self._element.get_attribute(name = key.strip().decode(encoding = 'utf_8', errors = 'strict'))
            if type(value) is unicode:
                value = value.encode(encoding = 'utf_8', errors = 'strict')

            self._phone._log.effect(effect = 'attibute [' + key.strip() + '] = ' + (value if value is not None else 'none'))

            return value
        except Exception as e:
            self._phone._log.error(error = e)
            raise e

    def width(self):
        time.sleep(self._phone._delay)
        self._phone._log.ignite(ignite = 'Element.width()')
        try:
            self._phone._log.clause(clause = 'none')

            width = self._element.size.get('width', None)

            self._phone._log.effect(effect = 'element width = ' + (str(width) if width is not None else 'none'))

            return width
        except Exception as e:
            self._phone._log.error(error = e)
            raise e

    def height(self):
        time.sleep(self._phone._delay)
        self._phone._log.ignite(ignite = 'Element.height()')
        try:
            self._phone._log.clause(clause = 'none')

            height = self._element.size.get('height', None)

            self._phone._log.effect(effect = 'element height = ' + (str(height) if height is not None else 'none'))

            return height
        except Exception as e:
            self._phone._log.error(error = e)
            raise e

    def abscissa(self):
        time.sleep(self._phone._delay)
        self._phone._log.ignite(ignite = 'Element.abscissa()')
        try:
            self._phone._log.clause(clause = 'none')

            abscissa = self._element.location_in_view[u'x'] + self._element.size['width'] - self._phone._width / 2

            self._phone._log.effect(effect = 'element abscissa = ' + str(abscissa))

            return abscissa
        except Exception as e:
            self._phone._log.error(error = e)
            raise e

    def ordinate(self):
        time.sleep(self._phone._delay)
        self._phone._log.ignite(ignite = 'Element.ordinate()')
        try:
            self._phone._log.clause(clause = 'none')

            ordinate = self._phone._height / 2 - self._element.location_in_view[u'y'] - self._element.size['height']

            self._phone._log.effect(effect = 'element ordinate = ' + str(ordinate))

            return ordinate
        except Exception as e:
            self._phone._log.error(error = e)
            raise e

    def isdisplay(self):
        time.sleep(self._phone._delay)
        self._phone._log.ignite(ignite = 'Element.isdisplay()')
        try:
            self._phone._log.clause(clause = 'none')

##            #the old fashioned way
##            if self._phone._platform == 'android':
##                result = self._element.is_displayed() is True
##            else:
##                result = self._element.get_attribute(name = 'visible') is True

            result = self._element.is_displayed() is True

            self._phone._log.effect(effect = 'element isdisplay = ' + ('true' if result else 'false'))

            return result
        except Exception as e:
            self._phone._log.error(error = e)
            raise e

    def isselect(self):
        time.sleep(self._phone._delay)
        self._phone._log.ignite(ignite = 'Element.isselect()')
        try:
            self._phone._log.clause(clause = 'none')

##            #the old fashioned way
##            if self._phone._platform == 'android':
##                result = self._element.get_attribute(name = 'checked') is True
##            else:
##                result = self._element.is_selected() is True

            result = self._element.is_selected() is True

            self._phone._log.effect(effect = 'element isselect = ' + ('true' if result else 'false'))

            return result
        except Exception as e:
            self._phone._log.error(error = e)
            raise e

    def isenable(self):
        time.sleep(self._phone._delay)
        self._phone._log.ignite(ignite = 'Element.isenable()')
        try:
            self._phone._log.clause(clause = 'none')

##            #the old fashioned way
##            result = self._element.get_attribute(name = 'enabled') is True

            result = self._element.is_enabled() is True

            self._phone._log.effect(effect = 'element isenable = ' + ('true' if result else 'false'))

            return result
        except Exception as e:
            self._phone._log.error(error = e)
            raise e

    def shoot(self, path, left = 0, top = 0, right = 0, bottom = 0):
##        time.sleep(self._delay)
        self._phone._log.ignite(ignite = 'Element.shoot()')
        try:
            if not ((type(path) is str) and (len(re.findall(pattern = '^\s*(.+[/\\\])(.*[.]png)\s*$', string = path, flags = re.IGNORECASE)) == 1) and (len(re.findall(pattern = '^\s*(.+[/\\\])(.*[.]png)\s*$', string = path, flags = re.IGNORECASE)[0]) == 2) and (type(left) is int) and (type(top) is int) and (type(right) is int) and (type(bottom) is int)):
                raise Exception('pass path/left/top/right/bottom as str(png_path)/int!')

            if not os.path.exists(path = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'utf_8', errors = 'strict')):
                os.makedirs(name = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'utf_8', errors = 'strict'), mode = 0777)

            self._phone._log.clause(clause = 'path = ' + (re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*[.]png)\s*$', string = path, flags = re.IGNORECASE)[0][1]).replace('/', '\\'))

            memory = StringIO.StringIO(buf = '')
            for i in range(0, 7, 1):
                try:
##                    memory.write(s = self._element._parent.get_screenshot_as_png())
                    memory.write(s = self._element._parent.get_screenshot_as_base64().decode(encoding = 'base64_codec', errors = 'strict'))
                    break
                except Exception as e:
                    time.sleep(0.07)
                    if i == 6:
                        raise e

            memory.seek(pos = 0, mode = 0)
            full_image = PIL.Image.open(fp = memory, mode = 'r')

            left = self._element.location_in_view[u'x'] + left
            top = self._element.location_in_view[u'y'] - top
            right = self._element.location_in_view[u'x'] + self._element.size['width'] + right
            bottom = self._element.location_in_view[u'y'] + self._element.size['height'] - bottom

            element_image = full_image.crop(box = (left, top, right, bottom))
            element_image.save(fp = (re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*[.]png)\s*$', string = path, flags = re.IGNORECASE)[0][1]).decode(encoding = 'utf_8', errors = 'strict'), format = 'PNG')
            memory.close()

            self._phone._log.effect(effect = 'element shoot')
        except Exception as e:
            self._phone._log.error(error = e)
            raise e







class Android(object):
    def __init__(self):
        self._key = None
        self._value = None
        self._strict = True

    #because 'class' is a python key word and could not be overridden, it leaves me no choise but to use such strang-looking naming rule on class and variable name
    @staticmethod
    def class_(class_):
        if not ((type(class_) is str) and (len(class_) > 0)):
            raise Exception('pass class_ as str(len>0)!')
        instance = Android()
        instance._key = 'class'
        instance._value = class_
        return instance

    @staticmethod
    def text_(text_, strict = True):
        if not ((type(text_) is str) and (len(text_) > 0)):
            raise Exception('pass text_ as str(len>0)!')
        instance = Android()
        instance._key = 'text'
        instance._value = "'" + text_ + "'"
        instance._strict = strict
        return instance

    @staticmethod
    def contentdesc_(contentdesc_, strict = True):
        if not ((type(contentdesc_) is str) and (len(contentdesc_) > 0)):
            raise Exception('pass contentdesc_ as str(len>0)!')
        instance = Android()
        instance._key = 'content-desc'
        instance._value = "'" + contentdesc_ + "'"
        instance._strict = strict
        return instance

    @staticmethod
##    def index_(index_, strict = True):
    def index_(index_):
##        if not (((type(index_) is int) and (index_ >= 0)) or ((type(index_) is str) and (len(re.findall(pattern = '^\s*\d+\s*$', string = index_, flags = 0)) == 1) and (int(index_) >= 0))):
        if not ((type(index_) is int) and (index_ >= 0)):
            raise Exception('pass index_ as int(>=0)!')
        instance = Android()
        instance._key = 'index'
##        instance._value = "'" + str(index_) + "'" if type(index_) is int else index_
        instance._value = "'" + str(index_) + "'"
##        instance._strict = strict
        return instance







class Ios(object):
    def __init__(self):
        self._key = None
        self._value = None
        self._strict = True

    @staticmethod
    def type_(type_):
        if not ((type(type_) is str) and (len(type_) > 0)):
            raise Exception('pass type_ as str(len>0)!')
        instance = Ios()
        instance._key = 'type'
        instance._value = type_
        return instance

    @staticmethod
    def name_(name_, strict = True):
        if not ((type(name_) is str) and (len(name_) > 0)):
            raise Exception('pass name_ as str(len>0)!')
        instance = Ios()
        instance._key = 'name'
        instance._value = "'" + name_ + "'"
        return instance

    @staticmethod
    def label_(label_, strict = True):
        if not ((type(label_) is str) and (len(label_) > 0)):
            raise Exception('pass label_ as str(len>0)!')
        instance = Ios()
        instance._key = 'label'
        instance._value = "'" + label_ + "'"
        return instance

    @staticmethod
    def value_(value_, strict = True):
        if not ((type(value_) is str) and (len(value_) > 0)):
            raise Exception('pass value_ as str(len>0)!')
        instance = Ios()
        instance._key = 'value'
        instance._value = "'" + value_ + "'"
        return instance







class Log(object):
    def __init__(self, path, phone):
        if not ((type(path) is str) and (len(re.findall(pattern = '^\s*(.+[/\\\])(.*)\s*$', string = path, flags = 0)) == 1) and (len(re.findall(pattern = '^\s*(.+[/\\\])\s*(.*)\s*$', string = path, flags = 0)[0][1]) > 0) and (isinstance(phone, Phone))):
            raise Exception('pass path/phone as str(log_path)/Phone()!')

        if not os.path.exists(path = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'utf_8', errors = 'strict')):
            os.makedirs(name = re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0].decode(encoding = 'utf_8', errors = 'strict'), mode = 0777)

        self._log = open(name = (re.findall(pattern = '^\s*(.+[/\\\]).*$', string = path, flags = 0)[0] + re.findall(pattern = '^\s*(.+[/\\\])\s*(.*)\s*$', string = path, flags = 0)[0][1]).decode(encoding = 'utf_8', errors = 'strict'), mode = 'w+', buffering = 0)
        self._phone = phone
        self._count = 1

    def ignite(self, ignite):
        self._log.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') + '\tDEF IGNITE:\t' + ignite)
        self._log.write('\n')

    def clause(self, clause):
        self._log.write('\t' * 4 + 'DEF CLAUSE:\t' + clause)
        self._log.write('\n')

    def effect(self, effect):
        self._log.write('\t' * 4 + 'DEF EFFECT:\t' + effect)
        self._log.write('\n' * 2)

    def error(self, error):
##        try:
##            self._phone._phone.quit()
##        except:
##            pass

        if isinstance(error, selenium.common.exceptions.WebDriverException):
            message = error.msg
        else:
            message = error.message

        self._log.write('DEF EXCEPTION:\t' + message)
        self._log.write('\n')
        self._log.write('DEF TRACEBACK:')
        self._log.write('\n')
        self._log.writelines(traceback.format_stack(f = None, limit = None))
        for i in range(0, 7, 1):
            try:
##                self._phone._phone.get_screenshot_as_file(filename = self._log.name + '.' + str(self._count).zfill(7) + '.png')
                with open(name = self._log.name + '.' + str(self._count).zfill(7) + '.png', mode = 'wb+', buffering = 0) as f:
                    f.write(self._phone._phone.get_screenshot_as_base64().decode(encoding = 'base64_codec', errors = 'strict'))
                self._log.write('DEF SCREENSHOT:\t' + self._log.name + '.' + str(self._count).zfill(7) + '.png')
                self._count += 1
                break
            except:
                time.sleep(0.07)
                if i == 6:
                    self._log.write('DEF SCREENSHOT:\tnone')
        self._log.write('\n' * 2)

##        self._log.close()