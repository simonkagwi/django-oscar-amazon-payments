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
http://docs.developer.amazonservices.com/en_US/apa_guide/APAGuide_GettingStarted.html.
Note that the website setup requires the "Allowed JavaScript origin" to be a HTTPS
URL, so you won't be able to test Amazon Payments integration with a site run using
the Django runserver command.

You will also need an Amazon MWS API key and secret key. These are used to 
interact with the Amazon MWS Off-Amazon Payments API to actually process the
payments. See http://docs.developer.amazonservices.com/en_US/off_amazon_payments/OffAmazonPayments_Overview.html

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

Automatic Payments
------------------
From http://docs.developer.amazonservices.com/en_US/pay_with_amazon_automatic_payments/APAGuide_Introduction.html:

*With the automatic payments feature, buyers can pre-authorize payments for 
future purchases. This enables you to charge a buyer’s Amazon Payments account 
on a regular basis for subscriptions and usage based billing without requiring 
the buyer to authorize a payment each time.*

Automatic payments are disabled by default. To enable such payments, override 
the Basket model in your oscar project to add a "has_subscriptions" property 
that returns True where appropriate. This has been done in the sandbox site, so
you will see the "Automatic payments" widget during checkout.
