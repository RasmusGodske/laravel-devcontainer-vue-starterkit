# Laravel Vue Starterkit

A modern Laravel + Vue.js starter template with AI-assisted development built in.

---

## 🚀 Use This Template

> **Delete this section after creating your project**

This starterkit gives you:

- **Complete dev environment** - Docker-based, works on any machine
- **AI-assisted development** - Claude Code integration with guardrails
- **Production-ready stack** - Laravel 12, Vue 3, TypeScript, Tailwind CSS
- **Quality tools built in** - Testing, linting, code review

### Why This Setup is Powerful

Claude Code isn't just a chatbot - it can actually **do things** in your project:

- **Read and write files** directly (no copy-paste needed)
- **Run commands** - tests, linting, database migrations
- **Check logs** - see errors from your app, database, and frontend
- **Restart services** - fix issues without leaving the conversation
- **Follow your rules** - learns your coding conventions from `.claude/rules/`
- **Research documentation** - look up Laravel docs, Vue guides, or any topic

**Safe by design:** Claude runs inside a devcontainer (sandbox), so it can't affect anything outside your project.

**[Create Your Project →](https://github.com/new?template_name=laravel-devcontainer-vue-starterkit&template_owner=RasmusGodske)**

After creating your repository, follow the [Setup Guide](docs/guides/02-setup-environment.md) to get started.

---

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- [Git](https://git-scm.com/downloads)

### Quick Start

1. Clone your repository
2. Open in VS Code
3. Click "Reopen in Container" when prompted
4. Run the "Dev: Start" task (`Ctrl+Shift+P` → "Tasks: Run Task" → "Dev: Start")
5. Open http://localhost:8080

**Default login:** test@example.com / password123

📖 **[Full Setup Guide →](docs/guides/02-setup-environment.md)**

---

## Choose Your Path

### 🤖 AI-First Development

Build by describing what you want. Claude handles the code.

Perfect for: Creators, rapid prototyping, or anyone who prefers conversation over commands.

**[Get Started →](docs/guides/ai-first/)**

### 🛠️ Hands-On Development

Run commands yourself and understand the tools.

Perfect for: Developers who want full control.

**[Get Started →](docs/guides/hands-on/)**

---

## What's Included

| Category | Features |
|----------|----------|
| **Stack** | Laravel 12, Vue 3, Inertia.js, TypeScript, Tailwind CSS |
| **Database** | PostgreSQL 17, Redis |
| **Quality** | PHPStan, ESLint, Prettier, PHPUnit |
| **AI Tools** | Claude Code, tarnished (change tracking), lumby (error diagnosis), reldo (code review) |
| **DX** | Hot reload, IDE helpers, type generation |

---

## Documentation

| Guide | Description |
|-------|-------------|
| [Create Your Project](docs/guides/01-create-your-project.md) | Create a repo from this template |
| [Setup Environment](docs/guides/02-setup-environment.md) | Install and configure everything |
| [AI-First Guides](docs/guides/ai-first/) | Build with Claude assistance |
| [Hands-On Guides](docs/guides/hands-on/) | Manual development reference |
| [Technical Docs](docs/development/) | Deep dives into specific features |

---

## Troubleshooting

**Container won't start**
- Make sure Docker Desktop is running
- Try restarting Docker Desktop

**Port 8080 in use**
- Stop whatever is using port 8080, or change the port in `.env`

**Something else broken?**
- Open Claude and describe the problem - it can help diagnose and fix issues

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This starter kit is open-sourced software licensed under the [MIT license](LICENSE).
