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
 
class ChunkedResponseResource(Resource):
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
 
        if conf.has_key('chunk_byte_value'):
            chunk_byte_value = conf['chunk_byte_value']
        else:
            chunk_byte_value = 42
 
        if conf.has_key('chunk_size_bytes'):
            chunk_size_bytes = conf['chunk_size_bytes']
        else:
            chunk_size_bytes = 1024
 
        self.__chunk = chr(chunk_byte_value) * chunk_size_bytes
 
    def __send_chunk(self, request, chunks_left):
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
