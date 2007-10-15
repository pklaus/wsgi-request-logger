from wsgilog import log

@log(tohtml=True, tofile='wsgi.log', htmlfile='test.html', tostream=True, toprint=True)
def app(environ, start_response):
    print 'STDOUT is logged.'
    environ['wsgilog.logger'].info('This information is logged.')
    # Exception will be logged and sent to the browser HTML formatted
    raise ImportError() 

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    http = make_server('', 8080, app)
    http.serve_forever()