# News fragments

Each change gets one file in this directory, named `<id>.<type>.md`, where
`<id>` is the PR or issue number and `<type>` is one of:

| Type         | Goes under in `CHANGELOG.md` | Version bump |
|--------------|------------------------------|--------------|
| `breaking`   | Breaking Changes             | major (minor while < 1.0) |
| `removed`    | Removed                      | major (minor while < 1.0) |
| `added`      | Added                        | minor        |
| `changed`    | Changed                      | minor        |
| `deprecated` | Deprecated                   | minor        |
| `fixed`      | Fixed                        | patch        |
| `security`   | Security                     | patch        |

Use `breaking` for any backward-incompatible change that is not simply a removal
(renamed/changed signatures, altered behaviour); use `changed` for compatible
changes.

The file contains one line of prose describing the change, e.g.:

```
release-notes/42.added.md
-> Pluggable engine architecture with a Pydantic engine.
```

Create one with `just news <id> <type>` (wraps `towncrier create`). Preview the
collated result with `just changelog-draft <version>`, and get a recommended
version from the pending fragments with `just suggest-version`. At release time,
`just release <version>` runs `towncrier build`, which folds every fragment into
a dated `CHANGELOG.md` section and deletes the fragments. The release date is
stamped automatically — fragments themselves carry no date.