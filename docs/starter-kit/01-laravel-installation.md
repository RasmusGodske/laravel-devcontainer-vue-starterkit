# Laravel Installation

## Why This Step
This step establishes the foundation of the starter kit by creating a fresh Laravel project with Vue.js integration. The Laravel installer provides a quick way to scaffold a project with pre-configured frontend tooling.

## What It Does
- Installs the Laravel CLI tool globally via Composer
- Creates a new Laravel project with Vue.js starter kit
- Sets up the basic project structure with Vue 3, Inertia.js, and frontend build tools
- Prepares the project for further customization

## Implementation

### Install Laravel CLI Tool
```bash
composer global require laravel/installer
```

### Create Laravel Project with Vue Starter Kit
```bash
laravel new new-app --vue --phpunit
```

**Important:** When prompted to install npm dependencies, select "no" as we'll handle this later with the devcontainer.

### Move Files to Root Directory
Since we're creating a starter kit template, we need to move all files from the temporary project directory to the root:

```bash
# Move files from vendor directory
mv ./new-app/vendor/* ./vendor/
rm -r ./new-app/vendor

# Move the rest of the files
cp -r ./new-app/. ./ && rm -rf ./new-app
```