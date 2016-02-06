#!/usr/bin/env python2

import os
import unittest
import tempfile

import main

class RelayControlTestCase(unittest.TestCase):

    def setUp(self):
        main.app.config['TESTING'] = True
        main.load_relays("settings/test.json")
        self.app = main.app.test_client()

    def test_list_relays(self):
        rv = self.app.get('/relays')
        assert '{"state": true, "id": "0"}' in rv.data
        assert '{"state": true, "id": "1"}' in rv.data

    def test_get_relay(self):
        rv = self.app.get('/relays/2')
        assert '{"state": true, "id": "2"}' in rv.data

    def test_set_relay(self):
        rv = self.app.post('/relays/3', data=dict(state="false"))
        assert '{"state": false, "id": "3"}' in rv.data
        rv = self.app.post('/relays/3', data=dict(state="true"))
        assert '{"state": true, "id": "3"}' in rv.data

    def test_toggle_relay(self):
        rv = self.app.post('/relays/3', data=dict(state="false"))
        assert '{"state": false, "id": "3"}' in rv.data
        rv = self.app.get('/relays/3/toggle')
        assert '{"state": true, "id": "3"}' in rv.data

if __name__ == '__main__':
    unittest.main()
