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
    && apt-get install -y postgresql-client sqlite3 python3-pip tmux jq

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs

# Install Playwright Chromium browser for both vscode (local dev) and root (CI).
ARG PLAYWRIGHT_VERSION=1.52.0
USER vscode
RUN npx playwright@${PLAYWRIGHT_VERSION} install chromium
USER root
RUN npx playwright@${PLAYWRIGHT_VERSION} install chromium

# Install Playwright system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y \
        libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
        libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
        libgbm1 libasound2t64 libpango-1.0-0 libcairo2 libatspi2.0-0 \
        libwayland-client0 libxext6 libx11-xcb1 xvfb fonts-freefont-ttf \
        fonts-noto-color-emoji libvulkan1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install desktop components for headed browser automation via noVNC
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y x11vnc novnc fluxbox \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/share/novnc/vnc.html /usr/share/novnc/index.html

# Install Claude Code CLI and uv for vscode user
USER vscode
RUN curl -fsSL https://claude.ai/install.sh | bash
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
# Install quality tools via uv
RUN /home/vscode/.local/bin/uv tool install lumby
RUN /home/vscode/.local/bin/uv tool install reldo
RUN /home/vscode/.local/bin/uv tool install tarnished
# Install mcp-proxy (bridges Claude Code's stdio MCP to Serena's SSE server)
RUN /home/vscode/.local/bin/uv tool install mcp-proxy
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
RUN echo "Installing lumby for root..." \
    && /root/.local/bin/uv tool install lumby \
    && ln -s /root/.local/bin/lumby /usr/local/bin/lumby \
    && ln -s /root/.local/bin/uvx /usr/local/bin/uvx
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
    && ln -s /home/vscode/project/devtools/lint/deadcode.sh /usr/local/bin/lint:deadcode \
    && ln -s /home/vscode/project/devtools/review/code.sh /usr/local/bin/review:code \
    && ln -s /home/vscode/project/devtools/qa.sh /usr/local/bin/qa

# Create symlinks for git helpers
RUN ln -s /home/vscode/project/devtools/git/commit.sh /usr/local/bin/git:commit \
    && ln -s /home/vscode/project/devtools/git/branch.sh /usr/local/bin/git:branch \
    && ln -s /home/vscode/project/devtools/git/pr.sh /usr/local/bin/git:pr

# Create symlinks for sync commands
RUN ln -s /home/vscode/project/devtools/sync/models.sh /usr/local/bin/sync:models \
    && ln -s /home/vscode/project/devtools/sync/types.sh /usr/local/bin/sync:types \
    && ln -s /home/vscode/project/devtools/sync/routes.sh /usr/local/bin/sync:routes \
    && ln -s /home/vscode/project/devtools/sync/all.sh /usr/local/bin/sync:all

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
