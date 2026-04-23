# 💰 Budget Tracker

A personal finance tracker built with Python and Tkinter.
Track income & expenses, filter by category, search transactions, and visualize your spending.

---

## 🚀 Features

- Add / Edit / Delete transactions (income & expense)
- Category-based filtering and keyword search
- Summary cards: Net Balance, Income, Expenses, Transaction count
- Live bar chart breakdown of expenses by category
- Export & Import CSV files
- Data persists in a local `transactions.json` file

---

## 📦 Requirements

Python 3.8+ (Tkinter is included in the standard library — no pip installs needed)

---

## ▶️ Run

```bash
python main.py
```

---

## 🌿 Git Branch Strategy

This project uses **3 branches** for a clean development workflow:

---

### `main` — Stable Production Branch

The always-deployable, fully tested version of the app.
Only merge here when a feature is complete and reviewed.

```bash
git checkout main
```

**Rules:**
- No direct commits
- Only accept merges from `develop` after QA
- Always has a working, bug-free app

---

### `develop` — Integration / Staging Branch

The active development branch where features are merged together and tested as a whole before hitting `main`.

```bash
git checkout develop
```

**Rules:**
- Branch off from `main`
- Feature branches merge here first
- Bugs found here are fixed before going to `main`

---

### `feature/reports` — Feature Branch (example)

Individual feature branches are created from `develop`.
This example branch adds a **Monthly Reports** screen with charts.

```bash
git checkout -b feature/reports develop
```

Other feature branch examples you might create:
- `feature/dark-mode-toggle`
- `feature/budget-goals`
- `feature/recurring-transactions`
- `bugfix/date-validation`

---

## 🔁 Branch Workflow (Git Flow Lite)

```
main
 └── develop
      ├── feature/reports        ← new screen
      ├── feature/budget-goals   ← set monthly limits
      └── bugfix/date-validation ← fix a bug
```

### Typical workflow:

```bash
# 1. Start a new feature from develop
git checkout develop
git pull origin develop
git checkout -b feature/reports

# 2. Work on the feature, commit often
git add .
git commit -m "feat: add monthly report screen"

# 3. Merge back to develop when done
git checkout develop
git merge feature/reports

# 4. Test on develop. When stable, merge to main
git checkout main
git merge develop

# 5. Tag the release
git tag -a v1.1.0 -m "Release v1.1.0 - Monthly Reports"
git push origin main --tags
```

---

## 📁 Project Structure

```
budget_tracker/
├── main.py              # Main application
├── transactions.json    # Auto-created on first run (gitignored)
├── README.md
└── .gitignore
```

---

## 🙈 .gitignore

```
transactions.json
__pycache__/
*.pyc
*.pyo
.DS_Store
```
