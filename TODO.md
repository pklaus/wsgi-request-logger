### ToDo

* The [extraction of the request and response meta data (done manually using the environ variable right now) could also be done](http://docs.webob.org/en/latest/comment-example.html#the-middleware) using webob's [Request](http://docs.webob.org/en/latest/modules/webob.html#request) and [Response](http://docs.webob.org/en/latest/modules/webob.html#response) classes.  
  Or using [pylons.util](http://stackoverflow.com/a/2655396/183995).
* Add the capability to log the requested site via the `Host: ` HTTP header as well.
* Add the capability to use the `X-Forwarded-For: ` HTTP header to log the IP address (needed when running you web app behind a reverse proxy).
