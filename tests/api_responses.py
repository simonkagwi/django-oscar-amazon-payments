RESPONSES = {
    "no_payment_method_and_shipping_address": """
    <GetBillingAgreementDetailsResponse xmlns="http://mws.amazonservices.com/schema/OffAmazonPayments/2013-01-01">
      <GetBillingAgreementDetailsResult>
        <BillingAgreementDetails>
          <BillingAgreementLimits>
            <AmountLimitPerTimePeriod>
              <Amount>500</Amount>
              <CurrencyCode>USD</CurrencyCode>
            </AmountLimitPerTimePeriod>
            <TimePeriodEndDate>2015-04-01T00:00:00Z</TimePeriodEndDate>
            <TimePeriodStartDate>2015-03-01T00:00:00Z</TimePeriodStartDate>
            <CurrentRemainingBalance>
              <Amount>500.00</Amount>
              <CurrencyCode>USD</CurrencyCode>
            </CurrentRemainingBalance>
          </BillingAgreementLimits>
          <Constraints>
            <Constraint>
              <ConstraintID>BuyerConsentNotSet</ConstraintID>
              <Description>The buyer has not given consent for this billing agreement.</Description>
            </Constraint>
            <Constraint>
              <ConstraintID>ShippingAddressNotSet</ConstraintID>
              <Description>The buyer has not selected a shipping address from the Amazon AddressBook widget.</Description>
            </Constraint>
            <Constraint>
              <ConstraintID>PaymentPlanNotSet</ConstraintID>
              <Description>The buyer has not been able to select a Payment method for the given Billing Agreement.</Description>
            </Constraint>
          </Constraints>
          <BillingAgreementConsent>false</BillingAgreementConsent>
          <BillingAgreementStatus>
            <State>Draft</State>
          </BillingAgreementStatus>
          <AmazonBillingAgreementId>C01-9258635-6970398</AmazonBillingAgreementId>
          <SellerBillingAgreementAttributes/>
          <ReleaseEnvironment>Sandbox</ReleaseEnvironment>
          <Buyer>
            <Email>thesimon.py@gmail.com</Email>
            <Name>Simon</Name>
          </Buyer>
          <CreationTimestamp>2015-03-20T16:43:55.286Z</CreationTimestamp>
        </BillingAgreementDetails>
      </GetBillingAgreementDetailsResult>
      <ResponseMetadata>
        <RequestId>d8b1ae53-1760-4ad3-b8ca-180fc4141cf3</RequestId>
      </ResponseMetadata>
    </GetBillingAgreementDetailsResponse>""",
    "subscriptions_consent_given": """
    <GetBillingAgreementDetailsResponse xmlns="http://mws.amazonservices.com/schema/OffAmazonPayments/2013-01-01">
      <GetBillingAgreementDetailsResult>
        <BillingAgreementDetails>
          <AmazonBillingAgreementId>C01-9258635-6970398</AmazonBillingAgreementId>
          <BillingAgreementStatus>
            <State>Draft</State>
          </BillingAgreementStatus>
          <BillingAgreementConsent>true</BillingAgreementConsent>
          <Destination>
            <DestinationType>Physical</DestinationType>
            <PhysicalDestination>
              <StateOrRegion>CA</StateOrRegion>
              <Phone>714538566</Phone>
              <City>Beverly Hills</City>
              <CountryCode>US</CountryCode>
              <PostalCode>90210</PostalCode>
              <Name>Simon Kagwi</Name>
              <AddressLine1>P,O Box 104147</AddressLine1>
              <AddressLine2>Line 2</AddressLine2>
            </PhysicalDestination>
          </Destination>
          <SellerBillingAgreementAttributes/>
          <Buyer>
            <Name>Simon</Name>
            <Email>test@example.com</Email>
          </Buyer>
          <ReleaseEnvironment>Sandbox</ReleaseEnvironment>
          <CreationTimestamp>2016-11-26T16:05:22.431Z</CreationTimestamp>
          <BillingAgreementLimits>
            <TimePeriodStartDate>2016-11-01T00:00:00Z</TimePeriodStartDate>
            <CurrentRemainingBalance>
              <CurrencyCode>USD</CurrencyCode>
              <Amount>500.00</Amount>
            </CurrentRemainingBalance>
            <AmountLimitPerTimePeriod>
              <CurrencyCode>USD</CurrencyCode>
              <Amount>500</Amount>
            </AmountLimitPerTimePeriod>
            <TimePeriodEndDate>2016-12-01T00:00:00Z</TimePeriodEndDate>
          </BillingAgreementLimits>
        </BillingAgreementDetails>
      </GetBillingAgreementDetailsResult>
      <ResponseMetadata>
        <RequestId>187b2710-0c69-4782-992d-5402a8d11d29</RequestId>
      </ResponseMetadata>
    </GetBillingAgreementDetailsResponse>
    """,
    "subscriptions_consent_not_given": """
    <GetBillingAgreementDetailsResponse xmlns="http://mws.amazonservices.com/schema/OffAmazonPayments/2013-01-01">
      <GetBillingAgreementDetailsResult>
        <BillingAgreementDetails>
          <BillingAgreementLimits>
            <AmountLimitPerTimePeriod>
              <Amount>500</Amount>
              <CurrencyCode>USD</CurrencyCode>
            </AmountLimitPerTimePeriod>
            <TimePeriodEndDate>2015-04-01T00:00:00Z</TimePeriodEndDate>
            <TimePeriodStartDate>2015-03-01T00:00:00Z</TimePeriodStartDate>
            <CurrentRemainingBalance>
              <Amount>500.00</Amount>
              <CurrencyCode>USD</CurrencyCode>
            </CurrentRemainingBalance>
          </BillingAgreementLimits>
          <Constraints>
            <Constraint>
              <ConstraintID>BuyerConsentNotSet</ConstraintID>
              <Description>The buyer has not given consent for this billing agreement.</Description>
            </Constraint>
          </Constraints>
          <BillingAgreementConsent>false</BillingAgreementConsent>
          <AmazonBillingAgreementId>C01-9258635-6970398</AmazonBillingAgreementId>
          <BillingAgreementStatus>
            <State>Draft</State>
          </BillingAgreementStatus>
          <SellerBillingAgreementAttributes/>
          <Destination>
            <DestinationType>Physical</DestinationType>
            <PhysicalDestination>
              <Phone>714538566</Phone>
              <PostalCode>90210</PostalCode>
              <Name>Simon Kagwi</Name>
              <CountryCode>US</CountryCode>
              <StateOrRegion>CA</StateOrRegion>
              <AddressLine2>Line 2</AddressLine2>
              <AddressLine1>P,O Box 104147</AddressLine1>
              <City>Beverly Hills</City>
            </PhysicalDestination>
          </Destination>
          <ReleaseEnvironment>Sandbox</ReleaseEnvironment>
          <Buyer>
            <Email>test@example.com</Email>
            <Name>Simon</Name>
          </Buyer>
          <CreationTimestamp>2015-03-20T13:47:53.169Z</CreationTimestamp>
        </BillingAgreementDetails>
      </GetBillingAgreementDetailsResult>
      <ResponseMetadata>
        <RequestId>04b6dc0b-5f3f-4efd-978c-9e52ce1e55eb</RequestId>
      </ResponseMetadata>
    </GetBillingAgreementDetailsResponse>
    """,
    "create_order_reference": """
    <CreateOrderReferenceForIdResponse xmlns="http://mws.amazonservices.com/schema/OffAmazonPayments/2013-01-01">
      <CreateOrderReferenceForIdResult>
        <OrderReferenceDetails>
          <ExpirationTimestamp>2015-09-16T14:43:17.823Z</ExpirationTimestamp>
          <AmazonOrderReferenceId>S01-6576755-3809974</AmazonOrderReferenceId>
          <OrderTotal>
            <Amount>9.99</Amount>
            <CurrencyCode>USD</CurrencyCode>
          </OrderTotal>
          <OrderReferenceStatus>
            <LastUpdateTimestamp>2015-03-20T14:43:18.573Z</LastUpdateTimestamp>
            <State>Open</State>
          </OrderReferenceStatus>
          <ReleaseEnvironment>Sandbox</ReleaseEnvironment>
          <Buyer>
            <Email>test@example.com</Email>
            <Name>Simon</Name>
          </Buyer>
          <SellerOrderAttributes/>
          <CreationTimestamp>2015-03-20T14:43:17.823Z</CreationTimestamp>
        </OrderReferenceDetails>
      </CreateOrderReferenceForIdResult>
      <ResponseMetadata>
        <RequestId>06c47e51-38fc-4a05-9707-df580b3eff08</RequestId>
      </ResponseMetadata>
    </CreateOrderReferenceForIdResponse>""",
    "authorize": """
    <AuthorizeResponse xmlns="http://mws.amazonservices.com/schema/OffAmazonPayments/2013-01-01">
      <AuthorizeResult>
        <AuthorizationDetails>
          <AuthorizationStatus>
            <LastUpdateTimestamp>2015-03-20T14:43:26.949Z</LastUpdateTimestamp>
            <State>Closed</State>
            <ReasonCode>MaxCapturesProcessed</ReasonCode>
          </AuthorizationStatus>
          <ExpirationTimestamp>2015-04-19T14:43:26.949Z</ExpirationTimestamp>
          <AuthorizationAmount>
            <Amount>9.99</Amount>
            <CurrencyCode>USD</CurrencyCode>
          </AuthorizationAmount>
          <CapturedAmount>
            <Amount>0</Amount>
            <CurrencyCode>USD</CurrencyCode>
          </CapturedAmount>
          <IdList>
            <member>S01-6576755-3809974-C067494</member>
          </IdList>
          <AmazonAuthorizationId>S01-6576755-3809974-A067494</AmazonAuthorizationId>
          <SellerAuthorizationNote/>
          <CaptureNow>true</CaptureNow>
          <AuthorizationReferenceId>7-1426862604</AuthorizationReferenceId>
          <SoftDescriptor>AMZ*simon-test</SoftDescriptor>
          <CreationTimestamp>2015-03-20T14:43:26.949Z</CreationTimestamp>
          <AuthorizationFee>
            <Amount>0.00</Amount>
            <CurrencyCode>USD</CurrencyCode>
          </AuthorizationFee>
        </AuthorizationDetails>
      </AuthorizeResult>
      <ResponseMetadata>
        <RequestId>d06dcdc5-38b9-4da9-b52c-057240f183e2</RequestId>
      </ResponseMetadata>
    </AuthorizeResponse>
    """,
    "authorization_details": """
    <GetAuthorizationDetailsResponse xmlns="http://mws.amazonservices.com/schema/OffAmazonPayments/2013-01-01">
      <GetAuthorizationDetailsResult>
        <AuthorizationDetails>
          <ExpirationTimestamp>2015-04-19T14:43:26.949Z</ExpirationTimestamp>
          <AuthorizationStatus>
            <LastUpdateTimestamp>2015-03-20T14:43:26.949Z</LastUpdateTimestamp>
            <State>Closed</State>
            <ReasonCode>MaxCapturesProcessed</ReasonCode>
          </AuthorizationStatus>
          <AuthorizationAmount>
            <Amount>9.99</Amount>
            <CurrencyCode>USD</CurrencyCode>
          </AuthorizationAmount>
          <CapturedAmount>
            <Amount>9.99</Amount>
            <CurrencyCode>USD</CurrencyCode>
          </CapturedAmount>
          <IdList>
            <member>S01-6576755-3809974-C067494</member>
          </IdList>
          <AmazonAuthorizationId>S01-6576755-3809974-A067494</AmazonAuthorizationId>
          <SellerAuthorizationNote/>
          <CaptureNow>true</CaptureNow>
          <AuthorizationReferenceId>7-1426862604</AuthorizationReferenceId>
          <SoftDescriptor>AMZ*simon-test</SoftDescriptor>
          <CreationTimestamp>2015-03-20T14:43:26.949Z</CreationTimestamp>
          <AuthorizationFee>
            <Amount>0.00</Amount>
            <CurrencyCode>USD</CurrencyCode>
          </AuthorizationFee>
        </AuthorizationDetails>
      </GetAuthorizationDetailsResult>
      <ResponseMetadata>
        <RequestId>fe31045f-88a3-45c9-8c74-05af7a8494d3</RequestId>
      </ResponseMetadata>
    </GetAuthorizationDetailsResponse>
    """,
    "confirm_billing_agreement": """
    <ConfirmBillingAgreementResponse xmlns="http://mws.amazonservices.com/schema/OffAmazonPayments/2013-01-01">
      <ConfirmBillingAgreementResult/>
      <ResponseMetadata>
        <RequestId>5ba4e7a9-2d33-4a7a-9585-5860e7748fc8</RequestId>
      </ResponseMetadata>
    </ConfirmBillingAgreementResponse>
    """,
    "validate_billing_agreement": """
    <ValidateBillingAgreementResponse xmlns="http://mws.amazonservices.com/schema/OffAmazonPayments/2013-01-01">
      <ValidateBillingAgreementResult>
        <BillingAgreementStatus>
          <LastUpdatedTimestamp>2016-11-26T16:08:44.832Z</LastUpdatedTimestamp>
          <State>Open</State>
        </BillingAgreementStatus>
        <ValidationResult>Success</ValidationResult>
      </ValidateBillingAgreementResult>
      <ResponseMetadata>
        <RequestId>49fc9ede-4c49-4883-bba1-953b699ca70a</RequestId>
      </ResponseMetadata>
    </ValidateBillingAgreementResponse>
    """
}
