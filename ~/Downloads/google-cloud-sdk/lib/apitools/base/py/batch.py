"""HTTP batch requests for apitools.

This library is copied heavily from apiclient's BatchHttpRequest.
Some unneeded parts are removed, and apitools' BatchHttpRequest is
modified to work with the classes in http_wrapper instead of httplib2.
"""

import collections
import email.generator as generator
import email.mime.multipart as mime_multipart
import email.mime.nonmultipart as mime_nonmultipart
import email.parser as email_parser
import itertools
import StringIO
import time
import urllib
import urlparse
import uuid

from apitools.base.py import exceptions
from apitools.base.py import http_wrapper

__all__ = [
    'BatchApiRequest',
    ]


RequestResponseHandler = collections.namedtuple(
    'RequestResponseHandler', ['request', 'response', 'handler'])


class BatchApiRequest(object):
  """Friendly interface for batching API requests."""

  class ApiRequestResponse(object):
    """Each individual request is stored in its own object."""

    def __init__(self, request, retryable_codes, service, method_config):
      """Initialize an individual API request.

      Args:
        request: An http_wrapper.Request object.
        retryable_codes: A list of HTTP codes that can be retried.
        service: A service inheriting from base_api.BaseApiService.
        method_config: Method config for the desired API request.
      """
      self.__retryable_codes = retryable_codes
      self.__http_response = None
      self.__service = service
      self.__method_config = method_config

      self.http_request = request
      # TODO(user): Add some validation to these fields.
      self.__response = None
      self.__exception = None

    @property
    def is_error(self):
      return self.exception is not None

    @property
    def response(self):
      return self.__response

    @property
    def exception(self):
      return self.__exception

    @property
    def terminal_state(self):
      return (self.__http_response and (
          self.__http_response.status_code not in self.__retryable_codes))

    def HandleResponse(self, http_response, exception):
      """Callback used with BatchApiRequest.

      Args:
        http_response: Deserialized http_wrapper.Response object.
        exception: apiclient.errors.HttpError object if an error occurred.
      """
      self.__http_response = http_response
      self.__exception = exception
      if self.terminal_state:
        self.__response = self.__service.ProcessHttpResponse(
            self.__method_config, self.__http_response)

  def __init__(self, batch_url=None, retryable_codes=None):
    """Initialize a batch API request object.

    Args:
      batch_url: Base URL for batch API calls.
      retryable_codes: A list of HTTP codes that can be retried.
    """
    self.api_requests = []
    self.retryable_codes = retryable_codes or []
    self.batch_url = batch_url or 'https://www.googleapis.com/batch'

  def Add(self, service, method, request, global_params=None):
    """Add a request to the batch.

    Args:
      service: A class inheriting base_api.BaseApiService.
      method: The desired method from the service.
      request: An input message appropriate for the specified service.method.
      global_params: Optional additional parameters to pass into
                     method.PrepareHttpRequest.

    Returns:
      None
    """
    # Retrieve the configs for the desired method and service.
    method_config = service.GetMethodConfig(method)
    upload_config = service.GetMethodUploadConfig(method)

    # Prepare the HTTP Request.
    http_request = service.PrepareHttpRequest(
        method_config, request, global_params=global_params,
        upload_config=upload_config)

    # Create the request and add it to our master list.
    api_request = self.ApiRequestResponse(
        http_request, self.retryable_codes, service, method_config)
    self.api_requests.append(api_request)

  def Execute(self, http, sleep_between_polls=5, max_retries=5):
    """Execute all of the requests in the batch.

    Args:
      http: httplib2.Http object for use in the request.
      sleep_between_polls: How long to sleep between polls, in seconds.
      max_retries: Max retries. Any requests that have not succeeded by
                   this number of retries simply report the last response or
                   exception, whatever it happened to be.

    Returns:
      List of ApiRequestResponses.
    """
    requests = [request for request in self.api_requests if not
                request.terminal_state]

    for attempt in xrange(max_retries):
      if attempt:
        time.sleep(sleep_between_polls)

      # Create a batch_http_request object and populate it with incomplete
      # requests.
      batch_http_request = BatchHttpRequest(batch_url=self.batch_url)
      for request in requests:
        batch_http_request.Add(request.http_request, request.HandleResponse)
      batch_http_request.Execute(http)

      # Collect retryable requests.
      requests = [request for request in self.api_requests if not
                  request.terminal_state]

      if not requests:
        break

    return self.api_requests


