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
import requests
import time
import logging

import helpers

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
        # remap to ATLAS host
        cls.atlas_host = 'qa01atlasdlv01.vpg.gq1.yahoo.com'
        cls.configs['remap.config'].add_line('map / http://{0}/\n'.format(cls.atlas_host))

        # only add server headers when there weren't any
        cls.configs['records.config']['CONFIG']['proxy.config.http.response_server_enabled'] = 2
        cls.configs['records.config']['CONFIG']['proxy.config.http.keep_alive_enabled_out'] = 1
        cls.configs['records.config']['CONFIG']['share_server_session'] = 2

        # set only one ET_NET thread (so we don't have to worry about the per-thread pools causing issues)
        cls.configs['records.config']['CONFIG']['proxy.config.exec_thread.limit'] = 1
        cls.configs['records.config']['CONFIG']['proxy.config.exec_thread.autoconfig'] = 0
    
    def test_POC_1(self):
        '''
        Test 1 that the origin does in fact support partial object caching
        '''
        with requests.Session() as s:
            url = 'http://{0}/qa/large'.format(self.atlas_host)
            queries = {'a': 'qa1', 's': '67c65b02bc8c7f7a95d9d7ba24aceebe'}
            ret = s.get(url, params=queries)
            log.info('content-length: {0}'.format(ret.headers['content-length']))
            self.assertEqual(ret.status_code, 200)
            self.assertEqual(len(ret.text), int(ret.headers['content-length']))
    
    def test_POC_1_proxy(self):
        '''
        Test 1 that partial object caching works through ATS to that origin
        '''
        url = 'http://{0}/qa/large'.format(self.atlas_host)
        queries = {'a': 'qa1', 's': '67c65b02bc8c7f7a95d9d7ba24aceebe'}
        ret = requests.get(url, params=queries, proxies=self.proxies)
        log.info('content-length: {0}'.format(ret.headers['content-length']))
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(len(ret.text), int(ret.headers['content-length']))
     
    def test_POC_2(self):
        '''
        Test 2 that the origin does in fact support partial object caching
        '''
        with requests.Session() as s:
            url = 'http://{0}/qa/big_buck_bunny.mp4'.format(self.atlas_host)
            queries = {'a': 'qa1', 's': '0d89160ab9e8c602c3772af8a152e03e'}
            ret = s.get(url, params=queries)
            log.info('content-length: {0}'.format(ret.headers['content-length']))
            self.assertEqual(ret.status_code, 200)
            self.assertEqual(len(ret.text), int(ret.headers['content-length']))
    
    def test_POC_2_proxy(self):
        '''
        Test 2 that partial object caching works through ATS to that origin
        '''
        url = 'http://{0}/qa/big_buck_bunny.mp4'.format(self.atlas_host)
        queries = {'a': 'qa1', 's': '0d89160ab9e8c602c3772af8a152e03e'}
        ret = requests.get(url, params=queries, proxies=self.proxies)
        log.info('content-length: {0}'.format(ret.headers['content-length']))
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(len(ret.text), int(ret.headers['content-length']))       

    def test_POC_3(self):
        '''
        Test 3 that the origin does in fact support partial object caching
        '''
        with requests.Session() as s:
            url = 'http://{0}/qa/big_buck_bunny.mp4'.format(self.atlas_host)
            queries = {'a': 'qa1', 's': '0d89160ab9e8c602c3772af8a152e03e'}
            headers = {'Range': 'bytes=0-20000'}
            ret = s.get(url, params=queries, headers=headers)
            log.info('content-length: {0}'.format(ret.headers['content-length']))
            self.assertEqual(ret.status_code, 206)
            self.assertEqual(len(ret.text), int(ret.headers['content-length']))
    
    def test_POC_3_proxy(self):
        '''
        Test 3 that partial object caching works through ATS to that origin
        '''
        url = 'http://{0}/qa/big_buck_bunny.mp4'.format(self.atlas_host)
        queries = {'a': 'qa1', 's': '0d89160ab9e8c602c3772af8a152e03e'}
        headers = {'Range': 'bytes=0-20000'}
        ret = requests.get(url, params=queries, headers=headers, proxies=self.proxies)
        log.info('content-length: {0}'.format(ret.headers['content-length']))
        self.assertEqual(ret.status_code, 206)
        self.assertEqual(len(ret.text), int(ret.headers['content-length']))

