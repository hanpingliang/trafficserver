#!/bin/env python
 
from twisted.web.resource import Resource, NoResource, UnsupportedMethod
from twisted.web.server import Site
from twisted.internet import reactor
from twisted.python import log
from twisted.web import server
 
import sys
import os
import json
 
# See http://twistedmatrix.com/documents/current/web/howto/web-in-60/index.html
port = 80

class GeneratedPatternResource:
    def parseRangeHeader(self, range):
        try:
            kind, value = range.split('=', 1)
        except ValueError:
            raise ValueError("Missing '=' separator")
        kind = kind.strip()
        if kind != 'bytes':
            raise ValueError("Unsupported Bytes-Unit: %r" % (kind,))
        parsedRanges = []
        unparsedRanges = filter(None, map(str.strip, value.split(',')))
        for byteRange in unparsedRanges:
            try:
                start, end = byteRange.split('-', 1)
            except ValueError:
                raise ValueError("Invalid Byte-Range: %r" % (byteRange,))
            if start:
                try:
                    start = int(start)
                except ValueError:
                    raise ValueError("Invalid Byte-Range: %r" % (byteRange,))
            else:
                start = None
            if end:
                try:
                    end = int(end)
                except ValueError:
                    raise ValueError("Invalid Byte-Range: %r" % (byteRange,))
            else:
                end = None
            if start is not None:
                if end is not None and start > end:
                    # Start must be less than or equal to end or it is invalid.
                    raise ValueError("Invalid Byte-Range: %r" % (byteRange,))
            elif end is None:
                # One or both of start and end must be specified.  Omitting
                # both is invalid.
                raise ValueError("Invalid Byte-Range: %r" % (byteRange,))
            parsedRanges.append((start, end))

        return parsedRanges[0] #right now we only support first range but can modify


    def seven_digit_hex(self, n):
        return "0x%s"%("0000000%x"%(n&0xfffffff))[-7:] 
    
    def generateBytes(self, start, end):
        if end < 0 or start < 0 or start > end:
            return 'invalid request, you get this string instead'
        
        #get start and end points for chunks in pattern
        start_point = int(start / 8)
        end_point = int(end / 8)

        start_chunk = int(self.seven_digit_hex(start_point), 16)
        end_chunk = int(self.seven_digit_hex(end_point), 16)

        #construct string
        temp_string = ''
        for i in xrange(start_chunk, end_chunk + 1):
            temp_string += self.seven_digit_hex(i)[2:]
            temp_string += ' '

        #return correct substring
        return temp_string[(start % 8):((start % 8) + (end - start + 1))]

class NonChunkedResponseResource(Resource, GeneratedPatternResource):
    def __init__(self, conf, method):
        self.__conf = conf
        self.__method = method
        self.isLeaf = 1
        
        if conf.has_key('status_code'):
            self.__status_code = conf['status_code']
        else:
            self.__status_code = 200
 
        if conf.has_key('headers'):
            self.__headers = conf['headers']
        else:
            self.__headers = {}

        if conf.has_key('content_length'):
            self.__content_length = conf['content_length']
        else:
            self.__content_length = 1000

        self.__body = self.generateBytes(0, self.__content_length - 1)

        if not self.__headers.has_key('content-length'):
            self.__headers['content-length'] = len(self.__body)
     
    
    
    def render(self, request):
        for field_name, field_value in self.__headers.iteritems():
            request.setHeader(bytes(field_name), bytes(field_value))
 
        byteRange = request.getHeader('range')
        if byteRange is None:
            request.setResponseCode(self.__status_code)
            request.write(self.__body)
            return ""

        #if we get here there's a range header
        try:
            start, end = self.parseRangeHeader(byteRange)
            # validate start/end
            if start < 0 or end > (self.__content_length - 1):
                raise ValueError("requesting bytes outside content length")
            else:
                # have to update content length header
                request.setHeader('content-length', bytes(str(end - start + 1)))
                # return range request
                request.setResponseCode(206)
                request.length = end - start + 1
                request.write(self.__body[start:(end + 1)])
                return ""
        except:
            log.msg("ignoring malformed range header %r" % (byteRange,))
            request.setResponseCode(self.__status_code)
            request.write(self.__body)
            return ""
 
