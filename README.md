# ⚡ GitPulse - GitHub Activity Visualizer & Persona Analyzer

A beautiful and interactive Python CLI/TUI tool designed to analyze any GitHub user's recent coding activity, top programming languages, active commit hours, and generate a gamified **Developer Persona** with dynamic feedback. It also exports a ready-to-share markdown report for your GitHub Profile README!

---

## ✨ Features
- **👤 Dynamic Profile Overview:** Displays name, bio, location, followers, and public repository counts.
- **📊 Coding Analytics:**
  - **Top Languages Chart:** Visualizes language distributions across repositories.
  - **Active Hours Graph:** Categorizes and plots commit times (Morning, Afternoon, Evening, Night) to analyze your circadian coding patterns.
- **🔔 Activity Log:** A beautifully structured table displaying the distribution of your last 100 public events (commits, PRs, issues, stars, etc.).
- **🧠 Developer Persona (AI Persona):** Automatically classifies you into unique developer archetypes:
  - *Night Owl 🦉* - Late-night coder.
  - *Early Bird 🌅* - Morning developer.
  - *Commit Machine 🚀* - High-frequency pusher.
  - *Team Collaborator 🤝* - PR and review master.
  - *Problem Solver 🛠️* - Issue investigator.
  - *Focused Craftsman 💎* - Calm and precise engineer.
- **📄 Auto-Exporter:** Automatically generates a comprehensive Markdown report (`{username}_gitpulse_report.md`) for your personal profile!
- **🔌 Mock Mode Fallback:** Automatically switches to an offline mock demo if you hit the GitHub API rate limit, ensuring that recruiters and visitors always see a stunning visualization.

---

## 🛠️ Installation

1. **Clone or create the folder:**
   ```bash
   cd D:\folder_coding\gitpulse
   ```

2. **Install the required libraries:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 How to Use

### 1. Run in Demo/Mock Mode (Instant Tryout):
To see the application in action instantly using mock demo data, run:
```bash
python main.py --mock
```

### 2. Analyze a Public GitHub User:
Analyze any public GitHub user (e.g. your own username):
```bash
python main.py --username your_github_username
```

### 3. Run with Personal Access Token (To Avoid API Rate Limits):
GitHub unauthenticated requests are limited to 60 per hour. If you run it frequently, pass a Personal Access Token:
```bash
python main.py --username your_github_username --token YOUR_GITHUB_TOKEN
```

---

## 📦 Project Structure
- `main.py` - Core logic, API client, analyzer, TUI rendering, and exporter.
- `requirements.txt` - Depedency file (`requests` & `rich`).
- `README.md` - Documentation and setup guide.

---
*Developed as part of the **1 Day 1 Project** challenge! ⚡*
