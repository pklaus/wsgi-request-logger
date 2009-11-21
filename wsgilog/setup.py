# Copyright (c) 2007 L. C. Rees.  All rights reserved.
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

'''setup - setuptools based setup for wsgilog.'''

import ez_setup
ez_setup.use_setuptools()

try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(name='wsgilog',
      version='0.2',
      description='''WSGI logging and event reporting middleware.''',
      long_description='''Supports logging events in WSGI applications to
STDOUT, time rotated log files, email, syslog, and web servers. Also
supports catching and sending HTML-formatted exception tracebacks to a
web browser for debugging.

# Simple usage example:

from wsgilog import log

@log(tohtml=True, tofile='wsgi.log', tostream=True, toprint=True)
def app(environ, start_response):
    print 'STDOUT is logged.'
    environ['wsgilog.logger'].info('This information is logged.')
    # Exception will be logged and sent to the browser formatted as HTML.
    raise Exception()

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    http = make_server('', 8080, app)
    http.serve_forever()
''',
      author='L. C. Rees',
      author_email='lcrees@gmail.com',
      license='BSD',
      packages = ['wsgilog'],
      zip_safe = True,
      keywords='WSGI logging middleware',
      classifiers=['Development Status :: 3 - Alpha',
                    'Environment :: Web Environment',
                    'License :: OSI Approved :: BSD License',
                    'Natural Language :: English',
                    'Operating System :: OS Independent',
                    'Programming Language :: Python',
                    'Topic :: System :: Monitoring',
                    'Topic :: System :: Logging',
                    'Topic :: Internet :: WWW/HTTP :: Site Management',
                    'Topic :: Internet :: WWW/HTTP :: WSGI',
                    'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware'])