# Contributing to Ariescan

Thank you for your interest in contributing to Ariescan! We welcome contributions from everyone.

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

## How to Contribute

### 1. Report Bugs

- Check [existing issues](https://github.com/HorRatha/Ariescan/issues) first
- Create a new issue with:
  - Clear title and description
  - Steps to reproduce
  - Expected vs actual behavior
  - Screenshots if applicable
  - Environment details (OS, Node version, etc.)

### 2. Suggest Features

- Open a [discussion](https://github.com/HorRatha/Ariescan/discussions)
- Describe the feature and use case
- Explain why it would be useful

### 3. Submit Code

#### Setup Development Environment

```bash
git clone https://github.com/HorRatha/Ariescan.git
cd Ariescan
```

#### Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

#### Make Changes

- Follow the project's code style
- Write tests for new features
- Keep commits atomic and descriptive

#### Run Tests

```bash
npm run test          # Run tests
npm run lint          # Check code style
npm run build         # Build for production
```

#### Push and Create a Pull Request

```bash
git push origin feature/your-feature-name
```

Then open a PR on GitHub with:
- Clear title describing changes
- Reference any related issues (#123)
- Description of what changed and why

### 4. Improve Documentation

- Fix typos or clarify confusing sections
- Add examples or guides
- Translate to other languages

## Development Guidelines

### Code Style

- Use consistent formatting (Prettier/ESLint configs provided)
- Write readable, self-documenting code
- Add comments for complex logic

### Testing

- Write unit tests for new features
- Aim for >80% code coverage
- Test edge cases

### Commit Messages

```
feat: add new test report format
fix: resolve memory leak in test executor
docs: update installation guide
style: format code
refactor: simplify test generator
test: add integration tests
```

## Project Structure

```
backend/          - Node.js/Python API server
frontend/         - React dashboard
docs/             - Documentation
docker/           - Docker configuration
tests/            - Test suites
```

## Getting Help

- Ask questions in [Discussions](https://github.com/HorRatha/Ariescan/discussions)
- Check [Documentation](./README.md)
- Open an issue for bugs

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for making Ariescan better! 🎉
