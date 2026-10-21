# Git Setup & Push to GitHub

## 🚀 Initial Repository Setup

### Step 1: Initialize Git (if not already done)

```bash
cd d:\Ariescan
git init
```

### Step 2: Configure Git (First Time Only)

```bash
git config user.name "Your Name"
git config user.email "your-email@example.com"

# Or use global config (for all repos):
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

### Step 3: Stage All Files

```bash
git add .
```

### Step 4: Create First Commit

```bash
git commit -m "Initial commit: Ariescan API testing platform with project structure and documentation"
```

### Step 5: Add Remote Repository

```bash
git remote add origin https://github.com/HorRatha/Ariescan.git
```

### Step 6: Rename Branch to Main (if needed)

```bash
git branch -M main
```

### Step 7: Push to GitHub

```bash
git push -u origin main
```

---

## ✅ Verify Setup

```bash
# Check remote is configured
git remote -v

# Should output:
# origin  https://github.com/HorRatha/Ariescan.git (fetch)
# origin  https://github.com/HorRatha/Ariescan.git (push)

# Check branch
git branch

# Should show: * main

# Check status
git status

# Should show: On branch main, nothing to commit, working tree clean
```

---

## 📝 Future Commits

### For regular updates:

```bash
# Make changes to files...

# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add API endpoint discovery feature"

# Push to GitHub
git push origin main
```

### For feature work (recommended):

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes...
git add .
git commit -m "feat: describe your feature"

# Push feature branch
git push -u origin feature/your-feature-name

# Create Pull Request on GitHub
# (merge after review)
```

---

## 🔧 Troubleshooting

### SSH vs HTTPS

**HTTPS** (what we used):
- Requires username/token
- Works everywhere
- No SSH key setup needed

**SSH** (alternative):
```bash
git remote set-url origin git@github.com:HorRatha/Ariescan.git
```
Requires SSH key setup in GitHub account

### Authentication Issues

**HTTPS with token:**
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Create new token with `repo` scope
3. Use token as password when prompted

**HTTPS with credentials cached:**
```bash
# Windows
git config --global credential.helper wincred
```

### Common Issues

**"fatal: remote origin already exists"**
```bash
git remote remove origin
git remote add origin https://github.com/HorRatha/Ariescan.git
```

**"fatal: not a git repository"**
```bash
git init
```

**"Please tell me who you are"**
```bash
git config user.name "Your Name"
git config user.email "your@email.com"
```

---

## 📊 Commit Message Format

Use conventional commits for clarity:

```
feat: add new feature
fix: resolve bug
docs: update documentation
style: format code
refactor: restructure code
test: add tests
chore: update dependencies
```

Example:
```bash
git commit -m "feat: implement test case generation from OpenAPI"
```

---

## 🎯 Next Steps

1. **Push to GitHub**: Follow the steps above
2. **Create Issues**: Add tasks in GitHub Issues
3. **Start Development**: Use feature branches for work
4. **Invite Contributors**: Add team members as collaborators
5. **Set up CI/CD**: Add GitHub Actions workflows

---

## 📚 GitHub Actions (Optional)

Create `.github/workflows/test.yml` to run tests automatically:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run lint
      - run: npm run test
```

---

**You're all set! 🎉**
