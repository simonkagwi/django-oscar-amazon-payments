from decimal import Decimal

from mock import patch, Mock
from bs4 import BeautifulSoup
from oscar.test.factories import create_product
from oscar.apps.order.models import Order
from oscar.apps.address.models import Country
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory
from django.conf import settings

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


class SaveToDBTestCase(APITestCase):

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


class ViewTestCase(APITestCase):
    def add_product_to_basket(self, price=Decimal('9.99')):
        product = create_product(price=price, num_in_stock=1)
        url = reverse('basket:add')
        self.client.post(url, {'product_id': product.pk, 'quantity': 1})

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()


class BasketViewTestCase(ViewTestCase):
    def test_required_vars_in_context(self):
        response = self.client.get(reverse('basket:summary'))
        assert (response.context["amazon_payments_seller_id"] ==
                settings.AMAZON_PAYMENTS_SELLER_ID)
        assert (response.context["amazon_payments_client_id"] ==
                settings.AMAZON_PAYMENTS_CLIENT_ID)
        assert (response.context["amazon_payments_is_live"] ==
                settings.AMAZON_PAYMENTS_IS_LIVE)


class OneStepCheckoutTestCase(ViewTestCase):
    login_url = reverse('checkout:amazon-payments-login-onestep')
    payment_url = reverse('checkout:amazon-payments-onestep')

    def test_empty_basket(self):
        """ Checks that an empty basket redirects back to basket page. """
        response = self.client.get(self.login_url)
        self.assertRedirects(response, reverse('basket:summary'))

    def test_no_billing_agreement_id_on_login(self):
        self.add_product_to_basket()
        response = self.client.get(self.login_url, follow=True)
        assert ("An error occurred during login. Please try again later." in
                response.content)
        self.assertRedirects(response, reverse('basket:summary'))

    def test_billing_agreement_id_set_on_login(self):
        self.add_product_to_basket()
        response = self.client.get(
            self.login_url, {"billing_agreement_id": "C01-9258635-6970398"})
        self.assertRedirects(response, self.payment_url)

    def test_required_vars_in_context_on_payment_page(self):
        self.add_product_to_basket()
        response = self.client.get(
            self.login_url, {"billing_agreement_id": "C01-9258635-6970398"},
            follow=True)
        assert (response.context["amazon_payments_seller_id"] ==
                settings.AMAZON_PAYMENTS_SELLER_ID)
        assert (response.context["amazon_payments_client_id"] ==
                settings.AMAZON_PAYMENTS_CLIENT_ID)
        assert (response.context["amazon_payments_is_live"] ==
                settings.AMAZON_PAYMENTS_IS_LIVE)
        # Also tests that an AmazonPaymentsSession was created for the basket
        basket = response.context["basket"]
        assert (
            response.context["amazon_payments_billing_agreement_id"] ==
            basket.amazonpaymentssession.billing_agreement_id)

    def test_error_handling(self):
        self.add_product_to_basket()
        self.client.get(
            self.login_url, {"billing_agreement_id": "C01-9258635-6970398"},
            follow=True)
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                RESPONSES["no_payment_method_and_shipping_address"])
            response = self.client.post(self.payment_url, {"place_order": "1"},
                                        follow=True)
            self.assertRedirects(response, self.payment_url)
            self.assertIn("Please select a payment method.", response.content)
            self.assertIn("Please select a shipping address.",
                          response.content)

    def test_successful_checkout(self):
        self.add_product_to_basket()
        self.client.get(
            self.login_url, {"billing_agreement_id": "C01-9258635-6970398"},
            follow=True)
        with patch('requests.post') as post:
            def side_effect(*args, **kwargs):
                action = kwargs["params"]["Action"]
                if action == "GetBillingAgreementDetails":
                    return self.create_mock_response(
                        RESPONSES["subscriptions_consent_given"])
                if action == "CreateOrderReferenceForId":
                    return self.create_mock_response(
                        RESPONSES["create_order_reference"])
                if action == "Authorize":
                    return self.create_mock_response(RESPONSES["authorize"])
                if action == "GetAuthorizationDetails":
                    return self.create_mock_response(
                        RESPONSES["authorization_details"])
                if action == "ConfirmBillingAgreement":
                    return self.create_mock_response(
                        RESPONSES["confirm_billing_agreement"])
                if action == "ValidateBillingAgreement":
                    return self.create_mock_response(
                        RESPONSES["validate_billing_agreement"])
                return self.create_mock_response("")
            post.side_effect = side_effect
            Country.objects.create(**{
                'iso_3166_1_a3': u'USA', 'iso_3166_1_a2': u'US',
                'name': u'UNITED STATES', 'display_order': 0,
                'printable_name': u'The United States of America',
                'iso_3166_1_numeric': 840, 'is_shipping_country': True})
            response = self.client.post(self.payment_url, {"place_order": "1"},
                                        follow=True)
            assert response.status_code == 200
            # self.assertRedirects(response, reverse("checkout:thank-you"))
            order = Order.objects.all()[0]
            assert order.shipping_address.first_name == "Simon Kagwi"
            assert order.shipping_address.line1 == "P,O Box 104147"
            assert order.shipping_address.line2 == "Line 2"
            assert order.shipping_address.line4 == "Beverly Hills"
            assert order.shipping_address.state == "CA"
            assert order.shipping_address.postcode == "90210"
            assert order.shipping_address.country.pk == "US"
            assert order.guest_email == "test@example.com"
            assert order.total_excl_tax == Decimal("9.99")
            assert unicode(order.shipping_address.phone_number) == "714538566"
            source = order.sources.all()[0]
            assert source.source_type.name == "Amazon Payments"
            assert source.amount_allocated == Decimal("9.99")
            assert source.amount_debited == Decimal("9.99")
            assert source.reference == "S01-6576755-3809974-A067494"


