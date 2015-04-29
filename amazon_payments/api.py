import datetime
import hmac
import hashlib
import base64
from urllib import urlencode, quote
from urlparse import urlparse
import logging
from decimal import Decimal

import requests

from bs4 import BeautifulSoup

logger = logging.getLogger("amazon_payments")

DEFAULT_API_URL = "https://mws.amazonservices.com/OffAmazonPayments/2013-01-01"


class AmazonPaymentsAPIError(Exception):
    pass


class AmazonPaymentsAPI(object):

    def __init__(self, access_key, secret_key, seller_id,
                 endpoint=DEFAULT_API_URL, version="2013-01-01", is_live=False,
                 exception_class=AmazonPaymentsAPIError):

        self.access_key = access_key
        self.secret_key = secret_key
        self.seller_id = seller_id
        self.endpoint = endpoint
        self.version = version
        self.is_live = is_live
        self.exception_class = exception_class

    def _quote(self, value):
        return quote(value).replace('%7E', '~')

    def _get_string_to_sign(self, data):
        """ Create the string to be used to calculate the signature. """
        url = urlparse(self.endpoint)
        params_string = urlencode(sorted(data.items())).replace('+', '%20')\
            .replace('%7E', '~')
        return "POST\n%s\n/%s\n%s" % (
            url.netloc,
            "/".join(map(self._quote, url.path.strip("/").split("/"))),
            params_string)

    def _calculate_signature(self, data):
        """ Calculates a HMAC-SHA signature for a request. """
        msg = self._get_string_to_sign(data)
        sig = hmac.new(self.secret_key, msg, hashlib.sha256).digest()
        return base64.encodestring(sig).strip()

    def _add_required_parameters(self, data):
        """ Adds parameters that are required for all API calls. """
        _data = {
            'AWSAccessKeyId': self.access_key,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': '2',
            'Version': self.version,
            'Timestamp': datetime.datetime.utcnow().strftime(
                "%Y-%m-%dT%H:%M:%SZ"),
            'SellerId': self.seller_id,
        }
        _data.update(data)
        _data["Signature"] = self._calculate_signature(_data)
        return _data

    def do_request(self, action, params={}, process=True, callback=None,
                   **kwargs):
        """
        Performs a call to the Amazon Payments API, then calls the
        callback function (if set) with 2 positional arguments:
        the raw request and the raw response.

        Returns a 2-tuple with:
        - a BeautifulSoup Tag object if process=True or the raw XML
          response if process=False
        - the result of the callback function if it was set, else None.
        """
        logger.info("Performing %s action" % action)
        params["Action"] = action
        params = self._add_required_parameters(params)
        logger.debug("Request data: %s" % params)
        kwargs["params"] = params
        response = requests.post(self.endpoint, **kwargs)
        logger.debug("Amazon response: \n%s", response.content)
        if callback:
            tx = callback(response.url, response.content)
        else:
            tx = None
        if process:
            try:
                value = self.process_response(response.content)
            except self.exception_class, e:
                logger.debug(e)
                raise
        else:
            value = response.content
        return value, tx

    def process_response(self, response):
        """
        Create a BeautifulSoup object from the XML response gotten from
        Amazon.
        """
        soup = BeautifulSoup(response, 'xml')
        if soup.ErrorResponse:
            error = soup.ErrorResponse.Error
            raise self.exception_class(error.Code.text, error.Message.text)
        elif response.startswith("InvalidOrderReferenceStatus"):
            # The error returned if trying Authorize action without
            # first doing ConfirmOrderReference action is not XML format
            raise self.exception_class("InvalidOrderReferenceStatus",
                                       response[28:])
        return soup

    def get_amazon_order_details(self, billing_agreement_id, access_token,
                                 has_subscriptions=False,
                                 validate_shipping_address=True,
                                 validate_payment_details=True,
                                 valid_shipping_countries=[], **kwargs):
        """
        Preforms a GetBillingAgreementDetails request, and checks if
        there the user has set a valid shipping address (if
        validate_shipping_address is True) and/or there is a valid
        payment method (if validate_payment_details is True).
        """
        # Cannot call do_request with process=False here
        kwargs.pop("process", None)
        response = self.do_request(
            "GetBillingAgreementDetails",
            {"AmazonBillingAgreementId": billing_agreement_id,
             "AddressConsentToken": access_token}, **kwargs)[0]
        amazon_order_details = response\
            .GetBillingAgreementDetailsResponse\
            .GetBillingAgreementDetailsResult\
            .BillingAgreementDetails
        constraints = amazon_order_details.Constraints
        errors = []
        if constraints:
            # Check relevant contraints based on the value of
            # validate_payment_details and validate_shipping_details,
            # and raise an error if it's necessary.
            for constraint in constraints.findAll("Constraint"):
                code = constraint.ConstraintID.text
                description = constraint.Description.text
                if validate_payment_details:
                    if code == "BuyerConsentNotSet":
                        if has_subscriptions:
                            # Automatic payments are needed for this order,
                            # but the user has not given consent.
                            errors.append(
                                "Please authorize us to charge future "
                                "payments to your Amazon account. This "
                                "is required as your order contains "
                                "subscription items.")
                        else:
                            continue
                    elif code == "PaymentPlanNotSet":
                        errors.append("Please select a payment method.")
                    elif code == "PaymentMethodNotAllowed":
                        errors.append(
                            "The payment method you've selected is not "
                            "allowed for this order. Please select "
                            "another payment method.")
                if validate_shipping_address:
                    if code == "ShippingAddressNotSet":
                        errors.append("Please select a shipping address.")
                if code not in ["BuyerConsentNotSet", "PaymentPlanNotSet",
                                "PaymentMethodNotAllowed",
                                "ShippingAddressNotSet"]:
                    errors.append(
                        "An error occurred when processing your order."
                        " Please try again later.")

                logger.debug("Amazon Payment Error: %s (%s)" % (
                    description, code))

        elif validate_shipping_address:
            # Check if the shipping country is one of the allowed
            # shipping countries
            country = amazon_order_details.Destination.PhysicalDestination\
                .CountryCode.text
            if country not in valid_shipping_countries:
                errors.append("Please select a different shipping address. "
                              "We currently don't ship to %s." % country)

        if errors:
            return False, errors
        return True, amazon_order_details

    def create_order_reference_id(self, billing_agreement_id, order_amount,
                                  currency, **kwargs):
        """
        Performs an "CreateOrderReferenceForId" API call and returns
        the created order reference ID.
        """
        # Cannot call do_request with process=False here
        kwargs.pop("process", None)
        response = self.do_request(
            "CreateOrderReferenceForId",
            {"Id": billing_agreement_id,
             "ConfirmNow": "true",
             "IdType": "BillingAgreement",
             "OrderReferenceAttributes.OrderTotal.Amount": order_amount,
             "OrderReferenceAttributes.OrderTotal.CurrencyCode": currency},
            **kwargs)[0]
        return response\
            .CreateOrderReferenceForIdResponse\
            .CreateOrderReferenceForIdResult\
            .OrderReferenceDetails\
            .AmazonOrderReferenceId.text

    def authorize(self, order_reference_id, auth_ref, order_amount, currency,
                  **kwargs):
        """
        Performs an "Authorize" API call and returns the authorization ID
        (Amazon's reference for the authorization) and the result
        of running the callback function if it was set.
        """
        # Cannot call do_request with process=False here
        kwargs.pop("process", None)
        response, tx = self.do_request(
            "Authorize",
            {"AmazonOrderReferenceId": order_reference_id,
             "AuthorizationReferenceId": auth_ref,
             "AuthorizationAmount.Amount": order_amount,
             "AuthorizationAmount.CurrencyCode": currency,
             "CaptureNow": "true",
             "TransactionTimeout": 0}, **kwargs)
        authorization_id = response\
            .AuthorizeResponse\
            .AuthorizeResult\
            .AuthorizationDetails\
            .AmazonAuthorizationId.text
        return authorization_id, tx

    def get_authorization_status(self, authorization_id, **kwargs):
        # Cannot call do_request with process=False here
        kwargs.pop("process", None)
        response = self.do_request(
            "GetAuthorizationDetails",
            {"AmazonAuthorizationId": authorization_id}, **kwargs)[0]
        amazon_auth_details = response\
            .GetAuthorizationDetailsResponse\
            .GetAuthorizationDetailsResult\
            .AuthorizationDetails
        auth_status = amazon_auth_details.AuthorizationStatus
        try:
            auth_amount = amazon_auth_details.CapturedAmount.Amount.text
        except AttributeError:
            auth_amount = None
        else:
            auth_amount = Decimal(auth_amount)
        return auth_status, auth_amount
