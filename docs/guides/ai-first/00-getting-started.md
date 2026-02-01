# Getting Started with Claude

Claude Code is an AI assistant that helps you build your project. Instead of writing code yourself, you describe what you want in plain English and Claude handles the implementation.

## Opening Claude

There are two ways to chat with Claude:

### Option A: In VS Code (Recommended)

1. Press `Ctrl+Shift+P` (Mac: `Cmd+Shift+P`) to open the command palette
2. Type "Claude Code: Open in New Tab"
3. Press Enter

Claude opens in a new tab where you can chat. You can keep this tab open alongside your code files.

### Option B: In the Terminal

1. Open the VS Code terminal: click **Terminal** → **New Terminal**
2. Type `claude` and press Enter
3. You're now chatting with Claude in the terminal

### When to Use Which

| Method | Best For |
|--------|----------|
| **VS Code tab** | Easier to read, keeps chat visible alongside code |
| **Terminal** | Quick access, preferred by some developers |

Both methods have the same capabilities - choose whichever feels more comfortable.

## Your First Conversation

Once Claude is open, try asking some questions to get familiar with your project:

**Understand the project:**
```
What is this project? Give me a brief overview.
```

**Explore the structure:**
```
Explain the folder structure. What's in each directory?
```

**Get ideas:**
```
What kind of features could I build with this?
```

## How Claude Knows About Your Project

Claude automatically understands your project because it can:

- **Read your code** - Claude can explore files and understand how things work
- **Read CLAUDE.md** - This file contains instructions about the project's conventions
- **Run commands** - Claude can run tests, check for errors, and verify changes work

This means you don't need to explain the basics - Claude already knows the tech stack and how the project is organized.

## Tips for Talking to Claude

**Be specific about what you want**
```
# Too vague
"Make a user page"

# Better
"Create a user profile page that shows the user's name, email, and a profile picture"
```

**Share error messages**

When something breaks, copy and paste the error message:
```
I'm seeing this error when I try to log in:

[paste error message here]

Can you fix it?
```

**Ask follow-up questions**

If Claude's response isn't quite right, just say so:
```
"That's close, but I wanted the button to be on the right side"
"Can you also add validation for the email field?"
"I don't understand that part - can you explain?"
```

**Let Claude verify its work**
```
"Run the tests to make sure this works"
"Check if there are any errors"
```

## What Claude Can Do

Claude isn't just a chatbot that gives you text to copy-paste. In this setup, Claude can actually **do things** in your project:

### Read and Write Files

Claude can read any file in your project and edit it directly:

```
"Read the User model and explain what it does"
"Update the homepage to show a welcome message"
"Create a new page for user settings"
```

No copy-paste needed - Claude makes the changes directly.

### Run Commands

Claude can run commands to test and verify your code:

```
"Run the tests"
"Check if there are any linting errors"
"Run the database migrations"
```

### Check Logs

When something goes wrong, Claude can check what happened:

```
"Check the Laravel logs for errors"
"What's happening in the Vite output?"
"Are there any database errors?"
```

Claude has access to logs from:
- Your Laravel app
- The database (PostgreSQL)
- The frontend build tool (Vite)
- The cache (Redis)

### Manage Services

Claude can restart services if they're not working:

```
"Restart the Laravel server"
"The frontend isn't updating - can you restart Vite?"
"Check if all services are running"
```

### Follow Your Rules

This project has coding conventions in `.claude/rules/`. Claude reads these and follows them automatically, so your code stays consistent.

### Research Documentation

Claude can search the web and look up documentation:

```
"How do I add authentication in Laravel?"
"What's the best way to validate forms in Vue?"
"Look up how to send emails with Laravel"
```

This is useful when you want to learn something new or find the right approach for a problem.

### Open Your App

Claude can open your app in the browser:

```
"Open the app in my browser"
"Show me the login page"
```

### Quick Reference

| Task | Example Prompt |
|------|----------------|
| Create features | "Add a contact form to the homepage" |
| Fix bugs | "The login button doesn't work - here's the error: ..." |
| Explain code | "How does the authentication system work?" |
| Run tests | "Run the tests and tell me if anything is broken" |
| Check logs | "Are there any errors in the logs?" |
| Restart services | "Restart the Laravel server" |
| Manage git | "Commit my changes and push to GitHub" |
| Review code | "Review what I've changed so far" |
| Research | "How do I add pagination in Laravel?" |

## Safe by Design

You might wonder: "Is it safe to let Claude modify my files and run commands?"

**Yes, because of the devcontainer sandbox.** Claude runs inside an isolated environment (the devcontainer) that:

- Only has access to your project folder
- Cannot access your personal files, passwords, or other projects
- Cannot install software on your actual computer
- Cannot access the internet except to talk to you

Think of it like giving Claude the keys to a workshop, but the workshop is in a separate building with no connection to your house.

## Next Steps

Now that you know how to talk to Claude, learn how to:

- **[Create Features](01-creating-features.md)** - Build new functionality with specs
- **[Fix Bugs](02-fixing-bugs.md)** - Report errors and let Claude fix them
- **[Work with Git](03-working-with-git.md)** - Branches, commits, and pull requests
- **[Run Quality Checks](04-quality-checks.md)** - Keep your code clean and tested
