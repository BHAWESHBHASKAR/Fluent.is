# Contributing to Fluent Language

Thank you for your interest in contributing to the Fluent Language project! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with the following information:
- A clear, descriptive title
- Steps to reproduce the bug
- Expected behavior vs. actual behavior
- Any relevant error messages or screenshots
- Your environment (OS, Python version, etc.)

### Suggesting Enhancements

We welcome suggestions for enhancements! Please create an issue with:
- A clear description of the enhancement
- Any specific use cases or examples
- How this would benefit the project

### Pull Requests

1. Fork the repository
2. Create a branch for your changes
3. Make your changes
4. Run the tests to ensure everything works
5. Submit a pull request

### Code Style

Please follow these guidelines for code style:
- Use 4 spaces for indentation
- Follow PEP 8 guidelines for Python code
- Write clear, descriptive comments
- Include docstrings for functions and classes

## Development Setup

1. Clone the repository
2. Install development dependencies:
```bash
pip install -r requirements.txt
```
3. Run the tests to ensure everything is working:
```bash
python -m pytest tests/
```

## Testing

- All new features should include appropriate tests
- Run the tests before submitting a pull request:
```bash
python -m pytest tests/
```

## Documentation

- Update the README.md if necessary
- Document new features or changes in behavior
- Add comments to your code to explain complex logic

## Fluent Language Specific Guidelines

When adding features to the Fluent language:
- Maintain the natural language style of existing features
- Consider compatibility with the existing transpiler architecture
- Minimize dependencies when possible
- Aim for simplicity and readability over complexity

Thank you for contributing to making Fluent Language better!
