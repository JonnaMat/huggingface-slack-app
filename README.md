<div align="center">
  <img src="https://huggingface.co/datasets/huggingface/brand-assets/resolve/main/hf-logo.svg?download=true" width="100px" alt="HuggingFace Slack Bot" />
  <h1 style="font-size: 28px; margin: 10px 0;">HuggingFace Slack App</h1>
  <p>Get real-time milestone notifications for Hugging Face models and organizations directly in your Slack channels!</p>
</div>

<p align="center">
  <a href="https://opensource.org/licenses/MIT">
    <img alt="License" src="https://img.shields.io/badge/License-MIT-yellow.svg" />
  </a>
  <a href="https://tools.slack.com/automation">
    <img alt="Slack Bolt" src="https://img.shields.io/badge/Slack%20Bolt-1.27.0-purple.svg" />
  </a>
  <a href="https://www.python.org/">
    <img alt="Python" src="https://img.shields.io/badge/Python-3.9+-blue.svg" />
  </a>
  <a href="https://huggingface.co/docs/hub">
    <img alt="HuggingFace Hub" src="https://img.shields.io/badge/HuggingFace%20Hub-latest-orange.svg" />
  </a>
</p>


---

## ✨ What does it do?

This Slack bot lets your team **subscribe to any Hugging Face model or organization** and receive automatic milestone 
notifications — downloads, likes, new followers, new models — right in your Slack channels. 
Stay on top of the ML ecosystem without leaving your workflow.

---

## 📸 Demo

<p align="center">
   <img src="docs/assets/demo.gif" width="75%">
</p>

### Subscribe to a model with a single command

<!-- screenshot: subscribe-command.png -->
![Subscribe to a model](docs/assets/hf_subscribe.png)

*Subscribe any model or organization to a channel with `/hf subscribe`.*

---

### Receive milestone notifications automatically

<!-- screenshot: milestone-notification.png -->
![Milestone notification](docs/assets/hf_download_milestone.png)

*The bot posts rich, formatted messages when models cross download, like, or follower milestones.*

---

### Track organization activity

<!-- screenshot: model-release.png -->
![New model release](docs/assets/hf_model_release.png)


<!-- screenshot: org-updates.png -->
![Organization updates](docs/assets/hf_org_update.png)

*Get notified about new models, follower growth, and top model ranking changes for entire organizations.*

---

## 🎯 Use Cases & Features

💡 Building in AI is hard work. In our team, we used to celebrate "small wins"—like reaching a download milestone or 
successfully pushing a new model—by sharing screenshots in Slack.
I built this app to automate that celebration and turn static screenshots into a live, interactive "playground." 
It's designed to keep team spirit high and make AI development a collaborative social experience.

> **Team Culture:** Automatically celebrate when your model hits 1k, 10k, or 50k downloads.
>
> **Release Monitoring:** Get a notification the second a new model is pushed to your organization's namespace.
>
> **🕵️ Market Intelligence:** It’s not just for your own wins. You can use it to keep a pulse on what other organizations are up to. 
Track their new model drops or download spikes... 👀 Sometimes even before the official announcement.

### Available Now

| Feature                           | Description                                                                                  |
|-----------------------------------|----------------------------------------------------------------------------------------------|
| **📦 Model Subscriptions**        | Subscribe any Slack channel to any Hugging Face model by ID.                                 |
| **🏢 Organization Subscriptions** | Subscribe to an entire organization and track all activity.                                  |
| **📈 Download Milestones**        | Automatic notifications at 100, 500, 1k, 2k, 5k, 10k, 15k, 20k, 30k+ downloads.              |
| **❤️ Like Milestones**            | Automatic notifications at 5, 10, 50, 100, 250, 500, 750, 1k+ likes.                         |
| **👥 New Follower Alerts**        | Get notified when organizations gain new followers, with names and associated organizations. |
| **🆕 New Model Alerts**           | Real-time notifications when organizations release new models.                               |
| **🏆 Top Model Rankings**         | Track ranking changes in an org's top 3 models by downloads (last 30d).                      |
| **⏰ On-Demand Stats**             | Run `/hf now` to get current stats for all subscriptions instantly.                          |
| **🔌 Socket Mode**                | Runs entirely via Slack Socket Mode — no public URL needed.                                  |
| **💾 Persistent Subscriptions**   | Subscriptions survive bot restarts via JSON file storage.                                    |
| **🔒 Thread-Safe Storage**        | File locking prevents data corruption in concurrent scenarios.                               |
| **📊 Weekly Digest**              | Weekly summary with total downloads, new followers, and new models every Friday.             |