class ChunkedResponseResource(Resource, GeneratedPatternResource):
    def __init__(self, conf, method):
        self.__conf = conf
        self.__method = method
        self.isLeaf = 1
        self.__patternedChunks = False
        self.__range_start = 0
        self.__range_end = sys.maxint
 
        if conf.has_key('status_code'):
            self.__status_code = conf['status_code']
        else:
            self.__status_code = 200
 
        if conf.has_key('headers'):
            self.__headers = conf['headers']
        else:
            self.__headers = {}
 
        if conf.has_key('num_chunks'):
            self.__chunks_to_send = conf['num_chunks']
        else:
            self.__chunks_to_send = 0
 
        if conf.has_key('delay_first_chunk_sec'):
            self.__delay_first_chunk_sec = conf['delay_first_chunk_sec']
        else:
            self.__delay_first_chunk_sec = 0
 
        if conf.has_key('delay_between_chunk_sec'):
            self.__delay_between_chunk_sec = conf['delay_between_chunk_sec']
        else:
            self.__delay_between_chunk_sec = 0
         
        if conf.has_key('chunk_size_bytes'):
            self.__chunk_size_bytes = conf['chunk_size_bytes']
        else:
            self.__chunk_size_bytes = 1024
 
        if conf.has_key('patterned_chunks') and conf['patterned_chunks'] == 'true':
            self.__patternedChunks = True
        else:
            if conf.has_key('chunk_byte_value'):
                chunk_byte_value = conf['chunk_byte_value']
            else:
                chunk_byte_value = 42
 
            self.__chunk = chr(chunk_byte_value) * self.__chunk_size_bytes
 
    def __send_chunk(self, request, chunks_left):
        if self.__patternedChunks: #right now can only do range requests for patterned requests
            first_byte = self.__chunk_size_bytes * (self.__chunks_to_send - chunks_left)
            last_byte = first_byte + self.__chunk_size_bytes - 1
            if last_byte < self.__range_start or first_byte > self.__range_end:
                pass
            else:
                request.write(self.generateBytes(max(self.__range_start, first_byte), min(self.__range_end, last_byte)))
        else:
            request.write(self.__chunk)
 
        if 1 == chunks_left:
            request.finish()
            return
 
        reactor.callLater(self.__delay_between_chunk_sec, self.__send_chunk, request, chunks_left - 1)
        return server.NOT_DONE_YET
 
 
    def render(self, request):
        """if self.__method != request.method:
            request.setResponseCode(405)
            return "" """
 
        chunks_left = self.__chunks_to_send
 
        for field_name, field_value in self.__headers.iteritems():
            request.setHeader(bytes(field_name), bytes(field_value))
 
        
        byteRange = request.getHeader('range')
        if byteRange is not  None:
            #if we get here there's a range header
            try:
                start, end = self.parseRangeHeader(byteRange)
                self.__range_start = start
                self.__range_end = end
                request.setResponseCode(206)
            except:
                log.msg("ignoring malformed range header %r" % (byteRange,))
        else:
            request.setResponseCode(self.__status_code)
       
        if 0 == chunks_left:
            return ""
 
        reactor.callLater(self.__delay_first_chunk_sec, self.__send_chunk, request, chunks_left)
        return server.NOT_DONE_YET

class CannedTwistedOrigin:
    def __init__(self, pname, cpath):
        self.process_name = pname
        self.config_path = cpath
     
        self.config = self.parse_config(self.config_path, self.process_name)
        conf = self.config
     
        if not conf.has_key('interfaces') or not conf['interfaces'].has_key('http') or \
            not conf['interfaces']['http'].has_key('port'):
            raise Exception("'interfaces:http:port' does not exist for process '%s'" % self.process_name)
     
        if not conf.has_key('actions'):
            raise Exception("'actions' does not exist for process '%s" % self.process_name)
     
        global port
        port = conf['interfaces']['http']['port']
    
    def run(self):
        log.startLogging(sys.stdout)
     
        reactor.listenTCP(port, Site(self.build_resource_tree(self.config['actions'])))
        try:
          reactor.run(installSignalHandlers=0)
        except:
          reactor.stop()

    def __del__(self):
        reactor.stop()
     
    def build_resource_tree(self, actions):
        """ build a static resource map that corresponds to the test case's config.json.  Limitation:  currently
        only one abs_path per method can be supported due to blattj's limited understanding of the twisted api.
     
        :param actions: The origin process's 'actions' section from the test case's config.json
        :return: a root resource with all sub-resources described in the config.json registered.
        """
        root = Resource()
     
        for method, paths in actions.iteritems():
            for abs_path, conf in paths.iteritems():
                if not conf.has_key('type'):
                    raise Exception("conf for '%s:%s' is missing type" % (method, abs_path))
     
                # Add interior resources
     
                parent = root
                abs_path = abs_path.split('/')
                length = len(abs_path)
     
                for i in range(1, length - 1):
                    child = parent.getStaticEntity(abs_path[i])
     
                    if not child or isinstance(child, NoResource):
                        child = Resource()
                        parent.putChild(abs_path[i], child)
                    elif child.isLeaf:
                        raise Exception("Leaf resource cannot contain other resources")
     
                    parent = child
     
                # Add leaf resource.   In the future other leaf resources can be added here
     
                type = conf['type']
     
                if type == 'chunkedresponse':
                    child = ChunkedResponseResource(conf, method)
                elif type == 'nonchunkedresponse':
                    child = NonChunkedResponseResource(conf, method)
                else:
                    raise Exception("conf for %s:%s has unknown type '%s'" % (method, abs_path, type))
     
                parent.putChild(abs_path[length - 1], child)

        return root

    def get_port(self):
        return port
     
    def parse_config(self, config_path='config.json', process_name=None):
        """ Get the test manager's parsed configuration file
        :param process_name: Optional: if supplied return only subdoc for the process.  Else return the entire config
        """
     
        if not os.path.isfile(config_path):
            raise Exception("Config file '%s' does not exist" % config_path)
     
        conf = json.load(open(config_path, 'r'), encoding='utf-8')
     
        if not process_name:
            return conf
     
        if not conf.has_key('processes'):
            raise Exception("Configuration has no 'processes' section")
     
        if not conf['processes'].has_key(process_name):
            raise Exception("Configuration has no '%s' process" % process_name)
     
        return conf['processes'][process_name]
