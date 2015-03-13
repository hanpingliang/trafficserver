# HTTP

## 1. Keep-alive

1. Keep-alive incoming connections.
  
		proxy.config.http.keep_alive_enabled_in

	Set to `1`: Test if client re-uses the TCP connection to ATS for new HTTP transactions.
	
	Set to `0`: Test if client opens new TCP connections to ATS for new HTTP transactions.

1. Keep-alive outgoing connections.

		proxy.config.http.keep_alive_enabled_out

	Set to `1`: Test if ATS re-uses the TCP connection to origin server for new HTTP transactions.
	
	Set to `0`: Test if ATS opens new TCP connections to origin server for new HTTP transactions.

1. Keep-alive connections for POST requests.

		proxy.config.http.keep_alive_post_out

	Set to `1`: Test if ATS re-uses the TCP connection for new POST requests.
	
	Set to `0`: Test if ATS opens new TCP connections for new POST requests.

**Done**: [test_keepalive](https://github.com/apache/trafficserver/blob/master/ci/new_tsqa/tests/test_keepalive.py), [test_keepalive2](https://git.corp.yahoo.com/ffcai/ATSTestScenarios/blob/master/HTTP/test_keepalive2.py)

## 2. Connection Timeouts

1. Keep-alive connection timeout

		proxy.config.http.keep_alive_no_activity_timeout_in
		proxy.config.http.keep_alive_no_activity_timeout_out

	Test if ATS closes TCP connection to client after `N` seconds since completing last HTTP transaction.

	Test if ATS closes TCP connection to origin server after `N` seconds since completing last HTTP transaction.

1. No activity transacion timeout

		proxy.config.http.transaction_no_activity_timeout_in
		proxy.config.http.transaction_no_activity_timeout_out
		

	Test if ATS keeps connection to client for `N` seconds when a transaction stalls.

	Test if ATS keeps connection to origin server for `N` seconds when a transaction stalls.

1. Active transaction timeout

		proxy.config.http.transaction_active_timeout_in
		proxy.config.http.transaction_active_timeout_out

	Test if ATS keeps connection to client for `N` seconds, then close the connection even if the transfer to client is not complete.

	Test if ATS keeps connection to origin server for `N` seconds, then close the connection even if the transfer to origin server is not complete.

1. No activity connection timeout

		proxy.config.http.accept_no_activity_timeout

	Set to `N`: Test if ATS closes a connection that has no activity after `N` seconds.

1. Active background fill timeout

		proxy.config.http.background_fill_active_timeout

	Set to `N`: Test if ATS keeps a background fill for `N` seconds before giving up and dropping the origin server connection.

1. Background fill completed threshold

		proxy.config.http.background_fill_completed_threshold

	Set to `0.x`: Test the proportion of total document size already transferred when a client aborts at which the proxy continues fetching the document from the origin server to get it into the cache (a background fill).

**Done**: [test_timeouts](https://git.corp.yahoo.com/ffcai/ATSTestScenarios/blob/master/HTTP/test_timeouts.py)

## 3. Origin Server Connect Attempts

1. Connect attempts timeout

		proxy.config.http.connect_attempts_timeout

	Set to `N`: Test if ATS attemps to connect to origin server for `N` seconds before receive the first byte.

1. Connect attempts timeout for POST/PUT requests

		proxy.config.http.post_connect_attempts_timeout

	Set to `N`: Test if ATS attemps to connect to origin server for `N` seconds before receive the first byte, when the client requests is a `POST` or `PUT` request.

1. Maximum number of connection retries

		proxy.config.http.connect_attempts_max_retries

	Set to `N`: Test if ATS retries `N` times, before the origin is marked dead.

1. Maximum number of connection retries to dead server

		proxy.config.http.connect_attempts_max_retries_dead_server

	Set to `N`: Test if ATS retries `N` times, after the origin is marked dead.

1. Maximum number of origin server connections

		proxy.config.http.server_max_connections

	Set to `N`: Test if ATS limits the number of socket connections across all origin servers to `N`.

1. Minimum number of origin server keep-alive connections

		proxy.config.http.origin_min_keep_alive_connections

	Set to `N`: Test if ATS keeps at least `N` connections open to origin server when connection is opened.

1. Maximum number of connection attempts with round-robin

		proxy.config.http.connect_attempts_rr_retries

	Set to `N`: Test if ATS retries `N` times before a round-robin entry is marked as ‘down’, if a server has round-robin DNS entries.

1. Server down cache time

		proxy.config.http.down_server.cache_time

	Set to `N`: Test if ATS remembers an origin server as unreachable for `N` seconds.

1. Server down abort threshold

		proxy.config.http.down_server.abort_threshold

	Set to `N`: Test that, after a client abandons a request because an origin server was too slow in sending the response header, if ATS marks that origin server as unavailable after `N` seconds.

## 4. 100 Continue Response

	proxy.config.http.send_100_continue_response

Set to `0`: Test if ATS buffers the request until the post body has been recieved and then send the request to origin.

Set to `1`: Test if ATS immediately returns a `100 Continue` response when receiving a `POST` request with `Expect: 100-continue` header, without waiting for the post body.

## 5. 408 Post Timeout Response

	proxy.config.http.send_408_post_timeout_response

Set to `1`: Test if ATS sends a `408 Request Timeout` response when a `POST` request timeout happends.

## 6. Redirection

	proxy.config.http.redirection_enabled
	proxy.config.http.number_of_redirections

Set `proxy.config.http.redirection_enabled` to 1, `proxy.config.http.number_of_redirections` to `N`: Test if ATS do the redirecion for client, with a limit number of `N-1`.

## 7. Server Session

	proxy.config.http.share_server_sessions
	proxy.config.http.server_session_sharing.match
	proxy.config.http.server_session_sharing.pool
	proxy.config.http.attach_server_session_to_client

...

## 8. Headers

1. Via

		proxy.config.http.insert_request_via_str
		proxy.config.http.insert_response_via_str

	Set to `0` - `4`: Test if `via` header shows up with configurated verbosity in request or response.

1. Server

		proxy.config.http.response_server_enabled
		proxy.config.http.response_server_str
	
	Set to `0`: Test if ATS sends response without a `Server` header.
	
	Set to `1` - `2`: Test if ATS adds a `Server` header in response.

1. Age

		proxy.config.http.insert_age_in_response

	Set to `0`: Test if ATS sends response without an `Age` header.
	
	Set to `1`: Test if ATS sends response with an `Age` header.

1. From

		proxy.config.http.anonymize_remove_from
	
	Set to `1`: Test if ATS removes the `from` header.

1. Referrer

		proxy.config.http.anonymize_remove_referer

	Set to `1`: Test if ATS removes the `referrer` header.

1. User-agent

		proxy.config.http.anonymize_remove_user_agent

	Set to `1`: Test if ATS removes the `User-agent` header.

1. Cookie

		proxy.config.http.anonymize_remove_cookie

	Set to `1`: Test if ATS removes the `Cookie` header.

1. Client-IP

		proxy.config.http.anonymize_remove_client_ip

	Set to `1`: Test if ATS removes the `Client-IP` header.

1. X-Forwarded-For

		proxy.config.http.insert_squid_x_forwarded_for

	Set to `1`: Test if ATS adds the client IP address to the `X-Forwarded-For` header.

1. Accept-Encoding

		proxy.config.http.normalize_ae_gzip

	Set to `1`: Test if ATS normalizes all `Accept-Encoding` headers.

1. Others

		proxy.config.http.anonymize_other_header_list

	Set to `header1;header2;...`: Test if ATS removes these comma separated list of headers from outgoing requests.

## 9. Domain Expansion.

	proxy.config.http.enable_url_expandomatic

Set to `1`: Test if ATS does domain expansion, which resolves unqualified hostnames by prepending with `www.` and appending with `.com` before redirecting to the expanded address.

## 10. Chunked Response

	proxy.config.http.chunking_enabled

Set to `0` - `3`: Test if ATS can generate a chunked response.

## 11. HTTP 1.1 Requests

	proxy.config.http.send_http11_requests

Set to `0` - `3`: Test if ATS uses HTTP/1.1 to communicate with the origin server.

# 12. Use Client Tartget Address

	proxy.config.http.use_client_target_addr

Set to `1`: Test if ATS uses the same origin server address as the client in fully transparent ports.

