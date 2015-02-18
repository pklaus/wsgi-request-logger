# -*- coding: utf-8 -*-

"""
Apache-like combined logging for WSGI Web Applications.

Homepage: https://github.com/pklaus/wsgi-request-logger

Copyright (c) 2013, Philipp Klaus. All rights reserved.
Copyright (c) 2007-2011 L. C. Rees. All rights reserved.

License: BSD (see LICENSE for details)
"""

import time
from datetime import datetime as dt
import logging

from .timehacks import Local

__all__ = ['WSGILogger', 'ApacheFormatter', 'log']

try:
    clock = time.perf_counter
except AttributeError:
    clock = time.time

class WSGILogger(object):
    ''' This is the generalized WSGI middleware for any style request logging. '''

    def __init__(self, application, handlers, formatter=None, **kw):
        self.formatter = formatter or WSGILogger.standard_formatter
        self.logger = logging.getLogger('requestlogger')
        self.logger.setLevel(logging.DEBUG)
        for handler in handlers:
            self.logger.addHandler(handler)
        self.application = application

    def __call__(self, environ, start_response):
        start = clock()
        status_codes = []
        content_lengths = []
        def custom_start_response(status, response_headers, exc_info=None):
            status_codes.append(int(status.partition(' ')[0]))
            for name, value in response_headers:
                if name.lower() == 'content-length':
                    content_lengths.append(int(value))
                    break
            return start_response(status, response_headers, exc_info)
        retval = self.application(environ, custom_start_response)
        runtime = int((clock() - start) * 10**6)
        content_length = content_lengths[0] if content_lengths else len(b''.join(retval))
        msg = self.formatter(status_codes[0], environ, content_length, rt_ms=runtime)
        self.logger.info(msg)
        return retval

    @staticmethod
    def standard_formatter(status_code, environ, content_length):
        return "{} {}".format(dt.now().isoformat(), status_code)

def ApacheFormatter(with_response_time=True):
    ''' A factory that returns the wanted formatter '''
    if with_response_time:
        return ApacheFormatters.format_with_response_time
    else:
        return ApacheFormatters.format_NCSA_log

class ApacheFormatters(object):

    @staticmethod
    def format_NCSA_log(status_code, environ, content_length):
        """
          Apache log format 'NCSA extended/combined log':
          "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\""
          see http://httpd.apache.org/docs/current/mod/mod_log_config.html#formats
        """
        
        # Let's collect log values
        val = dict()
        val['host'] = environ.get('REMOTE_ADDR', '')
        val['logname'] = '-'
        val['user'] = '-'
        date = dt.now(tz=Local)
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][date.month - 1]
        val['time'] = date.strftime("%d/{0}/%Y:%H:%M:%S %z".format(month))
        val['request'] = "{} {} {}".format(
              environ.get('REQUEST_METHOD', ''),
              environ.get('PATH_INFO', ''),
              environ.get('SERVER_PROTOCOL', '')
            )
        val['status'] = status_code
        val['size'] = content_length
        val['referer'] = environ.get('HTTP_REFERER', '')
        val['agent'] = environ.get('HTTP_USER_AGENT', '')
        
        # see http://docs.python.org/3/library/string.html#format-string-syntax
        FORMAT = '{host} {logname} {user} [{time}] "{request}" '
        FORMAT += '{status} {size} "{referer}" "{agent}"'
        return FORMAT.format(**val)

    @staticmethod
    def format_with_response_time(*args, **kw):
        """
          The dict kw should contain 'rt_ms', the response time in milliseconds.
          This is the format for TinyLogAnalyzer:
          https://pypi.python.org/pypi/TinyLogAnalyzer
        """
        rt_ms = kw.get('rt_ms')
        return ApacheFormatters.format_NCSA_log(*args) + " {}/{}".format(int(rt_ms/1000000), rt_ms)

def log(handlers, formatter=ApacheFormatter(), **kw):
    '''Decorator for logging middleware.'''
    def decorator(application):
        return WSGILogger(application, handlers, **kw)
    return decorator

