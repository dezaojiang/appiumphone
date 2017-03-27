#-*- coding: utf-8 -*-
#!/usr/bin/env python

import distutils.core

distutils.core.setup(
    name = 'appiumphone',
    version = '0.0.1',
    packages = ['appiumphone'],
    requires = ['appium'],
    author = 'dezaojiang',
    url = 'https://github.com/dezaojiang/appiumphone'
    )