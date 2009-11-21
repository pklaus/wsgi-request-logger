# Copyright (c) 2007-2009 L. C. Rees.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1.  Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 2.  Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 3.  Neither the name of the Portable Site Information Project nor the names
# of its contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

'''WSGI logging and event reporting middleware.'''

import pdb
import sys
import logging
from cgitb import html
from logging.handlers import HTTPHandler, SysLogHandler 
from logging.handlers import TimedRotatingFileHandler, SMTPHandler

__all__ = ['WsgiLog', 'log']

# File rotation constants
BACKUPS = 1
INTERVAL = 'h'
# Default logger name (should be changed)
LOGNAME = 'wsgilog.log'
# Default 'environ' entries
CATCHID = 'wsgilog.catch'
LOGGERID = 'wsgilog.logger'
# Current proposed 'environ' key signalling no middleware exception handling
THROWERR = 'x-wsgiorg.throw_errors'
# HTTP error messages
HTTPMSG = '500 Internal Error'
ERRORMSG = 'Server got itself in trouble'
# Default log formats
DATEFORMAT = '%a, %d %b %Y %H:%M:%S'
LOGFORMAT = '%(name)s: %(asctime)s %(levelname)-4s %(message)s'

def _errapp(environ, start_response):
    '''Default error handling WSGI application.'''
    start_response(HTTPMSG, [('Content-type', 'text/plain')], sys.exc_info())
    return [ERRORMSG]    

def log(**kw):
    '''Decorator for logging middleware.'''
    def decorator(application):
        return WsgiLog(application, **kw)
    return decorator


class LogStdout(object):

    '''File-like object for sending stdout output to a logger.'''    

    def __init__(self, logger, level=logging.DEBUG):
        # Set logger level
        if level == logging.DEBUG:
            self.logger = logger.debug
        elif level == logging.CRITICAL:
            self.logger = logger.critical
        elif level == logging.ERROR:
            self.logger = logger.warning
        elif level == logging.WARNING:
            self.logger = logger.warning
        elif level == logging.INFO:
            self.logger = logger.info        

    def write(self, info):
        '''Writes non-whitespace strings to logger.'''
        if info.lstrip().rstrip() != '': self.logger(info)


class WsgiLog(object):

    '''Class for WSGI logging and event recording middleware.'''    

    def __init__(self, application, **kw):
        self.application = application
        # Error handling WSGI app
        self._errapp = kw.get('errapp', _errapp)
        # Flag controlling logging
        self.log = kw.get('log', True)
        # Log if set
        if self.log:
            # Log error message 
            self.message = kw.get('logmessage', ERRORMSG)
            # Individual logger for WSGI app with custom name 'logname'
            self.logger = logging.getLogger(kw.get('logname', LOGNAME))
            # Set logger level
            self.logger.setLevel(kw.get('loglevel', logging.DEBUG))
            # Log formatter
            format = logging.Formatter(
                # Log entry format
                kw.get('logformat', LOGFORMAT),
                # Date format
                kw.get('datefmt', DATEFORMAT))
            # Coroutine for setting individual log handlers
            def setlog(logger):
                logger.setFormatter(format)
                self.logger.addHandler(logger)
            # Log to STDOUT
            if 'tostream' in kw:
                setlog(logging.StreamHandler())
            # Log to a rotating file that with periodic backup deletions
            if 'tofile' in kw:
                setlog(TimedRotatingFileHandler(
                    # Log file path
                    kw.get('file', LOGNAME),
                    # Interval to backup log file
                    kw.get('interval', INTERVAL),
                    # Number of backups to keep
                    kw.get('backups', BACKUPS)))
            # Send log entries to an email address
            if 'toemail' in kw:
                setlog(SMTPHandler(
                    # Mail server
                    kw.get('mailserver'),
                    # From email address
                    kw.get('frommail'),
                    # To email address
                    kw.get('toemail'),
                    # Email subject
                    kw.get('mailsubject')))
            # Send log entries to a web server
            if 'tohttp' in kw:
                setlog(HTTPHandler(
                    # Web server host
                    kw.get('httphost'),
                    # Web URL
                    kw.get('httpurl'),
                    # HTTP method 
                    kw.get('httpmethod', 'GET')))
            # Log to syslog
            if 'tosyslog' in kw:
                setlog(SysLogHandler(
                    # syslog host
                    kw.get('syshost', ('localhost', 514)),
                    # syslog user
                    kw.get('facility', 'LOG_USER')))
            assert self.logger.handlers, 'At least one logging handler must be configured'   
            # Redirect STDOUT to the logger
            if 'toprint' in kw:
                sys.stdout = LogStdout(self.logger,
                    # Sets log level STDOUT is displayed under
                    kw.get('prnlevel', logging.DEBUG))
        # Flag for turning on PDB in situ
        self.debug = kw.get('debug', False)
        # Flag for sending HTML-formatted exception tracebacks to the browser
        self.tohtml = kw.get('tohtml', False)
        # Write HTML-formatted exception tracebacks to a file if provided
        self.htmlfile = kw.get('htmlfile')
                
    def __call__(self, environ, start_response):
        # Make logger available to other WSGI apps/middlware
        if self.log: environ[LOGGERID] = self.logger
        # Make catch method available to other WSGI apps/middleware
        environ[CATCHID] = self.catch
        # Let exceptions "bubble up" to WSGI server/gateway
        if THROWERR in environ:
            return self.application(environ, start_response)
        # Try application
        try:
            return self.application(environ, start_response)
        # Log and/or report any errors
        except:
            return self.catch(environ, start_response)

    def catch(self, environ, start_response):
        '''Exception catcher.'''
        # Log exception
        if self.log: self.logger.exception(self.message)
        # Debug
        if self.debug: pdb.pm()
        # Write HTML-formatted exception tracebacks to a file
        if self.htmlfile is not None:
            open(self.htmlfile, 'wb').write(html(sys.exc_info()))
        # Send HTML-formatted exception tracebacks to the browser
        if self.tohtml:
            start_response(HTTPMSG, [('Content-type', 'text/html')])
            return [html(sys.exc_info())]
        # Return error handler
        return self._errapp(environ, start_response)