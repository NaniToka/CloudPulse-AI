# Contributing to CloudPulse AI

Thank you for your interest in contributing to **CloudPulse AI**! CloudPulse AI is an open-source, enterprise-grade AI-powered observability platform. We welcome contributions from developers, site reliability engineers (SREs), AI researchers, and security specialists worldwide.

---

## 📜 Code of Conduct

All contributors are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before participating in discussions or submitting code.

---

## 🚀 How to Contribute

### 1. Reporting Bugs
- Check existing [GitHub Issues](https://github.com/NaniToka/CloudPulse-AI/issues) to avoid duplicate reports.
- If not found, create a new issue using the **Bug Report** template.
- Include clear reproduction steps, environment details, and relevant terminal/API log tracebacks.

### 2. Suggesting Enhancements
- Open a **Feature Request** issue describing the problem, proposed solution, and operational/business impact.

### 3. Submitting Pull Requests
1. Fork the repository and create a feature branch (`git checkout -b feat/amazing-feature`).
2. Implement your changes adhering to code style standards.
3. Add unit/integration tests for your changes.
4. Run validation commands:
   ```bash
   # Backend validation
   ./backend/.venv/bin/pytest backend/tests/ -v

   # Frontend validation
   cd frontend && npm run build
   ```
5. Commit with clear, descriptive messages following [Conventional Commits](https://www.conventionalcommits.org/).
6. Open a Pull Request against the `main` branch.

---

## 💻 Local Development Setup

### Prerequisites
- **Node.js**: v20+
- **Python**: v3.12+
- **Docker & Docker Compose** (for PostgreSQL & ChromaDB)
- **Google Gemini API Key** (optional for AI engine testing)

### Backend Setup
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🎨 Code Style Guidelines

- **Python**: Follow PEP 8. Format code using `black` and lint with `ruff`.
- **TypeScript & React**: Follow standard ESLint rules, strict TypeScript types, and functional React components.
- **Git Commit Messages**: Use prefixes: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `perf:`, `chore:`.

---

## 📄 License

By contributing to CloudPulse AI, you agree that your contributions will be licensed under the [MIT License](LICENSE).
