# Release Checklist

## Before first public release

- Confirm the package names are available on PyPI and npm:
  - `webprinter-mcp`
- Replace any placeholder project metadata if you add an official repository homepage later.
- Confirm the chosen license text is correct for your intended distribution model.
- Verify the upstream WebPrinter API terms allow this package to be published publicly.

## GitHub repository settings

- Add `PYPI_API_TOKEN` to GitHub Actions secrets.
- Add `NPM_TOKEN` to GitHub Actions secrets.
- Decide whether releases should be tag-driven only, or also manual.

## Local release checks

- `python -m build`
- `python -m twine check dist/*`
- `npm pack --dry-run`

## Release steps

1. Update version in [pyproject.toml](/D:/workspaces/mcp/智睦云打印/pyproject.toml) and [package.json](/D:/workspaces/mcp/智睦云打印/package.json).
2. Add an entry to [CHANGELOG.md](/D:/workspaces/mcp/智睦云打印/CHANGELOG.md).
3. Commit changes.
4. Create a git tag like `v0.1.1`.
5. Push the branch and tag.
6. Let GitHub Actions publish to PyPI and npm.
