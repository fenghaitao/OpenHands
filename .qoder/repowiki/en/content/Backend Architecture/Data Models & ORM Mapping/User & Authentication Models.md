# User & Authentication Models

<cite>
**Referenced Files in This Document**   
- [UserSettings](file://enterprise/storage/user_settings.py)
- [AuthTokens](file://enterprise/storage/auth_tokens.py)
- [OfflineTokens](file://enterprise/storage/stored_offline_token.py)
- [APIKey](file://enterprise/storage/api_key.py)
- [auth_token_store.py](file://enterprise/storage/auth_token_store.py)
- [api_key_store.py](file://enterprise/storage/api_key_store.py)
- [keycloak_manager.py](file://enterprise/server/auth/keycloak_manager.py)
- [auth_utils.py](file://enterprise/server/auth/auth_utils.py)
- [user_settings.py](file://enterprise/storage/user_settings.py)
- [stored_settings.py](file://enterprise/storage/stored_settings.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Core Data Models](#core-data-models)
3. [Authentication Token Management](#authentication-token-management)
4. [API Key Authentication](#api-key-authentication)
5. [User Settings and Preferences](#user-settings-and-preferences)
6. [Keycloak Integration](#keycloak-integration)
7. [Data Validation and Security](#data-validation-and-security)
8. [GDPR Compliance and Data Privacy](#gdpr-compliance-and-data-privacy)
9. [Common Authentication Queries](#common-authentication-queries)
10. [Conclusion](#conclusion)

## Introduction

This document provides comprehensive documentation for the user and authentication models in the OpenHands enterprise application. The system implements a robust authentication framework that supports multiple identity providers, API key authentication, and session persistence through various token mechanisms. The core models include UserSettings, AuthTokens, OfflineTokens, and APIKey, which work together to manage user preferences, authentication credentials, and access control.

The authentication system is built around Keycloak for OAuth flows, providing secure user authentication and authorization. User preferences and settings are persisted in the database and retrieved as needed throughout the application lifecycle. The system also implements strict data validation rules and security considerations for storing sensitive authentication data, ensuring compliance with data privacy requirements including GDPR.

**Section sources**
- [UserSettings](file://enterprise/storage/user_settings.py)
- [AuthTokens](file://enterprise/storage/auth_tokens.py)
- [OfflineTokens](file://enterprise/storage/stored_offline_token.py)
- [APIKey](file://enterprise/storage/api_key.py)

## Core Data Models

The authentication system is built on four primary data models that handle different aspects of user authentication and preferences.

### UserSettings Model

The UserSettings model stores user preferences and configuration options. This model contains various fields that define the user's environment and preferences:

```mermaid
erDiagram
USER_SETTINGS {
integer id PK
string keycloak_user_id
string language
string agent
integer max_iterations
string security_analyzer
boolean confirmation_mode
string llm_model
string llm_api_key
string llm_api_key_for_byor
string llm_base_url
integer remote_runtime_resource_factor
boolean enable_default_condenser
integer condenser_max_size
boolean user_consents_to_analytics
float billing_margin
boolean enable_sound_notifications
boolean enable_proactive_conversation_starters
string sandbox_base_container_image
string sandbox_runtime_container_image
integer user_version
datetime accepted_tos
json mcp_config
string search_api_key
string sandbox_api_key
float max_budget_per_task
boolean enable_solvability_analysis
string email
boolean email_verified
string git_user_name
string git_user_email
}
USER_SETTINGS ||--o{ AUTH_TOKENS : "has"
USER_SETTINGS ||--o{ API_KEYS : "has"
USER_SETTINGS ||--o{ OFFLINE_TOKENS : "has"
```

**Diagram sources**
- [user_settings.py](file://enterprise/storage/user_settings.py)

**Section sources**
- [user_settings.py](file://enterprise/storage/user_settings.py)

### AuthTokens Model

The AuthTokens model manages OAuth tokens for various identity providers. It stores access and refresh tokens along with their expiration times:

```mermaid
erDiagram
AUTH_TOKENS {
integer id PK
string keycloak_user_id FK
string identity_provider
string access_token
string refresh_token
bigint access_token_expires_at
bigint refresh_token_expires_at
}
AUTH_TOKENS }o--|| USER_SETTINGS : "belongs to"
```

**Diagram sources**
- [auth_tokens.py](file://enterprise/storage/auth_tokens.py)

**Section sources**
- [auth_tokens.py](file://enterprise/storage/auth_tokens.py)

### OfflineTokens Model

The OfflineTokens model stores long-lived tokens that allow the system to maintain user sessions even when the user is not actively using the application:

```mermaid
erDiagram
OFFLINE_TOKENS {
string user_id PK
string offline_token
datetime created_at
datetime updated_at
}
OFFLINE_TOKENS }o--|| USER_SETTINGS : "belongs to"
```

**Diagram sources**
- [stored_offline_token.py](file://enterprise/storage/stored_offline_token.py)

**Section sources**
- [stored_offline_token.py](file://enterprise/storage/stored_offline_token.py)

### APIKey Model

The APIKey model handles API key authentication for programmatic access to the system:

```mermaid
erDiagram
API_KEYS {
integer id PK
string key UK
string user_id FK
string name
datetime created_at
datetime last_used_at
datetime expires_at
}
API_KEYS }o--|| USER_SETTINGS : "belongs to"
```

**Diagram sources**
- [api_key.py](file://enterprise/storage/api_key.py)

**Section sources**
- [api_key.py](file://enterprise/storage/api_key.py)

## Authentication Token Management

The authentication token management system handles the storage, retrieval, and refresh of OAuth tokens for various identity providers.

### Token Storage and Retrieval

The AuthTokenStore class provides methods for storing and retrieving authentication tokens. When a user authenticates with an identity provider, the access and refresh tokens are stored in the database with their expiration times.

```mermaid
sequenceDiagram
participant Client
participant AuthTokenStore
participant Database
Client->>AuthTokenStore : store_tokens()
AuthTokenStore->>Database : Check for existing record
alt Record exists
Database-->>AuthTokenStore : Return existing record
AuthTokenStore->>Database : Update token values
else Record doesn't exist
Database-->>AuthTokenStore : No record found
AuthTokenStore->>Database : Create new record
end
Database-->>AuthTokenStore : Commit transaction
AuthTokenStore-->>Client : Success
Client->>AuthTokenStore : load_tokens()
AuthTokenStore->>Database : Query for token record
Database-->>AuthTokenStore : Return token record
AuthTokenStore->>Client : Return tokens
```

**Diagram sources**
- [auth_token_store.py](file://enterprise/storage/auth_token_store.py)

**Section sources**
- [auth_token_store.py](file://enterprise/storage/auth_token_store.py)

### Token Refresh Mechanism

The system implements a robust token refresh mechanism that ensures uninterrupted access for users. When tokens are loaded, the system checks their expiration and automatically refreshes them if necessary:

```mermaid
flowchart TD
A[Load Tokens] --> B{Tokens Exist?}
B --> |No| C[Return None]
B --> |Yes| D{Check Expiration}
D --> |Not Expired| E[Return Current Tokens]
D --> |Expired| F[Acquire Row Lock]
F --> G{Refresh Needed?}
G --> |No| H[Return Current Tokens]
G --> |Yes| I[Call Refresh Function]
I --> J[Update Database]
J --> K[Return New Tokens]
style C fill:#f9f,stroke:#333
style E fill:#f9f,stroke:#333
style K fill:#f9f,stroke:#333
```

**Diagram sources**
- [auth_token_store.py](file://enterprise/storage/auth_token_store.py)

**Section sources**
- [auth_token_store.py](file://enterprise/storage/auth_token_store.py)

## API Key Authentication

The API key authentication system allows users to generate and manage API keys for programmatic access to the application.

### API Key Management

The ApiKeyStore class provides a complete API for managing API keys, including creation, validation, and deletion:

```mermaid
classDiagram
class ApiKeyStore {
+generate_api_key(length : int) : str
+create_api_key(user_id : str, name : str, expires_at : datetime) : str
+validate_api_key(api_key : str) : str | None
+delete_api_key(api_key : str) : bool
+delete_api_key_by_id(key_id : int) : bool
+list_api_keys(user_id : str) : list[dict]
+retrieve_mcp_api_key(user_id : str) : str | None
+get_instance() : ApiKeyStore
}
ApiKeyStore --> ApiKey : "uses"
```

**Diagram sources**
- [api_key_store.py](file://enterprise/storage/api_key_store.py)

**Section sources**
- [api_key_store.py](file://enterprise/storage/api_key_store.py)

### API Key Lifecycle

The API key lifecycle includes creation, validation, usage tracking, and expiration:

```mermaid
stateDiagram-v2
[*] --> Created
Created --> Valid : Key is active
Valid --> Expired : Expiration time reached
Valid --> Invalid : Manually deleted
Valid --> Used : Key is used for authentication
Used --> Valid : Update last_used_at
Expired --> [*]
Invalid --> [*]
```

**Diagram sources**
- [api_key_store.py](file://enterprise/storage/api_key_store.py)

**Section sources**
- [api_key_store.py](file://enterprise/storage/api_key_store.py)

## User Settings and Preferences

The user settings system allows users to customize their experience and store preferences across sessions.

### Settings Persistence

User settings are persisted in the database and retrieved when needed. The system supports both current and legacy settings storage:

```mermaid
erDiagram
USER_SETTINGS ||--o{ AUTH_TOKENS : "has"
USER_SETTINGS ||--o{ API_KEYS : "has"
USER_SETTINGS ||--o{ OFFLINE_TOKENS : "has"
USER_SETTINGS ||--o{ USER_SECRETS : "has"
USER_SETTINGS {
integer id PK
string keycloak_user_id
string language
string agent
integer max_iterations
string security_analyzer
boolean confirmation_mode
string llm_model
string llm_api_key
string llm_base_url
integer remote_runtime_resource_factor
boolean enable_default_condenser
float billing_margin
boolean enable_sound_notifications
boolean user_consents_to_analytics
}
USER_SECRETS {
integer id PK
string user_id FK
string name
string value
string description
}
```

**Diagram sources**
- [user_settings.py](file://enterprise/storage/user_settings.py)
- [stored_settings.py](file://enterprise/storage/stored_settings.py)

**Section sources**
- [user_settings.py](file://enterprise/storage/user_settings.py)
- [stored_settings.py](file://enterprise/storage/stored_settings.py)

### Settings Retrieval Flow

The process of retrieving user settings involves checking both the current and legacy storage systems:

```mermaid
flowchart TD
A[Request User Settings] --> B{User ID Available?}
B --> |No| C[Return Default Settings]
B --> |Yes| D[Query UserSettings Table]
D --> E{Record Found?}
E --> |Yes| F[Return Settings]
E --> |No| G[Query Legacy Settings Table]
G --> H{Record Found?}
H --> |Yes| I[Migrate to New Format]
I --> J[Return Settings]
H --> |No| K[Return Default Settings]
style C fill:#f9f,stroke:#333
style F fill:#f9f,stroke:#333
style J fill:#f9f,stroke:#333
style K fill:#f9f,stroke:#333
```

**Diagram sources**
- [user_settings.py](file://enterprise/storage/user_settings.py)
- [stored_settings.py](file://enterprise/storage/stored_settings.py)

**Section sources**
- [user_settings.py](file://enterprise/storage/user_settings.py)
- [stored_settings.py](file://enterprise/storage/stored_settings.py)

## Keycloak Integration

The system integrates with Keycloak for OAuth-based authentication and user management.

### Keycloak Authentication Flow

The Keycloak integration follows the standard OAuth authorization code flow:

```mermaid
sequenceDiagram
participant User
participant Application
participant Keycloak
User->>Application : Initiate Login
Application->>User : Redirect to Keycloak
User->>Keycloak : Enter Credentials
Keycloak-->>User : Authorization Code
User->>Application : Return with Code
Application->>Keycloak : Exchange Code for Tokens
Keycloak-->>Application : Access and Refresh Tokens
Application->>Application : Store Tokens
Application-->>User : Login Complete
```

**Diagram sources**
- [keycloak_manager.py](file://enterprise/server/auth/keycloak_manager.py)

**Section sources**
- [keycloak_manager.py](file://enterprise/server/auth/keycloak_manager.py)

### Keycloak Manager Implementation

The Keycloak manager provides singleton instances for Keycloak administration and authentication:

```mermaid
classDiagram
class KeycloakManager {
+get_keycloak_openid(external : bool) : KeycloakOpenID
+get_keycloak_admin(external : bool) : KeycloakAdmin
}
KeycloakManager --> KeycloakOpenID : "creates"
KeycloakManager --> KeycloakAdmin : "creates"
```

**Diagram sources**
- [keycloak_manager.py](file://enterprise/server/auth/keycloak_manager.py)

**Section sources**
- [keycloak_manager.py](file://enterprise/server/auth/keycloak_manager.py)

## Data Validation and Security

The system implements strict data validation and security measures to protect sensitive authentication data.

### Token Security

Authentication tokens are stored securely with proper expiration handling:

```mermaid
flowchart TD
A[Token Generation] --> B[Encrypt Sensitive Data]
B --> C[Set Proper Expiration]
C --> D[Store in Database]
D --> E[Validate on Access]
E --> F{Token Valid?}
F --> |Yes| G[Use Token]
F --> |No| H[Refresh or Re-authenticate]
style G fill:#f9f,stroke:#333
style H fill:#f9f,stroke:#333
```

**Diagram sources**
- [auth_token_store.py](file://enterprise/storage/auth_token_store.py)

**Section sources**
- [auth_token_store.py](file://enterprise/storage/auth_token_store.py)

### API Key Security

API keys are generated with high entropy and stored securely:

```mermaid
flowchart TD
A[Generate API Key] --> B[Use Cryptographic RNG]
B --> C[Store Hash, Not Plaintext]
C --> D[Set Expiration Policy]
D --> E[Track Usage]
E --> F[Monitor for Abuse]
F --> G[Revoke if Necessary]
style C fill:#f9f,stroke:#333
```

**Diagram sources**
- [api_key_store.py](file://enterprise/storage/api_key_store.py)

**Section sources**
- [api_key_store.py](file://enterprise/storage/api_key_store.py)

## GDPR Compliance and Data Privacy

The system implements features to ensure compliance with GDPR and other data privacy regulations.

### Data Minimization

The system follows data minimization principles by only storing necessary information:

```mermaid
erDiagram
USER_SETTINGS {
integer id PK
string keycloak_user_id
string language
string agent
integer max_iterations
string security_analyzer
boolean confirmation_mode
string llm_model
string llm_base_url
integer remote_runtime_resource_factor
boolean enable_default_condenser
float billing_margin
boolean enable_sound_notifications
boolean user_consents_to_analytics
}
USER_SECRETS {
integer id PK
string user_id FK
string name
string value
string description
}
USER_SETTINGS ||--o{ USER_SECRETS : "has"
```

**Diagram sources**
- [user_settings.py](file://enterprise/storage/user_settings.py)

**Section sources**
- [user_settings.py](file://enterprise/storage/user_settings.py)

### User Consent Management

The system tracks user consent for data processing and analytics:

```mermaid
flowchart TD
A[User Registration] --> B[Present Terms of Service]
B --> C{User Accepts?}
C --> |Yes| D[Record Acceptance Time]
C --> |No| E[Restrict Data Collection]
D --> F[Store accepted_tos Timestamp]
E --> G[Limit Data Processing]
F --> H[Respect User Preferences]
G --> H
style D fill:#f9f,stroke:#333
style G fill:#f9f,stroke:#333
```

**Diagram sources**
- [user_settings.py](file://enterprise/storage/user_settings.py)

**Section sources**
- [user_settings.py](file://enterprise/storage/user_settings.py)

## Common Authentication Queries

This section provides examples of common database queries for user authentication and token validation.

### User Authentication Query

Query to retrieve a user's authentication tokens:

```sql
SELECT 
    access_token,
    refresh_token,
    access_token_expires_at,
    refresh_token_expires_at
FROM auth_tokens
WHERE keycloak_user_id = :user_id
    AND identity_provider = :identity_provider;
```

### Token Validation Query

Query to check if an access token is still valid:

```sql
SELECT 
    CASE 
        WHEN access_token_expires_at > EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) + 30
        THEN TRUE 
        ELSE FALSE 
    END as is_valid
FROM auth_tokens
WHERE keycloak_user_id = :user_id
    AND identity_provider = :identity_provider;
```

### API Key Validation Query

Query to validate an API key and retrieve the associated user:

```sql
SELECT user_id
FROM api_keys
WHERE key = :api_key
    AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
LIMIT 1;
```

### User Settings Query

Query to retrieve a user's settings:

```sql
SELECT *
FROM user_settings
WHERE keycloak_user_id = :user_id;
```

**Section sources**
- [auth_tokens.py](file://enterprise/storage/auth_tokens.py)
- [api_key.py](file://enterprise/storage/api_key.py)
- [user_settings.py](file://enterprise/storage/user_settings.py)

## Conclusion

The OpenHands authentication system provides a comprehensive framework for managing user authentication, preferences, and access control. The system is built on four core models—UserSettings, AuthTokens, OfflineTokens, and APIKey—that work together to provide a secure and flexible authentication experience.

Key features of the system include:
- Integration with Keycloak for OAuth-based authentication
- Support for multiple identity providers
- API key authentication for programmatic access
- Secure token storage and refresh mechanisms
- Comprehensive user settings and preferences
- GDPR compliance and data privacy protections

The system implements robust security measures to protect sensitive authentication data, including proper token expiration handling, secure API key generation, and data minimization principles. The architecture supports both current and legacy settings storage, ensuring backward compatibility while moving toward a more modern data model.

Overall, the authentication system provides a solid foundation for secure user management and access control in the OpenHands enterprise application.