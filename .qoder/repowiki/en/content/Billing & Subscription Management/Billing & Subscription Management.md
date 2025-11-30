# Billing & Subscription Management

<cite>
**Referenced Files in This Document**   
- [billing.py](file://enterprise/server/routes/billing.py)
- [stripe_service.py](file://enterprise/integrations/stripe_service.py)
- [billing_session.py](file://enterprise/storage/billing_session.py)
- [subscription_access.py](file://enterprise/storage/subscription_access.py)
- [stripe_customer.py](file://enterprise/storage/stripe_customer.py)
- [constants.py](file://enterprise/server/constants.py)
- [database.py](file://enterprise/storage/database.py)
- [billing-service.api.ts](file://frontend/src/api/billing-service/billing-service.api.ts)
- [use-create-stripe-checkout-session.ts](file://frontend/src/hooks/mutation/stripe/use-create-stripe-checkout-session.ts)
- [use-create-subscription-checkout-session.ts](file://frontend/src/hooks/mutation/stripe/use-create-subscription-checkout-session.ts)
- [billing.types.ts](file://frontend/src/api/billing-service/billing.types.ts)
- [billing-handlers.ts](file://frontend/src/mocks/billing-handlers.ts)
- [004_create_billing_sessions_table.py](file://enterprise/migrations/versions/004_create_billing_sessions_table.py)
- [017_add_stripe_customers_table.py](file://enterprise/migrations/versions/017_add_stripe_customers_table.py)
- [074_create_subscription_access_table.py](file://enterprise/migrations/versions/074_create_subscription_access_table.py)
- [billing_session_type.py](file://enterprise/storage/billing_session_type.py)
- [subscription_access_status.py](file://enterprise/storage/subscription_access_status.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

## Introduction
The Billing & Subscription Management component in OpenHands provides a comprehensive system for handling credit-based billing and subscription management through Stripe integration. This system enables users to purchase credits for AI agent usage, subscribe to monthly plans, and manage their payment methods. The architecture follows a microservices pattern with clear separation between frontend interfaces, backend API routes, database models, and external payment processing via Stripe. The system is designed with security, scalability, and reliability in mind, incorporating webhook validation, database transactions, and proper error handling throughout the payment lifecycle.

## Project Structure
The billing system is organized across multiple directories in the enterprise module, following a clean separation of concerns. The backend implementation resides in the enterprise/server/routes directory for API endpoints, enterprise/storage for database models, and enterprise/integrations for external service connections. The frontend components are located in the frontend/src directory with dedicated billing service APIs and React hooks for state management. Database migrations are maintained in enterprise/migrations/versions to ensure schema consistency across environments.

```mermaid
graph TB
subgraph "Frontend"
BillingAPI[billing-service.api.ts]
BillingTypes[billing.types.ts]
Hooks[React Hooks]
UI[Payment UI Components]
end
subgraph "Backend"
Routes[billing.py]
Models[Database Models]
Integrations[stripe_service.py]
Migrations[Database Migrations]
end
subgraph "External Services"
Stripe[Stripe API]
LiteLLM[LiteLLM Proxy]
PostgreSQL[PostgreSQL Database]
end
Frontend --> Backend
Backend --> External Services
```

**Diagram sources**
- [billing.py](file://enterprise/server/routes/billing.py#L31-L647)
- [billing-service.api.ts](file://frontend/src/api/billing-service/billing-service.api.ts#L1-L84)
- [stripe_service.py](file://enterprise/integrations/stripe_service.py#L1-L74)

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L1-L647)
- [billing-service.api.ts](file://frontend/src/api/billing-service/billing-service.api.ts#L1-L84)

## Core Components
The billing system consists of several core components that work together to provide a seamless payment experience. The backend routes handle all billing-related operations including credit purchases, subscription management, and webhook processing. Database models track billing sessions, user subscriptions, and Stripe customer information. The Stripe integration service provides a wrapper around the Stripe API with additional business logic for customer management. Frontend components provide React hooks and API services to interact with the billing backend, while the database schema ensures data consistency and integrity through proper relationships and constraints.

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L31-L647)
- [billing_session.py](file://enterprise/storage/billing_session.py#L1-L46)
- [subscription_access.py](file://enterprise/storage/subscription_access.py#L1-L46)
- [stripe_customer.py](file://enterprise/storage/stripe_customer.py#L1-L26)

## Architecture Overview
The billing system follows a layered architecture with clear separation between presentation, application logic, data access, and external services. The frontend communicates with the backend via REST APIs, which in turn interact with the database and external payment gateway. The system uses Stripe Checkout for payment processing, with webhook integration to handle asynchronous events like subscription renewals and cancellations. Credit management is integrated with the LiteLLM proxy service, which tracks usage against allocated budgets. The architecture emphasizes idempotency, security, and fault tolerance, with proper error handling and logging throughout the payment workflow.

```mermaid
graph TB
User[User] --> |1. Initiate Payment| Frontend
Frontend --> |2. API Request| Backend
Backend --> |3. Create Stripe Session| Stripe
Stripe --> |4. Payment Processing| PaymentGateway
PaymentGateway --> |5. Webhook| Backend
Backend --> |6. Update Database| Database
Backend --> |7. Update LiteLLM| LiteLLM
Database --> |8. Store Records| PostgreSQL
LiteLLM --> |9. Apply Credits| AIService
style User fill:#f9f,stroke:#333
style Frontend fill:#bbf,stroke:#333
style Backend fill:#f96,stroke:#333
style Stripe fill:#69f,stroke:#333
style PaymentGateway fill:#69f,stroke:#333
style Database fill:#6f9,stroke:#333
style LiteLLM fill:#9f6,stroke:#333
style AIService fill:#9f6,stroke:#333
style PostgreSQL fill:#6f9,stroke:#333
```

**Diagram sources**
- [billing.py](file://enterprise/server/routes/billing.py#L31-L647)
- [stripe_service.py](file://enterprise/integrations/stripe_service.py#L1-L74)
- [database.py](file://enterprise/storage/database.py#L1-L115)

## Detailed Component Analysis

### Billing System Components
The billing system comprises several interconnected components that handle different aspects of the payment and subscription workflow. These components work together to provide a seamless experience for users purchasing credits or subscribing to plans, while ensuring data consistency and security throughout the process.

#### Class Diagram for Billing Components
```mermaid
classDiagram
class BillingSession {
+string id
+string user_id
+string status
+DECIMAL price
+string price_code
+BillingSessionType billing_session_type
+DateTime created_at
+DateTime updated_at
}
class SubscriptionAccess {
+int id
+string status
+string user_id
+DateTime start_at
+DateTime end_at
+DECIMAL amount_paid
+string stripe_invoice_payment_id
+DateTime cancelled_at
+string stripe_subscription_id
+DateTime created_at
+DateTime updated_at
}
class StripeCustomer {
+int id
+string keycloak_user_id
+string stripe_customer_id
+DateTime created_at
+DateTime updated_at
}
class BillingSessionType {
+DIRECT_PAYMENT
+MONTHLY_SUBSCRIPTION
}
class SubscriptionAccessStatus {
+ACTIVE
+DISABLED
}
BillingSession --> BillingSessionType : "has type"
SubscriptionAccess --> SubscriptionAccessStatus : "has status"
SubscriptionAccess --> StripeCustomer : "belongs to"
BillingSession --> StripeCustomer : "belongs to"
```

**Diagram sources**
- [billing_session.py](file://enterprise/storage/billing_session.py#L7-L46)
- [subscription_access.py](file://enterprise/storage/subscription_access.py#L7-L46)
- [stripe_customer.py](file://enterprise/storage/stripe_customer.py#L5-L26)
- [billing_session_type.py](file://enterprise/storage/billing_session_type.py#L4-L6)
- [subscription_access_status.py](file://enterprise/storage/subscription_access_status.py#L4-L7)

#### Sequence Diagram for Credit Purchase Workflow
```mermaid
sequenceDiagram
participant User as "User"
participant Frontend as "Frontend UI"
participant Backend as "Billing API"
participant Stripe as "Stripe API"
participant Database as "PostgreSQL"
participant LiteLLM as "LiteLLM Proxy"
User->>Frontend : Click "Buy Credits"
Frontend->>Backend : POST /api/billing/create-checkout-session
Backend->>Stripe : Create Checkout Session
Stripe-->>Backend : Session URL
Backend->>Database : Store BillingSession (in_progress)
Database-->>Backend : Confirmation
Backend-->>Frontend : Redirect URL
Frontend->>User : Redirect to Stripe Checkout
User->>Stripe : Complete Payment
Stripe->>Backend : GET /api/billing/success
Backend->>Database : Verify BillingSession
Database-->>Backend : Session Details
Backend->>LiteLLM : Update User Budget
LiteLLM-->>Backend : Success
Backend->>Database : Update BillingSession (completed)
Database-->>Backend : Confirmation
Backend->>Frontend : Redirect to Settings
Frontend->>User : Show Success Message
```

**Diagram sources**
- [billing.py](file://enterprise/server/routes/billing.py#L210-L263)
- [billing-service.api.ts](file://frontend/src/api/billing-service/billing-service.api.ts#L16-L24)

#### Sequence Diagram for Subscription Management
```mermaid
sequenceDiagram
participant User as "User"
participant Frontend as "Frontend UI"
participant Backend as "Billing API"
participant Stripe as "Stripe API"
participant Database as "PostgreSQL"
User->>Frontend : Click "Subscribe"
Frontend->>Backend : POST /api/billing/subscription-checkout-session
Backend->>Database : Check for existing subscription
Database-->>Backend : No active subscription
Backend->>Stripe : Create Subscription Checkout Session
Stripe-->>Backend : Session URL
Backend->>Database : Store BillingSession
Database-->>Backend : Confirmation
Backend-->>Frontend : Redirect URL
Frontend->>User : Redirect to Stripe Checkout
User->>Stripe : Complete Payment
Stripe->>Backend : webhook : invoice.paid
Backend->>Database : Create SubscriptionAccess
Database-->>Backend : Confirmation
Backend-->>Stripe : Acknowledge webhook
loop Daily
Stripe->>LiteLLM : Charge for usage
end
User->>Frontend : Click "Cancel Subscription"
Frontend->>Backend : POST /api/billing/cancel-subscription
Backend->>Stripe : Modify Subscription (cancel_at_period_end)
Stripe-->>Backend : Confirmation
Backend->>Database : Update SubscriptionAccess (cancelled_at)
Database-->>Backend : Confirmation
Backend-->>Frontend : Success Response
Frontend->>User : Show Cancellation Confirmation
```

**Diagram sources**
- [billing.py](file://enterprise/server/routes/billing.py#L265-L336)
- [billing.py](file://enterprise/server/routes/billing.py#L123-L192)
- [billing.py](file://enterprise/server/routes/billing.py#L467-L576)

#### Flowchart for Payment Processing Logic
```mermaid
flowchart TD
Start([Payment Initiated]) --> ValidateUser["Validate User Authentication"]
ValidateUser --> CheckExisting["Check for Existing Subscription"]
CheckExisting --> HasActive{"Has Active Subscription?"}
HasActive --> |Yes| ShowError["Show Error: Already Subscribed"]
HasActive --> |No| CreateSession["Create Stripe Checkout Session"]
CreateSession --> StoreSession["Store BillingSession in Database"]
StoreSession --> Redirect["Redirect to Stripe Checkout"]
Redirect --> UserPayment["User Completes Payment on Stripe"]
UserPayment --> Webhook["Stripe Sends Webhook"]
Webhook --> VerifyWebhook["Verify Webhook Signature"]
VerifyWebhook --> ProcessEvent["Process Event Type"]
ProcessEvent --> IsInvoicePaid{"Event: invoice.paid?"}
IsInvoicePaid --> |Yes| CreateSubscription["Create SubscriptionAccess Record"]
IsInvoicePaid --> |No| IsSubscriptionUpdated{"Event: customer.subscription.updated?"}
IsSubscriptionUpdated --> |Yes| HandleCancellation["Handle Subscription Cancellation"]
IsSubscriptionUpdated --> |No| IsSubscriptionDeleted{"Event: customer.subscription.deleted?"}
IsSubscriptionDeleted --> |Yes| DisableSubscription["Disable SubscriptionAccess"]
IsSubscriptionDeleted --> |No| LogUnhandled["Log Unhandled Event"]
CreateSubscription --> UpdateLiteLLM["Update LiteLLM User Budget"]
UpdateLiteLLM --> Complete["Payment Processing Complete"]
HandleCancellation --> UpdateDatabase["Update cancelled_at in SubscriptionAccess"]
UpdateDatabase --> Complete
DisableSubscription --> ResetSettings["Reset User to Free Tier Settings"]
ResetSettings --> Complete
LogUnhandled --> Complete
Complete --> End([Process Complete])
ShowError --> End
```

**Diagram sources**
- [billing.py](file://enterprise/server/routes/billing.py#L467-L576)
- [billing.py](file://enterprise/server/routes/billing.py#L77-L84)
- [billing.py](file://enterprise/server/routes/billing.py#L579-L613)

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L1-L647)
- [stripe_service.py](file://enterprise/integrations/stripe_service.py#L1-L74)
- [billing-service.api.ts](file://frontend/src/api/billing-service/billing-service.api.ts#L1-L84)

### Database Schema Analysis
The billing system utilizes a well-designed database schema to track payment transactions, user subscriptions, and customer information. The schema includes three main tables: billing_sessions, subscription_access, and stripe_customers, each serving a specific purpose in the billing workflow.

#### Entity Relationship Diagram
```mermaid
erDiagram
BILLING_SESSIONS {
string id PK
string user_id FK
string status
decimal price
string price_code
string billing_session_type
timestamp created_at
timestamp updated_at
}
SUBSCRIPTION_ACCESS {
int id PK
string status
string user_id FK
timestamp start_at
timestamp end_at
decimal amount_paid
string stripe_invoice_payment_id
timestamp cancelled_at
string stripe_subscription_id
timestamp created_at
timestamp updated_at
}
STRIPE_CUSTOMERS {
int id PK
string keycloak_user_id FK
string stripe_customer_id
timestamp created_at
timestamp updated_at
}
BILLING_SESSIONS ||--o{ STRIPE_CUSTOMERS : "belongs to"
SUBSCRIPTION_ACCESS ||--o{ STRIPE_CUSTOMERS : "belongs to"
BILLING_SESSIONS }|--|| SUBSCRIPTION_ACCESS : "may create"
```

**Diagram sources**
- [004_create_billing_sessions_table.py](file://enterprise/migrations/versions/004_create_billing_sessions_table.py#L21-L47)
- [074_create_subscription_access_table.py](file://enterprise/migrations/versions/074_create_subscription_access_table.py#L21-L66)
- [017_add_stripe_customers_table.py](file://enterprise/migrations/versions/017_add_stripe_customers_table.py#L21-L55)

**Section sources**
- [billing_session.py](file://enterprise/storage/billing_session.py#L1-L46)
- [subscription_access.py](file://enterprise/storage/subscription_access.py#L1-L46)
- [stripe_customer.py](file://enterprise/storage/stripe_customer.py#L1-L26)

## Dependency Analysis
The billing system has a well-defined dependency structure that ensures loose coupling between components while maintaining the necessary integration points for a cohesive system. The backend routes depend on the database models and Stripe integration service, while the frontend components depend on the API endpoints. The system also integrates with external services like LiteLLM for credit management and Keycloak for user authentication.

```mermaid
graph TD
A[billing.py] --> B[stripe_service.py]
A --> C[billing_session.py]
A --> D[subscription_access.py]
A --> E[stripe_customer.py]
A --> F[constants.py]
A --> G[database.py]
H[billing-service.api.ts] --> I[open-hands-axios]
J[use-create-stripe-checkout-session.ts] --> K[billing-service.api.ts]
J --> L[React Query]
M[use-create-subscription-checkout-session.ts] --> N[billing-service.api.ts]
M --> O[React Query]
B --> P[stripe]
B --> Q[TokenManager]
C --> R[Base]
D --> R
E --> R
G --> H[SQLAlchemy]
G --> I[google.cloud.sql.connector]
style A fill:#f96,stroke:#333
style B fill:#f96,stroke:#333
style C fill:#f96,stroke:#333
style D fill:#f96,stroke:#333
style E fill:#f96,stroke:#333
style F fill:#f96,stroke:#333
style G fill:#f96,stroke:#333
style H fill:#bbf,stroke:#333
style I fill:#bbf,stroke:#333
style J fill:#bbf,stroke:#333
style K fill:#bbf,stroke:#333
style L fill:#bbf,stroke:#333
style M fill:#bbf,stroke:#333
style N fill:#bbf,stroke:#333
style O fill:#bbf,stroke:#333
style P fill:#69f,stroke:#333
style Q fill:#69f,stroke:#333
style R fill:#6f9,stroke:#333
```

**Diagram sources**
- [billing.py](file://enterprise/server/routes/billing.py#L1-L647)
- [stripe_service.py](file://enterprise/integrations/stripe_service.py#L1-L74)
- [billing_session.py](file://enterprise/storage/billing_session.py#L1-L46)
- [subscription_access.py](file://enterprise/storage/subscription_access.py#L1-L46)
- [stripe_customer.py](file://enterprise/storage/stripe_customer.py#L1-L26)
- [constants.py](file://enterprise/server/constants.py#L1-L107)
- [database.py](file://enterprise/storage/database.py#L1-L115)

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L1-L647)
- [stripe_service.py](file://enterprise/integrations/stripe_service.py#L1-L74)
- [database.py](file://enterprise/storage/database.py#L1-L115)

## Performance Considerations
The billing system is designed with performance and scalability in mind. Database queries are optimized with appropriate indexes on frequently queried fields such as user_id and status. The system uses connection pooling for database access to minimize connection overhead. For high-traffic scenarios, the architecture supports horizontal scaling of the application servers. The Stripe webhook endpoint is designed to be idempotent and can handle duplicate events safely. The system also implements proper error handling and logging to facilitate monitoring and troubleshooting of performance issues.

**Section sources**
- [database.py](file://enterprise/storage/database.py#L20-L22)
- [017_add_stripe_customers_table.py](file://enterprise/migrations/versions/017_add_stripe_customers_table.py#L41-L51)
- [074_create_subscription_access_table.py](file://enterprise/migrations/versions/074_create_subscription_access_table.py#L47-L51)

## Troubleshooting Guide
When troubleshooting issues with the billing system, consider the following common scenarios and their solutions:

1. **Payment not reflecting in user account**: Verify that the Stripe webhook is being received and processed correctly. Check the server logs for webhook events and ensure the database transaction completes successfully.

2. **Subscription not activating**: Confirm that the user doesn't already have an active subscription. Check the subscription_access table for existing records and verify the webhook processing logic.

3. **Credit balance not updating**: Ensure the LiteLLM proxy integration is working correctly. Verify the API credentials and network connectivity between the billing service and LiteLLM.

4. **Stripe session creation failures**: Check that the Stripe API key is correctly configured in the environment variables. Verify that the customer record exists in both the local database and Stripe.

5. **Webhook signature verification failures**: Ensure the STRIPE_WEBHOOK_SECRET environment variable matches the secret configured in the Stripe dashboard.

**Section sources**
- [billing.py](file://enterprise/server/routes/billing.py#L467-L576)
- [constants.py](file://enterprise/server/constants.py#L54-L55)
- [stripe_service.py](file://enterprise/integrations/stripe_service.py#L1-L74)

## Conclusion
The Billing & Subscription Management component in OpenHands provides a robust and secure system for handling credit-based billing and subscription management. The architecture follows best practices with clear separation of concerns, proper error handling, and integration with external services like Stripe and LiteLLM. The system is designed to be scalable and maintainable, with comprehensive logging and monitoring capabilities. The frontend and backend components work together seamlessly to provide a smooth user experience for purchasing credits and managing subscriptions. With its well-defined API endpoints, database schema, and integration patterns, the billing system forms a critical part of the OpenHands platform's monetization strategy.