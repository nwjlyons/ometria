#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_ometria
----------------------------------

Tests for `ometria` module.
"""

import unittest
import httpretty

from ometria import Client


class TestOmetria(unittest.TestCase):

    def setUp(self):
        self.client = Client(key="ometria_api_key", secret="ometria_api_secret")

    @httpretty.activate
    def test_retrieving_products(self):
        httpretty.register_uri(httpretty.GET, self.client.base_url + "products",
            body="{}")

        r = self.client.products.get()
        self.assertEqual(r.response.status_code, 200)

if __name__ == '__main__':
    unittest.main()