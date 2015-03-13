# Cache

## Cache Control

1. Cache

		proxy.config.http.cache.http
	Set to `0`: Test if ATS disables caching HTTP requests.
	
	Set to `1`: Test if ATS enables caching HTTP requests.

## Caching HTTP Objects

1. Client Directives

	By default, ATS does not cache objects with the following request headers:
	* `Authorization`
	* `Cache-Control: no-store`
	* `Cache-Control: no-cache`
	* `Cookie`(for text objects)

	We need to test the following scenarios:
	* Test if ATS does not cache objects with the above request headers.
	* Test if ATS can ignore client no-cache headers.
	* Test if ATS caches cookied content.
	
1. Origin Server Directives

	By default, Traffic Server does not cache objects with the following response headers:
	* `Cache-Control: no-store`
	* `Cache-Control: private`
	* `WWW-Authenticate`
	* `Set-Cookie`
	* `Cache-Control: no-cache`
	* `Expires`

	We need to test the following scenarios:
	* Test if ATS does not cache objects with the above response headers.
	* Test if ATS can ignore `WWW-Authenticate` headers.
	* Test if ATS can ignore server `no-cache` headers.

## Heuristic Expiration


## Dynamic Content Negotiation


## Negative Response Caching


## Negative Revalidate


## PUSH

	proxy.config.http.push_method_enabled

Set to `1`: Test if ATS allows to deliver content directly to the cache without a user request via `PUSH` method.
