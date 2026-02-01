# Creating Features

With Claude, you build features by describing what you want. Claude writes the code, creates the files, and makes it work.

## How It Works

1. **You describe** what you want to build
2. **Claude builds** it - writing code, creating files, updating the database
3. **You review** and ask for changes if needed
4. **Claude verifies** by running tests

## Simple Requests

Just tell Claude what you want:

```
Add a logout button to the navigation bar
```

```
Create a contact form on the homepage
```

```
Add a page that shows a list of all users
```

Claude will figure out where to put the code, what files to create, and how to make it work with the rest of your app.

## Being Specific Helps

The more detail you provide, the closer the result will be to what you want.

**Vague:**
```
Add a profile page
```

**Better:**
```
Add a profile page that shows:
- The user's name and email
- Their profile picture
- A button to edit their information
```

**Even better:**
```
Add a profile page that shows:
- The user's name and email at the top
- Their profile picture (use a placeholder if they don't have one)
- A button to edit their information
- Their account creation date at the bottom
```

## Iterating on Features

Your first request doesn't have to be perfect. You can refine as you go:

```
Move the button to the right side
```

```
Make the header blue instead of gray
```

```
Also add a phone number field to the form
```

```
The profile picture should be circular, not square
```

Claude remembers what you've been working on, so you can refer to things naturally.

## Describing Visual Changes

When you want something to look a certain way:

```
Make the login form centered on the page with a white background and rounded corners
```

```
Add some spacing between the form fields
```

```
Use a larger font for the page title
```

## Asking for Multiple Things

You can ask for several things at once:

```
Create a settings page with:
- A section to change your password
- A section to update your email
- A toggle to enable email notifications
- A delete account button at the bottom (with a confirmation)
```

## Verifying Your Feature Works

After Claude builds something, ask it to verify:

```
Run the tests to make sure everything works
```

```
Check if there are any errors
```

Then open your browser and go to http://localhost:8080 to see the changes yourself.

## Saving Your Work

When you're happy with a feature:

```
Commit these changes with a message describing what we built
```

See [Working with Git](03-working-with-git.md) for more on saving and managing your code.

## Examples

Here are some complete feature requests to inspire you:

**A blog:**
```
Create a simple blog where:
- There's a page listing all blog posts (title and date)
- Clicking a post shows the full content
- There's an admin page where I can create new posts
- Only logged-in users can create posts
```

**User dashboard:**
```
Create a dashboard that users see after logging in:
- Show a welcome message with their name
- Display some stats (when they joined, number of posts)
- Have quick links to common actions
```

**Contact form:**
```
Add a contact page with a form that has:
- Name field
- Email field
- Message textarea
- Submit button
When submitted, save it to the database and show a thank you message
```

## Next Steps

- [Fixing Bugs](02-fixing-bugs.md) - What to do when something breaks
- [Working with Git](03-working-with-git.md) - Save your work and track changes
