# Frontend Architecture

<cite>
**Referenced Files in This Document**   
- [package.json](file://frontend/package.json)
- [root.tsx](file://frontend/src/root.tsx)
- [routes.ts](file://frontend/src/routes.ts)
- [query-client-config.ts](file://frontend/src/query-client-config.ts)
- [tailwind.config.js](file://frontend/tailwind.config.js)
- [agent-store.ts](file://frontend/src/stores/agent-store.ts)
- [home-store.ts](file://frontend/src/stores/home-store.ts)
- [use-active-conversation.ts](file://frontend/src/hooks/query/use-active-conversation.ts)
- [use-create-conversation.ts](file://frontend/src/hooks/mutation/use-create-conversation.ts)
- [conversation-service.api.ts](file://frontend/src/api/conversation-service/conversation-service.api.ts)
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
The OpenHands frontend architecture is built on React with a component-based design pattern, leveraging modern state management and data fetching techniques. This document provides a comprehensive overview of the frontend architecture, focusing on the React-based implementation, state management with Zustand, data fetching with React Query, and integration patterns with backend services. The architecture follows component-based principles with clear separation of concerns between UI components, state management, and service layers.

## Project Structure

```mermaid
graph TD
A[Frontend] --> B[src]
A --> C[public]
A --> D[__tests__]
A --> E[scripts]
B --> F[api]
B --> G[components]
B --> H[stores]
B --> I[hooks]
B --> J[routes]
B --> K[types]
H --> L[agent-store.ts]
H --> M[home-store.ts]
I --> N[query]
I --> O[mutation]
I --> P[chat]
F --> Q[conversation-service.api.ts]
style A fill:#f9f,stroke:#333
style B fill:#bbf,stroke:#333
```

**Diagram sources**
- [package.json](file://frontend/package.json)
- [src](file://frontend/src)

**Section sources**
- [package.json](file://frontend/package.json)
- [src](file://frontend/src)

## Core Components

The frontend architecture is organized around several core component categories:
- **Stores**: Zustand-based state management for global application state
- **Hooks**: Custom React hooks for data fetching, mutations, and UI logic
- **Services**: API service layer for backend communication
- **Components**: Reusable UI components organized by feature
- **Routes**: React Router-based routing configuration

The architecture follows a clear separation between presentation components and business logic, with hooks serving as the bridge between UI and data layers.

**Section sources**
- [agent-store.ts](file://frontend/src/stores/agent-store.ts)
- [home-store.ts](file://frontend/src/stores/home-store.ts)
- [use-active-conversation.ts](file://frontend/src/hooks/query/use-active-conversation.ts)
- [use-create-conversation.ts](file://frontend/src/hooks/mutation/use-create-conversation.ts)

## Architecture Overview

```mermaid
graph TD
A[UI Components] --> B[React Hooks]
B --> C[React Query]
C --> D[API Services]
D --> E[Backend API]
F[Zustand Stores] --> A
G[React Router] --> A
H[Tailwind CSS] --> A
I[WebSocket] --> A
style A fill:#f9f,stroke:#333
style B fill:#bbf,stroke:#333
style C fill:#bbf,stroke:#333
style D fill:#bbf,stroke:#333
style F fill:#bbf,stroke:#333
style G fill:#bbf,stroke:#333
style H fill:#bbf,stroke:#333
style I fill:#bbf,stroke:#333
```

**Diagram sources**
- [root.tsx](file://frontend/src/root.tsx)
- [routes.ts](file://frontend/src/routes.ts)
- [query-client-config.ts](file://frontend/src/query-client-config.ts)
- [agent-store.ts](file://frontend/src/stores/agent-store.ts)

## Detailed Component Analysis

### State Management with Zustand

The frontend uses Zustand for state management, providing a lightweight and efficient solution for global state. Stores are created using the `create` function and follow a consistent pattern of state definition and action implementation.

```mermaid
classDiagram
class ZustandStore {
+state : object
+actions : object
+create() : Store
+persist() : Middleware
}
class AgentStore {
+curAgentState : AgentState
+setCurrentAgentState(state : AgentState) : void
+reset() : void
}
class HomeStore {
+recentRepositories : GitRepository[]
+addRecentRepository(repo : GitRepository) : void
+clearRecentRepositories() : void
+getRecentRepositories() : GitRepository[]
}
ZustandStore <|-- AgentStore
ZustandStore <|-- HomeStore
HomeStore --> "persist" ZustandStore : uses
```

**Diagram sources**
- [agent-store.ts](file://frontend/src/stores/agent-store.ts)
- [home-store.ts](file://frontend/src/stores/home-store.ts)

### Data Fetching with React Query

The architecture implements React Query for data fetching, caching, and synchronization. The QueryClient is configured with global error handling and toast notifications for user feedback.

```mermaid
sequenceDiagram
participant Component as "UI Component"
participant Hook as "Custom Hook"
participant Query as "React Query"
participant Service as "API Service"
participant Backend as "Backend API"
Component->>Hook : useQuery()/useMutation()
Hook->>Query : query/mutation request
Query->>Query : Check cache
alt Data in cache
Query-->>Hook : Return cached data
else Data not in cache
Query->>Service : fetch data
Service->>Backend : HTTP Request
Backend-->>Service : Response
Service-->>Query : Data
Query->>Query : Update cache
Query-->>Hook : Return data
end
Hook-->>Component : Data/Status
Note over Query,Service : Global error handling with toast notifications
```

**Diagram sources**
- [query-client-config.ts](file://frontend/src/query-client-config.ts)
- [use-active-conversation.ts](file://frontend/src/hooks/query/use-active-conversation.ts)
- [use-create-conversation.ts](file://frontend/src/hooks/mutation/use-create-conversation.ts)

### Component Interaction Patterns

The architecture follows a clear pattern of component interaction, with data flowing from services through hooks to UI components. The MVC pattern is implemented through the separation of concerns between views (components), controllers (hooks), and models (stores and services).

```mermaid
flowchart TD
A[User Interaction] --> B[UI Component]
B --> C[Hook]
C --> D{Data Needed?}
D --> |Yes| E[React Query]
E --> F[API Service]
F --> G[Backend]
G --> F
F --> E
E --> C
C --> H[Zustand Store]
H --> B
D --> |No| I[Use Store Data]
I --> B
B --> J[Render UI]
style A fill:#f9f,stroke:#333
style J fill:#f9f,stroke:#333
```

**Diagram sources**
- [agent-store.ts](file://frontend/src/stores/agent-store.ts)
- [use-active-conversation.ts](file://frontend/src/hooks/query/use-active-conversation.ts)
- [conversation-service.api.ts](file://frontend/src/api/conversation-service/conversation-service.api.ts)

## Dependency Analysis

```mermaid
graph TD
A[React] --> B[Zustand]
A --> C[React Query]
A --> D[React Router]
A --> E[Tailwind CSS]
B --> F[Global State]
C --> G[Data Fetching]
C --> H[Caching]
C --> I[Error Handling]
D --> J[Routing]
E --> K[Styling]
F --> L[UI Components]
G --> L
H --> L
I --> L
J --> L
K --> L
style A fill:#f96,stroke:#333
style B fill:#69f,stroke:#333
style C fill:#69f,stroke:#333
style D fill:#69f,stroke:#333
style E fill:#69f,stroke:#333
```

**Diagram sources**
- [package.json](file://frontend/package.json)
- [root.tsx](file://frontend/src/root.tsx)
- [tailwind.config.js](file://frontend/tailwind.config.js)

## Performance Considerations

The architecture incorporates several performance optimizations:
- React Query's caching mechanism reduces unnecessary API calls
- Zustand's efficient state updates minimize re-renders
- Code splitting through React Router improves initial load time
- Tailwind CSS's utility-first approach enables efficient styling
- WebSocket connections for real-time updates reduce polling frequency

The implementation also includes debouncing, infinite scrolling, and lazy loading patterns to enhance user experience with large datasets.

## Troubleshooting Guide

Common issues and their solutions:
- **State not updating**: Check if Zustand store actions are properly called and state immutability is maintained
- **Data not fetching**: Verify React Query keys and API service endpoints
- **Routing issues**: Check route configuration in routes.ts and component imports
- **Styling problems**: Ensure Tailwind classes are properly applied and dark mode configuration is correct
- **Authentication errors**: Verify 401 error handling in query client configuration

**Section sources**
- [query-client-config.ts](file://frontend/src/query-client-config.ts)
- [agent-store.ts](file://frontend/src/stores/agent-store.ts)
- [routes.ts](file://frontend/src/routes.ts)

## Conclusion

The OpenHands frontend architecture demonstrates a modern React application design with clear separation of concerns, efficient state management, and robust data fetching capabilities. The combination of React, Zustand, React Query, and Tailwind CSS provides a solid foundation for building a responsive and maintainable user interface. The architecture supports scalability through modular component design and efficient data handling patterns, making it well-suited for the application's requirements.