import logging

from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.conf import settings
from django.utils.translation import ugettext as _
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.views import generic
from django import http

from oscar.core.loading import get_class, get_model

from oscar.apps.checkout.views import (
    PaymentDetailsView, ShippingMethodView, PaymentMethodView, IndexView)

from models import AmazonPaymentsSession
from amazon_payments import AmazonPaymentsAPI, AmazonPaymentsAPIError

logger = logging.getLogger("amazon_payments")

Country = get_model('address', 'country')
ShippingAddress = get_model('order', 'ShippingAddress')
Source = get_model('payment', 'Source')
SourceType = get_model('payment', 'SourceType')

Repository = get_class('shipping.repository', 'Repository')
UnableToTakePayment = get_class('payment.exceptions', 'UnableToTakePayment')
PaymentError = get_class('payment.exceptions', 'PaymentError')
CheckoutSessionMixin = get_class('checkout.session', 'CheckoutSessionMixin')
FailedPreCondition = get_class('checkout.exceptions', 'FailedPreCondition')
NoShippingRequired = get_class('shipping.methods', 'NoShippingRequired')


class AmazonLoginRedirectView(generic.RedirectView):
    """
    Redirects to the next step after a user clicks on the
    'Pay with Amazon' button.
    """

    permanent = False
    _redirect_url = reverse_lazy('checkout:amazon-payments-index')

    def get_redirect_url(self, **kwargs):
        """
        Gets the billing agreement ID and access token created when the
        user clicks on the 'Pay with Amazon' button and saves them to the DB,
        then redirects to the URL in self._redirect_url.
        """
        billing_agreement_id = self.request.GET.get('billing_agreement_id')
        access_token = self.request.GET.get('access_token')
        if billing_agreement_id:
            try:
                session = self.request.basket.amazonpaymentssession
            except AmazonPaymentsSession.DoesNotExist:
                session = AmazonPaymentsSession(basket=self.request.basket)
            session.billing_agreement_id = billing_agreement_id
            session.access_token = access_token
            session.save()
        else:
            messages.error(self.request,
                           _("An error occurred during login. Please try again"
                             " later."))
            return reverse('basket:summary')
        return self._redirect_url


class AmazonCheckoutView(object):

    def init_amazon_payments(self):
        """
        Creates a `session` and `api` variables to be used for interacting
        with the Amazon Payments API. Returns True if successful, else
        returns False
        """
        try:
            self.session = self.request.basket.amazonpaymentssession
        except (AmazonPaymentsSession.DoesNotExist, AttributeError):
            return False
        logger.debug("Amazon Billing Agreement ID: %s" % (
            self.session.billing_agreement_id))
        self.api = AmazonPaymentsAPI(
            settings.AMAZON_PAYMENTS_ACCESS_KEY,
            settings.AMAZON_PAYMENTS_SECRET_KEY,
            settings.AMAZON_PAYMENTS_SELLER_ID,
            settings.AMAZON_PAYMENTS_API_ENDPOINT,
            settings.AMAZON_PAYMENTS_API_VERSION,
            settings.AMAZON_PAYMENTS_IS_LIVE,
        )
        return True

    def save_to_db_callback(self, raw_request, raw_response):
        return self.session.transactions.create(
            request=raw_request, response=raw_response)

    def get_amazon_payments_context_vars(self):
        """
        Returns a dict with all the Amazon Payments data that would
        be needed in a template in order to display widgets.
        """
        return {
            'amazon_payments_seller_id': settings.AMAZON_PAYMENTS_SELLER_ID,
            'amazon_payments_client_id': settings.AMAZON_PAYMENTS_CLIENT_ID,
            'amazon_payments_is_live': settings.AMAZON_PAYMENTS_IS_LIVE,
            'amazon_payments_billing_agreement_id': (
                self.session.billing_agreement_id),
        }

    def get_amazon_order_details(self, request, **kwargs):
        """
        Preforms a GetBillingAgreementDetails request, and checks if
        there the user has set a valid shipping address (if
        validate_shipping_address is True) and/or there is a valid
        payment method (if validate_payment_details is True).
        """
        if kwargs.get("validate_shipping_address", True):
            kwargs["valid_shipping_countries"] = Country.objects\
                .filter(is_shipping_country=True)\
                .values_list("iso_3166_1_a2", flat=True)
        kwargs["callback"] = self.save_to_db_callback
        success, result = self.api.get_amazon_order_details(
            self.session.billing_agreement_id, self.session.access_token,
            getattr(request.basket, "has_subscriptions", False), **kwargs)
        if success:
            return result
        for error in result:
            messages.error(request, _(error))

    def check_user_email_is_captured(self, request):
        """
        Overrides Oscar's pre-condition to change URL to redirect
        to if condition not satisfied.
        """
        if not request.user.is_authenticated() \
                and not self.checkout_session.get_guest_email():
            raise FailedPreCondition(
                url=reverse('checkout:amazon-payments-index'),
                message=_(
                    "Please either sign in or enter your email address")
            )

    def check_basket_requires_shipping(self, request):
        """
        Overrides Oscar's pre-condition to change URL to redirect
        to if condition not satisfied.
        """
        # Check to see that a shipping address is actually required.  It may
        # not be if the basket is purely downloads
        if not request.basket.is_shipping_required():
            raise FailedPreCondition(
                url=reverse('checkout:amazon-payments-shipping-method'),
                message=_(
                    "Your basket does not require a shipping"
                    "address to be submitted")
            )

    def check_shipping_data_is_captured(self, request):
        """
        Overrides Oscar's pre-condition to change URL to redirect
        to if condition not satisfied.
        """
        if not request.basket.is_shipping_required():
            return

        # Check that shipping address has been completed
        if not self.checkout_session.is_shipping_address_set():
            raise FailedPreCondition(
                url=reverse('checkout:amazon-payments-shipping-address'),
                message=_("Please choose a shipping address")
            )

        # Check that shipping method has been set
        if not self.checkout_session.is_shipping_method_set(
                self.request.basket):
            raise FailedPreCondition(
                url=reverse('checkout:amazon-payments-shipping-method'),
                message=_("Please choose a shipping method")
            )


