'''
Created on Apr 20, 2016

@author: caleb kandoro
'''
import unittest as ut
import requests
import os
import data
import random

class ServerTest(ut.TestCase):
    def setUp(self):
        self.s = requests.Session()
        login = {"user":"nakamura9a", 
                 "password":"123"}
        r = self.s.get("http://localhost:8080/authenticate", params=login)
        print(r.url)
        print("login response")
        
    def test_failed_login(self):
        login = {"user":"some_guy", 
                 "password":"123"}
        r = self.s.get("http://localhost:8080/authenticate", params=login)
        #print(r.text)
        self.assertEqual(r.status_code, 200)
        
    @ut.expectedFailure
    def test_security(self):
        rr = self.s.get("http://localhost:8080/new")
        self.assertEqual(rr.status_code, 200)
        self.assertEqual(rr.url, "http://localhost:8080/index")
        
    def test_summary(self):
        rr = self.s.get("http://localhost:8080/summary")
        self.assertEqual(rr.status_code, 200)
        
    
    
    def test_general(self):
        rr = self.s.get("http://localhost:8080/general?_type=pressure")
        self.assertEqual(rr.status_code, 200)
    
    
    
    def test_calibration_balance(self):
        calibrate = {
                     '_customer': "test",
                     '_instrument': 'mass pieces',
                     '_sn': '{}test'.format(random.randint(10, 100)),
                     '_man': 'AnD',
                     '_model': 'o123',
                     '_range': '0.1- 1000',
                     '_resolution': '0.001',
                     '_units': 'grams',
                     '_procedure': "procedure",
                     'off_center_mass': '200',
                     'warm_up_nominal': "100",
                     'mass_pieces_set': "brass",
                     '_location': 'some__place_far_far_away',
                     '_comments': 'bleh ,blah, blah,blah, blah'}
        
        r = self.s.post("http://localhost:8080/captured_balance", params=calibrate)
        print("calibration response")
        print(r.text)
        
    def test_index(self):
        r = self.s.get("http://localhost:8080")
        self.assertEqual(r.status_code, 200)
    
    def test_login_success(self):
        login = {"user":"nakamura9a", 
                 "password":"123"}
        r = self.s.get("http://localhost:8080/authenticate", params=login)
        print(r.url)
        print("login response")
        #print(r.text)
        self.assertEqual(r.status_code, 200)
        
        
ut.main()