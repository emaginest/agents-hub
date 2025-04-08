# Contributing to Agents Hub

Thank you for your interest in contributing to Agents Hub! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to foster an inclusive and respectful community.

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** to your local machine:
   ```bash
   git clone https://github.com/your-username/agents-hub.git
   cd agents-hub
   ```
3. **Create a virtual environment** and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Guidelines

### Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code style.
- Use [Black](https://black.readthedocs.io/) for code formatting:
  ```bash
  black agents_hub/
  ```
- Use [isort](https://pycqa.github.io/isort/) for import sorting:
  ```bash
  isort agents_hub/
  ```

### Type Hints

- Use type hints for all function and method signatures.
- Use `Optional` for parameters that can be `None`.
- Use `Any` sparingly and only when necessary.

### Documentation

- Write docstrings for all modules, classes, methods, and functions.
- Follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for docstrings.
- Update README files when adding new features or changing existing ones.
- Add examples for new features.

### Testing

- Write unit tests for all new functionality.
- Ensure all tests pass before submitting a pull request:
  ```bash
  pytest
  ```
- Aim for high test coverage.

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code changes that neither fix bugs nor add features
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat: add support for OpenAI function calling
```

## Pull Request Process

1. **Update your fork** with the latest changes from the main repository:
   ```bash
   git remote add upstream https://github.com/emagine-solutions/agents-hub.git
   git fetch upstream
   git rebase upstream/main
   ```
2. **Run tests** to ensure your changes don't break existing functionality:
   ```bash
   pytest
   ```
3. **Update documentation** to reflect your changes.
4. **Submit a pull request** to the main repository.
5. **Describe your changes** in the pull request description:
   - What changes were made
   - Why the changes were made
   - How to test the changes
   - Any relevant issues or documentation
6. **Address review comments** and make requested changes.
7. **Wait for approval** from maintainers.

## Project Structure

The project follows this structure:

```
agents-hub/
├── agents_hub/                      # Main package
│   ├── agents/                      # Base agent implementations
│   ├── coding/                      # Coding agents and tools
│   ├── cognitive/                   # Cognitive architecture
│   ├── llm/                         # LLM providers and interfaces
│   ├── memory/                      # Memory systems
│   ├── moderation/                  # Content moderation
│   ├── monitoring/                  # Monitoring and observability
│   ├── orchestration/               # Agent orchestration
│   ├── rag/                         # Retrieval-Augmented Generation
│   ├── security/                    # Security features
│   ├── templates/                   # Code templates
│   ├── tools/                       # Tools for agents
│   └── utils/                       # Utility functions
├── docs/                            # Documentation
├── examples/                        # Example applications
└── tests/                           # Tests
```

When adding new features, follow the existing structure and patterns.

## Adding New Components

### Adding a New Agent

1. Create a new file in the appropriate directory (e.g., `agents_hub/agents/specialized/your_agent.py`).
2. Implement your agent by extending the `Agent` class.
3. Add comprehensive documentation and examples.
4. Update the appropriate `__init__.py` file to export your agent.
5. Add tests for your agent.

### Adding a New Tool

1. Create a new file in the appropriate directory (e.g., `agents_hub/tools/standard/your_tool.py`).
2. Implement your tool by extending the `BaseTool` class.
3. Add comprehensive documentation and examples.
4. Update the appropriate `__init__.py` file to export your tool.
5. Add tests for your tool.

### Adding a New LLM Provider

1. Create a new file in the `agents_hub/llm/providers/` directory.
2. Implement your provider by extending the `BaseLLM` class.
3. Add comprehensive documentation and examples.
4. Update the `agents_hub/llm/providers/__init__.py` file to export your provider.
5. Add tests for your provider.

## License

By contributing to Agents Hub, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

## Questions and Support

If you have questions or need support, please:

1. Check the [documentation](docs/) and [examples](examples/).
2. Open an issue on GitHub for bugs or feature requests.
3. Reach out to the maintainers for other inquiries.

Thank you for contributing to Agents Hub!