class BatchHttpRequest(object):
  """Batches multiple http_wrapper.Request objects into a single request."""

  def __init__(self, batch_url, callback=None):
    """Constructor for a BatchHttpRequest.

    Args:
      batch_url: string, URL to send batch requests to.
      callback: callable, A callback to be called for each response, of the
        form callback(response, exception). The first parameter is
        the deserialized Response object. The second is an
        apiclient.errors.HttpError exception object if an HTTP error
        occurred while processing the request, or None if no error occurred.
    """
    # Endpoint to which these requests are sent.
    self.__batch_url = batch_url

    # Global callback to be called for each individual response in the batch.
    self.__callback = callback

    # List of requests, responses and handlers.
    self.__request_response_handlers = {}

    # The last auto generated id.
    self.__last_auto_id = itertools.count()

    # Unique ID on which to base the Content-ID headers.
    self.__base_id = uuid.uuid4()

  def _IdToHeader(self, request_id):
    """Convert an id to a Content-ID header value.

    Args:
      request_id: string, identifier of individual request.

    Returns:
      A Content-ID header with the id_ encoded into it. A UUID is prepended to
      the value because Content-ID headers are supposed to be universally
      unique.
    """
    return '<%s+%s>' % (self.__base_id, urllib.quote(request_id))

  def _HeaderToId(self, header):
    """Convert a Content-ID header value to an id.

    Presumes the Content-ID header conforms to the format that _IdToHeader()
    returns.

    Args:
      header: string, Content-ID header value.

    Returns:
      The extracted id value.

    Raises:
      BatchError if the header is not in the expected format.
    """
    if not (header.startswith('<') or header.endswith('>')):
      raise exceptions.BatchError('Invalid value for Content-ID: %s' % header)
    if '+' not in header:
      raise exceptions.BatchError('Invalid value for Content-ID: %s' % header)
    _, request_id = header[1:-1].rsplit('+', 1)

    return urllib.unquote(request_id)

  def _SerializeRequest(self, request):
    """Convert a http_wrapper.Request object into a string.

    Args:
      request: http_wrapper.Request, the request to serialize.

    Returns:
      The request as a string in application/http format.
    """
    # Construct status line
    parsed = urlparse.urlsplit(request.url)
    request_line = urlparse.urlunsplit(
        (None, None, parsed.path, parsed.query, None))
    status_line = request.http_method + ' ' + request_line + ' HTTP/1.1\n'
    major, minor = request.headers.get(
        'content-type', 'application/json').split('/')
    msg = mime_nonmultipart.MIMENonMultipart(major, minor)
    headers = request.headers.copy()

    # MIMENonMultipart adds its own Content-Type header.
    # Keep all of the other headers in headers.
    for key, value in headers.iteritems():
      if key == 'content-type':
        continue
      msg[key] = value

    msg['Host'] = parsed.netloc
    msg.set_unixfrom(None)

    if request.body is not None:
      msg.set_payload(request.body)

    # Serialize the mime message.
    fp = StringIO.StringIO()
    # maxheaderlen=0 means don't line wrap headers.
    g = generator.Generator(fp, maxheaderlen=0)
    g.flatten(msg, unixfrom=False)
    body = fp.getvalue()

    # Strip off the \n\n that the MIME lib tacks onto the end of the payload.
    if request.body is None:
      body = body[:-2]

    return status_line.encode('utf-8') + body

  def _DeserializeResponse(self, payload):
    """Convert string into Response and content.

    Args:
      payload: string, headers and body as a string.

    Returns:
      A Response object
    """
    # Strip off the status line.
    status_line, payload = payload.split('\n', 1)
    _, status, _ = status_line.split(' ', 2)

    # Parse the rest of the response.
    parser = email_parser.Parser()
    msg = parser.parsestr(payload)

    # Get the headers.
    info = dict(msg)
    info['status'] = status

    # Create Response from the parsed headers.
    content = msg.get_payload()

    return http_wrapper.Response(info, content, self.__batch_url)

  def _NewId(self):
    """Create a new id.

    Auto incrementing number that avoids conflicts with ids already used.

    Returns:
       string, a new unique id.
    """
    return str(self.__last_auto_id.next())

  def Add(self, request, callback=None):
    """Add a new request.

    Args:
      request: http_wrapper.Request, http_wrapper.Request to add to the batch.
      callback: callable, A callback to be called for this response, of the
        form callback(response, exception). The first parameter is the
        deserialized response object. The second is an
        apiclient.errors.HttpError exception object if an HTTP error
        occurred while processing the request, or None if no errors occurred.

    Returns:
      None
    """
    self.__request_response_handlers[self._NewId()] = RequestResponseHandler(
        request, None, callback)

  def _Execute(self, http):
    """Serialize batch request, send to server, process response.

    Args:
      http: httplib2.Http, an http object to be used to make the request with.

    Raises:
      httplib2.HttpLib2Error if a transport error has occured.
      apiclient.errors.BatchError if the response is the wrong format.
    """
    message = mime_multipart.MIMEMultipart('mixed')
    # Message should not write out its own headers.
    setattr(message, '_write_headers', lambda self: None)

    # Add all the individual requests.
    for key in self.__request_response_handlers:
      msg = mime_nonmultipart.MIMENonMultipart('application', 'http')
      msg['Content-Transfer-Encoding'] = 'binary'
      msg['Content-ID'] = self._IdToHeader(key)

      body = self._SerializeRequest(
          self.__request_response_handlers[key].request)
      msg.set_payload(body)
      message.attach(msg)

    request = http_wrapper.Request(self.__batch_url, 'POST')
    request.body = message.as_string()
    request.headers['content-type'] = (
        'multipart/mixed; boundary="%s"') % message.get_boundary()

    response = http_wrapper.MakeRequest(http, request)

    if response.status_code >= 300:
      raise exceptions.HttpError.FromResponse(response)

    # Prepend with a content-type header so Parser can handle it.
    header = 'content-type: %s\r\n\r\n' % response.info['content-type']

    parser = email_parser.Parser()
    mime_response = parser.parsestr(header + response.content)

    if not mime_response.is_multipart():
      raise exceptions.BatchError('Response not in multipart/mixed format.')

    for part in mime_response.get_payload():
      request_id = self._HeaderToId(part['Content-ID'])
      response = self._DeserializeResponse(part.get_payload())

      self.__request_response_handlers[request_id] = (
          self.__request_response_handlers[request_id]._replace(  # pylint: disable=protected-access
              response=response))

  def Execute(self, http):
    """Execute all the requests as a single batched HTTP request.

    Args:
      http: httplib2.Http object to be used with the request.

    Returns:
      None

    Raises:
      BatchError if the response is the wrong format.
    """

    self._Execute(http)

    for key in self.__request_response_handlers:
      response = self.__request_response_handlers[key].response
      callback = self.__request_response_handlers[key].handler

      exception = None

      if response.status_code >= 300:
        exception = exceptions.HttpError.FromResponse(response)
        response = None

      if callback is not None:
        callback(response, exception)
      if self.__callback is not None:
        self.__callback(response, exception)
