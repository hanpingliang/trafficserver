# SSL

## Certificate Configurations

Configure server certificate and private key file.

Test if SSL connection works.

## Protocol Version

	proxy.config.ssl.SSLv2
	proxy.config.ssl.SSLv3
	proxy.config.ssl.TLSv1
	proxy.config.ssl.TLSv1_1
	proxy.config.ssl.TLSv1_2

Set `proxy.config.ssl.SSLv2` to `0`, ..., `proxy.config.ssl.TLSv1` to `1`, ...: Test if ATS does not use SSL version 2, ..., uses TLS version 1, ..., when it handshakes with client.

## Protocol Version (ATS as client)

	proxy.config.ssl.client.SSLv2
	proxy.config.ssl.client.SSLv3
	proxy.config.ssl.client.TLSv1
	proxy.config.ssl.client.TLSv1_1
	proxy.config.ssl.client.TLSv1_2

Set `proxy.config.ssl.SSLv2` to `0`, ..., `proxy.config.ssl.TLSv1` to `1`, ...: Test if ATS does not use SSL version 2, ..., uses TLS version 1, ..., when it handshakes with origin server.


## Cipher Suite

	proxy.config.ssl.server.cipher_suite

Set `proxy.config.ssl.server.cipher_suite` to `ECDHE-RSA-AES256-GCM-SHA384:...`: Test if ATS is using a cipher suite in the list when it handshakes with client.

## Cipher Suite (ATS as client)

	proxy.config.ssl.client.cipher_suite

Set `proxy.config.ssl.client.cipher_suite` to `ECDHE-RSA-AES256-GCM-SHA384:...`: Test if ATS is using a cipher suite in the list when it handshakes with origin server.

## Multicert Loading

The ssl_multicert.config file lets you configure Traffic Server to use multiple SSL server certificates to terminate the SSL sessions. If you have a Traffic Server system with more than one IP address assigned to it, then you can assign a different SSL certificate to be served when a client requests a particular IP address or host name.

**Rewrite with new_tsqa**: [test-multicert-loading](https://github.com/apache/trafficserver/blob/master/ci/tsqa/test-multicert-loading)

## Privilege Elevation

Set `records.config`:

	CONFIG proxy.config.ssl.cert.load_elevated INT 1
	CONFIG proxy.config.plugin.load_elevated INT 1

	CONFIG proxy.config.diags.debug.enabled INT 1
	CONFIG proxy.config.diags.debug.tags STRING 'privileges'

**Rewrite with new_tsqa**: [test-privilege-elevation](https://github.com/apache/trafficserver/blob/master/ci/tsqa/test-privilege-elevation)

## Verify Client's Certificate

We can authenticate client during SSL handshake, and client is required to provide a certificate.

	proxy.config.ssl.client.certification_level

Set `records.config`:

This is a test certificate signed by a test CA, which is not in system PKI or browser. So, we need to specify the CA certificate:
	
	# 1: optional 2: required
	CONFIG proxy.config.ssl.client.certification_level INT 2
	
	# specify CA file name and path, who signed client's certificate
	CONFIG proxy.config.ssl.CA.cert.filename STRING ca.crt
	CONFIG proxy.config.ssl.CA.cert.path STRING etc/trafficserver

Test if ATS verifies client's certificate.

## Verify Origin Server's Certificate

We can configure it to verify the origin server certificate with the Certificate Authority (CA).

**Notice**: By default, ATS does not verify the origin server!

	proxy.config.ssl.client.verify.server

Set `records.config`:

	CONFIG proxy.config.ssl.client.verify.server INT 1
	
	# specify CA file name and path, who signed origin server's certificate
	CONFIG proxy.config.ssl.client.CA.cert.filename STRING ca.crt
	CONFIG proxy.config.ssl.client.CA.cert.path STRING etc/trafficserver

Test if ATS verifies origin server's certificate.

## Verified by Origin Server

Send origin server certificate for verification. Here ATS is SSL client, and origin server requires to verify ATS.

	proxy.config.ssl.client.cert.filename
	proxy.config.ssl.client.cert.path
	proxy.config.ssl.client.private_key.filename
	proxy.config.ssl.client.private_key.path

Test if ATS passed origin server's verification.

## SNI

**Done**: [test_https](https://github.com/apache/trafficserver/blob/master/ci/new_tsqa/tests/test_https.py)

## Session Reuse

1. Session Ticket
2. Session ID

## OCSP Stapling

	proxy.config.ssl.ocsp.enabled

By default, ATS does not enable OCSP Stapling.

1. Good OCSP response.

	Generate a test certificate with OCSP extensions; start an OCSP server. Test if ATS staples the **good** OCSP response and sends it to client along with certificate in SSL handshake.

1. Revoked OCSP response.

	Generate a test certificate with OCSP extensions, then revoke it; start an OCSP server. Test if ATS staples the **revoked** OCSP response and sends it to client along with certificate in SSL handshake.

1. Unknown OCSP response.

	Generate a test certificate with OCSP extensions, then remove the entry in test CA's database; start an OCSP server. Test if ATS staples the **unknown** OCSP response and sends it to client along with certificate in SSL handshake.

## Dual Certificate (ECDSA + RSA)

