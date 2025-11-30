# Authentication Middleware

<cite>
**Referenced Files in This Document**   
- [middleware.py](file://enterprise/server/middleware.py)
- [user_auth.py](file://openhands/server/user_auth/user_auth.py)
- [saas_user_auth.py](file://enterprise/server/auth/saas_user_auth.py)
- [auth_error.py](file://enterprise/server/auth/auth_error.py)
- [token_manager.py](file://enterprise/server/auth/token_manager.py)
- [dependencies.py](file://openhands/server/dependencies.py)
- [auth.py](file://enterprise/server/routes/auth.py)
- [api_key_store.py](file://enterprise/storage/api_key_store.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Authentication Middleware Architecture](#authentication-middleware-architecture)
3. [Request Flow Through Middleware](#request-flow-through-middleware)
4. [Authentication Methods and Validation Strategies](#authentication-methods-and-validation-strategies)
5. [Exception Handling and Error Responses](#exception-handling-and-error-responses)
6. [Integration with FastAPI Dependency System](#integration-with-fastapi-dependency-system)
7. [User Context Injection](#user-context-injection)
8. [Performance Considerations](#performance-considerations)
9. [Conclusion](#conclusion)

## Introduction

The authentication middleware layer in the OpenHands system provides a comprehensive security framework for protecting API endpoints and ensuring authorized access to resources. This documentation details the implementation of the authentication system, which supports multiple authentication methods including session cookies, API keys, and Bearer tokens. The middleware intercepts incoming HTTP requests, validates authentication state, and injects user context into the request flow for downstream processing.

The system is designed with extensibility in mind, allowing for custom authentication implementations through the `UserAuth` abstract base class. The authentication flow is integrated with Keycloak for identity management, with additional support for GitHub, GitLab, and Bitbucket integrations. The middleware handles token validation, refresh operations, and proper error responses for various authentication failure scenarios.

**Section sources**
- [middleware.py](file://enterprise/server/middleware.py#L1-L175)
- [user_auth.py](file://openhands/server/user_auth/user_auth.py#L1-L107)

## Authentication Middleware Architecture

The authentication system is built around a middleware-based architecture that intercepts requests before they reach the application endpoints. The core component is the `SetAuthCookieMiddleware` class, which handles the authentication lifecycle including token validation, refresh operations, and cookie management.

```mermaid
classDiagram
class SetAuthCookieMiddleware {
+__call__(request, call_next)
+_check_tos(request)
+_get_user_auth(request)
+_logout(request)
+_should_attach(request)
}
class UserAuth {
+get_user_id()
+get_user_email()
+get_access_token()
+get_provider_tokens()
+get_user_settings_store()
+get_secrets_store()
+get_user_secrets()
+get_auth_type()
+get_instance(request)
+get_for_user(user_id)
}
class SaasUserAuth {
+refresh_token : SecretStr
+user_id : str
+email : str | None
+email_verified : bool | None
+access_token : SecretStr | None
+provider_tokens : PROVIDER_TOKEN_TYPE | None
+refreshed : bool
+settings_store : SaasSettingsStore | None
+secrets_store : SaasSecretsStore | None
+_settings : Settings | None
+_user_secrets : UserSecrets | None
+accepted_tos : bool | None
+auth_type : AuthType
+get_user_id()
+get_user_email()
+refresh()
+_is_token_expired(token)
+get_auth_type()
+get_user_settings()
+get_secrets_store()
+get_user_secrets()
+get_access_token()
+get_provider_tokens()
+get_user_settings_store()
+get_instance(request)
+get_for_user(user_id)
}
class AuthError {
+__init__(message)
}
class NoCredentialsError {
+__init__(message)
}
class EmailNotVerifiedError {
+__init__(message)
}
class BearerTokenError {
+__init__(message)
}
class CookieError {
+__init__(message)
}
class TosNotAcceptedError {
+__init__(message)
}
class ExpiredError {
+__init__(message)
}
SetAuthCookieMiddleware --> UserAuth : "uses"
SetAuthCookieMiddleware --> SaasUserAuth : "uses"
SetAuthCookieMiddleware --> AuthError : "handles"
UserAuth <|-- SaasUserAuth : "extends"
AuthError <|-- NoCredentialsError : "extends"
AuthError <|-- EmailNotVerifiedError : "extends"
AuthError <|-- BearerTokenError : "extends"
AuthError <|-- CookieError : "extends"
AuthError <|-- TosNotAcceptedError : "extends"
AuthError <|-- ExpiredError : "extends"
```

**Diagram sources**
- [middleware.py](file://enterprise/server/middleware.py#L26-L175)
- [user_auth.py](file://openhands/server/user_auth/user_auth.py#L18-L87)
- [saas_user_auth.py](file://enterprise/server/auth/saas_user_auth.py#L43-L324)
- [auth_error.py](file://enterprise/server/auth/auth_error.py#L1-L41)

## Request Flow Through Middleware

The authentication middleware processes incoming requests through a well-defined flow that ensures proper authentication state validation before allowing access to protected resources. The request flow begins with the `SetAuthCookieMiddleware.__call__` method, which serves as the entry point for all incoming requests.

```mermaid
sequenceDiagram
participant Client as "Client Application"
participant Middleware as "SetAuthCookieMiddleware"
participant UserAuth as "UserAuth System"
participant TokenManager as "TokenManager"
participant Response as "Response Handler"
Client->>Middleware : HTTP Request
activate Middleware
Middleware->>Middleware : Extract keycloak_auth cookie
alt No Cookie Present
Middleware->>UserAuth : Check Bearer token or API key
UserAuth-->>Middleware : Authentication result
else Cookie Present
Middleware->>Middleware : Validate authentication state
Middleware->>Middleware : Check Terms of Service acceptance
Middleware->>UserAuth : Get user authentication instance
UserAuth-->>Middleware : SaasUserAuth object
alt Token Refresh Required
Middleware->>TokenManager : Refresh tokens
TokenManager-->>Middleware : New tokens
Middleware->>Middleware : Update refreshed flag
end
end
Middleware->>Response : Call next middleware/handler
Response-->>Middleware : Response object
alt Token Was Refreshed
Middleware->>Middleware : Update auth cookie
Middleware->>Middleware : Schedule GitLab repo sync
end
alt Email Not Verified
Middleware->>Response : Return 403 Forbidden
else Authentication Failed
Middleware->>Response : Return 401 Unauthorized
Middleware->>Middleware : Clear auth cookie if needed
end
Middleware-->>Client : HTTP Response
deactivate Middleware
```

**Diagram sources**
- [middleware.py](file://enterprise/server/middleware.py#L32-L97)
- [saas_user_auth.py](file://enterprise/server/auth/saas_user_auth.py#L207-L225)
- [token_manager.py](file://enterprise/server/auth/token_manager.py#L589-L599)

## Authentication Methods and Validation Strategies

The authentication system supports multiple authentication methods, each with its own validation strategy. The system determines the appropriate validation approach based on the authentication credentials provided in the request. The primary authentication methods include session cookies, Bearer tokens, and API keys.

```mermaid
flowchart TD
Start([Request Received]) --> ExtractAuth["Extract Authentication Credentials"]
ExtractAuth --> HasCookie{"Cookie Present?"}
HasCookie --> |Yes| ValidateCookie["Validate Session Cookie"]
HasCookie --> |No| HasBearer{"Bearer Token Present?"}
HasBearer --> |Yes| ValidateBearer["Validate Bearer Token"]
HasBearer --> |No| HasAPIKey{"API Key Present?"}
HasAPIKey --> |Yes| ValidateAPIKey["Validate API Key"]
HasAPIKey --> |No| NoCredentials["No Credentials Provided"]
ValidateCookie --> DecodeJWT["Decode JWT Token"]
DecodeJWT --> VerifySignature["Verify JWT Signature"]
VerifySignature --> ExtractUserInfo["Extract User Information"]
ExtractUserInfo --> CreateSaasUserAuth["Create SaasUserAuth Instance"]
ValidateBearer --> ExtractToken["Extract Bearer Token"]
ExtractToken --> ValidateAPIKeyStore["Validate Against API Key Store"]
ValidateAPIKeyStore --> LoadOfflineToken["Load Offline Token"]
LoadOfflineToken --> CreateSaasUserAuth
ValidateAPIKey --> ExtractHeader["Extract X-Session-API-Key Header"]
ExtractHeader --> CheckSessionKey["Check Against SESSION_API_KEY"]
CheckSessionKey --> CreateSaasUserAuth
NoCredentials --> RaiseNoCredentialsError["Raise NoCredentialsError"]
VerifySignature --> |Invalid| RaiseAuthError["Raise AuthError"]
ValidateAPIKeyStore --> |Invalid| RaiseBearerTokenError["Raise BearerTokenError"]
CheckSessionKey --> |Invalid| RaiseAuthError
CreateSaasUserAuth --> StoreInRequest["Store UserAuth in Request State"]
StoreInRequest --> ContinueProcessing["Continue Request Processing"]
RaiseNoCredentialsError --> ContinueProcessing
RaiseAuthError --> ContinueProcessing
RaiseBearerTokenError --> ContinueProcessing
```

**Diagram sources**
- [middleware.py](file://enterprise/server/middleware.py#L102-L149)
- [saas_user_auth.py](file://enterprise/server/auth/saas_user_auth.py#L207-L225)
- [dependencies.py](file://openhands/server/dependencies.py#L10-L17)
- [api_key_store.py](file://enterprise/storage/api_key_store.py#L49-L72)

## Exception Handling and Error Responses

The authentication middleware implements comprehensive exception handling for various authentication failure scenarios. When authentication validation fails, the middleware catches specific exception types and returns appropriate HTTP status codes and error responses to the client.

```mermaid
stateDiagram-v2
[*] --> ProcessRequest
ProcessRequest --> ValidateAuth : "Extract credentials"
ValidateAuth --> AuthSuccess : "Valid credentials"
AuthSuccess --> ContinueRequest : "Continue processing"
ValidateAuth --> NoCredentials : "No credentials provided"
NoCredentials --> Return401 : "Return 401 Unauthorized"
ValidateAuth --> InvalidCookie : "Invalid cookie"
InvalidCookie --> Return401 : "Return 401 Unauthorized"
Return401 --> ClearCookie : "Clear auth cookie"
ValidateAuth --> ExpiredToken : "Expired token"
ExpiredToken --> Return401 : "Return 401 Unauthorized"
ExpiredToken --> ClearCookie
ValidateAuth --> EmailNotVerified : "Email not verified"
EmailNotVerified --> Return403 : "Return 403 Forbidden"
ValidateAuth --> TosNotAccepted : "Terms of Service not accepted"
TosNotAccepted --> Return403 : "Return 403 Forbidden"
ValidateAuth --> GeneralAuthError : "General authentication error"
GeneralAuthError --> Return401 : "Return 401 Unauthorized"
GeneralAuthError --> ClearCookie
ContinueRequest --> [*]
Return401 --> [*]
Return403 --> [*]
ClearCookie --> Return401
```

The system defines several specific exception types that inherit from the base `AuthError` class:

- **NoCredentialsError**: Raised when no authentication credentials are provided in the request
- **EmailNotVerifiedError**: Raised when the user's email address has not been verified
- **BearerTokenError**: Raised when there is an error decoding or validating a Bearer token
- **CookieError**: Raised when there is an error decoding or validating the authentication cookie
- **TosNotAcceptedError**: Raised when the user has not accepted the Terms of Service
- **ExpiredError**: Raised when an authentication token has expired

Each exception type triggers a specific error response with the appropriate HTTP status code (401 for unauthorized access, 403 for forbidden access) and a JSON response body containing an error message.

**Section sources**
- [middleware.py](file://enterprise/server/middleware.py#L69-L97)
- [auth_error.py](file://enterprise/server/auth/auth_error.py#L1-L41)

## Integration with FastAPI Dependency System

The authentication system integrates seamlessly with FastAPI's dependency injection system, allowing protected routes to declare authentication requirements through dependency parameters. The system provides several mechanisms for route protection, including direct middleware application and dependency-based authentication checks.

```mermaid
classDiagram
class APIRouter {
+prefix : str
+dependencies : list[Depends]
}
class Depends {
+dependency : Callable
}
class check_session_api_key {
+session_api_key : str | None
}
class get_user_auth {
+request : Request
}
class get_for_user {
+user_id : str
}
APIRouter --> Depends : "has"
Depends --> check_session_api_key : "references"
Depends --> get_user_auth : "references"
Depends --> get_for_user : "references"
get_user_auth --> Request : "takes"
get_for_user --> str : "takes"
check_session_api_key --> str : "takes"
class ProtectedRoute {
+@app.get("/protected", dependencies=[Depends(get_user_auth)])
+def protected_endpoint(user_auth : UserAuth = Depends(get_user_auth))
}
ProtectedRoute --> APIRouter : "uses"
ProtectedRoute --> get_user_auth : "depends on"
```

The integration works through several key components:

1. **Dependency Functions**: The system provides dependency functions like `get_user_auth` and `get_for_user` that can be used as FastAPI dependencies in route definitions.

2. **Session API Key Protection**: The `check_session_api_key` function validates the `X-Session-API-Key` header against an environment variable, providing an additional layer of protection for specific endpoints.

3. **Route-Level Protection**: API routers can be configured with dependencies that apply to all routes within that router, ensuring consistent authentication requirements across related endpoints.

4. **Parameter-Level Injection**: Routes can request the authenticated user context directly as a parameter, with FastAPI automatically resolving the dependency through the `get_user_auth` function.

This integration allows for flexible security configurations, where different routes or route groups can have different authentication requirements based on their sensitivity and intended use.

**Section sources**
- [dependencies.py](file://openhands/server/dependencies.py#L10-L24)
- [user_auth.py](file://openhands/server/user_auth/user_auth.py#L89-L106)
- [auth.py](file://enterprise/server/routes/auth.py#L398-L401)

## User Context Injection

The authentication middleware injects user context into the request flow, making authenticated user information available to downstream route handlers and services. This is achieved through the `UserAuth` abstraction, which provides a consistent interface for accessing user-related data regardless of the authentication method used.

```mermaid
classDiagram
class Request {
+state : State
+cookies : dict
+headers : dict
}
class UserAuth {
+get_user_id()
+get_user_email()
+get_access_token()
+get_provider_tokens()
+get_user_settings()
+get_secrets_store()
+get_user_secrets()
}
class SaasUserAuth {
+user_id : str
+email : str
+access_token : SecretStr
+provider_tokens : dict
+settings : Settings
+secrets : UserSecrets
}
class Settings {
+email : str
+email_verified : bool
+accepted_tos : datetime | None
+user_version : int
}
class UserSecrets {
+provider_tokens : dict
}
Request --> UserAuth : "stores in state"
UserAuth <|-- SaasUserAuth : "implements"
SaasUserAuth --> Settings : "has"
SaasUserAuth --> UserSecrets : "has"
SaasUserAuth --> SettingsStore : "uses"
SaasUserAuth --> SecretsStore : "uses"
class RouteHandler {
+def my_route(user_auth : UserAuth = Depends(get_user_auth))
}
RouteHandler --> UserAuth : "depends on"
```

The user context injection process works as follows:

1. When a request is received, the middleware checks for authentication credentials and validates them.

2. If authentication is successful, an instance of `SaasUserAuth` (or another `UserAuth` implementation) is created and stored in the request state.

3. Subsequent route handlers can access the authenticated user context by declaring a dependency on the `get_user_auth` function.

4. The `UserAuth` interface provides methods to access various aspects of the user's context, including:
   - User identifier and email address
   - Access tokens for the main authentication system
   - Provider tokens for integrated services (GitHub, GitLab, etc.)
   - User settings and preferences
   - User secrets and API keys

5. The system implements lazy loading and caching for expensive operations like database queries, ensuring that user data is only retrieved when needed and reused within the same request context.

This approach provides a clean separation between authentication concerns and business logic, allowing route handlers to focus on their primary functionality while having access to the authenticated user's context.

**Section sources**
- [user_auth.py](file://openhands/server/user_auth/user_auth.py#L35-L77)
- [saas_user_auth.py](file://enterprise/server/auth/saas_user_auth.py#L43-L205)

## Performance Considerations

The authentication system incorporates several performance optimizations to minimize overhead and reduce database queries during the authentication validation process. These optimizations are critical for maintaining responsive API performance, especially under high load conditions.

### Caching Mechanisms

The system implements multiple levels of caching to avoid redundant operations:

1. **Request-Scoped Caching**: User authentication instances are cached within the request state, ensuring that multiple calls to retrieve the same user's authentication context within a single request do not result in redundant database queries.

2. **Token Expiration Checking**: Before attempting to refresh tokens, the system checks token expiration times by decoding the JWT payload without signature verification, avoiding unnecessary network calls to the authentication server.

3. **Rate Limiting**: The system implements rate limiting at the middleware level to prevent abuse and protect backend services from excessive authentication requests.

### Database Query Optimization

The authentication flow is designed to minimize database interactions:

1. **Lazy Loading**: User settings and secrets are only loaded when explicitly requested through their respective methods, rather than being eagerly loaded for every authenticated request.

2. **Batched Operations**: When multiple pieces of user information are needed, the system attempts to retrieve them in a single database query where possible.

3. **Connection Pooling**: The system leverages SQLAlchemy's connection pooling to reuse database connections, reducing the overhead of establishing new connections for each authentication operation.

### Asynchronous Operations

All authentication operations are implemented asynchronously to prevent blocking the event loop:

1. **Non-Blocking I/O**: Network requests to external services (Keycloak, GitHub, GitLab) are performed asynchronously using `httpx.AsyncClient`.

2. **Background Tasks**: Certain operations, such as GitLab repository synchronization, are scheduled as background tasks to avoid delaying the main request response.

3. **Concurrent Validation**: When multiple validation steps are required, they are performed concurrently where possible to reduce overall latency.

These performance considerations ensure that the authentication middleware adds minimal overhead to request processing while maintaining robust security guarantees.

**Section sources**
- [saas_user_auth.py](file://enterprise/server/auth/saas_user_auth.py#L99-L120)
- [token_manager.py](file://enterprise/server/auth/token_manager.py#L288-L327)
- [middleware.py](file://enterprise/server/middleware.py#L218-L224)

## Conclusion

The authentication middleware layer in the OpenHands system provides a robust, extensible framework for securing API endpoints and managing user authentication. By supporting multiple authentication methods and integrating seamlessly with FastAPI's dependency system, the middleware offers flexibility in security configuration while maintaining a consistent interface for authenticated user context.

Key features of the authentication system include:

- Support for multiple authentication methods (session cookies, Bearer tokens, API keys)
- Comprehensive exception handling with appropriate HTTP status codes
- Seamless integration with FastAPI's dependency injection system
- Efficient user context injection for downstream route handlers
- Performance optimizations including caching and asynchronous operations

The system's modular design, centered around the `UserAuth` abstract base class, allows for easy extension and customization to meet specific security requirements. The implementation demonstrates best practices in authentication middleware design, balancing security, performance, and developer experience.