---

## 🚀 Installation

### Prerequisites

- Python **3.9+**
- A Slack workspace with permissions to install apps
- A Slack app created at [api.slack.com/apps](https://api.slack.com/apps)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/huggingface-slack-app.git
cd huggingface-slack-app
```

### 2. Set up a virtual environment

**Option A: With uv (recommended)**

[uv](https://github.com/astral-sh/uv) is a fast Python package manager that handles environments automatically:

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run directly - uv creates a virtual environment automatically
uv run --with-requirements requirements.txt python app.py
```

**Option B: Traditional**

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt

python3 app.py
```

### 4. Create a Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps) and click **Create New App** → **From an app manifest**.
2. Select your workspace and paste the contents of [`manifest.json`](manifest.json).
3. Review and create the app.
4. Navigate to **Basic Information** → **App Icon** and upload `docs/assets/hf_logo.png` as the icon.
5. Navigate to **Install App** and install the app to your workspace.

### 5. Configure environment variables

Create a `.env` file in the project root:

```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-level-token-here
```

> **Security note:** Never commit your `.env` file or tokens to version control. The project includes a `.gitignore`.

### 6. Run the bot

```bash
python3 app.py
```

You should see:

```
⚡ Bolt app is running on Socket Mode!
```

### 7. Invite the bot to a channel

In Slack, run:

```
/invite @HuggingFace
```

Then subscribe to a model:

```
/hf subscribe meta-llama/Llama-3-8B-Instruct
```

---

## 📖 Usage

All interaction happens through the `/hf` slash command in any channel where the bot is present.

```
/hf subscribe <model/org>     Subscribe to a model or organization
/hf unsubscribe <model/org>   Unsubscribe from updates
/hf now                       Get current stats for all subscriptions
```

**Examples:**

```
/hf subscribe meta-llama/Llama-3-8B-Instruct
/hf subscribe microsoft
/hf subscribe stabilityai/stable-diffusion-3-medium
/hf unsubscribe meta-llama/Llama-3-8B-Instruct
/hf now
```

---

## 🔧 Project Structure

```
huggingface-slack-app/
├── app.py                          # Application entry point
├── manifest.json                   # Slack app manifest
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Project config (ruff, pytest)
├── database.json                   # Subscription & stats persistence
├── weekly_stats.json               # Weekly stats (downloads, followers, models)
│
├── listeners/                      # Slack event handlers
│   └── commands/
│       └── hf.py                   # /hf slash command handler
│
├── jobs/                           # Scheduled background jobs
│   ├── hourly.py                   # Hourly update checker & notifier
│   └── weekly_digest.py            # Weekly digest generator (Mondays 9am)
│
├── services/                       # Business logic layer
│   ├── hf.py                       # HuggingFace Hub API integration
│   └── milestones.py               # Milestone detection engine
│
├── schemas/                        # Data models
│   ├── hf.py                       # ModelStatistics, OrganizationStatistics, User
│   └── icons.py                    # Emoji constants for messages
│
├── persistence/                    # Data storage layer
│   └── subscription_store.py       # JSON file storage with FileLock
```

---

## 🛤️ Coming Features

| Feature                                                                           | Status        |
|-----------------------------------------------------------------------------------|---------------|
| **Per-channel settings** — configure which milestone types a channel receives     | 🏗️ Planned   |
| **Leaderboard commands** — `/hf top` to see trending models                       | 🏗️ Planned   |
| **Database backend** — swap JSON storage for PostgreSQL/SQLite                    | 🏗️ Planned   |

Want a feature? [Open an issue](https://github.com/your-username/huggingface-slack-app/issues/new)!

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

### Development Setup

```bash
# Clone and set up
git clone https://github.com/your-username/huggingface-slack-app.git
cd huggingface-slack-app
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Copy env and fill in your tokens
cp .env.example .env   # (or create .env manually)
```

### Workflow

1. **Fork** the repository and create a branch:
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes.** Follow the existing code style (enforced by `ruff`).

3. **Test any new functionality.**

4. **Commit** with a clear message:
   ```bash
   git commit -m "feat: add support for daily digest mode"
   ```

5. **Push** and open a Pull Request.

### Guidelines

- Keep pull requests focused and small — one feature or fix per PR.
- Run `ruff check . && ruff format .` before committing.
- Update this README if you add user-facing features.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- [Slack Bolt](https://tools.slack.com/automation) — the Python framework that powers this app
- [HuggingFace Hub](https://huggingface.co/docs/hub) — for the API that makes this all possible
- All contributors who help improve this project