class TestPartialObjectCachingHTTPS(helpers.EnvironmentCase):
    @classmethod
    def setUpEnv(cls, env):
        '''
        This function is responsible for setting up the environment for this fixture
        This includes everything pre-daemon start
        '''
        # remap to ATLAS host
        cls.atlas_host = 'qa01atlasdlv01.vpg.gq1.yahoo.com'
        cls.configs['remap.config'].add_line('map / https://{0}/\n'.format(cls.atlas_host))

        # only add server headers when there weren't any
        cls.configs['records.config']['CONFIG']['proxy.config.http.response_server_enabled'] = 2
        cls.configs['records.config']['CONFIG']['proxy.config.http.keep_alive_enabled_out'] = 1
        cls.configs['records.config']['CONFIG']['share_server_session'] = 2

        # set only one ET_NET thread (so we don't have to worry about the per-thread pools causing issues)
        cls.configs['records.config']['CONFIG']['proxy.config.exec_thread.limit'] = 1
        cls.configs['records.config']['CONFIG']['proxy.config.exec_thread.autoconfig'] = 0
    
    def test_POC_1(self):
        '''
        Test 1 that the origin does in fact support partial object caching
        '''
        with requests.Session() as s:
            url = 'https://{0}/qa/large'.format(self.atlas_host)
            queries = {'a': 'qa1', 's': '67c65b02bc8c7f7a95d9d7ba24aceebe'}
            ret = s.get(url, params=queries, verify=False)
            log.info('content-length: {0}'.format(ret.headers['content-length']))
            self.assertEqual(ret.status_code, 200)
            self.assertEqual(len(ret.text), int(ret.headers['content-length']))
    
    def test_POC_1_proxy(self):
        '''
        Test 1 that partial object caching works through ATS to that origin
        '''
        url = 'https://{0}/qa/large'.format(self.atlas_host)
        queries = {'a': 'qa1', 's': '67c65b02bc8c7f7a95d9d7ba24aceebe'}
        ret = requests.get(url, params=queries, proxies=self.proxies, verify=False)
        log.info('content-length: {0}'.format(ret.headers['content-length']))
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(len(ret.text), int(ret.headers['content-length']))
     
    def test_POC_2(self):
        '''
        Test 2 that the origin does in fact support partial object caching
        '''
        with requests.Session() as s:
            url = 'https://{0}/qa/big_buck_bunny.mp4'.format(self.atlas_host)
            queries = {'a': 'qa1', 's': '0d89160ab9e8c602c3772af8a152e03e'}
            ret = s.get(url, params=queries, verify=False)
            log.info('content-length: {0}'.format(ret.headers['content-length']))
            self.assertEqual(ret.status_code, 200)
            self.assertEqual(len(ret.text), int(ret.headers['content-length']))
    
    def test_POC_2_proxy(self):
        '''
        Test 2 that partial object caching works through ATS to that origin
        '''
        url = 'https://{0}/qa/big_buck_bunny.mp4'.format(self.atlas_host)
        queries = {'a': 'qa1', 's': '0d89160ab9e8c602c3772af8a152e03e'}
        ret = requests.get(url, params=queries, proxies=self.proxies, verify=False)
        log.info('content-length: {0}'.format(ret.headers['content-length']))
        self.assertEqual(ret.status_code, 200)
        self.assertEqual(len(ret.text), int(ret.headers['content-length']))       

    def test_POC_3(self):
        '''
        Test 3 that the origin does in fact support partial object caching
        '''
        with requests.Session() as s:
            url = 'https://{0}/qa/big_buck_bunny.mp4'.format(self.atlas_host)
            queries = {'a': 'qa1', 's': '0d89160ab9e8c602c3772af8a152e03e'}
            headers = {'Range': 'bytes=0-20000'}
            ret = s.get(url, params=queries, headers=headers, verify=False)
            log.info('content-length: {0}'.format(ret.headers['content-length']))
            self.assertEqual(ret.status_code, 206)
            self.assertEqual(len(ret.text), int(ret.headers['content-length']))
    
    def test_POC_3_proxy(self):
        '''
        Test 3 that partial object caching works through ATS to that origin
        '''
        url = 'https://{0}/qa/big_buck_bunny.mp4'.format(self.atlas_host)
        queries = {'a': 'qa1', 's': '0d89160ab9e8c602c3772af8a152e03e'}
        headers = {'Range': 'bytes=0-20000'}
        ret = requests.get(url, params=queries, headers=headers, proxies=self.proxies, verify=False)
        log.info('content-length: {0}'.format(ret.headers['content-length']))
        self.assertEqual(ret.status_code, 206)
        self.assertEqual(len(ret.text), int(ret.headers['content-length']))
