# Getting Started

<cite>
**Referenced Files in This Document**   
- [README.md](file://README.md)
- [docker-compose.yml](file://docker-compose.yml)
- [containers/app/Dockerfile](file://containers/app/Dockerfile)
- [containers/app/entrypoint.sh](file://containers/app/entrypoint.sh)
- [containers/dev/compose.yml](file://containers/dev/compose.yml)
- [containers/dev/Dockerfile](file://containers/dev/Dockerfile)
- [pyproject.toml](file://pyproject.toml)
- [Development.md](file://Development.md)
- [enterprise/README.md](file://enterprise/README.md)
- [openhands/cli/entry.py](file://openhands/cli/entry.py)
- [openhands/server/config/server_config.py](file://openhands/server/config/server_config.py)
- [frontend/src/components/features/settings/git-settings/configure-github-repositories-anchor.tsx](file://frontend/src/components/features/settings/git-settings/configure-github-repositories-anchor.tsx)
- [frontend/src/components/features/waitlist/auth-modal.tsx](file://frontend/src/components/features/waitlist/auth-modal.tsx)
- [frontend/src/routes/git-settings.tsx](file://frontend/src/routes/git-settings.tsx)
- [frontend/src/hooks/query/use-llm-api-key.ts](file://frontend/src/hooks/query/use-llm-api-key.ts)
- [enterprise/migrations/versions/056_add_llm_api_key_for_byor_to_user_settings.py](file://enterprise/migrations/versions/056_add_llm_api_key_for_byor_to_user_settings.py)
- [frontend/src/components/features/settings/api-keys-manager.tsx](file://frontend/src/components/features/settings/api-keys-manager.tsx)
- [openhands/core/const/guide_url.py](file://openhands/core/const/guide_url.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Installation Methods](#installation-methods)
4. [Configuration and Environment Setup](#configuration-and-environment-setup)
5. [Authentication with GitHub/GitLab](#authentication-with-githubgitlab)
6. [Connecting a Repository](#connecting-a-repository)
7. [Basic Usage Patterns](#basic-usage-patterns)
8. [Deployment Scenarios](#deployment-scenarios)
9. [Troubleshooting Common Issues](#troubleshooting-common-issues)
10. [Performance Considerations](#performance-considerations)

## Introduction

OpenHands is a platform for software development agents powered by AI, capable of performing tasks that human developers can do, including modifying code, running commands, browsing the web, calling APIs, and copying code snippets from resources like StackOverflow. This guide provides comprehensive instructions for setting up and using the OpenHands platform, focusing on installation via Docker and docker-compose, environment configuration, and basic usage patterns.

The platform can be accessed through a web interface or CLI, and supports integration with GitHub and GitLab for repository management and authentication. This document covers the complete setup process, from prerequisites to advanced configuration for different deployment scenarios.

**Section sources**
- [README.md](file://README.md#L34-L38)
- [Development.md](file://Development.md#L1-L10)

## Prerequisites

Before installing OpenHands, ensure your system meets the following requirements:

- **Operating System**: Linux, Mac OS, or Windows Subsystem for Linux (WSL) with Ubuntu >= 22.04
- **Docker**: Required for containerized deployment. For macOS users, ensure the default Docker socket is enabled in advanced settings
- **Python**: Version 3.12 required for development and local execution
- **Node.js**: Version 22.x or higher required for frontend development
- **Poetry**: Package manager for Python, version 1.8 or higher
- **System-specific dependencies**:
  - Ubuntu: build-essential (`sudo apt-get install build-essential python3.12-dev`)
  - WSL: netcat (`sudo apt-get install netcat`)

For users without sudo access, conda or mamba can be used to manage packages:

```bash
# Install dependencies using mamba
mamba install python=3.12
mamba install conda-forge::nodejs
mamba install conda-forge::poetry
```

The platform also requires sufficient system resources, with recommended specifications including at least 8GB of RAM and adequate CPU resources for running containerized environments.

**Section sources**
- [Development.md](file://Development.md#L13-L21)
- [README.md](file://README.md#L58-L73)

## Installation Methods

OpenHands can be installed and run using several methods, with Docker being the most straightforward approach for most users.

### CLI Launcher (Recommended)

The recommended installation method uses the CLI launcher with uv, providing better isolation from your project's virtual environment:

```bash
# Install uv (if not already installed)
# Follow instructions at https://docs.astral.sh/uv/getting-started/installation/

# Launch the GUI server
uvx --python 3.12 --from openhands-ai openhands serve

# Or launch the CLI
uvx --python 3.12 --from openhands-ai openhands
```

After launching, OpenHands will be accessible at [http://localhost:3000](http://localhost:3000).

### Docker Installation

OpenHands can be run directly with Docker using the following command:

```bash
docker pull docker.all-hands.dev/all-hands-ai/runtime:0.59-nikolaik

docker run -it --rm --pull=always \
    -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.59-nikolaik \
    -e LOG_ALL_EVENTS=true \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ~/.openhands:/.openhands \
    -p 3000:3000 \
    --add-host host.docker.internal:host-gateway \
    --name openhands-app \
    docker.all-hands.dev/all-hands-ai/openhands:0.59
```

### Docker Compose

For more complex setups, use the provided docker-compose.yml file:

```yaml
services:
  openhands:
    build:
      context: ./
      dockerfile: ./containers/app/Dockerfile
    image: openhands:latest
    container_name: openhands-app-${DATE:-}
    environment:
      - SANDBOX_RUNTIME_CONTAINER_IMAGE=openhands-runtime:local
      - WORKSPACE_MOUNT_PATH=${WORKSPACE_BASE:-$PWD/workspace}
    ports:
      - "3000:3000"
    extra_hosts:
      - "host.docker.internal:host-gateway"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ~/.openhands:/.openhands
      - ${WORKSPACE_BASE:-./workspace}:/opt/workspace_base
      - ./proxy-patch.py:/app/.venv/lib/python3.13/site-packages/sitecustomize.py:ro
```

**Section sources**
- [README.md](file://README.md#L58-L96)
- [docker-compose.yml](file://docker-compose.yml#L2-L36)
- [containers/app/Dockerfile](file://containers/app/Dockerfile#L1-L96)

## Configuration and Environment Setup

Proper configuration is essential for OpenHands to function correctly. The platform uses environment variables and configuration files to manage settings.

### Environment Variables

Key environment variables include:

- `SANDBOX_RUNTIME_CONTAINER_IMAGE`: Specifies the container image for the sandbox environment
- `WORKSPACE_MOUNT_PATH`: Defines the path to mount the workspace
- `LOG_ALL_EVENTS`: When set to true, logs all events for debugging
- `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`: Proxy configuration for network access

### Configuration Files

The main configuration files are:

- **pyproject.toml**: Contains Python dependencies and project metadata
- **docker-compose.yml**: Defines the Docker services and their configurations
- **entrypoint.sh**: Script that runs when the container starts, handling user setup and permissions

The Dockerfile builds a multi-stage image with separate stages for frontend and backend components:

```dockerfile
FROM node:24-slim AS frontend-builder
# Frontend build steps...

FROM python:3.13-slim AS backend-builder
# Backend build steps...

FROM base AS openhands-app
# Final application setup...
```

### Development Environment

For development purposes, a dedicated development container is available:

```bash
make docker-dev
```

This creates a container with all necessary development tools pre-installed, including Docker, Python 3.12, Node.js 22.x, and Poetry.

**Section sources**
- [pyproject.toml](file://pyproject.toml#L1-L222)
- [containers/app/entrypoint.sh](file://containers/app/entrypoint.sh#L1-L74)
- [containers/dev/Dockerfile](file://containers/dev/Dockerfile#L1-L125)

## Authentication with GitHub/GitLab

OpenHands supports authentication with GitHub and GitLab through OAuth integration.

### GitHub Authentication

To authenticate with GitHub:

1. Navigate to the authentication modal in the OpenHands interface
2. Click the "Connect to GitHub" button
3. You will be redirected to GitHub's OAuth authorization page
4. Grant the necessary permissions to the OpenHands application
5. Upon successful authentication, you'll be redirected back to OpenHands

The frontend component handles the authentication flow:

```typescript
function handleGitHubAuth() {
  if (githubAuthUrl) {
    window.location.href = githubAuthUrl;
  }
}
```

### GitLab Authentication

GitLab authentication follows a similar process:

1. Click the "Connect to GitLab" button in the authentication modal
2. You will be redirected to GitLab's OAuth authorization page
3. Grant the necessary permissions to the OpenHands application
4. Upon successful authentication, you'll be redirected back to OpenHands

### Authentication Configuration

The authentication process is configured through environment variables and server settings:

- `GITHUB_APP_CLIENT_ID`: Client ID for the GitHub OAuth application
- `OPENHANDS_CONFIG_CLS`: Configuration class that determines authentication behavior
- `APP_MODE`: Determines whether the application runs in OSS or SaaS mode

In enterprise mode, authentication is handled through Keycloak, providing additional security features and user management capabilities.

**Section sources**
- [frontend/src/components/features/waitlist/auth-modal.tsx](file://frontend/src/components/features/waitlist/auth-modal.tsx#L48-L74)
- [openhands/server/config/server_config.py](file://openhands/server/config/server_config.py#L8-L34)
- [enterprise/README.md](file://enterprise/README.md#L27-L48)

## Connecting a Repository

After authentication, you can connect repositories from GitHub or GitLab to OpenHands.

### GitHub Repository Connection

To connect a GitHub repository:

1. After authenticating with GitHub, navigate to the Git settings page
2. Click the "Configure Repositories" button
3. You will be redirected to GitHub's application installation page
4. Select the repositories you want to connect to OpenHands
5. Complete the installation process

The frontend component for repository configuration:

```typescript
function ConfigureGitHubRepositoriesAnchor({ slug }: ConfigureGitHubRepositoriesAnchorProps) {
  return (
    <BrandButton
      onClick={() =>
        window.open(
          `https://github.com/apps/${slug}/installations/new`,
          "_blank",
          "noreferrer noopener"
        )
      }
    >
      {t(I18nKey.GITHUB$CONFIGURE_REPOS)}
    </BrandButton>
  );
}
```

### GitLab Repository Connection

For GitLab repositories:

1. After authenticating with GitLab, navigate to the Git settings page
2. The connected repositories will be displayed in the interface
3. You can now use OpenHands to interact with these repositories

### Repository Management

Once connected, repositories can be managed through the OpenHands interface:

- View repository files and directory structure
- Create and modify files
- Commit changes directly to the repository
- Create pull requests
- Review and comment on existing pull requests

The platform stores repository connection information in the user settings, allowing for persistent connections across sessions.

**Section sources**
- [frontend/src/components/features/settings/git-settings/configure-github-repositories-anchor.tsx](file://frontend/src/components/features/settings/git-settings/configure-github-repositories-anchor.tsx#L1-L32)
- [frontend/src/routes/git-settings.tsx](file://frontend/src/routes/git-settings.tsx#L23-L184)

## Basic Usage Patterns

OpenHands can be used through both web interface and CLI access, providing flexibility for different workflows.

### Web Interface Usage

The web interface provides a user-friendly way to interact with OpenHands:

1. Access the interface at [http://localhost:3000](http://localhost:3000)
2. Configure your LLM provider and add an API key
3. Select a repository to work with
4. Start a conversation with the AI agent
5. Issue commands and receive responses

The interface supports various features including:
- File browsing and editing
- Terminal access
- Web browsing capabilities
- Conversation history
- Settings management

### CLI Usage

For scriptable and headless operations, OpenHands provides a CLI interface:

```bash
# Start the CLI interface
openhands

# Or use the uv launcher
uvx --python 3.12 --from openhands-ai openhands
```

The CLI entry point handles command parsing and execution:

```python
def main():
    """Main entry point with subcommand support and backward compatibility."""
    if handle_fast_commands():
        sys.exit(0)
    
    from openhands.core.config import get_cli_parser
    parser = get_cli_parser()
    
    if args.command == 'serve':
        from openhands.cli.gui_launcher import launch_gui_server
        launch_gui_server(mount_cwd=args.mount_cwd, gpu=args.gpu)
    elif args.command == 'cli' or args.command is None:
        from openhands.cli.main import run_cli_command
        run_cli_command(args)
```

### Starting an Agent Conversation

To start a basic agent conversation:

1. Select an LLM provider (Anthropic's Claude Sonnet 4.5 is recommended)
2. Add your API key for the selected provider
3. Choose a repository to work with
4. Enter your first command or question
5. The agent will respond with a plan and begin executing tasks

The agent can perform various tasks including:
- Code modification and refactoring
- Bug fixing
- Feature implementation
- Documentation generation
- Test creation

**Section sources**
- [openhands/cli/entry.py](file://openhands/cli/entry.py#L1-L55)
- [README.md](file://README.md#L106-L113)

## Deployment Scenarios

OpenHands supports different deployment scenarios for development and production environments.

### Development Deployment

For development purposes, use the development container:

```bash
make docker-dev
```

This creates a container with all development tools and dependencies pre-installed, allowing for easy code modification and testing.

### Production Deployment

For production deployment, consider the following:

- Use hardened Docker installation for security
- Restrict network binding to prevent unauthorized access
- Implement proper authentication and authorization
- Monitor resource usage and performance
- Set up proper logging and monitoring

The production deployment should use the official Docker images and follow security best practices.

### Configuration for Different Scenarios

Environment-specific configuration can be achieved through environment variables:

```yaml
# Development configuration
SANDBOX_USER_ID: 1234
WORKSPACE_MOUNT_PATH: $PWD/workspace
LOG_ALL_EVENTS: true

# Production configuration
SANDBOX_RUNTIME_CONTAINER_IMAGE: production-runtime:latest
FILE_STORE: s3
FILE_STORE_PATH: s3://bucket-name/openhands
```

The enterprise version provides additional configuration options for multi-tenant environments and commercial deployments.

**Section sources**
- [containers/dev/compose.yml](file://containers/dev/compose.yml#L2-L40)
- [enterprise/README.md](file://enterprise/README.md#L1-L57)
- [README.md](file://README.md#L103-L104)

## Troubleshooting Common Issues

This section addresses common setup issues and their solutions.

### Docker-Related Issues

**Issue**: Permission denied when accessing Docker socket
**Solution**: Ensure your user is part of the docker group:
```bash
sudo usermod -aG docker $USER
```

**Issue**: Container fails to start with "Cannot connect to the Docker daemon"
**Solution**: Ensure Docker service is running:
```bash
sudo systemctl start docker
```

### Network and Proxy Issues

**Issue**: Unable to pull Docker images due to network restrictions
**Solution**: Configure proxy settings in docker-compose.yml:
```yaml
environment:
  - http_proxy=${http_proxy:-}
  - https_proxy=${https_proxy:-}
  - no_proxy=${no_proxy:-localhost,127.0.0.1}
```

### Authentication Issues

**Issue**: GitHub authentication fails
**Solution**: Verify that the GitHub App is properly configured and that you have the necessary permissions.

**Issue**: Token expiration
**Solution**: The enterprise version automatically handles token refresh through the GitHubTokenManager.

### Performance Issues

**Issue**: Slow response times
**Solution**: Ensure adequate system resources and consider using a more powerful LLM provider.

### Configuration Issues

**Issue**: Custom configuration not being applied
**Solution**: Remember that configuration priority is: Environment variables > config.toml variables > default variables

For additional troubleshooting guidance, refer to the comprehensive troubleshooting guide available at [https://docs.all-hands.dev/usage/troubleshooting](https://docs.all-hands.dev/usage/troubleshooting).

**Section sources**
- [containers/app/entrypoint.sh](file://containers/app/entrypoint.sh#L11-L19)
- [docker-compose.yml](file://docker-compose.yml#L8-L10)
- [openhands/core/const/guide_url.py](file://openhands/core/const/guide_url.py#L1)

## Performance Considerations

Proper resource allocation and configuration are essential for optimal OpenHands performance.

### Resource Requirements

Minimum recommended specifications:
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 20GB free space
- **Network**: Stable internet connection for LLM API access

### Performance Optimization

To optimize performance:

1. **Use appropriate resource factors**: The platform supports resource scaling through the DEFAULT_RUNTIME_RESOURCE_FACTOR environment variable
2. **Configure the sandbox environment**: Use optimized container images for faster startup times
3. **Implement caching**: The development container includes cache volumes to speed up repeated operations
4. **Optimize LLM configuration**: Choose appropriate models and configure rate limiting to prevent throttling

### Monitoring and Scaling

Monitor the following performance metrics:
- **Response time**: Time taken for the agent to respond to queries
- **Resource utilization**: CPU, memory, and disk usage
- **Error rates**: Frequency of failed operations
- **Throughput**: Number of tasks completed per unit time

For production deployments, consider implementing:
- Load balancing for multiple instances
- Auto-scaling based on demand
- Comprehensive monitoring and alerting
- Regular performance testing and optimization

The platform includes built-in support for performance monitoring through the MonitoringListener class and integration with analytics tools.

**Section sources**
- [evaluation/benchmarks/nocode_bench/resource/mapping.py](file://evaluation/benchmarks/nocode_bench/resource/mapping.py#L1-L39)
- [enterprise/storage/user_settings.py](file://enterprise/storage/user_settings.py#L1-L30)
- [enterprise/migrations/versions/072_add_condenser_max_size_to_user_settings.py](file://enterprise/migrations/versions/072_add_condenser_max_size_to_user_settings.py#L1-L28)