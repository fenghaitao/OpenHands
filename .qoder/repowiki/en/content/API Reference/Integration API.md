# Integration API

<cite>
**Referenced Files in This Document**   
- [github_proxy.py](file://enterprise/server/routes/github_proxy.py)
- [github.py](file://enterprise/server/routes/integration/github.py)
- [gitlab.py](file://enterprise/server/routes/integration/gitlab.py)
- [token_manager.py](file://enterprise/server/auth/token_manager.py)
- [github_service.py](file://enterprise/integrations/github/github_service.py)
- [gitlab_manager.py](file://enterprise/integrations/gitlab/gitlab_manager.py)
- [github_callback_processor.py](file://enterprise/server/conversation_callback_processor/github_callback_processor.py)
- [gitlab_callback_processor.py](file://enterprise/server/conversation_callback_processor/gitlab_callback_processor.py)
- [rate_limit.py](file://enterprise/server/rate_limit.py)
- [models.py](file://enterprise/integrations/models.py)
- [gitlab_webhook_store.py](file://enterprise/storage/gitlab_webhook_store.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [API Endpoints](#api-endpoints)
3. [Authentication Flow](#authentication-flow)
4. [Data Synchronization](#data-synchronization)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Configuration Examples](#configuration-examples)
8. [Conclusion](#conclusion)

## Introduction

The OpenHands integration API provides seamless connectivity between OpenHands and external development platforms, primarily GitHub and GitLab. This documentation details the API endpoints, authentication mechanisms, data synchronization processes, and error handling strategies that enable developers to integrate their repositories and collaborate effectively through OpenHands.

The integration system is designed to support repository connection, webhook management, and proxy endpoints for API requests. It leverages OAuth-based authentication flows to securely connect user accounts and implements robust data synchronization mechanisms to ensure consistent state between OpenHands and external platforms.

This integration architecture enables developers to trigger automated workflows from GitHub and GitLab events, receive status updates in pull requests and issues, and securely proxy API requests through OpenHands while maintaining proper authentication context.

**Section sources**
- [github.py](file://enterprise/server/routes/integration/github.py#L1-L84)
- [gitlab.py](file://enterprise/server/routes/integration/gitlab.py#L1-L85)

## API Endpoints

### GitHub Integration Endpoints

The GitHub integration provides endpoints for handling webhook events and proxying authentication requests. The primary endpoint for receiving GitHub webhook events is:

```
POST /integration/github/events
```

This endpoint processes incoming webhook payloads from GitHub, verifies their authenticity using the `x-hub-signature-256` header, and routes the events to the appropriate handlers. The endpoint validates that the GitHub webhook secret matches the expected signature before processing the payload.

The integration also includes a GitHub proxy system that facilitates authentication for feature branches. This proxy system includes several endpoints:

```
GET /github-proxy/{subdomain}/login/oauth/authorize
GET /github-proxy/callback
POST /github-proxy/{subdomain}/login/oauth/access_token
POST /github-proxy/{subdomain}/{path:path}
```

These proxy endpoints intercept OAuth authorization requests, encode state information including the subdomain and redirect URI, and securely redirect users through the authentication flow. The proxy also handles access token requests and can proxy arbitrary requests to the GitHub API.

### GitLab Integration Endpoints

The GitLab integration provides a dedicated endpoint for receiving webhook events:

```
POST /integration/gitlab/events
```

This endpoint accepts GitLab webhook payloads and verifies their authenticity using custom headers including `x-gitlab-token`, `x-openhands-webhook-id`, and `x-openhands-user-id`. The verification process ensures that the webhook secret matches the stored secret for the specific webhook configuration.

The endpoint implements deduplication logic to prevent processing the same event multiple times within a 60-second window, using Redis to track recently processed events by their unique identifiers.

```mermaid
flowchart TD
A[GitHub Webhook] --> B[/integration/github/events]
B --> C{Verify Signature}
C --> |Valid| D[Process Event]
C --> |Invalid| E[Return 403]
D --> F[Route to Handler]
G[GitLab Webhook] --> H[/integration/gitlab/events]
H --> I{Verify Headers}
I --> |Valid| J[Check Deduplication]
J --> K{Duplicate?}
K --> |Yes| L[Return 200]
K --> |No| M[Process Event]
M --> N[Update Last Synced]
N --> O[Route to Handler]
I --> |Invalid| P[Return 403]
```

**Diagram sources**
- [github.py](file://enterprise/server/routes/integration/github.py#L45-L84)
- [gitlab.py](file://enterprise/server/routes/integration/gitlab.py#L35-L85)

**Section sources**
- [github.py](file://enterprise/server/routes/integration/github.py#L45-L84)
- [gitlab.py](file://enterprise/server/routes/integration/gitlab.py#L35-L85)

## Authentication Flow

### OAuth-Based Integration

The OpenHands integration system implements OAuth-based authentication flows for connecting user accounts with external platforms. The authentication process begins when a user initiates a connection to GitHub or GitLab through the OpenHands interface.

For GitHub integration, the system uses the GitHub App OAuth flow, which requires the following environment variables to be configured:
- `GITHUB_APP_CLIENT_ID`
- `GITHUB_APP_CLIENT_SECRET`
- `GITHUB_APP_WEBHOOK_SECRET`
- `GITHUB_APP_PRIVATE_KEY`

When a user authorizes the GitHub App, OpenHands receives an authorization code that is exchanged for access and refresh tokens. These tokens are securely stored in the database, encrypted using Fernet encryption derived from the application's JWT secret.

```mermaid
sequenceDiagram
participant User
participant OpenHands
participant GitHub
participant Database
User->>OpenHands : Initiate GitHub Connection
OpenHands->>GitHub : Redirect to OAuth URL
GitHub->>User : Show Authorization Prompt
User->>GitHub : Approve Authorization
GitHub->>OpenHands : Send Authorization Code
OpenHands->>GitHub : Exchange Code for Tokens
GitHub->>OpenHands : Return Access and Refresh Tokens
OpenHands->>Database : Store Encrypted Tokens
OpenHands->>User : Connection Successful
```

**Diagram sources**
- [token_manager.py](file://enterprise/server/auth/token_manager.py#L88-L111)
- [github_service.py](file://enterprise/integrations/github/github_service.py#L39-L73)

### Token Management System

The token management system is responsible for storing, retrieving, and refreshing OAuth tokens for connected accounts. The `TokenManager` class handles all aspects of token lifecycle management, including:

- Storing tokens in encrypted form in the database
- Retrieving tokens for API requests
- Refreshing expired access tokens using refresh tokens
- Validating token status and handling expired tokens

The system implements a layered approach to token retrieval, supporting multiple methods:
1. Direct access token
2. External authentication ID
3. User ID with associated offline token

When making API requests to external platforms, the system automatically handles token refresh if the access token has expired. The refresh process uses the refresh token to obtain new access and refresh tokens, ensuring uninterrupted service.

The token manager also supports GitHub App installation tokens, which are used for organization-level access. These tokens are stored separately and have a shorter lifespan, typically expiring after one hour.

**Section sources**
- [token_manager.py](file://enterprise/server/auth/token_manager.py#L77-L670)
- [github_service.py](file://enterprise/integrations/github/github_service.py#L39-L73)

## Data Synchronization

### Repository Connection and Event Processing

The data synchronization mechanism between OpenHands and external platforms is event-driven, with webhook events triggering specific actions in the system. When a user connects their repository, the system establishes a webhook subscription to receive notifications of relevant events.

For GitHub repositories, the system listens for events such as:
- Issue comments
- Pull request comments
- Issue assignments
- Pull request reviews

For GitLab repositories, the system processes events including:
- Issue comments
- Merge request comments
- Inline comments on merge requests
- Issue and merge request updates

When an event is received, the system performs the following steps:
1. Verify the authenticity of the webhook payload
2. Extract relevant information from the payload
3. Check if the user has write access to the repository
4. Create or update the corresponding conversation in OpenHands
5. Trigger the appropriate agent workflow

The GitLab integration includes additional deduplication logic to prevent processing the same event multiple times. This is achieved by storing a hash of the payload in Redis with a 60-second expiration, ensuring that duplicate events within this window are ignored.

### Conversation Callback Processing

The system implements a callback processor architecture to send updates from OpenHands conversations back to the external platforms. When a conversation reaches certain states (such as awaiting user input or finished), the callback processor sends a summary back to the original issue or pull request.

The GitHub callback processor sends messages to GitHub issues and pull requests, providing status updates and summaries of the agent's work. Similarly, the GitLab callback processor sends updates to GitLab issues and merge requests.

```mermaid
flowchart TD
A[External Platform Event] --> B{Event Valid?}
B --> |Yes| C[Create/Update Conversation]
C --> D[Run Agent Workflow]
D --> E{Agent State Change}
E --> |Awaiting Input| F[Send Status Update]
E --> |Finished| G[Send Summary]
F --> H[External Platform]
G --> H
E --> |Other| I[No Action]
J[User Response] --> C
```

**Diagram sources**
- [gitlab_manager.py](file://enterprise/integrations/gitlab/gitlab_manager.py#L74-L262)
- [github_callback_processor.py](file://enterprise/server/conversation_callback_processor/github_callback_processor.py#L66-L144)
- [gitlab_callback_processor.py](file://enterprise/server/conversation_callback_processor/gitlab_callback_processor.py#L119-L142)

**Section sources**
- [gitlab_manager.py](file://enterprise/integrations/gitlab/gitlab_manager.py#L74-L262)
- [github_callback_processor.py](file://enterprise/server/conversation_callback_processor/github_callback_processor.py#L66-L144)

## Error Handling

### Integration Failure Strategies

The integration system implements comprehensive error handling strategies to manage failures when interacting with external APIs. When an integration failure occurs, the system follows a structured approach to handle the error and provide meaningful feedback.

For authentication-related errors, the system distinguishes between different types of authentication failures:
- Invalid credentials
- Expired tokens
- Revoked permissions
- Missing required scopes

When a token has expired, the system automatically attempts to refresh it using the refresh token. If the refresh fails, the user is prompted to re-authenticate with the external platform.

For API request failures, the system categorizes errors into specific types:
- Authentication errors (401 status)
- Rate limiting errors (429 status)
- Resource not found errors (404 status)
- Server errors (5xx status)

The system logs detailed error information, including the request URL, method, and response body, to facilitate debugging while ensuring sensitive information is not exposed.

### Webhook Payload Validation

The system implements strict validation of webhook payloads to ensure data integrity and security. For GitHub webhooks, the system verifies the `x-hub-signature-256` header by computing the HMAC-SHA256 hash of the payload using the webhook secret and comparing it to the provided signature.

For GitLab webhooks, the system validates three custom headers:
- `x-gitlab-token`: The webhook secret
- `x-openhands-webhook-id`: The webhook UUID
- `x-openhands-user-id`: The user ID

The system retrieves the expected webhook secret from the database using the webhook UUID and user ID, then compares it to the provided token. This multi-factor verification ensures that only legitimate webhook requests are processed.

When invalid payloads are received, the system returns appropriate HTTP status codes:
- 403 Forbidden for authentication failures
- 400 Bad Request for malformed payloads
- 200 OK for successfully processed but duplicate events

**Section sources**
- [github.py](file://enterprise/server/routes/integration/github.py#L26-L42)
- [gitlab.py](file://enterprise/server/routes/integration/gitlab.py#L21-L32)
- [http_client.py](file://openhands/integrations/protocols/http_client.py#L77-L99)

## Rate Limiting

### Rate Limit Implementation

The OpenHands integration system implements rate limiting to prevent abuse and ensure fair usage of external API resources. The rate limiting system is built on the `limits` library with Redis as the backend storage.

Rate limiters are created using the `create_redis_rate_limiter` function, which accepts a string specifying the rate limits in the format "count/period". For example, "10/second; 100/minute" creates a rate limiter that allows 10 requests per second or 100 requests per minute.

The system applies rate limiting at multiple levels:
- Per-user rate limits
- Per-action rate limits
- Global rate limits

When a rate limit is exceeded, the system raises a `RateLimitException` which is caught by the exception handler and converted to a proper HTTP response with appropriate headers.

```mermaid
flowchart TD
A[Incoming Request] --> B{Rate Limit Check}
B --> |Within Limit| C[Process Request]
B --> |Exceeded Limit| D[Return 429]
C --> E[Update Rate Counter]
D --> F[Add Rate Limit Headers]
F --> G[X-RateLimit-Limit]
F --> H[X-RateLimit-Remaining]
F --> I[X-RateLimit-Reset]
F --> J[Retry-After]
```

**Diagram sources**
- [rate_limit.py](file://enterprise/server/rate_limit.py#L50-L106)
- [rate_limit.py](file://enterprise/server/rate_limit.py#L123-L137)

### Rate Limit Headers

When a rate limit is exceeded, the system includes standard rate limit headers in the response to help clients understand their rate limit status:

- `X-RateLimit-Limit`: The total number of requests allowed in the time window
- `X-RateLimit-Remaining`: The number of requests remaining in the current window
- `X-RateLimit-Reset`: The time at which the rate limit will reset (Unix timestamp)
- `Retry-After`: The number of seconds to wait before retrying the request

These headers follow the convention used by major APIs like GitHub and GitLab, making it easier for clients to implement proper retry logic.

The system also logs rate limit events for monitoring and analysis, allowing administrators to identify patterns of excessive usage and adjust rate limits as needed.

**Section sources**
- [rate_limit.py](file://enterprise/server/rate_limit.py#L32-L48)
- [rate_limit.py](file://enterprise/server/rate_limit.py#L123-L137)

## Configuration Examples

### Repository Access Configuration

To configure repository access for GitHub integration, the following environment variables must be set:

```bash
GITHUB_APP_CLIENT_ID=your_client_id
GITHUB_APP_CLIENT_SECRET=your_client_secret
GITHUB_APP_WEBHOOK_SECRET=your_webhook_secret
GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\nyour_private_key_here\n-----END RSA PRIVATE KEY-----"
```

For GitLab integration, the following environment variables are required:

```bash
GITLAB_APP_CLIENT_ID=your_client_id
GITLAB_APP_CLIENT_SECRET=your_client_secret
```

The system also supports enterprise SSO configuration through Keycloak, which requires additional environment variables:

```bash
KEYCLOAK_SERVER_URL=https://your-keycloak-server/auth
KEYCLOAK_REALM_NAME=your_realm
KEYCLOAK_CLIENT_ID=your_client_id
KEYCLOAK_CLIENT_SECRET=your_client_secret
```

### Webhook Payload Handling

When handling webhook payloads, the system extracts relevant information based on the event type. For GitHub issue comment events, the system processes the payload as follows:

```python
payload_data = await request.json()
installation_id = payload_data.get('installation', {}).get('id')
issue_number = payload_data.get('issue', {}).get('number')
comment_body = payload_data.get('comment', {}).get('body')
user_login = payload_data.get('sender', {}).get('login')
```

For GitLab merge request comment events, the extraction process is similar:

```python
payload_data = await request.json()
object_attributes = payload_data.get('object_attributes', {})
mr_iid = object_attributes.get('iid')
mr_title = object_attributes.get('title')
note_body = payload_data.get('object_attributes', {}).get('note')
user_username = payload_data.get('user', {}).get('username')
```

### GitHub Proxy Usage

The GitHub proxy can be used to make authenticated requests to the GitHub API. To use the proxy for API requests, configure the request to go through the proxy endpoint:

```python
import httpx

async def make_github_request(subdomain, path, headers, data=None):
    url = f"https://{subdomain}.example.com/github-proxy/{subdomain}/{path}"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        return response
```

This allows the system to maintain the authentication context while making requests to the GitHub API on behalf of the user.

**Section sources**
- [constants.py](file://enterprise/server/auth/constants.py#L3-L33)
- [github.py](file://enterprise/server/routes/integration/github.py#L60-L65)
- [gitlab.py](file://enterprise/server/routes/integration/gitlab.py#L49-L50)

## Conclusion

The OpenHands integration API provides a robust and secure framework for connecting with external development platforms like GitHub and GitLab. Through well-defined endpoints, OAuth-based authentication, and event-driven data synchronization, the system enables seamless collaboration between OpenHands and popular code hosting platforms.

The architecture prioritizes security through encrypted token storage, signature verification for webhook payloads, and proper authentication context management. The system also implements comprehensive error handling and rate limiting to ensure reliability and fair usage of resources.

By following the patterns and examples outlined in this documentation, developers can effectively configure and utilize the integration features to enhance their development workflows and leverage the power of OpenHands within their existing development environments.