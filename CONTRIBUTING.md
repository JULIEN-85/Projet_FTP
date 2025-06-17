# Contributing to Photo Transfer System

🎉 Thank you for your interest in contributing to the Photo Transfer System!

## 🚀 How to Contribute

### 1. **Getting Started**
- Fork the repository
- Clone your fork locally
- Set up the development environment

### 2. **Development Setup**
```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/photo-transfer-system.git
cd photo-transfer-system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
make test
```

### 3. **Types of Contributions**

#### 🐛 **Bug Reports**
- Use the bug report template
- Include system information (Pi model, OS version)
- Provide reproduction steps
- Include relevant logs

#### ✨ **Feature Requests**
- Check existing issues first
- Describe the use case clearly
- Explain why it would be beneficial

#### 🔧 **Code Contributions**
- New camera/phone support
- FTP protocol improvements
- Web interface enhancements
- Performance optimizations
- Documentation improvements

### 4. **Development Guidelines**

#### **Code Style**
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings for functions
- Keep functions focused and small

#### **Testing**
- Add tests for new features
- Ensure existing tests pass
- Test on actual Raspberry Pi hardware when possible
- Include both unit and integration tests

#### **Documentation**
- Update README.md for new features
- Add inline code comments
- Update configuration examples
- Create/update relevant guides

### 5. **Pull Request Process**

#### **Before Submitting**
```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes
# ... code changes ...

# Test your changes
make test
python3 test_system.py

# Commit with clear message
git commit -m "feat: Add support for Sony Alpha cameras"
```

#### **Pull Request Template**
- Describe what your PR does
- Link to related issues
- Include testing information
- Add screenshots for UI changes

### 6. **Supported Hardware**

When adding support for new hardware, please include:

#### **Cameras**
- gPhoto2 compatibility confirmation
- Testing on actual hardware
- Configuration examples
- Known limitations

#### **Phones**
- Android version compatibility
- PTP mode testing
- Specific setup instructions
- Troubleshooting guide

### 7. **Priority Areas**

We especially welcome contributions in:

#### 🎯 **High Priority**
- Camera/phone compatibility improvements
- FTP reliability enhancements
- Web interface mobile optimization
- Performance optimizations for Pi 5

#### 📈 **Medium Priority**
- Additional FTP protocols (SFTP, FTPS)
- Cloud storage integration (Google Drive, Dropbox)
- Email notifications
- Multi-language support

#### 🔮 **Future Ideas**
- RAW file processing
- Automatic photo organization
- Face recognition integration
- Time-lapse automation

### 8. **Testing Guidelines**

#### **Required Tests**
- All existing tests must pass
- New features need corresponding tests
- Test on Raspberry Pi hardware when possible

#### **Test Categories**
```bash
# Unit tests
python3 test_system.py

# Camera detection
make test-camera

# FTP connectivity
make test-ftp

# Web interface
make test-web

# Phone setup
make setup-phone
```

### 9. **Code Review Process**

1. **Automated Checks**
   - CI/CD pipeline runs tests
   - Code style validation
   - Security scanning

2. **Manual Review**
   - Code quality assessment
   - Architecture consistency
   - Documentation completeness

3. **Testing**
   - Functionality verification
   - Hardware compatibility
   - Performance impact

### 10. **Community Guidelines**

#### **Be Respectful**
- Use inclusive language
- Respect different skill levels
- Provide constructive feedback
- Help newcomers

#### **Be Patient**
- Reviews take time
- Hardware testing requires access
- Maintainers are volunteers

#### **Be Collaborative**
- Discuss big changes in issues first
- Accept feedback gracefully
- Help others with their contributions

### 11. **Getting Help**

#### **Resources**
- 📖 **Documentation**: Check the README and guides
- 🐛 **Issues**: Search existing issues first
- 💬 **Discussions**: Use GitHub Discussions for questions
- 📧 **Contact**: Reach out to maintainers

#### **Common Questions**
- "How do I add support for my camera?" → Check camera compatibility guide
- "My phone isn't detected" → Run `make setup-phone`
- "Tests are failing" → Check your development environment

### 12. **Recognition**

Contributors will be:
- ✨ **Listed** in CONTRIBUTORS.md
- 🏆 **Mentioned** in release notes
- 💫 **Featured** in project highlights

### 13. **License**

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

## 🎉 Ready to Contribute?

1. **Fork** the repository
2. **Create** your feature branch
3. **Make** your awesome changes
4. **Test** thoroughly
5. **Submit** a pull request

**Every contribution makes this project better for the entire Raspberry Pi community!** 🚀

---

## 📞 Questions?

Don't hesitate to open an issue or start a discussion if you have any questions about contributing!

**Happy coding!** 🎊
