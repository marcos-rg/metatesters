# Contributing to Metatesters

Thank you for your interest in contributing to Metatesters! We welcome contributions from the community.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. Search existing issues to avoid duplicates
2. Create a new issue with a clear title and description
3. Include steps to reproduce the bug (if applicable)
4. Provide relevant system information

### Making Changes

1. **Fork the repository**
   ```bash
   git fork https://github.com/marcos-rg/metatesters.git
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/metatesters.git
   cd metatesters
   ```

3. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Set up development environment**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync
   ```

5. **Make your changes**
   - Write clear, readable code
   - Add comments where necessary
   - Follow existing code style


6. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: brief description of your changes"
   ```

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Provide a clear description of your changes

## Code Style

- Use clear, descriptive variable and function names
- Add docstrings to functions and classes
- Keep lines under 100 characters when possible
- Use type hints where appropriate

## Areas for Contribution

- New tester personas and testing strategies
- UI/UX improvements
- Documentation improvements
- Bug fixes and performance optimizations
- New example target systems for testing

## Questions?

Feel free to open an issue for any questions about contributing. We're happy to help!

## Code of Conduct

Please be respectful and constructive in all interactions. We want to maintain a welcoming environment for all contributors.
