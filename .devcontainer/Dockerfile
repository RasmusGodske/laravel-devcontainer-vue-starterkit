FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

RUN mkdir -p /home/vscode/project
WORKDIR /home/vscode/project

# Install PHP and additional PHP extensions and dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y php php-cli php-fpm php-json php-common php-mysql \
       php-zip php-gd php-mbstring php-curl php-xml php-pear php-bcmath \
       php-pgsql php-redis php-intl php-soap \
       php-dev libzip-dev libsodium-dev libfreetype6-dev libjpeg-turbo8-dev \
       libpng-dev

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
RUN echo 'export PATH="/home/vscode/project/vendor/bin/:$PATH"' >> /home/vscode/.zshrc

# Add Composer global bin directory to PATH
RUN echo 'export PATH="$PATH:$HOME/.composer/vendor/bin"' >> /home/vscode/.zshrc
RUN echo 'export PATH="$PATH:$HOME/.composer/vendor/bin"' >> /home/vscode/.bashrc

# Define the location of the npm cache. This is needed because permission problems
# will occur if the cache is stored in the default location (/root/tmp/.npm)
RUN echo 'export npm_config_cache=/home/vscode/tmp/npm-cache' >> /home/vscode/.zshrc

RUN git clone https://github.com/zsh-users/zsh-completions.git /home/vscode/.oh-my-zsh/custom/plugins/zsh-completions && \
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git /home/vscode/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting && \
    git clone https://github.com/zsh-users/zsh-autosuggestions.git /home/vscode/.oh-my-zsh/custom/plugins/zsh-autosuggestions

RUN cp /home/vscode/.zshrc /home/vscode/.zshrc.bak

RUN echo "$(cat /home/vscode/.zshrc)" | awk '{gsub(/plugins=\(git\)/, "plugins=(git zsh-completions zsh-syntax-highlighting zsh-autosuggestions)")}1' > /home/vscode/.zshrc.replaced && mv /home/vscode/.zshrc.replaced /home/vscode/.zshrc

# Install PostgreSQL client
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y postgresql-client \
    && apt-get install -y python3-pip

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN echo 'export PATH="/root/.local/bin:$PATH"' >> /home/vscode/.zshrc

# Install Claude Code CLI globally
RUN curl -fsSL https://claude.ai/install.sh | bash

RUN chown -R vscode:vscode /home/vscode/project
RUN chmod -R 700 /home/vscode/project

# Fix ownership of vscode home directory files
RUN chown -R vscode:vscode /home/vscode
