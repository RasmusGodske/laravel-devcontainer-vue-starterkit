FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

RUN mkdir -p /home/vscode/project
WORKDIR /home/vscode/project

# Install PHP 8.3 and required extensions
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y software-properties-common \
    && add-apt-repository ppa:ondrej/php \
    && apt-get update \
    && apt-get install -y php8.3 php8.3-cli php8.3-fpm php8.3-mysql php8.3-zip \
       php8.3-gd php8.3-mbstring php8.3-curl php8.3-xml php8.3-bcmath \
       php8.3-pgsql php8.3-redis php8.3-intl php8.3-soap php8.3-sqlite3 \
       php8.3-dev php8.3-xdebug libzip-dev libsodium-dev libfreetype6-dev libjpeg-dev libpng-dev

# Configure Xdebug for debugging
RUN echo "xdebug.mode=debug" >> /etc/php/8.3/cli/conf.d/20-xdebug.ini \
    && echo "xdebug.start_with_request=yes" >> /etc/php/8.3/cli/conf.d/20-xdebug.ini \
    && echo "xdebug.client_host=127.0.0.1" >> /etc/php/8.3/cli/conf.d/20-xdebug.ini \
    && echo "xdebug.client_port=9003" >> /etc/php/8.3/cli/conf.d/20-xdebug.ini \
    && echo "xdebug.idekey=VSCODE" >> /etc/php/8.3/cli/conf.d/20-xdebug.ini

# Install Composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

# Install Laravel installer globally
USER vscode
RUN composer global require laravel/installer
USER root

# Create useful aliases for Laravel development
RUN echo "alias art='php artisan'" >> /home/vscode/.zshrc
RUN echo "alias artisan='php artisan'" >> /home/vscode/.zshrc
RUN echo "alias test='php artisan test'" >> /home/vscode/.zshrc
RUN echo "alias migrate='php artisan migrate'" >> /home/vscode/.zshrc
RUN echo "alias e2e='npm run test:e2e'" >> /home/vscode/.zshrc
RUN echo 'export PATH="/home/vscode/project/vendor/bin/:$PATH"' >> /home/vscode/.zshrc

# Add Composer global bin directory to PATH
RUN echo 'export PATH="$PATH:$HOME/.composer/vendor/bin"' >> /home/vscode/.zshrc
RUN echo 'export PATH="$PATH:$HOME/.composer/vendor/bin"' >> /home/vscode/.bashrc

# Define the location of the npm cache. This is needed because permission problems
# will occur if the cache is stored in the default location (/root/tmp/.npm)
RUN echo 'export npm_config_cache=/home/vscode/tmp/npm-cache' >> /home/vscode/.zshrc

# Install zsh plugins
RUN git clone https://github.com/zsh-users/zsh-completions.git /home/vscode/.oh-my-zsh/custom/plugins/zsh-completions && \
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git /home/vscode/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting && \
    git clone https://github.com/zsh-users/zsh-autosuggestions.git /home/vscode/.oh-my-zsh/custom/plugins/zsh-autosuggestions

RUN cp /home/vscode/.zshrc /home/vscode/.zshrc.bak

RUN echo "$(cat /home/vscode/.zshrc)" | awk '{gsub(/plugins=\(git\)/, "plugins=(git zsh-completions zsh-syntax-highlighting zsh-autosuggestions)")}1' > /home/vscode/.zshrc.replaced && mv /home/vscode/.zshrc.replaced /home/vscode/.zshrc

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y gh

# Install PostgreSQL client, Python, and tmux
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y postgresql-client python3-pip tmux

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Install Playwright browser dependencies
# These are required for running Chromium, Firefox, and WebKit browsers
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2t64 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    libwayland-client0 \
    libxext6 \
    libx11-xcb1 \
    libvulkan1 \
    xvfb \
    fonts-freefont-ttf \
    fonts-noto-color-emoji

# Install desktop components for headed browser automation via noVNC
# x11vnc: exposes the Xvfb display as a VNC server
# novnc: web-based VNC viewer (includes websockify for WebSocket proxying)
# fluxbox: lightweight window manager so browser windows render correctly
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y x11vnc novnc fluxbox \
    && ln -sf /usr/share/novnc/vnc.html /usr/share/novnc/index.html

