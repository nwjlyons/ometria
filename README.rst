=======
Ometria
=======

.. image:: https://badge.fury.io/py/ometria.png
    :target: http://badge.fury.io/py/ometria
    
.. image:: https://travis-ci.org/nwjlyons/ometria.png?branch=master
        :target: https://travis-ci.org/nwjlyons/ometria

.. image:: https://pypip.in/d/ometria/badge.png
        :target: https://crate.io/packages/ometria?version=latest


Python wrapper for the `Ometria API`_.

Install
=======

::

    pip install ometria

Usage
====

::

    import ometria
    
    client = ometria.Client(key="...", secret="...")
    
    # GET /products?offset=10&limit=10
    r = client.products.get(params={"offset":10, "limit":10})
    
    r.response # Original response object from Python requests library.
    r.data # Dictionary from HTTP response body.
    
    # PUT /products/1234
    client.products(1234).put(data={"url": "http://example.com",
                "title": "T-shirt", "price": 5.99})
                
    # POST /transactions/1234/lineitems
    client.transactions(1234).lineitems.post(data={
        "product_id": "blue_tshirt", "quantity": 3, "unit_price": 2.31, "subtotal": 14.32, "total": 6.04})

    # POST /products/_bulk
    client.products._bulk.post(data=[{"id": ""}, {"id": ""}])

.. _Ometria API: http://docs.ometria.com/Developers/
