#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base64 import b64encode
from hmac import HMAC
from hashlib import sha256
import json
from urllib import urlencode
import time

import requests


class ServerError(ValueError):
    """
    Indicates HTTP error code.
    """
    def __init__(self, message, status_code):
        super(ServerError, self).__init__(message)
        self.status_code = status_code


class ClientError(ValueError):
    """
    Indicates error made by programmer using this library.
    Used when the server returns a JSON document indicating the error.
    """
    def __init__(self, message, status_code):
        super(ClientError, self).__init__(message)
        self.status_code = status_code


class Response(object):
    """
    Response object returned by resource object.
    """
    def __init__(self, response):
        #: Original response object from Python requests library.
        self.response = response
        #: Dictionary from HTTP response body.
        self.data = self.response.json()

    def __repr__(self):
        return "<Response(status=%r, <Request(method=%r, url=%r)>)>" % (
            self.response.status_code, self.response.request.method,
            self.response.request.url)


class Resource(object):
    """
    REST resource.
    """
    def __init__(self, client, path):
        self.client = client
        self.path = path
        self.id = None

    def __repr__(self):
        return "<Resource(path=%r)>" % self.path

    def __getattr__(self, name):
        """
        Create new Resource.
        """
        key = self.path + '/' + name

        self.client.resources[key] = Resource(self.client, key)

        return self.client.resources[key]

    def __call__(self, id=None):
        """
        Capture resource ID and append to path.

        Example::

            # /products
            client.products

            # /products/1234
            client.products(1234)
        """
        if id == None:
            return self

        self.id = str(id)

        key = self.path + '/' + self.id

        self.client.resources[key] = Resource(self.client, key)

        return self.client.resources[key]

    def get(self, **kwargs):
        """
        Sends a GET request. Returns :class:`Response` object.

        :param params: (optional) Dictionary of arguments to be sent via HTTP request query string.
        :param data: (optional) Dictionary of arguments to be sent via HTTP request body.

        Usage::

            # GET /products?offset=10&limit=10
            client.products.get(params={"offset":10, "limit":10})
        """
        return self._make_request("GET", **kwargs)

    def put(self, **kwargs):
        """
        Sends a PUT request. Returns :class:`Response` object.

        :param params: (optional) Dictionary of arguments to be sent via HTTP request query string.
        :param data: (optional) Dictionary of arguments to be sent via HTTP request body.

        Usage::

            # PUT /products/1234
            client.products(1234).put(data={"url": "http://example.com",
                "title": "T-shirt", "price": 5.99})
        """
        return self._make_request("PUT", **kwargs)

    def post(self, **kwargs):
        """
        Sends a POST request. Returns :class:`Response` object.

        :param params: (optional) Dictionary of arguments to be sent via HTTP request query string.
        :param data: (optional) Dictionary of arguments to be sent via HTTP request body.

        Usage::

            # POST /transactions/1234/lineitems
            client.transactions(1234).lineitems.post(data={
                "product_id": "blue_tshirt", "quantity": 3, "unit_price": 2.31,
                "subtotal": 14.32, "total": 6.04})

            # POST /products/_bulk
            client.products._bulk.post(data=[{"id": ""}, {"id": ""}])
        """
        return self._make_request("POST", **kwargs)

    def _make_request(self, method, params=None, data=None):
        """
        Sign request.
        """
        if params is None:
            params = {}

        params["nonce"] = int(time.time() * 1000)

        url =  self.client.base_url + self.path + "?" +  urlencode(params)

        if data is None:
            data = {}

        data = json.dumps(data)

        sig = b64encode(HMAC(self.client.secret, url + data, sha256).hexdigest())

        response = requests.request(method, url, data=data, headers={
            "Auth-Signature": sig, "Auth-API-Key": self.client.key,
            "Accept": "application/json", "Content-Type": "application/json"})

        return self._handle_response(response)

    def _handle_response(self, response):
        """
        Raise exception for client and server errors.
        """
        if response.status_code >= 500:
            raise ServerError(response.content, response.status_code)
        elif response.status_code >= 300:
            raise ClientError(response.json(), response.status_code)

        return Response(response)


class Client(object):
    """
    Main entry point.

    :param key: Ometria API key.
    :param secret: Ometria API secret.
    :param version: (optional) Ometria API version to use.

    Usage::

        >>> c = Client(key="...", secret="...")
        >>> c.customers(1234).orders.get()
    """
    def __init__(self, key, secret, version="1"):
        self.key = key
        self.secret = secret
        self.version = version
        self.base_url = "https://api.ometria.com/v%s/" % self.version
        self.resources = {}

    def __getattr__(self, name):
        """
        Access REST resources via Python attributes API. Returns :class:`Resource` object.

        Example::

            >>> type(client.customers)
            <Resource(path='customers')>

            >>> c.customers(123).orders
            <Resource(path='customers/123/orders')>
        """
        key = name

        if key not in self.resources:
            self.resources[key] = Resource(self, key)

        return self.resources[key]

    def __repr__(self):
        return "<Client(key=%r, secret=%r)>" % (self.key, self.secret)