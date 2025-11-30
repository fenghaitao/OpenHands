# Stripe Integration

<cite>
**Referenced Files in This Document**   
- [stripe_service.py](file://enterprise/integrations/stripe_service.py)
- [billing.py](file://enterprise/server/routes/billing.py)
- [stripe_customer.py](file://enterprise/storage/stripe_customer.py)
- [subscription_access.py](file://enterprise/storage/subscription_access.py)
- [billing_session.py](file://enterprise/storage/billing_session.py)
- [constants.py](file://enterprise/server/constants.py)
- [use-create-stripe-checkout-session.ts](file://frontend/src/hooks/mutation/stripe/use-create-stripe-checkout-session.ts)
- [billing-service.api.ts](file://frontend/src/api/billing-service/billing-service.api.ts)
- [billing.types.ts](file://frontend/src/api/billing-service/billing.types.ts)
- [test_billing_stripe_integration.py](file://enterprise/tests/unit/test_billing_stripe_integration.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [API Endpoints](#api-endpoints)
3. [Webhook Handling](#webhook-handling)
4. [Error Handling and Security](#error-handling-and-security)
5. [Client Implementation Examples](#client-implementation-examples)
6. [Monitoring and Logging](#monitoring-and-logging)
7. [Migration and Compatibility](#migration-and-compatibility)

## Introduction

The Stripe Integration component provides a comprehensive payment processing system for the OpenHands platform, enabling users to purchase credits and subscribe to premium plans. The integration handles payment processing, subscription management, and customer data synchronization through a RESTful API that interfaces with Stripe's payment platform.

The system is designed with PCI compliance in mind, using Stripe Checkout to handle sensitive payment information without exposing card details to the application servers. Payment methods are securely stored in Stripe, while the application maintains references to customer and subscription data in its own database for efficient lookups and state management.

Key features include:
- One-time credit purchases through Stripe Checkout
- Recurring subscription management
- Webhook-based event handling for payment confirmation
- Customer data synchronization between the application and Stripe
- Secure authentication using JWT tokens

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L1-L647)
- [stripe_service.py](file://enterprise/integrations/stripe_service.py#L1-L74)

## API Endpoints

The Stripe Integration exposes several RESTful endpoints for payment processing and subscription management. All endpoints require authentication via JWT tokens, which are validated through the `get_user_id` dependency.

### Payment Processing Endpoints

#### Create Checkout Session for Credit Purchase
Creates a Stripe Checkout session for one-time credit purchases.

- **HTTP Method**: POST
- **URL Pattern**: `/api/billing/create-checkout-session`
- **Authentication**: JWT token (via cookie or Authorization header)
- **Request Schema**:
```json
{
  "amount": 25
}
```
- **Response Schema**:
```json
{
  "redirect_url": "https://checkout.stripe.com/session_abc123"
}
```
- **Parameters**:
  - `amount`: The amount to charge in USD (integer)

This endpoint creates a Stripe Checkout session in 'payment' mode, allowing users to purchase credits. After successful payment, users are redirected to the success callback, which updates their credit balance in the system.

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L210-L263)
- [use-create-stripe-checkout-session.ts](file://frontend/src/hooks/mutation/stripe/use-create-stripe-checkout-session.ts#L1-L12)

#### Create Customer Setup Session
Creates a Stripe Checkout session for managing payment methods.

- **HTTP Method**: POST
- **URL Pattern**: `/api/billing/create-customer-setup-session`
- **Authentication**: JWT token
- **Request Body**: None
- **Response Schema**:
```json
{
  "redirect_url": "https://checkout.stripe.com/setup_abc123"
}
```

This endpoint allows users to add, update, or remove payment methods from their account. The session is created in 'setup' mode, which securely collects payment information without immediately charging the user.

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L194-L208)

### Subscription Management Endpoints

#### Create Subscription Checkout Session
Creates a Stripe Checkout session for subscribing to a monthly plan.

- **HTTP Method**: POST
- **URL Pattern**: `/api/billing/subscription-checkout-session`
- **Authentication**: JWT token
- **Request Body**: None
- **Response Schema**:
```json
{
  "redirect_url": "https://checkout.stripe.com/subscription_abc123"
}
```

This endpoint creates a subscription checkout session in 'subscription' mode, setting up recurring billing for the user. The subscription details are configured with a monthly interval and exclusive tax behavior.

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L265-L337)

#### Get Subscription Access
Retrieves the user's current subscription status.

- **HTTP Method**: GET
- **URL Pattern**: `/api/billing/subscription-access`
- **Authentication**: JWT token
- **Response Schema**:
```json
{
  "start_at": "2024-01-01T00:00:00Z",
  "end_at": "2024-12-31T23:59:59Z",
  "created_at": "2024-01-01T00:00:00Z",
  "cancelled_at": null,
  "stripe_subscription_id": "sub_abc123"
}
```
- **Response Schema (No Active Subscription)**: `null`

This endpoint returns the user's active subscription details if they have a valid subscription that hasn't been cancelled and is within its active period. The response includes the subscription's start and end dates, creation timestamp, cancellation status, and Stripe subscription ID.

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L88-L112)
- [billing.types.ts](file://frontend/src/api/billing-service/billing.types.ts#L1-L7)

#### Cancel Subscription
Cancels the user's active subscription at the end of the current billing period.

- **HTTP Method**: POST
- **URL Pattern**: `/api/billing/cancel-subscription`
- **Authentication**: JWT token
- **Request Body**: None
- **Response Schema**:
```json
{
  "status": "success",
  "message": "Subscription cancelled successfully"
}
```

This endpoint cancels the user's subscription by updating the `cancel_at_period_end` flag in Stripe and recording the cancellation timestamp in the local database. The subscription remains active until the end of the current billing period.

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L123-L192)
- [billing.types.ts](file://frontend/src/api/billing-service/billing.types.ts#L9-L12)

### Customer Data Synchronization Endpoints

#### Check Payment Method
Checks if the user has a payment method on file.

- **HTTP Method**: POST
- **URL Pattern**: `/api/billing/has-payment-method`
- **Authentication**: JWT token
- **Request Body**: None
- **Response Schema**: `true` or `false`

This endpoint queries Stripe to determine if the user has any saved payment methods, returning a boolean response.

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L115-L119)
- [stripe_service.py](file://enterprise/integrations/stripe_service.py#L63-L74)

#### Get Credit Balance
Retrieves the user's current credit balance.

- **HTTP Method**: GET
- **URL Pattern**: `/api/billing/credits`
- **Authentication**: JWT token
- **Response Schema**:
```json
{
  "credits": "25.50"
}
```

This endpoint calculates the user's available credits by querying the LiteLLM proxy for their maximum budget and subtracting their current spending.

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L77-L85)

## Webhook Handling

The Stripe Integration includes a webhook endpoint to handle asynchronous events from Stripe, ensuring the application's state remains synchronized with Stripe's records.

### Webhook Endpoint

#### Stripe Webhook
Receives and processes events from Stripe.

- **HTTP Method**: POST
- **URL Pattern**: `/api/billing/stripe-webhook`
- **Authentication**: Signature verification (Stripe webhook secret)
- **Request Headers**:
  - `stripe-signature`: Stripe's signature for payload verification
- **Request Body**: Raw Stripe event payload
- **Response Schema**:
```json
{
  "status": "success"
}
```

The webhook endpoint verifies the authenticity of incoming requests using Stripe's signature verification mechanism before processing the event payload.

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L467-L576)

### Webhook Event Processing

The integration handles several key Stripe event types:

#### invoice.paid
Triggered when a subscription invoice is successfully paid.

- **Processing Logic**:
  1. Extract payment amount and user metadata from the invoice
  2. Validate the amount matches the expected subscription price
  3. Create a new `SubscriptionAccess` record with ACTIVE status
  4. Set the subscription period (1 month from current date)
  5. Store Stripe subscription and payment IDs
  6. Commit the record to the database

This event establishes or renews a user's subscription access, granting them premium features for the billing period.

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L487-L514)

#### customer.subscription.updated
Triggered when a subscription is modified, including cancellation requests.

- **Processing Logic**:
  1. Check if `cancel_at_period_end` is true
  2. Find the corresponding `SubscriptionAccess` record
  3. Set the `cancelled_at` timestamp if not already cancelled
  4. Update the record in the database

This event captures subscription cancellation requests, allowing the application to track when users have opted to cancel their subscriptions at the end of the current period.

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L515-L544)

#### customer.subscription.deleted
Triggered when a subscription is fully terminated.

- **Processing Logic**:
  1. Find the active `SubscriptionAccess` record
  2. Change status to DISABLED
  3. Reset the user's settings to free tier defaults
  4. Update the record in the database

This event handles the final termination of a subscription, downgrading the user to the free tier and resetting their configuration to default values.

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L545-L573)
- [billing.py](file://enterprise/server/routes/billing.py#L579-L614)

## Error Handling and Security

The Stripe Integration implements comprehensive error handling and security measures to ensure reliable payment processing and protect sensitive data.

### Error Handling Strategies

#### Payment Failures
The system handles various payment failure scenarios:

- **Invalid Payload**: Returns HTTP 400 with "Invalid payload" message when the webhook payload cannot be parsed
- **Invalid Signature**: Returns HTTP 400 with "Invalid signature" message when Stripe's signature verification fails
- **Missing Subscription**: Returns HTTP 404 when attempting to cancel a non-existent subscription
- **Stripe API Errors**: Catches `stripe.StripeError` exceptions and returns HTTP 500 with the error message

The integration also includes client-side error handling in the frontend, displaying appropriate messages for different error conditions.

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L477-L483)
- [billing.py](file://enterprise/server/routes/billing.py#L189-L191)

#### Rate Limiting Considerations
While the current implementation doesn't include explicit rate limiting, the architecture considerations include:

- Database connection pooling to prevent resource exhaustion
- Asynchronous processing of webhook events to handle spikes in traffic
- Idempotent webhook handling to safely retry failed processing

For production deployments, additional rate limiting should be implemented at the API gateway level to prevent abuse.

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L467-L576)

### Security Measures

#### PCI Compliance
The integration maintains PCI compliance through several key design decisions:

- **No Sensitive Data Storage**: Payment card details are never stored in the application database
- **Stripe Checkout**: All payment information is collected through Stripe's secure checkout interface
- **Tokenization**: Stripe returns tokens that reference payment methods, which are stored instead of actual card data
- **Secure Transmission**: All communication with Stripe uses HTTPS with signature verification

#### Authentication
The API uses JWT-based authentication to verify user identity:

- User authentication is handled by Keycloak
- JWT tokens are validated on each request
- User ID is extracted from the token and used to authorize operations
- The `get_user_id` dependency ensures only authenticated users can access billing endpoints

#### Data Protection
Additional security measures include:

- **Environment Variables**: Stripe API keys and webhook secrets are stored in environment variables
- **Input Validation**: Request data is validated using Pydantic models
- **Database Isolation**: Billing data is stored in separate tables with appropriate access controls
- **Audit Logging**: All billing operations are logged with user ID and relevant identifiers

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L30)
- [constants.py](file://enterprise/server/constants.py#L54-L55)
- [billing.py](file://enterprise/server/routes/billing.py#L474-L483)

## Client Implementation Examples

The following examples demonstrate how to implement the Stripe Integration in client applications.

### Python Implementation

```python
import requests
import json

class OpenHandsBillingClient:
    def __init__(self, base_url, auth_token):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        }
    
    def create_checkout_session(self, amount):
        """Create a checkout session for credit purchase."""
        url = f'{self.base_url}/api/billing/create-checkout-session'
        payload = {'amount': amount}
        
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        
        return response.json()['redirect_url']
    
    def create_subscription_session(self):
        """Create a subscription checkout session."""
        url = f'{self.base_url}/api/billing/subscription-checkout-session'
        
        response = requests.post(url, headers=self.headers)
        response.raise_for_status()
        
        return response.json()['redirect_url']
    
    def get_subscription_status(self):
        """Get current subscription status."""
        url = f'{self.base_url}/api/billing/subscription-access'
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def cancel_subscription(self):
        """Cancel the current subscription."""
        url = f'{self.base_url}/api/billing/cancel-subscription'
        
        response = requests.post(url, headers=self.headers)
        response.raise_for_status()
        
        return response.json()

# Usage example
client = OpenHandsBillingClient(
    'https://app.all-hands.dev', 
    'your-jwt-token-here'
)

# Create a $25 credit purchase session
redirect_url = client.create_checkout_session(25)
print(f'Redirect user to: {redirect_url}')

# Check current subscription status
subscription = client.get_subscription_status()
if subscription:
    print(f'Subscription active until: {subscription["end_at"]}')
else:
    print('No active subscription')
```

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L210-L263)
- [billing.py](file://enterprise/server/routes/billing.py#L88-L112)

### JavaScript Implementation

```javascript
// Using the existing billing service API
import BillingService from '#/api/billing-service/billing-service.api';

// React hook for creating checkout sessions
export const useCreateStripeCheckoutSession = () => {
  return useMutation({
    mutationFn: async (variables) => {
      const redirectUrl = await BillingService.createCheckoutSession(
        variables.amount
      );
      window.location.href = redirectUrl;
    },
  });
};

// React hook for creating subscription sessions
export const useCreateSubscriptionCheckoutSession = () => {
  return useMutation({
    mutationFn: BillingService.createSubscriptionCheckoutSession,
    onSuccess: (data) => {
      if (data.redirect_url) {
        window.location.href = data.redirect_url;
      }
    },
  });
};

// Example usage in a React component
function PaymentForm() {
  const createCheckoutSession = useCreateStripeCheckoutSession();
  const createSubscriptionSession = useCreateSubscriptionCheckoutSession();
  
  const handleCreditPurchase = () => {
    createCheckoutSession.mutate({ amount: 25 });
  };
  
  const handleSubscription = () => {
    createSubscriptionSession.mutate();
  };
  
  return (
    <div>
      <button onClick={handleCreditPurchase}>
        Buy $25 Credits
      </button>
      <button onClick={handleSubscription}>
        Subscribe Monthly
      </button>
    </div>
  );
}
```

**Section sources**
- [billing-service.api.ts](file://frontend/src/api/billing-service/billing-service.api.ts#L1-L84)
- [use-create-stripe-checkout-session.ts](file://frontend/src/hooks/mutation/stripe/use-create-stripe-checkout-session.ts#L1-L12)

### Webhook Event Handling

```python
from flask import Flask, request, jsonify
import stripe

app = Flask(__name__)
stripe.api_key = 'your-stripe-secret-key'
webhook_secret = 'your-webhook-secret'

@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'invoice.paid':
        invoice = event['data']['object']
        print(f'Invoice {invoice.id} was paid')
        # Update your database with subscription info
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        if subscription.get('cancel_at_period_end'):
            print(f'Subscription {subscription.id} will cancel at period end')
            # Update subscription status in your database
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        print(f'Subscription {subscription.id} was deleted')
        # Downgrade user to free tier
    else:
        print(f'Unhandled event type: {event["type"]}')
    
    return jsonify({'status': 'success'})
```

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L467-L576)

## Monitoring and Logging

The Stripe Integration includes comprehensive monitoring and logging capabilities to track payment success rates and maintain audit trails.

### Payment Success Rate Monitoring

The system provides several metrics for monitoring payment success:

- **Checkout Session Creation**: Logs when checkout sessions are created, including user ID, amount, and session ID
- **Payment Success**: Logs successful payments with amount, user ID, and Stripe customer ID
- **Payment Cancellation**: Logs when users cancel the payment process
- **Subscription Events**: Logs all subscription lifecycle events (creation, update, cancellation, deletion)

These logs can be aggregated to calculate key metrics:
- Payment success rate (successful payments / total checkout sessions)
- Subscription conversion rate (subscriptions created / subscription checkout sessions)
- Churn rate (subscriptions cancelled / active subscriptions)

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L242-L250)
- [billing.py](file://enterprise/server/routes/billing.py#L408-L417)

### Logging Practices

The integration uses structured logging with the following practices:

- **Audit Trails**: All billing operations are logged with relevant identifiers (user ID, Stripe customer ID, checkout session ID)
- **Error Context**: Errors include contextual information to aid debugging
- **Sensitive Data Protection**: Payment details are never logged; only references are recorded
- **Timestamps**: All logs include UTC timestamps for correlation across systems

Example log entries:
```
INFO created_stripe_checkout_session user_id=test123 amount=25 checkout_session_id=cs_abc123
INFO stripe_checkout_success user_id=test123 amount_subtotal=2500 checkout_session_id=cs_abc123
ERROR stripe_cancellation_failed user_id=test123 stripe_subscription_id=sub_def456 error=No such subscription: sub_def456
```

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L242-L250)
- [billing.py](file://enterprise/server/routes/billing.py#L165-L173)

## Migration and Compatibility

The Stripe Integration is designed with backward compatibility and smooth migration in mind.

### API Version Updates

When updating the Stripe API version, follow these steps:

1. **Test in Staging**: Deploy the updated integration to a staging environment first
2. **Webhook Compatibility**: Ensure webhook handlers can process events from both old and new API versions
3. **Gradual Rollout**: Use feature flags to gradually enable the new version for users
4. **Monitor Metrics**: Closely monitor payment success rates during the transition

The current implementation is compatible with Stripe API version 2023-08-16 or later, which includes the asynchronous methods used in the integration.

### Backwards Compatibility

The integration maintains backwards compatibility through:

- **Database Migrations**: Alembic migrations ensure schema changes are applied safely
- **Graceful Degradation**: Features gracefully degrade when Stripe integration is disabled
- **Configuration Flags**: Environment variables control Stripe integration behavior

Deprecated features include:
- Direct payment method storage (replaced by Stripe Customer objects)
- Local credit balance tracking (replaced by LiteLLM integration)
- Synchronous Stripe API calls (replaced by async methods)

**Section sources**
- [constants.py](file://enterprise/server/constants.py#L40-L51)
- [074_create_subscription_access_table.py](file://enterprise/migrations/versions/074_create_subscription_access_table.py#L1-L45)
- [004_create_billing_sessions_table.py](file://enterprise/migrations/versions/004_create_billing_sessions_table.py#L1-L47)