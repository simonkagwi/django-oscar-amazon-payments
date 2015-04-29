from decimal import Decimal

from mock import patch, Mock
from bs4 import BeautifulSoup

from unittest import TestCase

from amazon_payments import AmazonPaymentsAPI
from api_responses import RESPONSES


class APITestCase(TestCase):

    def setUp(self):
        self.api = AmazonPaymentsAPI("access_key", "secret_key", "seller_id")

    def create_mock_response(self, body, status_code=200):
        response = Mock()
        response.content = body
        response.status_code = status_code
        return response


def SaveToDBTestCase(APITestCase):

    def setUp(self):
        super(SaveToDBTestCase, self).setUp()
        self.db_callback_list = []

    def save_to_db_callback(self, raw_request, raw_response):
        self.db_callback_list.append((raw_request, raw_response))
        return "saved"

    def test_callback_called(self):
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response("xml response")
            self.db_callback_list = []
            response, tx = self.api.do_request(
                "GetOrderReferenceDetails", {}, False,
                callback=self.save_to_db_callback)
            self.assertEqual(tx, "saved")
            self.assertEqual(len(self.db_callback_list), 1)


class GetAgreementDetailsTestCase(APITestCase):
    """ Tests for the get_amazon_order_details method. """

    def test_missing_payment_method_and_address(self):
        """
        Check that error messages are returned if the user has not
        selected a payment method and shipping address and both
        validate_shipping_address and validate_payment_method are set.
        """
        response_xml = RESPONSES["no_payment_method_and_shipping_address"]
        response = self.create_mock_response(response_xml)
        with patch('requests.post') as post:
            post.return_value = response
            result = self.api.get_amazon_order_details(
                "billing_agreement_id", "access_token")
            self.assertFalse(result[0])
            self.assertIn("Please select a payment method.", result[1])
            self.assertIn("Please select a shipping address.", result[1])

    def test_automatic_payments_consent_not_needed(self):
        """
        Check that the method returns True and the BeautifulSoup object
        for the "BillingAgreementDetails" tag when the user's consent is
        not needed for automatic payments / subscriptions.
        """
        response_xml = RESPONSES["subscriptions_consent_not_given"]
        response = self.create_mock_response(response_xml)
        with patch('requests.post') as post:
            post.return_value = response
            result = self.api.get_amazon_order_details(
                "billing_agreement_id", "access_token")
            amazon_order_details = BeautifulSoup(response_xml, "xml").find(
                "BillingAgreementDetails")
            self.assertEqual(result, (True, amazon_order_details))

    def test_automatic_payments_consent_needed(self):
        """
        Check that the method returns False and an error message if
        has_subscriptions = True and the user has not given consent.
        """
        response_xml = RESPONSES["subscriptions_consent_not_given"]
        response = self.create_mock_response(response_xml)
        with patch('requests.post') as post:
            post.return_value = response
            result = self.api.get_amazon_order_details(
                "billing_agreement_id", "access_token", has_subscriptions=True)
            self.assertFalse(result[0])
            self.assertIsInstance(result[1], list)
            error = ("Please authorize us to charge future payments to your "
                     "Amazon account. This is required as your order contains "
                     "subscription items.")
            self.assertIn(error, result[1])


class PaymentAuthorizationTestCase(APITestCase):

    def test_create_order_reference_id(self):
        response_xml = RESPONSES["create_order_reference"]
        response = self.create_mock_response(response_xml)
        with patch('requests.post') as post:
            post.return_value = response
            result = self.api.create_order_reference_id(
                "billing_agreement_id", "9.99", "USD")
            self.assertEqual(result, "S01-6576755-3809974")

    def test_payment_authorization(self):
        response_xml = RESPONSES["authorize"]
        response = self.create_mock_response(response_xml)
        with patch('requests.post') as post:
            post.return_value = response
            self.db_callback_list = []
            result = self.api.authorize(
                "order_reference_id", "auth_ref", "9.99", "USD")
            self.assertEqual(result, ("S01-6576755-3809974-A067494", None))

    def test_get_authorization_details(self):
        response_xml = RESPONSES["authorization_details"]
        response = self.create_mock_response(response_xml)
        with patch('requests.post') as post:
            post.return_value = response
            result = self.api.get_authorization_status("authorization_id")
            auth_status = BeautifulSoup(response_xml, "xml").find(
                "AuthorizationStatus")
            self.assertEqual(result, (auth_status, Decimal("9.99")))