# Pre-install @playwright/mcp globally so the launcher doesn't cold-download it
# on first use (which can exceed Claude Code's MCP initialization timeout).
# Also install its bundled Chromium — @playwright/mcp uses its own mcp-chromium-*
# variant separate from any project-level Playwright install.
#
# Node.js is managed by apt (installed above), so npm root -g is stable for both
# root and vscode users. We install the package once globally as root, then run
# the chromium install for the vscode user so the browser ends up in their cache.
RUN npm install -g @playwright/mcp@0.0.68

# Pre-install the MCP-managed Chromium browser for vscode user.
# @playwright/mcp uses its own mcp-chromium-* variant separate from any system Playwright.
USER vscode
RUN node "$(npm root -g)/@playwright/mcp/node_modules/.bin/playwright" install chromium
USER root

# Install Claude Code CLI and uv for vscode user
USER vscode
RUN curl -fsSL https://claude.ai/install.sh | bash
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
# Install quality tools via uv
RUN /home/vscode/.local/bin/uv tool install reldo
RUN /home/vscode/.local/bin/uv tool install tarnished
USER root
RUN echo 'export PATH="$PATH:/home/vscode/.claude/local/bin"' >> /home/vscode/.zshrc
RUN echo 'export PATH="$PATH:/home/vscode/.local/bin"' >> /home/vscode/.zshrc

# Install Bun and Claude Code for root user (GitHub Actions runs as root)
RUN echo "Installing Bun for root..." \
    && curl -fsSL https://bun.sh/install | bash \
    && echo 'export BUN_INSTALL="$HOME/.bun"' >> /root/.bashrc \
    && echo 'export PATH="$BUN_INSTALL/bin:$PATH"' >> /root/.bashrc
RUN echo "Installing Claude Code for root..." \
    && curl -fsSL https://claude.ai/install.sh | bash \
    && echo 'export PATH="$HOME/.local/bin:$PATH"' >> /root/.bashrc
RUN echo "Installing uv for root..." \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && echo 'export PATH="$HOME/.local/bin:$PATH"' >> /root/.bashrc
RUN ln -s /root/.local/bin/uvx /usr/local/bin/uvx
RUN echo "Installing reldo for root..." \
    && /root/.local/bin/uv tool install reldo \
    && ln -s /root/.local/bin/reldo /usr/local/bin/reldo
RUN echo "Installing tarnished for root..." \
    && /root/.local/bin/uv tool install tarnished \
    && ln -s /root/.local/bin/tarnished /usr/local/bin/tarnished

# Create symlinks for devtools commands (short aliases)
RUN ln -s /home/vscode/project/devtools/test/php.sh /usr/local/bin/test:php \
    && ln -s /home/vscode/project/devtools/lint/php.sh /usr/local/bin/lint:php \
    && ln -s /home/vscode/project/devtools/lint/js.sh /usr/local/bin/lint:js \
    && ln -s /home/vscode/project/devtools/lint/ts.sh /usr/local/bin/lint:ts \
    && ln -s /home/vscode/project/devtools/review/code.sh /usr/local/bin/review:code \
    && ln -s /home/vscode/project/devtools/qa.sh /usr/local/bin/qa

# Create symlinks for service commands
RUN ln -s /home/vscode/project/devtools/services/database.sh /usr/local/bin/service:database \
    && ln -s /home/vscode/project/devtools/services/cache.sh /usr/local/bin/service:cache \
    && ln -s /home/vscode/project/devtools/services/serve.sh /usr/local/bin/service:serve \
    && ln -s /home/vscode/project/devtools/services/vite.sh /usr/local/bin/service:vite \
    && ln -s /home/vscode/project/devtools/services/logs.sh /usr/local/bin/service:logs \
    && ln -s /home/vscode/project/devtools/services/desktop.sh /usr/local/bin/service:desktop

# Create symlinks for dev orchestration commands
RUN ln -s /home/vscode/project/devtools/dev/start.sh /usr/local/bin/dev:start \
    && ln -s /home/vscode/project/devtools/dev/stop.sh /usr/local/bin/dev:stop \
    && ln -s /home/vscode/project/devtools/dev/status.sh /usr/local/bin/dev:status

RUN chown -R vscode:vscode /home/vscode/project
RUN chmod -R 700 /home/vscode/project

# Symlink tmux config
RUN ln -sf /home/vscode/project/.tmux.conf /home/vscode/.tmux.conf

# Fix ownership of vscode home directory files
RUN chown -R vscode:vscode /home/vscode