class MultiStepCheckoutTestCase(ViewTestCase):
    login_url = reverse('checkout:amazon-payments-login-onestep')
    shipping_address_url = reverse("checkout:amazon-payments-shipping-address")
    shipping_method_url = reverse("checkout:amazon-payments-shipping-method")
    payment_details_url = reverse("checkout:amazon-payments-payment-details")
    confirm_order_url = reverse("checkout:amazon-payments-preview")

    def _do_step_one(self):
        session = self.client.session
        session["checkout_data"].update({
            "guest": {"email": "test@example.com"}
        })
        session.save()

    def test_shipping_address_selected(self):
        self.add_product_to_basket()
        self.client.get(
            self.login_url, {"billing_agreement_id": "C01-9258635-6970398"},
            follow=True)
        self._do_step_one()
        assert "shipping" not in self.client.session["checkout_data"]
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                RESPONSES["subscriptions_consent_not_given"])
            response = self.client.post(self.shipping_address_url, follow=True)
            assert self.client.session["checkout_data"]["shipping"] == {
                'method_code': u'free-shipping',
                'new_address_fields': {
                    'first_name': 'Simon Kagwi',
                    'line1': 'P,O Box 104147',
                    'line2': 'Line 2',
                    'line4': 'Beverly Hills',
                    'postcode': '90210',
                    'state': 'CA',
                    'country_id': 'US',
                    'phone_number': '714538566',
                }
            }
            # We have only one shipping method so should redirect to
            # payment details page
            self.assertRedirects(response, self.payment_details_url)

    def test_error_in_shipping_address_selection(self):
        self.add_product_to_basket()
        self.client.get(
            self.login_url, {"billing_agreement_id": "C01-9258635-6970398"},
            follow=True)
        self._do_step_one()
        assert "shipping" not in self.client.session["checkout_data"]
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                RESPONSES["no_payment_method_and_shipping_address"])
            response = self.client.post(self.shipping_address_url, follow=True)
            assert "shipping" not in self.client.session["checkout_data"]
            assert response.status_code == 200
            assert "Where should we ship to?" in response.content

    def test_payment_method_selected(self):
        self.add_product_to_basket()
        self.client.get(
            self.login_url, {"billing_agreement_id": "C01-9258635-6970398"},
            follow=True)
        self._do_step_one()
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                RESPONSES["subscriptions_consent_not_given"])
            response = self.client.post(self.shipping_address_url, follow=True)
        with patch('requests.post') as post:
            def side_effect(*args, **kwargs):
                action = kwargs["params"]["Action"]
                if action == "GetBillingAgreementDetails":
                    return self.create_mock_response(
                        RESPONSES["subscriptions_consent_given"])
                if action == "CreateOrderReferenceForId":
                    return self.create_mock_response(
                        RESPONSES["create_order_reference"])
                return self.create_mock_response("")
            post.side_effect = side_effect
            Country.objects.create(**{
                'iso_3166_1_a3': u'USA', 'iso_3166_1_a2': u'US',
                'name': u'UNITED STATES', 'display_order': 0,
                'printable_name': u'The United States of America',
                'iso_3166_1_numeric': 840, 'is_shipping_country': True})
            response = self.client.post(self.payment_details_url, follow=True)
            assert response.status_code == 200
            self.assertRedirects(response, self.confirm_order_url)

    def test_error_in_payment_method_selection(self):
        self.add_product_to_basket()
        self.client.get(
            self.login_url, {"billing_agreement_id": "C01-9258635-6970398"},
            follow=True)
        self._do_step_one()
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                RESPONSES["subscriptions_consent_not_given"])
            response = self.client.post(self.shipping_address_url, follow=True)
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                RESPONSES["subscriptions_consent_not_given"])
            response = self.client.post(self.payment_details_url, follow=True)
            self.assertRedirects(response, self.payment_details_url)
            self.assertIn(
                "Please authorize us to charge future payments to your Amazon "
                "account. This is required as your order contains "
                "subscription items", response.content)

    def test_order_confirmation(self):
        self.add_product_to_basket()
        self.client.get(
            self.login_url, {"billing_agreement_id": "C01-9258635-6970398"},
            follow=True)
        self._do_step_one()
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                RESPONSES["subscriptions_consent_not_given"])
            self.client.post(self.shipping_address_url, follow=True)
        with patch('requests.post') as post:
            def side_effect(*args, **kwargs):
                action = kwargs["params"]["Action"]
                if action == "GetBillingAgreementDetails":
                    return self.create_mock_response(
                        RESPONSES["subscriptions_consent_given"])
                if action == "CreateOrderReferenceForId":
                    return self.create_mock_response(
                        RESPONSES["create_order_reference"])
                if action == "Authorize":
                    return self.create_mock_response(RESPONSES["authorize"])
                if action == "GetAuthorizationDetails":
                    return self.create_mock_response(
                        RESPONSES["authorization_details"])
                if action == "ConfirmBillingAgreement":
                    return self.create_mock_response(
                        RESPONSES["confirm_billing_agreement"])
                if action == "ValidateBillingAgreement":
                    return self.create_mock_response(
                        RESPONSES["validate_billing_agreement"])
                return self.create_mock_response("")
            post.side_effect = side_effect
            Country.objects.create(**{
                'iso_3166_1_a3': u'USA', 'iso_3166_1_a2': u'US',
                'name': u'UNITED STATES', 'display_order': 0,
                'printable_name': u'The United States of America',
                'iso_3166_1_numeric': 840, 'is_shipping_country': True})
            response = self.client.post(
                self.confirm_order_url, {"action": "place_order"}, follow=True)
            assert response.status_code == 200
            # self.assertRedirects(response, self.confirm_order_url)
            order = Order.objects.all()[0]
            assert order.shipping_address.first_name == "Simon Kagwi"
            assert order.shipping_address.line1 == "P,O Box 104147"
            assert order.shipping_address.line2 == "Line 2"
            assert order.shipping_address.line4 == "Beverly Hills"
            assert order.shipping_address.state == "CA"
            assert order.shipping_address.postcode == "90210"
            assert order.shipping_address.country.pk == "US"
            assert order.guest_email == "test@example.com"
            assert order.total_excl_tax == Decimal("9.99")
            assert unicode(order.shipping_address.phone_number) == "714538566"
            source = order.sources.all()[0]
            assert source.source_type.name == "Amazon Payments"
            assert source.amount_allocated == Decimal("9.99")
            assert source.amount_debited == Decimal("9.99")
            assert source.reference == "S01-6576755-3809974-A067494"

    def test_error_in_order_confirmation(self):
        self.add_product_to_basket()
        self.client.get(
            self.login_url, {"billing_agreement_id": "C01-9258635-6970398"},
            follow=True)
        self._do_step_one()
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                RESPONSES["subscriptions_consent_not_given"])
            response = self.client.post(self.shipping_address_url, follow=True)
        with patch('requests.post') as post:
            post.return_value = self.create_mock_response(
                RESPONSES["subscriptions_consent_not_given"])
            response = self.client.post(
                self.confirm_order_url, {"action": "place_order"}, follow=True)
            self.assertRedirects(response, self.confirm_order_url)
            self.assertIn(
                "Please authorize us to charge future payments to your Amazon "
                "account. This is required as your order contains "
                "subscription items", response.content)
