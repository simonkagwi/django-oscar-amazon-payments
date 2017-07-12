===========================================
An Amazon Payments package for django-oscar
===========================================

This package provides integration between `django-oscar`_ and `Amazon Payments (Login and Pay with Amazon)`_.

.. _django-oscar: https://github.com/django-oscar/django-oscar
.. _`Amazon Payments (Login and Pay with Amazon)`: https://payments.amazon.com

Tested with **Python 2.7**, **Django 1.6** and **django-oscar 0.7.3**.

Setup
-----
Follow the instructions on configuring your website for Login and Pay with Amazon under
https://payments.amazon.com/documentation/lpwa/201749840#201749930.
Note that the website setup requires the "Allowed JavaScript origin" to be a HTTPS
URL, so you won't be able to test Amazon Payments integration with a site run using
the Django runserver command.

You will also need an Amazon MWS API key and secret key. These are used to 
interact with the Amazon MWS Off-Amazon Payments API to actually process the
payments. For more information on how to register for Amazon MWS, see
http://docs.developer.amazonservices.com/en_US/dev_guide/DG_Registering.html

Add 'amazon_payments' to your INSTALLED_APPS, and also add the following settings in your django settings:

* AMAZON_PAYMENTS_ACCESS_KEY
* AMAZON_PAYMENTS_SECRET_KEY
* AMAZON_PAYMENTS_SELLER_ID
* AMAZON_PAYMENTS_CLIENT_ID
* AMAZON_PAYMENTS_CURRENCY

Other settings:

* AMAZON_PAYMENTS_API_ENDPOINT: defaults to "https://mws.amazonservices.com/OffAmazonPayments_Sandbox/2013-01-01"
* AMAZON_PAYMENTS_API_VERSION: defaults to "2013-01-01".
* AMAZON_PAYMENTS_IS_LIVE: defaults to False. Set True to enable live payments.

Sandbox site
------------
The sandbox site demonstrates how you can set up 2 different Amazon Payments
checkout procedures:

1. **One-step checkout**: User selects the shipping address and payment method 
   in one step. Clicking the "Place order" button will immediately attempt to
   charge the user's Amazon account and takes them to the confirmation / thank you
   page if successful. Assumes there is one shipping method.
2. **Multi-step checkout**: The default oscar checkout process.

Setting up the sandbox site:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
1. Change directory to the sandbox directory
2. Activate your virtualenv
3. ``pip install -r requirements.txt``
4. ``python manage.py syncdb``
5. ``python manage.py migrate``
6. ``python manage.py loaddata fixtures/countries.json``

   The countries.json bundled with this project is different from the one
   in oscar in that it sets is_shipping_country to True for all countries,
   otherwise because of the validation we do for shipping addresses gotten
   from Amazon you would get an error message for all countries except GB.

7. ``python manage.py oscar_import_catalogue fixtures/catalogue.csv``
8. ``mkdir -p public/media``
9. Create the image_not_found.jpg file:

   ``ln -s /<INSERT PATH TO OSCAR>/static/oscar/img/image_not_found.jpg public/media/``

**Remember: Amazon Payments requires your "Allowed JavaScript origin" (one of
the settings when you're setting up your Amazon Payments account) to be a HTTPS URL,
so you will not be able to test the Amazon Payments functionality with a site
run using Django's runserver. You can set up a simple webserver that uses a
self-signed SSL certificate in something like nginx or Apache.**


Recurring Payments
------------------
From https://payments.amazon.com/documentation/automatic/201752090:

*With the recurring payments feature, buyers can pre-authorize payments for 
future purchases. This enables you to charge a buyer’s Amazon Payments account 
on a regular basis for subscriptions and usage based billing without requiring 
the buyer to authorize a payment each time.*

Recurring payments are disabled by default. To enable such payments, override 
the Basket model in your oscar project to add a "has_subscriptions" property 
that returns True where appropriate. This has been done in the sandbox site, so
you will see the "Recurring payments" widget during checkout.

Testing
-------
::

    mkvirtualenv <VIRTUALENV_NAME>
    git clone https://github.com/simonkagwe/django-oscar-amazon-payments.git
    cd django-oscar-amazon-payments
    pip install -e .[oscar]
    python setup.py test

TODO
----
- Support newer versions of Django and Oscar
