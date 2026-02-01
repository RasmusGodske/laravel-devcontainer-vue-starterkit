# Setup Your Environment

This guide walks you through setting up your computer to work on your project.

## What's a Devcontainer?

A devcontainer is like a mini computer inside your computer.

**Why do we need this?** Every developer's computer is different - different operating systems, different software versions, different settings. This causes the classic "it works on my machine" problem.

A devcontainer solves this by creating an identical environment for everyone:

```
┌─────────────────────────────────────────┐
│  Your Computer                          │
│  ┌───────────────────────────────────┐  │
│  │  Devcontainer (Docker)            │  │
│  │  - Same for everyone              │  │
│  │  - All tools pre-installed        │  │
│  │  - Your code runs here            │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**What you need to know:**
- **Docker** is the software that creates and runs these mini computers (containers). Docker Desktop is the app you install to get Docker.
- VS Code connects to the container (that's what "Reopen in Container" does)
- Your code files are shared - when you edit a file, it's saved on your computer AND visible inside the container
- Everything else (PHP, Node, databases) runs inside the container

**Think of it like:** A fully-equipped workshop that comes with the project. Docker is the building that houses the workshop. Instead of buying all the tools yourself, you just open the workshop door.

## Prerequisites

Before you begin, install these tools **in this order**:

| Step | Tool | What It's For | Download Link |
|------|------|---------------|---------------|
| 1 | **Docker Desktop** | Runs the devcontainer (the mini computer) | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) |
| 2 | **Git** | Downloads and tracks your code | [git-scm.com/downloads](https://git-scm.com/downloads) |
| 3 | **Visual Studio Code** | Where you'll write code and talk to Claude | [code.visualstudio.com](https://code.visualstudio.com/) |
| 4 | **Dev Containers extension** | Lets VS Code connect to Docker | [Install from Marketplace](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) (click the link, then click "Install") |

**After installing Docker Desktop**, make sure to start it. You'll see a whale icon in your system tray (Windows) or menu bar (Mac) when it's running.

**What's an extension?** Extensions add features to VS Code. The Dev Containers extension adds the ability to work inside Docker containers. When you click the install link, it will open VS Code and show an "Install" button.

If you're not sure whether you have these installed, just try the download links - they'll help you install what's missing.

## Step 1: Open a Terminal

A **terminal** (also called command prompt or command line) is a text-based way to tell your computer what to do. Instead of clicking buttons, you type commands. You'll only need it for a few steps.

**On Mac:**
1. Press `Cmd + Space` to open Spotlight
2. Type "Terminal"
3. Press Enter

**On Windows:**
1. Press the Windows key
2. Type "PowerShell"
3. Press Enter

## Step 2: Clone Your Repository

**Cloning** means downloading a copy of your project from GitHub to your computer. Your project on GitHub is called a **repository** (or "repo" for short).

In the terminal, run this command:

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-PROJECT-NAME.git
```

Replace `YOUR-USERNAME` with your GitHub username and `YOUR-PROJECT-NAME` with your repository name.

**Tip:** You can copy the exact URL from your GitHub repository page - click the green **Code** button and copy the HTTPS URL.

## Step 3: Open VS Code

**On Mac:**
1. Press `Cmd + Space` to open Spotlight
2. Type "Visual Studio Code"
3. Press Enter

**On Windows:**
1. Press the Windows key
2. Type "Visual Studio Code"
3. Press Enter

## Step 4: Open Your Project in VS Code

1. In VS Code, click **File** in the top menu bar
2. Click **Open Folder...**
3. Navigate to where you cloned the project:
   - **Mac:** Usually `/Users/YOUR-NAME/YOUR-PROJECT-NAME`
   - **Windows:** Usually `C:\Users\YOUR-NAME\YOUR-PROJECT-NAME`
4. Select the project folder
5. Click **Open**

## Step 5: Reopen in Container

When you open the project, VS Code will detect the development container configuration.

1. A popup appears in the bottom-right corner saying:
   > "Folder contains a Dev Container configuration file..."
2. Click **Reopen in Container**

**If you missed the popup:**
1. Press `F1` to open the command palette
2. Type "Reopen in Container"
3. Select **Dev Containers: Reopen in Container**

**Wait for the build to complete.** The first time takes **5-10 minutes** because it's downloading and setting up the entire development environment. You'll see progress in the bottom-right corner.

Don't worry if it seems slow - this only happens once. Future startups are much faster.

## Step 6: Start the Development Environment

Once the container is ready, start the development services:

1. Press `Ctrl+Shift+P` (Mac: `Cmd+Shift+P`) to open the **command palette**
   - The command palette is a search box that lets you find and run any VS Code action
2. Type "Tasks: Run Task"
3. Press Enter
4. Select **"Dev: Start"** from the list

You'll see several terminal panels open as the services start up:
- **Database** - Where your app's data is stored
- **Cache** - Makes your app faster by remembering things
- **Laravel server** - Runs your app's backend code
- **Vite** - Handles the frontend (what you see in the browser)
- **Log viewer** - Shows what's happening behind the scenes

Wait until you see "Server running on" in one of the terminals.

## Step 7: You're Ready!

Open your web browser and go to:

**http://localhost:8080**

(**localhost** means "this computer" - your app is running on your own machine, not on the internet.)

You should see your application running!

### Default Login

A test account is already set up for you:

| Field | Value |
|-------|-------|
| **Email** | test@example.com |
| **Password** | password123 |

Use these credentials to log in and explore the application.

## Opening the VS Code Terminal

You'll need the terminal for some tasks. To open it:

1. In VS Code, click **Terminal** in the top menu bar
2. Click **New Terminal**

Or use the keyboard shortcut: `Ctrl + `` ` `` (Control plus the backtick key). The backtick looks like this: **`** and is often found near the Escape key or the 1 key, depending on your keyboard.

## Troubleshooting

**"Reopen in Container" doesn't appear**
- Make sure Docker Desktop is running (look for the whale icon in your system tray/menu bar)
- Make sure you installed the Dev Containers extension

**Container build fails**
- Make sure Docker Desktop has enough resources (at least 4GB RAM recommended)
- Try restarting Docker Desktop

**Port 8080 already in use**
- A **port** is like a door number - your app uses door 8080 to communicate
- Another application is already using that door
- Close the other application, or restart your computer

### Ask Claude for Help

If something goes wrong during setup or anytime later, just tell Claude:

```
I'm having a problem. When I try to [what you were doing], I see this error:

[paste the error message]
```

Claude will investigate and help you fix it. See [Fixing Bugs](ai-first/02-fixing-bugs.md) for more tips on getting help when things break.

## Step 8: Set Up Your Profile

The first time you open Claude, it will welcome you and ask a few questions about your experience level and preferences. This helps Claude adjust how it works with you - whether to ask technical questions, how much detail to show, and more.

Just answer the questions and you're all set!

You can change your preferences anytime by typing `/setup-profile` in Claude. (Commands starting with `/` are shortcuts - just type them exactly as shown and press Enter.)

## Next Steps

Your development environment is ready! Now choose how you'd like to work:

| Path | Best For |
|------|----------|
| **[AI-First Development](ai-first/)** | Building with Claude Code assistance - describe what you want in plain English |
| **[Hands-On Development](hands-on/)** | Running commands yourself and understanding the tools |

Not sure? Start with [AI-First Development](ai-first/) - you can always explore the hands-on guides later.
