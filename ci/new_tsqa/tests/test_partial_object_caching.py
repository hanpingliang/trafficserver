#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import sys
import requests
import time
import logging
import threading

import helpers
import canned_twisted_origin

import tsqa.test_cases
import tsqa.utils
import tsqa.endpoint

log = logging.getLogger(__name__)

class TestPartialObjectCachingHTTP(helpers.EnvironmentCase):
    @classmethod
    def setUpEnv(cls, env):
        '''
        This function is responsible for setting up the environment for this fixture
        This includes everything pre-daemon start
        '''
        # remap to canned origin host
        cls.origin_process = canned_twisted_origin.CannedTwistedOrigin('origin1',
          helpers.tests_file_path('partial_object_caching_origin.json'))
        cls.__background_thread = threading.Thread(target=cls.origin_process.run)
        cls.__background_thread.setDaemon(True)
        cls.__background_thread.start()
        
        cls.origin_port = cls.origin_process.get_port() #TODO remname origin procies
        cls.configs['remap.config'].add_line('map / http://127.0.0.1:{0}/\n'.format(cls.origin_port))

        # only add server headers when there weren't any
        cls.configs['records.config']['CONFIG']['proxy.config.http.response_server_enabled'] = 2
        cls.configs['records.config']['CONFIG']['proxy.config.http.keep_alive_enabled_out'] = 1
        cls.configs['records.config']['CONFIG']['share_server_session'] = 2

        # set only one ET_NET thread (so we don't have to worry about the per-thread pools causing issues)
        cls.configs['records.config']['CONFIG']['proxy.config.exec_thread.limit'] = 1
        cls.configs['records.config']['CONFIG']['proxy.config.exec_thread.autoconfig'] = 0
    
    def test_POC_1(self):
        '''
        Test 1 that the origin does in fact support partial object caching (known 404)
        '''
        with requests.Session() as s:
            url = 'http://127.0.0.1:{0}/'.format(self.origin_port)
            ret = s.get(url)
            self.assertEqual(ret.status_code, 404)
            self.assertEqual(len(ret.text), int(ret.headers['content-length']))
    
    def test_POC_1_proxy(self):
        '''
        Test 1 that partial object caching works through ATS to that origin (known 404)
        '''
        url = 'http://127.0.0.1:{0}/'.format(self.origin_port)
        ret = requests.get(url, proxies=self.proxies)
        self.assertEqual(ret.status_code, 404)
        self.assertEqual(len(ret.text), int(ret.headers['content-length']))

    def test_POC_2(self):
        '''
        Test 2 that the origin does in fact support partial object caching (full chunked)
        '''
        with requests.Session() as s:
            url = 'http://127.0.0.1:{0}/chunked/down_pat'.format(self.origin_port)
            ret = s.get(url)
            self.assertEqual(ret.status_code, 200)
    
    def test_POC_2_proxy(self):
        '''
        Test 2 that partial object caching works through ATS to that origin (full chunked)
        '''
        url = 'http://127.0.0.1:{0}/chunked/down_pat'.format(self.origin_port)
        ret = requests.get(url, proxies=self.proxies)
        self.assertEqual(ret.status_code, 200)

    def test_POC_3(self):
        '''
        Test 3 that the origin does in fact support partial object caching (full nonchunked)
        '''
        with requests.Session() as s:
            url = 'http://127.0.0.1:{0}/nochunked/down'.format(self.origin_port)
            ret = s.get(url)
            self.assertEqual(ret.status_code, 200)
            self.assertEqual(len(ret.text), int(ret.headers['content-length']))
    
    def test_POC_3_proxy(self):
        '''
        Test 3 that partial object caching works through ATS to that origin (full nonchunked)
        '''
        url = 'http://127.0.0.1:{0}/nochunked/down'.format(self.origin_port)
        ret = requests.get(url, proxies=self.proxies)
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(len(ret.text), int(ret.headers['content-length']))

    def test_POC_4(self):
        '''
        Test 4 that the origin does in fact support partial object caching (range chunked)
        '''
        with requests.Session() as s:
            url = 'http://127.0.0.1:{0}/chunked/down_pat'.format(self.origin_port)
            headers = {'range': 'bytes=6-16'}
            ret = s.get(url, headers = headers)
            self.assertEqual(ret.status_code, 206)
            self.assertEqual(ret.text, '0 0000001 0')
    
    def test_POC_4_proxy(self):
        '''
        Test 4 that partial object caching works through ATS to that origin (range chunked)
        '''
        url = 'http://127.0.0.1:{0}/chunked/down_pat'.format(self.origin_port)
        headers = {'range': 'bytes=6-16'}
        ret = requests.get(url, headers=headers, proxies=self.proxies)
        self.assertEqual(ret.status_code, 206)
        self.assertEqual(ret.text, '0 0000001 0')

   
    def test_POC_5(self):
        '''
        Test 5 that the origin does in fact support partial object caching (range nonchunked)
        '''
        with requests.Session() as s:
            url = 'http://127.0.0.1:{0}/nochunked/down'.format(self.origin_port)
            headers = {'range': 'bytes=6-16'}
            ret = s.get(url, headers=headers)
            self.assertEqual(ret.status_code, 206)
            self.assertEqual(len(ret.text), int(ret.headers['content-length']))
            self.assertEqual(ret.text, '0 0000001 0')
    
    def test_POC_5_proxy(self):
        '''
        Test 5 that partial object caching works through ATS to that origin (range nonchunked)
        '''
        url = 'http://127.0.0.1:{0}/nochunked/down'.format(self.origin_port)
        headers = {'range': 'bytes=6-16'}
        ret = requests.get(url, headers=headers, proxies=self.proxies)
        self.assertEqual(ret.status_code, 206)
        self.assertEqual(len(ret.text), int(ret.headers['content-length']))
        self.assertEqual(ret.text, '0 0000001 0')
