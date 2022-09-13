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
    """ This is the generalized WSGI middleware for any style request logging. """

    def __init__(self, application, handlers, formatter=None, propagate=True, ip_header=None, **kwargs):
        self.formatter = formatter or WSGILogger.standard_formatter
        self.logger = logging.getLogger('requestlogger')
        self.logger.propagate = propagate
        self.logger.setLevel(logging.DEBUG)
        for handler in handlers:
            self.logger.addHandler(handler)
        self.ip_header = ip_header
        self.application = application
        self._status_code = ''
        self._content_length = 0

    def __call__(self, environ, start_response):
        start = clock()

        def _start_response(status, response_headers, exc_info=None):
            self._status_code = status.split()[0]
            self._content_length = 0
            for name, value in response_headers:
                    if name.lower() == 'content-length':
                        self._content_length += int(value)
                        break
            return start_response(status, response_headers, exc_info) 

        retval = self.application(environ, _start_response)
        runtime = int((clock() - start) * 10**6)
        msg = self.formatter(self._status_code, environ, self._content_length, ip_header=self.ip_header, rt_us=runtime)
        self.logger.info(msg)
        return retval



    @staticmethod
    def standard_formatter(status_code, environ, content_length, **kwargs):
        _host = environ.get('REMOTE_ADDR', '')
        _timestamp = dt.now(Local).strftime("%d/%b/%Y:%H:%M:%S %z")
        _request = "{0} {1}{2}{3} {4}".format(
              environ.get('REQUEST_METHOD', ''),
              environ.get('PATH_INFO', ''),
              '?' if environ.get('QUERY_STRING', '') else '',
              environ.get('QUERY_STRING', ''),
              environ.get('SERVER_PROTOCOL', '')
            )
        _status = status_code
        _size = content_length
        
        return f'{_host} - - [{_timestamp}] "{_request}" {_status} {_size}' 


def ApacheFormatter(with_response_time=True):
    """ A factory that returns the wanted formatter """
    if with_response_time:
        return ApacheFormatters.format_with_response_time
    else:
        return ApacheFormatters.format_NCSA_log


class ApacheFormatters(object):
    @staticmethod
    def format_NCSA_log(status_code, environ, content_length, **kwargs):
        """
          Apache log format 'NCSA extended/combined log':
          "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\""
          see http://httpd.apache.org/docs/current/mod/mod_log_config.html#formats
        """
        
        # Let's collect log values
        val = dict()
        ip_header = kwargs.get('ip_header', None)
        if ip_header:
            try:
                val['host'] = environ.get(ip_header, '')
            except:
                val['host'] = environ.get('REMOTE_ADDR', '')
        else:
            val['host'] = environ.get('REMOTE_ADDR', '')
        val['logname'] = '-'
        val['user'] = '-'
        date = dt.now(tz=Local)
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][date.month - 1]
        val['time'] = date.strftime("%d/{0}/%Y:%H:%M:%S %z".format(month))
        val['request'] = "{0} {1}{2}{3} {4}".format(
              environ.get('REQUEST_METHOD', ''),
              environ.get('PATH_INFO', ''),
              '?' if environ.get('QUERY_STRING', '') else '',
              environ.get('QUERY_STRING', ''),
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
    def format_with_response_time(*args, **kwargs):
        """
          The dict kwargs should contain 'rt_us', the response time in milliseconds.
          This is the format for TinyLogAnalyzer:
          https://pypi.python.org/pypi/TinyLogAnalyzer
        """
        rt_us = kwargs.get('rt_us')
        return ApacheFormatters.format_NCSA_log(*args, **kwargs) + " {0}/{1}".format(int(rt_us/1000000), rt_us)


def log(handlers, formatter=ApacheFormatter(), **kwargs):
    """Decorator for logging middleware."""
    def decorator(application):
        return WSGILogger(application, handlers, **kwargs)
    return decorator