class AmazonPaymentsIndexView(IndexView):

    success_url = reverse_lazy('checkout:amazon-payments-shipping-address')


class AmazonShippingAddressView(AmazonCheckoutView, CheckoutSessionMixin,
                                generic.TemplateView):

    template_name = 'amazon_payments/shipping_address.html'
    pre_conditions = ('check_basket_is_not_empty',
                      'check_basket_is_valid',
                      'check_user_email_is_captured',
                      'check_basket_requires_shipping')

    def dispatch(self, *args, **kwargs):
        if not self.init_amazon_payments():
            messages.error(self.request,
                           _("Please click on the 'Pay with Amazon' button to "
                             "begin the Amazon checkout process."))
            return redirect('basket:summary')
        return super(AmazonShippingAddressView, self).dispatch(
            *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs = super(AmazonShippingAddressView, self).get_context_data(
            **kwargs)
        kwargs.update(self.get_amazon_payments_context_vars())
        return kwargs

    def get(self, request, **kwargs):
        ctx = self.get_context_data(**kwargs)
        return self.render_to_response(ctx)

    def post(self, request, *args, **kwargs):
        amazon_order_details = self.get_amazon_order_details(
            request, validate_payment_details=False)
        if amazon_order_details:
            # Get shipping address
            amazon_shipping_address = amazon_order_details.Destination\
                .PhysicalDestination
            address_fields = dict(
                first_name=amazon_shipping_address.Name.text,
                line1=amazon_shipping_address.AddressLine1.text,
                line4=amazon_shipping_address.City.text,
                state=amazon_shipping_address.StateOrRegion.text,
                postcode=amazon_shipping_address.PostalCode.text,
                country_id=amazon_shipping_address.CountryCode.text,
            )
            if amazon_shipping_address.AddressLine2:
                address_fields["line2"] = amazon_shipping_address.AddressLine2\
                    .text
            self.checkout_session.ship_to_new_address(address_fields)
            return redirect("checkout:amazon-payments-shipping-method")
        ctx = self.get_context_data()
        return self.render_to_response(ctx)


class AmazonShippingMethodView(AmazonCheckoutView, ShippingMethodView):

    def get(self, request, *args, **kwargs):
        # These pre-conditions can't easily be factored out into the normal
        # pre-conditions as they do more than run a test and then raise an
        # exception if it fails.

        # Check that shipping is required at all
        if not request.basket.is_shipping_required():
            # No shipping required - we store a special code to indicate so.
            self.checkout_session.use_shipping_method(
                NoShippingRequired().code)
            return self.get_success_response()

        # Check that shipping address has been completed
        if not self.checkout_session.is_shipping_address_set():
            messages.error(request, _("Please choose a shipping address"))
            return http.HttpResponseRedirect(
                reverse('checkout:amazon-payments-shipping-address'))

        # Save shipping methods as instance var as we need them both here
        # and when setting the context vars.
        self._methods = self.get_available_shipping_methods()
        if len(self._methods) == 0:
            # No shipping methods available for given address
            messages.warning(request, _(
                "Shipping is unavailable for your chosen address - please "
                "choose another"))
            return http.HttpResponseRedirect(
                reverse('checkout:amazon-payments-shipping-address'))
        elif len(self._methods) == 1:
            # Only one shipping method - set this and redirect onto the next
            # step
            self.checkout_session.use_shipping_method(self._methods[0].code)
            return self.get_success_response()

        # Must be more than one available shipping method, we present them to
        # the user to make a choice.
        return super(ShippingMethodView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Need to check that this code is valid for this user
        method_code = request.POST.get('method_code', None)
        is_valid = False
        for method in self.get_available_shipping_methods():
            if method.code == method_code:
                is_valid = True
        if not is_valid:
            messages.error(request, _("Your submitted shipping method is not"
                                      " permitted"))
            return http.HttpResponseRedirect(
                reverse('checkout:amazon-payments-shipping-method'))

        # Save the code for the chosen shipping method in the session
        # and continue to the next step.
        self.checkout_session.use_shipping_method(method_code)
        return self.get_success_response()

    def get_success_response(self):
        return redirect(reverse('checkout:amazon-payments-payment-method'))


class AmazonPaymentMethodView(AmazonCheckoutView, PaymentMethodView):

    def get_success_response(self):
        return redirect(reverse('checkout:amazon-payments-payment-details'))


class BaseAmazonPaymentDetailsView(AmazonCheckoutView, PaymentDetailsView):

    def dispatch(self, *args, **kwargs):
        if not self.init_amazon_payments():
            messages.error(self.request,
                           _("Please click on the 'Pay with Amazon' button to "
                             "begin the Amazon checkout process."))
            return redirect('basket:summary')
        return super(BaseAmazonPaymentDetailsView, self).dispatch(
            *args, **kwargs)

    def set_order_details(self, total, order_id=None):
        data = {
            "AmazonOrderReferenceId": self.session.order_reference_id,
            "OrderReferenceAttributes.OrderTotal.Amount": total,
            "OrderReferenceAttributes.OrderTotal.CurrencyCode": (
                settings.AMAZON_PAYMENTS_CURRENCY)
        }
        if order_id:
            data[
                "OrderReferenceAttributes.SellerOrderAttributes.SellerOrderId"
            ] = order_id
        self.api.do_request("SetOrderReferenceDetails", data,
                            False, self.save_to_db_callback)

    def handle_automatic_payments_agreement(self):
        """
        Confirms and validates billing agreement to enable automatic payments.
        """
        try:
            self.api.do_request(
                "ConfirmBillingAgreement",
                {"AmazonBillingAgreementId": (
                    self.session.billing_agreement_id)},
                False, self.save_to_db_callback)
        except self.api.exception_class, e:
            if e.args[0] != "BillingAgreementConstraintsExist":
                raise
        else:
            self.api.do_request(
                "ValidateBillingAgreement",
                {"AmazonBillingAgreementId": (
                    self.session.billing_agreement_id)},
                False, self.save_to_db_callback)

    def handle_payment(self, order_number, total, **kwargs):
        self.set_order_details(total.incl_tax, order_number)
        auth_attempt = self.session.auth_attempts.create()
        auth_ref = "%s-%s" % (auth_attempt.pk,
                              auth_attempt.created_at.strftime("%s"))
        try:
            authorization_id, tx = self.api.authorize(
                self.session.order_reference_id, auth_ref, total.incl_tax,
                settings.AMAZON_PAYMENTS_CURRENCY,
                callback=self.save_to_db_callback)
        except self.api.exception_class, e:
            raise PaymentError(*e.args)
        auth_attempt.authorization_id = authorization_id
        auth_attempt.transaction = tx
        auth_attempt.save()
        try:
            auth_status, captured_amount = self.api.get_authorization_status(
                auth_attempt.authorization_id,
                callback=self.save_to_db_callback)
        except self.api.exception_class, e:
            raise PaymentError(*e.args)
        if auth_status.State.text == "Declined":
            if auth_status.ReasonCode.text in ["InvalidPaymentMethod",
                                               "AmazonRejected"]:
                raise UnableToTakePayment(_(
                    "The payment was rejected by Amazon. Please update the "
                    "payment method, or choose another method."))
            else:
                raise PaymentError(auth_status.State.text,
                                   auth_status.ReasonCode.text)
        elif (auth_status.State.text == "Closed" and
              auth_status.ReasonCode.text != "MaxCapturesProcessed"):
            raise PaymentError(auth_status.State.text,
                               auth_status.ReasonCode.text)
        source_type = SourceType.objects.get_or_create(
            name="Amazon Payments")[0]
        source = Source(
            source_type=source_type,
            currency="USD",
            amount_allocated=captured_amount,
            amount_debited=captured_amount,
            reference=auth_attempt.authorization_id)
        self.add_payment_source(source)
        self.add_payment_event("Purchase", total.incl_tax,
                               reference=auth_attempt.authorization_id)

    def handle_successful_order(self, order):
        response = super(BaseAmazonPaymentDetailsView, self)\
            .handle_successful_order(order)
        if getattr(self.request.basket, "has_subscriptions", False):
            # Set up automatic future payments. Should not affect current
            # order.
            try:
                self.handle_automatic_payments_agreement()
            except self.api.exception_class, e:
                logger.error(
                    "Unable to set up automatic payments for order %s: %s" % (
                        order, e))
        self.session.order = order
        self.session.save()
        return response


class AmazonPaymentDetailsView(BaseAmazonPaymentDetailsView):

    template_name = 'amazon_payments/payment_details.html'
    template_name_preview = 'amazon_payments/preview.html'

    def get_context_data(self, **kwargs):
        kwargs = super(AmazonPaymentDetailsView, self).get_context_data(
            **kwargs)
        kwargs.update(self.get_amazon_payments_context_vars())
        return kwargs

    def post(self, request, *args, **kwargs):
        if request.POST.get('action', '') == 'place_order':
            return self.handle_place_order_submission(request)
        return self.handle_payment_details_submission(request)

    def handle_payment_details_submission(self, request):
        # Check if shipping address and payment method have been selected
        amazon_order_details = self.get_amazon_order_details(self.request)
        if not amazon_order_details:
            return redirect("checkout:amazon-payments-payment-details")
        if not self.session.order_reference_id:
            basket = self.request.basket
            shipping_address = self.get_shipping_address(basket)
            shipping_method = self.get_shipping_method(
                basket, shipping_address)
            total = self.get_order_totals(
                basket, shipping_method=shipping_method)
            try:
                order_reference_id = self.api.create_order_reference_id(
                    self.session.billing_agreement_id, total.incl_tax,
                    settings.AMAZON_PAYMENTS_CURRENCY,
                    callback=self.save_to_db_callback)
            except self.api.exception_class:
                messages.error(self.request, _(
                    "An error occurred when processing your payment. "
                    "Please try again later."))
                return redirect("checkout:amazon-payments-payment-details")
            self.session.order_reference_id = order_reference_id
            self.session.save()
        return redirect("checkout:amazon-payments-preview")

    def handle_place_order_submission(self, request):
        amazon_order_details = self.get_amazon_order_details(self.request)
        if not amazon_order_details:
            return redirect("checkout:amazon-payments-preview")
        return super(AmazonPaymentDetailsView, self)\
            .handle_place_order_submission(request)


# VIEWS FOR ONE-STEP CHECKOUT
class AmazonOneStepLoginRedirectView(AmazonLoginRedirectView):
    _redirect_url = reverse_lazy('checkout:amazon-payments-onestep')


class AmazonOneStepPaymentDetailsView(BaseAmazonPaymentDetailsView):

    template_name = 'amazon_payments/onestep_checkout.html'
    pre_conditions = (
        'check_basket_is_not_empty',
        'check_basket_is_valid',)

    def get_default_shipping_method(self, basket):
        return Repository().get_default_shipping_method(
            user=self.request.user, basket=self.request.basket,
            request=self.request)

    def get(self, request, *args, **kwargs):
        if request.basket.is_empty:
            messages.error(request, _("You need to add some items to your"
                                      " basket to checkout"))
            return redirect('basket:summary')
        context = self.get_context_data()
        return render_to_response(self.template_name, context)

    def handle_payment(self, order_number, total, **kwargs):
        if not self.session.order_reference_id:
            try:
                order_reference_id = self.api.create_order_reference_id(
                    self.session.billing_agreement_id, total.incl_tax,
                    settings.AMAZON_PAYMENTS_CURRENCY,
                    callback=self.save_to_db_callback)
            except self.api.exception_class, e:
                raise PaymentError(*e.args)
            self.session.order_reference_id = order_reference_id
            self.session.save()
        # We've already checked for valid shipping address and
        # payment details in the post() method
        super(AmazonOneStepPaymentDetailsView, self).handle_payment(
            order_number, total, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.basket.is_empty:
            msg = _("You need to add some items to your basket to check out.")
        elif 'place_order' in request.POST:
            try:
                amazon_order_details = self.get_amazon_order_details(request)
            except AmazonPaymentsAPIError, e:
                logger.debug(unicode(e))
                if e.args[0] == "InvalidAddressConsentToken":
                    msg = _("Your session has expired. Please sign in again by"
                            " clicking on the 'Pay with Amazon' button.")
                else:
                    msg = _("Sorry, there's a problem processing your order "
                            "via Amazon. Please try again later.")
                messages.error(request, msg)
                return redirect("basket:summary")
            if not amazon_order_details:
                return redirect(request.path)
            # Get shipping address
            amazon_shipping_address = amazon_order_details.Destination\
                .PhysicalDestination
            shipping_address = ShippingAddress(
                first_name=amazon_shipping_address.Name.text,
                line1=amazon_shipping_address.AddressLine1.text,
                line4=amazon_shipping_address.City.text,
                state=amazon_shipping_address.StateOrRegion.text,
                postcode=amazon_shipping_address.PostalCode.text,
                country=Country.objects.get(
                    iso_3166_1_a2=amazon_shipping_address.CountryCode.text),
            )
            if amazon_shipping_address.AddressLine2:
                shipping_address.line2 = amazon_shipping_address.AddressLine2\
                    .text
            shipping_method = self.get_default_shipping_method(
                self.request.basket)
            order_total = self.get_order_totals(
                self.request.basket,
                shipping_method=shipping_method)
            submission = self.build_submission(
                user=request.user, shipping_method=shipping_method,
                order_total=order_total, shipping_address=shipping_address)
            if (not request.user.is_authenticated() and
                    not self.checkout_session.get_guest_email()):
                submission['order_kwargs']['guest_email'] = (
                    amazon_order_details.Buyer.Email.text)
            result = self.submit(**submission)
            return result

        amazon_error_code = request.POST.get("amazon_error_code")
        amazon_error_message = request.POST.get("amazon_error_message")
        if amazon_error_code in ["BuyerSessionExpired", "BuyerNotAssociated",
                                 "StaleOrderReference"]:
            msg = ("Your session has expired. Please sign in again by "
                   "clicking on the 'Pay with Amazon' button.")
        else:
            msg = ("Sorry, there's a problem processing your order via Amazon."
                   " Please try again later.")
        if amazon_error_code or amazon_error_message:
            logger.debug("Amazon widget error response: %s (code: %s)" % (
                amazon_error_code, amazon_error_message))
        logger.debug(msg)
        messages.error(request, _(msg))
        return redirect("basket:summary")

    def get_context_data(self, **kwargs):
        kwargs = RequestContext(self.request, kwargs)
        kwargs['basket'] = self.request.basket
        method = self.get_default_shipping_method(self.request.basket)
        kwargs['shipping_method'] = method
        kwargs['order_total'] = self.get_order_totals(
            self.request.basket, method)
        kwargs.update(self.get_amazon_payments_context_vars())
        return kwargs

    def render_preview(self, request, **kwargs):
        self.preview = False
        ctx = self.get_context_data(**kwargs)
        return self.render_to_response(ctx)
