# -*- coding: utf-8 -*-

"""
Copyright (c) 2013, Philipp Klaus. All rights reserved.
Copyright (c) 2007-2011 L. C. Rees. All rights reserved.

License: BSD (see LICENSE for details)
"""

from distutils.core import setup
try:
    import pypandoc
    LDESC = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    LDESC = ''

setup(name='wsgi-request-logger',
      version = '0.4.3',
      description = 'Apache-like combined logging for WSGI Web Applications',
      long_description = LDESC,
      author = 'Philipp Klaus',
      author_email = 'philipp.l.klaus@web.de',
      url = 'https://github.com/pklaus/wsgi-request-logger',
      license = 'BSD',
      packages = ['requestlogger'],
      zip_safe = True,
      platforms = 'any',
      keywords = 'WSGI Apache-like request logging',
      classifiers = [
          'Development Status :: 4 - Beta',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Environment :: Web Environment',
          'License :: OSI Approved :: BSD License',
          'Topic :: System :: Monitoring',
          'Topic :: System :: Logging',
          'Topic :: Internet :: WWW/HTTP :: Site Management',
          'Topic :: Internet :: WWW/HTTP :: WSGI',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
      ]
)

