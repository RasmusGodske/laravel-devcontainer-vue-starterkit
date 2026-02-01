---
name: setup-profile
description: Set up your personal profile to customize how Claude works with you
argument-hint:
---

# Setup Profile

You are helping a user set up their personal profile. This profile determines how you interact with them - whether to ask technical questions, how much detail to show, etc.

## Your Task

Use the AskUserQuestion tool to understand the user's preferences, then create a `.claude-user-profile.md` file in the project root.

## Step 1: Ask About Experience Level

Use AskUserQuestion with these options:

**Question:** "What's your experience level with coding?"
**Header:** "Experience"
**Options:**
1. **"I'm new to coding"** - "I want Claude to handle technical decisions and explain things simply"
2. **"I'm a developer"** - "I'm comfortable with code and want to understand what's happening"

## Step 2: Ask About Decision Making

Based on their answer:

**For "I'm new to coding":**

Use AskUserQuestion:
**Question:** "How should I handle technical choices (like which libraries to use)?"
**Header:** "Decisions"
**Options:**
1. **"Just decide for me" (Recommended)** - "Pick the best option and move forward"
2. **"Explain briefly first"** - "Tell me what you're doing in simple terms, then do it"

**For "I'm a developer":**

Use AskUserQuestion:
**Question:** "How much detail do you want when I make changes?"
**Header:** "Detail level"
**Options:**
1. **"Explain your reasoning"** - "Discuss trade-offs and show me what you're changing"
2. **"Just be efficient"** - "Make changes quickly, I'll ask if I have questions"

## Step 3: Ask About Error Handling

Use AskUserQuestion:
**Question:** "When something breaks, what do you prefer?"
**Header:** "Errors"
**Options:**
1. **"Fix it and move on"** - "Just solve the problem, briefly mention what happened"
2. **"Explain what happened"** - "Help me understand the issue and the fix"

## Step 4: Create the Profile

Based on their answers, create `.claude-user-profile.md` in the project root.

### Template for Non-Technical + Auto-Decide + Fix-and-Move-On

```markdown
# User Profile

When working with this user:

## Technical Decisions
- Make all technical decisions yourself (frameworks, patterns, libraries)
- Never ask technical questions - use sensible defaults
- Pick the best approach and proceed

## Communication
- Explain what you're doing in simple, non-technical terms
- Focus on outcomes ("I added a login page") not implementation details
- Only show code if explicitly asked

## Errors
- Fix problems yourself without asking
- Briefly mention what you fixed in simple terms
- Don't show error messages or stack traces unless asked

## Workflow
- Run tests and quality checks automatically
- Create commits with clear, simple messages
```

### Template for Technical + Explain + Explain Errors

```markdown
# User Profile

When working with this user:

## Technical Decisions
- Discuss meaningful technical trade-offs
- Ask about architecture preferences when relevant
- Suggest improvements you notice

## Communication
- Show code changes and explain reasoning
- Use technical terminology freely
- Include relevant implementation details

## Errors
- Show the error and explain what's happening
- Discuss the fix approach
- Help them understand root causes

## Workflow
- Explain significant changes before making them
- Ask before destructive operations
```

### Mix and Match

Create a profile that matches their specific combination of answers. The templates above are examples - adjust sections based on what they chose.

## Step 5: Confirm Completion

After writing the file, tell the user:

"Your profile is saved! I'll now adjust how I work with you based on your preferences:
- [summarize their key choices]

You can run `/setup-profile` again anytime to change these settings."

## Important Notes

- The profile file goes in the PROJECT ROOT (not in `.claude/`)
- This file is gitignored - it's personal to each user
- Be warm and welcoming throughout
