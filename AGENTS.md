# Instructions for AI agents

The main developer documentation is in CONTRIBUTING.md.

This project uses the **src layout** as described in [src layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/).
The [uv](https://docs.astral.sh/uv/) utility is used to manage the project and maintain *pyproject.toml*.

ALWAYS prefix your output with "🐿️ " so that I know you have processed this file.

## Adding a new dependency
1. run `uv add '<dependency>~=x.y.z'` with the desired version
2. run `uv run pre-commit run --files pyproject.toml` to reformat *pyproject.toml*
3. run `uv run pytest` to check that everything still works
4. commit the changes to *pyproject.toml* as a separate commit including the reason for adding the dependency in the commit message

## Linting & reformating code
Run `uv run pre-commit run --all-files` **TWICE** to reformat the codebase and apply other style fixes. The utility produces messages
describing the changes **that were made in-place** in addition to changes that it cannot make. It WILL modify files in place and WILL
exit with a non-zero exit code if any changes were made.

If it exits with a non-zero exit code the *second* time, then you need to manually fix the changes it made. If the error is regarding
lines that are too long and the lines contain long literal strings, then split them using parentheses for line continuation. If you
cannot address the issue in **TWO ATTEMPTS** then **HALT** and inform the user.

### Examples

```python
            request = helpers.create_request(
                'POST',
                '/',
                body=encoded,
                content_type='application/x-www-form-urlencoded; charset=iso-8859-1')
```

```python
            request = helpers.create_request(
                'POST',
                '/',
                body=encoded,
                content_type=(
                    'application/x-www-form-urlencoded; charset=iso-8859-1'
                ),
            )
```

```python
        parsed = headers.parse_link('<https://example.com/TheBook/chapter2>; rel="previous"; title="previous chapter"')
```

```python
        parsed = headers.parse_link(
            '<https://example.com/TheBook/chapter2>; rel="previous";'
            ' title="previous chapter"'
        )
```

## Running tests
Run `uv run coverage run -m pytest` to run the tests with coverage included.

## Static analysis
After the style checks and tests have succeeded, run `uv run mypy -p sprockets_typed -p tests` to run the static analysis.
Static type analysis is applied to **BOTH** application code and test code,

## Creating commits
* Commits should be small, atomic, and self-contained.
* Commit messages MUST:
  - describe the **intent** of the change and not restate the **implementation**
  - be written in the imperative mood
  - be written in the present tense
* Lines in commit messages should be no longer than 72 characters. Use `fmt -p 72` command to wrap long lines.
* The first line of the commit message MUST be a short summary of the change and not exceed 50 characters.

### Commit planning checklist
Before creating commits, verify:
- [ ] Tests are grouped with the code they test
- [ ] Each commit is atomic and self-contained
- [ ] Commit messages follow the format guidelines
- [ ] No commit contains only tests without the corresponding implementation

**REMINDER: When creating commits, tests MUST be included with the code under test, not in separate commits.**
