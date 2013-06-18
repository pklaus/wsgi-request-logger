## Request Logging for WSGI Web Applications

This is a middleware which you can use to log requests to your WSGI based site.
It's even imitating Apache's combined log format to allow you to use any of the
many tools for Apache log file analysis.

By making use of Python's Logger Facilities, you can easily log to STDOUT, time rotated log files, email, syslog, etc.

#### Installation

Simply install this Python module via

    pip install wsgi-request-logger

#### Usage

To add this plugin to your WSGI `application` and log to the file *access.log*, do:

    from requestlogger import ApacheLogger
    from logging.handlers import TimedRotatingFileHandler
    
    def application(environ, start_response):
        response_body = 'The request method was %s' % environ['REQUEST_METHOD']
        response_body = response_body.encode('utf-8')
        response_headers = [('Content-Type', 'text/plain'),
                            ('Content-Length', str(len(response_body)))]
        start_response('200 OK', response_headers)
        return [response_body]
    
    handlers = [ TimedRotatingFileHandler('access.log', 'd', 7) , ]
    loggingapp = ApacheLogger(application, handlers)
    
    if __name__ == '__main__':
        from wsgiref.simple_server import make_server
        http = make_server('', 8080, loggingapp)
        http.serve_forever()


#### The Authors

This WSGI middlewre was originally developed under the name [wsgilog](https://pypi.python.org/pypi/wsgilog/) by  **L. C. Rees**.
It was forked by **Philipp Klaus** in 2013 to build a WSGI middleware for request logging rather than exception handling and logging.  


#### License

This software, *wsgi-request-logger*, is published under a *3-clause BSD license*.

#### Developers' Resources

* To read about your options for the logging handler, you may want to read [Python's Logging Cookbook](http://docs.python.org/3/howto/logging-cookbook.html).
* Documentation on Apache's log format can be found [here](http://httpd.apache.org/docs/current/mod/mod_log_config.html#logformat).
* The [WSGI](http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) - Web Server Gateway Interface - is defined in [PEP 333](http://www.python.org/dev/peps/pep-0333/) with an update for Python 3 in [PEP 3333](http://www.python.org/dev/peps/pep-3333/).

#### General References

* PyPI's [listing of wsgi-request-logger](https://pypi.python.org/pypi/wsgi-request-logger)
* The source code for this Python module is [hosted on Github](https://github.com/pklaus/wsgi-request-logger).



