# Contributing to Bridge GAD Generator

Thank you for your interest in contributing to the Bridge GAD Generator! We welcome contributions from the community.

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/bridge-gad.git
   cd bridge-gad
   ```
3. **Set up the development environment**:
   ```bash
   # Create and activate a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install the package in development mode with all dependencies
   pip install -e ".[dev]"
   ```

## Development Workflow

1. **Create a new branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-description
   ```

2. **Make your changes** and ensure tests pass:
   ```bash
   # Run tests
   pytest
   
   # Run with coverage
   pytest --cov=bridge_gad --cov-report=term-missing
   
   # Run linting
   ruff check .
   
   # Run type checking
   mypy src/
   ```

3. **Commit your changes** with a descriptive message:
   ```bash
   git add .
   git commit -m "Add feature/fix: brief description of changes"
   ```

4. **Push your changes** to your fork:
   ```bash
   git push origin your-branch-name
   ```

5. **Open a Pull Request** against the `main` branch.

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide.
- Use type hints for all function/method signatures.
- Keep lines under 88 characters (Black's default).
- Document all public functions and classes with docstrings.
- Write tests for new functionality.

## Testing

- Write unit tests for all new features and bug fixes.
- Ensure all tests pass before submitting a PR.
- Add integration tests for end-to-end functionality.
- Update tests when fixing bugs to prevent regressions.

## Pull Request Guidelines

- Keep PRs focused on a single feature or bug fix.
- Include a clear description of the changes.
- Reference any related issues.
- Ensure all CI checks pass.
- Update documentation as needed.

## Reporting Issues

When reporting issues, please include:

1. A clear description of the problem
2. Steps to reproduce the issue
3. Expected vs. actual behavior
4. Version information (Python, package version, OS)

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
