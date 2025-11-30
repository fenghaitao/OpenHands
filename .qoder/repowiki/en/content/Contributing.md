# Contributing

<cite>
**Referenced Files in This Document**   
- [CONTRIBUTING.md](file://CONTRIBUTING.md)
- [Development.md](file://Development.md)
- [README.md](file://README.md)
- [ISSUE_TRIAGE.md](file://ISSUE_TRIAGE.md)
- [COMMUNITY.md](file://COMMUNITY.md)
- [pyproject.toml](file://pyproject.toml)
- [dev_config/python/ruff.toml](file://dev_config/python/ruff.toml)
- [dev_config/python/mypy.ini](file://dev_config/python/mypy.ini)
- [pytest.ini](file://pytest.ini)
- [containers/dev/compose.yml](file://containers/dev/compose.yml)
- [frontend/README.md](file://frontend/README.md)
- [openhands/README.md](file://openhands/README.md)
- [evaluation/README.md](file://evaluation/README.md)
- [tests/unit/README.md](file://tests/unit/README.md)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Development Workflow](#development-workflow)
3. [Setting Up the Development Environment](#setting-up-the-development-environment)
4. [Running Tests](#running-tests)
5. [Submitting Pull Requests](#submitting-pull-requests)
6. [Code Style Guidelines](#code-style-guidelines)
7. [Testing Requirements](#testing-requirements)
8. [Review Process](#review-process)
9. [Common Contribution Scenarios](#common-contribution-scenarios)
10. [Issue Triage and Feature Requests](#issue-triage-and-feature-requests)
11. [Community Participation](#community-participation)
12. [Contribution Prerequisites and Tooling Requirements](#contribution-prerequisites-and-tooling-requirements)
13. [Development Best Practices](#development-best-practices)
14. [Troubleshooting Development Environment Issues](#troubleshooting-development-environment-issues)

## Introduction

This guide provides comprehensive information on how to contribute to the OpenHands project. OpenHands is an open platform for AI software developers as generalist agents, enabling AI agents to perform software development tasks such as modifying code, running commands, browsing the web, and calling APIs.

The OpenHands community welcomes contributions from everyone, whether you're a developer, researcher, or simply enthusiastic about advancing the field of software engineering with AI. This document outlines the development workflow, contribution guidelines, code style requirements, testing procedures, and review processes to help you get started with contributing to the project.

**Section sources**
- [CONTRIBUTING.md](file://CONTRIBUTING.md#L1-L124)
- [README.md](file://README.md#L1-L185)

## Development Workflow

The development workflow for OpenHands follows a structured process that enables contributors to effectively participate in the project. The workflow begins with setting up the development environment, followed by making changes to the codebase, running tests, and submitting pull requests for review.

The core development cycle involves:
1. Forking the repository and creating a feature branch
2. Making changes to implement new features, fix bugs, or improve documentation
3. Running tests locally to ensure code quality
4. Committing changes with descriptive messages
5. Submitting a pull request for review
6. Addressing feedback from maintainers
7. Merging the pull request after approval

This workflow ensures that all contributions go through a thorough review process, maintaining the quality and stability of the codebase. The project uses GitHub for issue tracking, pull requests, and code reviews, with continuous integration tests running on all pull requests to verify code quality.

**Section sources**
- [CONTRIBUTING.md](file://CONTRIBUTING.md#L63-L124)
- [Development.md](file://Development.md#L1-L205)

## Setting Up the Development Environment

To set up the development environment for OpenHands, you need to install the required dependencies and configure your development setup. The project provides detailed instructions for setting up the environment on Linux, Mac OS, or Windows using WSL.

### Prerequisites

The following prerequisites are required for development:

- Linux, Mac OS, or WSL on Windows (Ubuntu >= 22.04)
- Docker
- Python 3.12
- NodeJS >= 22.x
- Poetry >= 1.8
- OS-specific dependencies:
  - Ubuntu: build-essential (`sudo apt-get install build-essential python3.12-dev`)
  - WSL: netcat (`sudo apt-get install netcat`)

### Development Setup

The recommended way to set up the development environment is by using the provided Makefile targets:

```bash
make build
```

This command builds the project, sets up the environment, and installs all dependencies. After building, you can configure the language model by running:

```bash
make setup-config
```

This prompts you to enter the LLM API key, model name, and other variables. Once configured, you can run the application using:

```bash
make run
```

This starts both the backend and frontend servers. Alternatively, you can start them individually:

```bash
make start-backend
make start-frontend
```

For developers who prefer to work in a containerized environment, OpenHands provides a dev container configuration that can be used with supported editors like VS Code.

**Section sources**
- [Development.md](file://Development.md#L9-L142)
- [containers/dev/compose.yml](file://containers/dev/compose.yml#L1-L40)

## Running Tests

OpenHands has a comprehensive testing framework that includes unit tests and integration tests to ensure code quality and functionality.

### Unit Tests

Unit tests are located in the `tests/unit/` directory and can be run using pytest:

```bash
poetry run pytest ./tests/unit
```

To run a specific test file:

```bash
poetry run pytest ./tests/unit/test_llm_fncall_converter.py
```

For more verbose output, use the `-v` flag:

```bash
poetry run pytest -v ./tests/unit/test_llm_fncall_converter.py
```

The project uses pytest with specific configuration options defined in `pytest.ini`, including async mode for testing asynchronous code.

### Integration Tests

Integration tests are located in the `evaluation/integration_tests/` directory and test the interaction between different components of the system. These tests are run as part of the continuous integration pipeline to ensure that changes don't break existing functionality.

### Test Configuration

The testing framework is configured with the following tools and libraries:
- pytest for test discovery and execution
- pytest-asyncio for testing asynchronous code
- pytest-cov for code coverage
- pytest-playwright for frontend testing
- pytest-xdist for parallel test execution

The test configuration ensures that all tests run in an isolated environment and that test results are consistent across different development setups.

**Section sources**
- [tests/unit/README.md](file://tests/unit/README.md#L1-L30)
- [pytest.ini](file://pytest.ini#L1-L5)
- [CONTRIBUTING.md](file://CONTRIBUTING.md#L59-L62)

## Submitting Pull Requests

When submitting a pull request to OpenHands, follow these guidelines to ensure a smooth review process.

### Pull Request Title

The pull request title should follow conventional commit types, beginning with one of the following prefixes:

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white space, formatting, etc.)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `build`: Changes that affect the build system or external dependencies
- `ci`: Changes to CI configuration files and scripts
- `chore`: Other changes that don't modify src or test files
- `revert`: Reverts a previous commit

For example: `feat(frontend): add dark mode toggle` or `fix: resolve memory leak in runtime`.

### Pull Request Description

The pull request description should include:

- A summary of the changes made
- The motivation for the changes
- Any user-facing changes that should be included in the changelog
- References to related issues or discussions

For small changes like typo fixes, a brief description is sufficient. For larger changes, provide more detailed information about the implementation and any design decisions made.

### Review Process

Pull requests are reviewed based on the type of change:

- **Small improvements**: Reviewed and approved quickly if CI tests pass
- **Core agent changes**: Evaluated based on accuracy, efficiency, and code complexity metrics
- **UI/UX changes**: Reviewed for consistency with the project's design principles

Maintainers may request changes or additional testing before approving a pull request. Contributors should respond to feedback promptly and make requested changes.

**Section sources**
- [CONTRIBUTING.md](file://CONTRIBUTING.md#L63-L124)

## Code Style Guidelines

OpenHands follows specific code style guidelines to maintain consistency across the codebase.

### Python Code Style

The project uses the following tools for Python code style enforcement:

- **Ruff**: For linting and formatting
- **Mypy**: For type checking
- **Black**: For code formatting (configured in pyproject.toml)

The ruff configuration is defined in `dev_config/python/ruff.toml` and includes the following rules:

- Uses single quotes for strings
- Follows Google docstring convention
- Ignores line length warnings (E501)
- Enforces modern Python syntax (e.g., `X | Y` instead of `Union[X, Y]`)

The mypy configuration in `dev_config/python/mypy.ini` enables strict type checking with specific settings for error reporting and type inference.

### Frontend Code Style

The frontend codebase follows these guidelines:

- TypeScript with strict type checking
- React with functional components and hooks
- Tailwind CSS for styling
- Redux for state management
- TanStack Query for data fetching

Code should be well-documented with JSDoc comments, and components should be designed for reusability and testability.

### Configuration

Code style configuration is defined in the following files:
- `pyproject.toml`: Poetry configuration and Python dependencies
- `dev_config/python/ruff.toml`: Ruff linting rules
- `dev_config/python/mypy.ini`: Mypy type checking rules
- `frontend/.eslintrc`: ESLint configuration for frontend code
- `frontend/tailwind.config.js`: Tailwind CSS configuration

These configuration files ensure consistent code style across the entire codebase and are enforced through pre-commit hooks and CI checks.

**Section sources**
- [dev_config/python/ruff.toml](file://dev_config/python/ruff.toml#L1-L43)
- [dev_config/python/mypy.ini](file://dev_config/python/mypy.ini#L1-L17)
- [pyproject.toml](file://pyproject.toml#L1-L222)
- [frontend/README.md](file://frontend/README.md#L1-L255)

## Testing Requirements

OpenHands has comprehensive testing requirements to ensure code quality and reliability.

### Test Coverage

The project requires high test coverage, especially for critical components. All new features and bug fixes should include appropriate tests to verify functionality and prevent regressions.

### Unit Testing

Unit tests should:
- Test individual functions and classes in isolation
- Cover both success and error cases
- Use mocking to isolate dependencies
- Be fast and reliable
- Include assertions for expected outcomes

The unit test framework uses pytest with async support for testing asynchronous code. Tests are organized by module and feature, with clear naming conventions to indicate what is being tested.

### Integration Testing

Integration tests verify the interaction between different components of the system. These tests:
- Test the integration between frontend and backend
- Verify API endpoints and data flow
- Ensure compatibility between different modules
- Validate end-to-end workflows

Integration tests are located in the `evaluation/integration_tests/` directory and use realistic test scenarios to validate system behavior.

### Test Organization

Tests are organized in the following directory structure:
- `tests/unit/`: Unit tests for individual components
- `evaluation/integration_tests/`: Integration tests for system workflows
- `frontend/__tests__/`: Frontend component tests
- `tests/e2e/`: End-to-end tests

Each test file should be named to clearly indicate what is being tested, and test functions should have descriptive names that explain the scenario being tested.

**Section sources**
- [tests/unit/README.md](file://tests/unit/README.md#L1-L30)
- [evaluation/README.md](file://evaluation/README.md#L1-L148)
- [frontend/README.md](file://frontend/README.md#L139-L247)

## Review Process

The review process for OpenHands contributions is designed to maintain code quality and ensure that changes align with the project's goals.

### Initial Triage

When a pull request is submitted, it goes through an initial triage process where maintainers:
- Verify that the PR follows contribution guidelines
- Check that CI tests are passing
- Assess the scope and impact of the changes
- Assign appropriate labels and reviewers

### Technical Review

The technical review focuses on:
- Code quality and adherence to style guidelines
- Correctness of the implementation
- Test coverage and quality
- Performance implications
- Security considerations
- Documentation updates

Reviewers may request changes to improve code quality, fix bugs, or enhance functionality. Contributors are expected to address feedback and make requested changes.

### Core Agent Changes

Changes to the core agent are evaluated more rigorously based on three key metrics:
1. **Accuracy**: Does the change improve the agent's ability to complete tasks correctly?
2. **Efficiency**: Does the change reduce the number of steps or time required to complete tasks?
3. **Code Complexity**: Does the change introduce unnecessary complexity?

For significant changes to the core agent, maintainers may request additional evaluation using benchmarks like SWE-bench to measure the impact on agent performance.

### Final Approval

Once all feedback has been addressed and CI tests are passing, the pull request can be approved and merged. At least one maintainer must approve the PR before it can be merged.

The review process is collaborative, with maintainers providing guidance and feedback to help contributors improve their submissions. Contributors are encouraged to participate in discussions and ask questions during the review process.

**Section sources**
- [CONTRIBUTING.md](file://CONTRIBUTING.md#L96-L124)
- [ISSUE_TRIAGE.md](file://ISSUE_TRIAGE.md#L1-L28)

## Common Contribution Scenarios

This section provides detailed examples of common contribution scenarios to help new contributors get started.

### Fixing Bugs

To fix a bug:
1. Identify the issue by reviewing existing bug reports or reproducing the problem
2. Create a new branch from the main branch
3. Implement the fix with appropriate tests
4. Verify that the fix resolves the issue without introducing new problems
5. Submit a pull request with a clear description of the bug and the solution

Bug fixes should include regression tests to prevent the issue from recurring.

### Adding Features

To add a new feature:
1. Discuss the feature in an issue to gather feedback from the community
2. Design the implementation, considering existing patterns and architecture
3. Implement the feature with comprehensive tests
4. Update documentation to reflect the new functionality
5. Submit a pull request with a detailed description of the feature and its benefits

New features should follow the project's design principles and code style guidelines.

### Improving Documentation

To improve documentation:
1. Identify areas that need improvement (missing information, unclear explanations, outdated content)
2. Update the relevant documentation files
3. Ensure that examples are accurate and up-to-date
4. Submit a pull request with a clear description of the changes

Documentation improvements are highly valued and help make the project more accessible to new users.

### Adding a New Agent

To add a new agent:
1. Create a new directory in `openhands/agenthub/` for the agent
2. Implement the agent class following the existing patterns
3. Add configuration options if needed
4. Write tests to verify the agent's functionality
5. Update documentation to describe the new agent

New agents should be designed to work within the existing agent framework and follow the same interface patterns as existing agents.

### Adding a New Runtime

To add a new runtime:
1. Implement the interface specified in `openhands/runtime/base.py`
2. Create a new runtime class that inherits from the base runtime
3. Implement the required methods for executing commands and managing the environment
4. Add configuration options for the runtime
5. Write tests to verify the runtime's functionality

New runtimes should be designed to be secure, reliable, and compatible with the existing system architecture.

**Section sources**
- [CONTRIBUTING.md](file://CONTRIBUTING.md#L26-L58)

## Issue Triage and Feature Requests

The OpenHands project has a structured process for triaging issues and handling feature requests.

### Issue Triage Process

Issues are triaged according to the following guidelines:

- **Labeling**: All issues must be tagged with `enhancement`, `bug`, or `troubleshooting/help`
- **Severity**: Issues are categorized by severity:
  - **High**: High visibility issues or affecting many users
  - **Critical**: Affecting all users or potential security issues
- **Difficulty**: Issues with low implementation difficulty may be tagged with `good first issue`
- **Information**: Issues that lack sufficient information are marked as needing more information, and the author is asked to provide details such as logs and reproduction steps

### Feature Requests

Feature requests should:
- Clearly describe the desired functionality
- Explain the use case and benefits
- Consider potential implementation approaches
- Be open to discussion and feedback

The community and maintainers discuss feature requests to assess their value, feasibility, and alignment with the project's goals. Popular feature requests with "thumbs-up" reactions are prioritized for implementation.

### Issue Management

To keep the backlog maintainable:
- Issues with no activity for 30 days are automatically marked as "Stale"
- Stale issues with no further activity for 7 days are automatically closed
- Closed issues can be reopened if they are deemed important

Multiple requests in a single issue are narrowed down to one request per issue for better tracking and resolution.

**Section sources**
- [ISSUE_TRIAGE.md](file://ISSUE_TRIAGE.md#L1-L28)
- [CONTRIBUTING.md](file://CONTRIBUTING.md#L98-L103)

## Community Participation

The OpenHands community is built around the belief that AI and AI agents will fundamentally change software development, and that the benefits of this technology should be accessible to everyone.

### Joining the Community

To join the OpenHands community:
- [Join the Slack workspace](https://all-hands.dev/joinslack) to participate in discussions about research, architecture, and future development
- Participate in GitHub issues to discuss bugs, feature requests, and implementation details
- Contribute to the project through code, documentation, or testing

The community is welcoming and inclusive, with a focus on collaboration and knowledge sharing.

### Becoming a Contributor

There are many ways to contribute to OpenHands:
- **Code Contributions**: Develop new functionality, improve agents, enhance the frontend, or contribute to other aspects of the project
- **Research and Evaluation**: Participate in evaluating models, suggest improvements, or contribute to the understanding of LLMs in software engineering
- **Feedback and Testing**: Use OpenHands, report bugs, suggest features, or provide usability feedback

All contributions are valued, and the project maintains a [Code of Conduct](file://CODE_OF_CONDUCT.md) to ensure a positive and respectful community environment.

### Becoming a Maintainer

Contributors who have made significant and sustained contributions may be considered for maintainer status. The process involves:
1. Nomination by an existing maintainer
2. A discussion period among maintainers (at least 3 days)
3. Acceptance by acclamation or vote if concerns are raised

Maintainer status is based on sustained high-quality contributions, good teamwork, and adherence to the Code of Conduct, not just the number of PRs submitted.

**Section sources**
- [COMMUNITY.md](file://COMMUNITY.md#L1-L44)
- [CONTRIBUTING.md](file://CONTRIBUTING.md#L18-L25)

## Contribution Prerequisites and Tooling Requirements

To contribute to OpenHands, you need to set up the appropriate development tools and meet the project's prerequisites.

### Required Tools

The following tools are required for development:
- **Git**: For version control and code contributions
- **Docker**: For running the application and tests in a consistent environment
- **Python 3.12**: The project's primary programming language
- **Node.js >= 22.x**: For frontend development
- **Poetry**: For Python dependency management
- **Make**: For running development commands

### Development Environment Setup

The recommended way to set up the development environment is through the provided Makefile targets:
- `make build`: Sets up the environment and installs dependencies
- `make setup-config`: Configures the language model
- `make run`: Starts the application
- `make start-backend`: Starts only the backend server
- `make start-frontend`: Starts only the frontend server

### Optional Tools

Additional tools that can enhance the development experience:
- **VS Code with Dev Containers extension**: For working in a pre-configured development container
- **uv**: For running OpenHands with better isolation from the host environment
- **pre-commit**: For running code checks before commits

### Dependency Management

Python dependencies are managed through Poetry in `pyproject.toml`. To add a new dependency:
1. Add the dependency in `pyproject.toml` or use `poetry add xxx`
2. Update the poetry.lock file via `poetry lock --no-update`

The project uses optional dependency groups for different use cases:
- `dev`: Development dependencies (ruff, mypy, pre-commit)
- `test`: Testing dependencies (pytest, coverage tools)
- `runtime`: Runtime dependencies (Jupyter, notebook)
- `evaluation`: Evaluation framework dependencies (streamlit, benchmarks)

**Section sources**
- [Development.md](file://Development.md#L11-L51)
- [pyproject.toml](file://pyproject.toml#L1-L222)

## Development Best Practices

Following these best practices will help ensure high-quality contributions to the OpenHands project.

### Code Quality

- Write clean, readable code with descriptive variable and function names
- Follow the project's code style guidelines
- Use type hints to improve code clarity and catch errors
- Write comprehensive docstrings that explain the purpose and usage of functions and classes
- Keep functions and methods focused on a single responsibility

### Testing

- Write tests for all new code
- Ensure high test coverage, especially for critical functionality
- Test both success and error cases
- Use mocking to isolate dependencies in unit tests
- Write integration tests for complex workflows
- Run tests locally before submitting a pull request

### Documentation

- Update documentation when adding new features or changing existing functionality
- Write clear and concise documentation that is easy to understand
- Include examples to illustrate usage
- Keep documentation up-to-date with code changes
- Use consistent terminology throughout the documentation

### Performance

- Consider performance implications of code changes
- Avoid unnecessary computations or I/O operations
- Use efficient algorithms and data structures
- Profile code to identify performance bottlenecks
- Optimize critical paths while maintaining code readability

### Security

- Follow secure coding practices
- Validate and sanitize all user inputs
- Avoid introducing security vulnerabilities
- Use secure dependencies and keep them updated
- Be cautious with code that executes commands or accesses external resources

### Collaboration

- Communicate clearly and respectfully in discussions
- Respond promptly to feedback and questions
- Be open to suggestions and alternative approaches
- Provide constructive feedback on others' contributions
- Participate in code reviews to help improve code quality

Following these best practices will help ensure that your contributions are of high quality and align with the project's goals and standards.

**Section sources**
- [CONTRIBUTING.md](file://CONTRIBUTING.md#L96-L124)
- [Development.md](file://Development.md#L1-L205)

## Troubleshooting Development Environment Issues

This section provides guidance for troubleshooting common issues that may arise when setting up or working with the OpenHands development environment.

### Docker Issues

Common Docker-related issues and solutions:
- **Permission denied accessing Docker socket**: Ensure your user is in the docker group (`sudo usermod -aG docker $USER`)
- **Docker daemon not running**: Start the Docker service (`sudo systemctl start docker`)
- **Image build failures**: Check Docker logs and ensure all dependencies are available
- **Container networking issues**: Verify that `host.docker.internal` is properly resolved

### Python Environment Issues

Common Python-related issues:
- **Python version mismatch**: Ensure Python 3.12 is installed and used
- **Poetry installation issues**: Install Poetry using the official installer
- **Dependency conflicts**: Update poetry.lock with `poetry lock --no-update`
- **Virtual environment issues**: Use `poetry shell` to activate the virtual environment

### Frontend Development Issues

Common frontend issues:
- **Node.js version issues**: Ensure Node.js >= 22.x is installed
- **Package installation failures**: Clear npm cache (`npm cache clean --force`) and reinstall
- **Build failures**: Check for syntax errors and missing dependencies
- **Hot reload not working**: Restart the development server

### LLM Configuration Issues

Common LLM-related issues:
- **API key errors**: Verify that the API key is correctly configured in `config.toml`
- **Model not found**: Check that the model name is correct and supported
- **Rate limiting**: Implement appropriate retry logic and respect API rate limits
- **Authentication failures**: Verify credentials and permissions

### General Troubleshooting Tips

- Check the project's logs for error messages
- Verify that all prerequisites are installed and properly configured
- Consult the project documentation and README files
- Search existing issues for similar problems
- Ask for help in the community Slack channel

When reporting issues, provide detailed information including:
- Steps to reproduce the problem
- Expected vs. actual behavior
- Error messages and logs
- System information (OS, versions of tools)
- Any relevant configuration files (with sensitive information redacted)

**Section sources**
- [Development.md](file://Development.md#L129-L133)
- [README.md](file://README.md#L133-L134)