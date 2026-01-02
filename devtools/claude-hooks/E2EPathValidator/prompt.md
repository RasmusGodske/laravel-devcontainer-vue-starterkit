# E2E Test Path Validation

<context>
<file_path_being_created>
{file_path}
</file_path_being_created>
</context>

## Instructions

You are validating an E2E test file path for convention compliance.

### Step 1: Find E2E Test Conventions

Search for E2E test conventions in the project:
- Check `.claude/rules/` for e2e or test conventions
- Look for patterns like "test directories MUST mirror..." or similar

### Step 2: Understand the Convention

The convention typically states that test directories must mirror the pages/views structure.
For example:
- If a page exists at `resources/js/Pages/Feature/Example.vue`
- Then the test should be at `e2e/tests/Feature/Example/smoke.spec.ts`

### Step 3: Verify the Corresponding File Exists

This is the CRITICAL step. You MUST:
1. Determine what page/view file the test path is trying to mirror
2. Use `Glob` or `ls` to CHECK if that page/view file actually exists
3. If it doesn't exist, find where the actual page is located

For example:
- Test path: `e2e/tests/Feature/Settings/Users/Index/smoke.spec.ts`
- Expected page: `resources/js/Pages/Feature/Settings/Users/Index.vue` (or similar)
- Check: Does this page exist? If not, where is the actual Users/Index page?

### Step 4: Output Your Decision

<output_instructions>
- Do NOT explain your process in detail
- Do NOT include unnecessary commentary
- You MUST wrap your entire response in a <validation_result> tag
- You MUST include a <decision> tag with value "allow" or "block"
</output_instructions>

<report_format>
If the path is CORRECT (page exists at expected location):

```
<validation_result>
<decision>allow</decision>
</validation_result>
```

If the path is INCORRECT (page doesn't exist or is in a different location):

```
<validation_result>
<decision>block</decision>
<reason>
The test path `{test_path}` is incorrect.

**Problem:** There is no page at `{expected_page_path}`

**Actual page location:** `{actual_page_path}`

**Correct test path:** `{correct_test_path}`
</reason>
</validation_result>
```

Replace the placeholders with actual paths you discovered.
</report_format>
