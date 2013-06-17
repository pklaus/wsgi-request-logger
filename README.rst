Supports logging events in WSGI applications to STDOUT, time rotated log files, email, syslog, and web servers. Also supports catching and sending HTML-formatted exception tracebacks to a web browser for debugging.

Simple usage example::

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

