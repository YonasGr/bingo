# Contributing to Ethio Bingo

Thank you for your interest in contributing to Ethio Bingo! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Environment details (OS, Python version, etc.)

### Suggesting Features

1. Check if the feature has been suggested
2. Create a new issue with:
   - Clear use case
   - Expected behavior
   - Why it would be useful
   - Potential implementation approach

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the code style guidelines
   - Add tests for new functionality
   - Update documentation as needed

4. **Test your changes**
   ```bash
   pytest
   black src/
   flake8 src/
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add feature: description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Provide a clear description
   - Reference related issues
   - Explain what changed and why

## Development Setup

See ETHIO_BINGO_GUIDE.md for detailed setup instructions.

Quick start:
```bash
git clone https://github.com/YonasGr/bingo.git
cd bingo
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Code Style

- Follow PEP 8
- Use type hints where possible
- Write docstrings for functions and classes
- Keep functions focused and small
- Use meaningful variable names

### Formatting

```bash
# Format code
black src/

# Check linting
flake8 src/

# Type checking
mypy src/
```

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for high test coverage

```bash
# Run tests
pytest

# With coverage
pytest --cov=src
```

## Documentation

- Update relevant documentation for changes
- Add docstrings to new functions/classes
- Update API_REFERENCE.md for API changes
- Update ETHIO_BINGO_GUIDE.md for user-facing changes

## Commit Messages

Format: `<type>: <description>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

Examples:
- `feat: Add 90-ball variant support`
- `fix: Correct pattern verification for diagonal wins`
- `docs: Update API reference with new endpoints`

## Project Structure

```
src/
├── api/          # FastAPI application
├── bot/          # Telegram bot
├── core/         # Core utilities (config, database, redis)
├── models/       # Database models
├── services/     # Business logic
├── static/       # Frontend assets
├── templates/    # HTML templates
└── tests/        # Test files
```

## Review Process

1. PRs are reviewed by maintainers
2. Address feedback and make requested changes
3. Once approved, PR will be merged

## Questions?

- Open an issue for questions
- Check existing documentation
- Review closed issues and PRs

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🎉
