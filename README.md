# DiscordBotStarter

<p align="center">
  <img src="./assets/logo.png" alt="Logo" height="128px">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" />
  <img src="https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white"/>
  <img src="https://img.shields.io/github/license/DavyJonesCodes/DiscordBotStarter?style=for-the-badge" />
</p>

A starter template for creating a Discord bot in Python. This template includes basic command handling, event listeners, automatic backups, a configurable dashboard, and utility functions for logging and configuration. Easily customizable for various bot functionalities.

## ✨ Features

- Basic command handling
- Event listeners
- Automatic backups
- Configurable dashboard
- Utility functions for logging and configuration

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### 📋 Prerequisites

- Python 3.8+
- Discord bot token

### 🛠️ Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/DavyJonesCodes/DiscordBotStarter.git
    cd DiscordBotStarter
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Create a `.env` file with your bot token and other configurations:**

    ```plaintext
    TOKEN=your-bot-token-here
    DEVELOPER=your-developer-id-here
    DATABASE=your-database-file-here
    ```

5. **Run the bot:**

    ```bash
    python main.py
    ```

## 📂 Project Structure

```
DiscordBotStarter/
│
├── .env.example            # Example environment file with placeholder values
├── .gitignore              # Specifies files and directories to ignore in Git
├── README.md               # This README file
├── requirements.txt        # Project dependencies
├── main.py                 # Main bot file
├── cogs/                   # Directory for cog files
│   └── example_cog.py      # Example cog file
├── jsonDB.py               # JSON database handling script
└── data.json               # JSON database file (if applicable)
```

## 📚 Usage

### Slash Commands

- **/hello**: Sends a hello message with a button
- **/sync**: Syncs the commands (developer only)
- **/refresh**: Refreshes the commands (developer only)
- **/ping**: Checks the bot latency (developer only)
- **/dashboard**: Opens the dashboard (administrator only)

### Configurable Dashboard

The dashboard allows you to view and update key settings for your server, including log channels and backup channels.

## 🛡️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Contact

For any inquiries or issues, please open an issue on the GitHub repository or contact the developer.

---

Happy coding! 🎉
