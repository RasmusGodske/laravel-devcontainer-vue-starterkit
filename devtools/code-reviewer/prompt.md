# Code Review

<context>
<files_to_review>
{files}
</files_to_review>

<original_task>
{original_task}
</original_task>
</context>

## Instructions

Review the files listed above. The files may include PHP, Vue, TypeScript, or JavaScript.

### Step 1: Identify File Types

Look at the file extensions to determine what types of files are being reviewed:
- `.php` files → Backend (PHP/Laravel)
- `.vue`, `.ts`, `.tsx`, `.js`, `.jsx` files → Frontend (Vue/TypeScript)

### Step 2: Run Linters (based on file types)

**For PHP files:**
```bash
pint --test <php-files>
```
Only Pint formatting errors matter.

**For Vue/TypeScript/JavaScript files:**
```bash
npm run type-check:files -- <frontend-files>
```

### Step 3: Read Relevant Rules

Based on the file types being reviewed:
- For PHP files: Read rules from `.claude/rules/backend/`
- For Vue/TS/JS files: Read rules from `.claude/rules/frontend/`

These rules define what conventions MUST be followed.

### Step 4: Review the Code

Read each file and check against the applicable rules.

### Step 5: Output Your Findings

Use the exact format specified below.

## Output Format

<output_instructions>
- Do NOT explain your process
- Do NOT praise the code
- Do NOT include unnecessary commentary
- You MUST wrap your entire response in a <review_result> tag
- You MUST include a <decision> tag with value "passed" or "blocked"
</output_instructions>

<report_format>
If there are NO issues at all:

```
<review_result>
<decision>passed</decision>
</review_result>
```

If there ARE issues:

```
<review_result>
<decision>blocked</decision>
<issues>

### Linting/Type Errors

- **File:** path/to/file.ext:LINE
- **Error:** [exact error from linter output]
- **Fix:** [how to fix]

### Rule Violations

- **File:** path/to/file.ext:LINE
- **Rule:** [which rule file was violated]
- **Violation:** [what the code does wrong]
- **Required:** [what the rule says should happen instead]
- **Fix:** [specific change needed]

### Other Issues

- **File:** path/to/file.ext:LINE
- **Category:** [Bug Risk | Security | Code Quality | Accessibility]
- **Issue:** [description]
- **Fix:** [how to fix]

</issues>
</review_result>
```

Omit any section within <issues> that has no problems.
</report_format>
