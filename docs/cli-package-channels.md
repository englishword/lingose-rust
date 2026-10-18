# CLI7 package channels

The user requested WinGet → Scoop → Chocolatey → Homebrew on 2026-10-18.
Anonymous GitHub API and downloads now confirm the repository is public.
All six v0.2.0 assets match the frozen CLI6 publication byte identities.
No crate, tag or Release asset is replaced by this work.

## WinGet

Candidate ID: `Lingose.Lingose`, Windows x64 portable ZIP. Three manifests are
under `packaging/winget/manifests/l/Lingose/Lingose/0.2.0/`. They specify the
actual nested executable, a user-scope command alias and the Microsoft VC++
runtime dependency. Official 1.12.0 schemas pass locally.

The ID directory currently returns 404 in `microsoft/winget-pkgs`; availability
is a point-in-time check, not an approval. After native acceptance, copy the
three-file directory into that repository and submit a new-version PR under
its [contribution rules](https://github.com/microsoft/winget-pkgs/blob/master/CONTRIBUTING.md).
Until that PR is accepted and indexed, `winget install --id Lingose.Lingose -e`
is not an available community installation instruction.

## Scoop

The root `bucket/lingose.json` makes this existing public repository a custom
bucket. It uses only the actual Windows x64 asset, its SHA256, the archive's
root directory, an executable shim, GitHub version detection and SHA256SUMS
updates. The VC++ runtime is suggested as `extras/vcredist2022`, rather than
silently invoking its administrative installer. The bundled notices remain.

Once the manifest is pushed to the public default branch:

```powershell
scoop bucket add lingose https://github.com/englishword/lingose-rust
scoop install lingose/lingose
```

The [Main criteria](https://github.com/ScoopInstaller/Scoop/wiki/Criteria-for-including-apps-in-the-main-bucket)
include established usage; this two-day-old repository is not a Main candidate
on current evidence. Main/Extras contain no `lingose.json` at this check.
Their [contribution process](https://github.com/ScoopInstaller/.github/blob/main/.github/CONTRIBUTING.md)
requires an issue and maintainer approval before a new-package PR.
This work does not submit that issue or claim Main/Extras distribution.

## Chocolatey

`packaging/chocolatey/` contains a download-type `lingose` 0.2.0 package.
It rejects 32-bit installation, requires `vcredist140`, verifies SHA256 and
downloads the complete official ZIP into the package's tools directory.
Chocolatey creates and removes the executable shim automatically.
No executable is embedded in the nupkg. Project/source/license links and
third-party/provenance limitations are included in its metadata.

```powershell
choco pack packaging/chocolatey/lingose.nuspec --output-directory .local/cli7
```

The current public OData query for `lingose` returned an empty feed. Upload
needs a Chocolatey community account/API key and is a separate action;
[validation, verification and moderation](https://docs.chocolatey.org/en-us/community-repository/moderation/)
must then pass. Local `pack` does not make `choco install lingose` publicly
available. Do not put an API key in scripts, command transcripts or this repo.

## Homebrew

`Formula/lingose.rb` is a custom-tap binary formula for macOS Intel and Apple
Silicon, with independent official archive URLs/SHA256. It preserves all
project, data and dependency notices in `share/lingose`; its tests compare
complete query JSON and stdin annotation. Linux Homebrew is not offered by
this initial formula; existing direct Linux Release archives remain available.

Once the formula is pushed to the public default branch:

```sh
brew tap englishword/lingose https://github.com/englishword/lingose-rust
# If your Homebrew requires explicit formula trust:
# brew trust --formula englishword/lingose/lingose
brew install englishword/lingose/lingose
brew test englishword/lingose/lingose
```

See the official [custom tap guide](https://docs.brew.sh/How-to-Create-and-Maintain-a-Tap).
This is not a homebrew/core submission. The repository's age and current zero
stars/forks do not meet its [new-package acceptance policy](https://docs.brew.sh/Package-Acceptance-Policy).
Core also requires its own source-build/license review. No popularity, license
approval, Developer ID signing, notarization or Gatekeeper acceptance is claimed.

## Verification and maintenance

`tools/check_package_channels.py preflight --output PATH` downloads all assets
without authentication, compares the fixed CLI6 identities, validates the
official schemas and checks current channel URL/hash wiring. PyYAML and
jsonschema are development-only requirements. `smoke --executable PATH
--output PATH` exercises an installed command/shim from an unrelated temporary
working directory, checking version, all query fields, Unicode/CRLF annotation,
stdin JSON, thresholds, empty input and error exit codes. It uses only stdlib;
it does not assert a network or filesystem sandbox.

The manual `Package channel acceptance` Actions workflow runs WinGet, then
Scoop, then Chocolatey on a disposable Windows runner, followed by Homebrew
on native Intel and Apple Silicon macOS runners. It checks install/uninstall,
preserved notices, and same-version reinstallation where applicable. Reinstall
is not evidence of a future-version upgrade. It publishes evidence artifacts,
never packages to a community registry. Actual results are recorded separately.

For each future release, review all URL/hash/version/directory fields; Scoop's
update metadata helps generate a change but does not approve it. WinGet needs
a new version directory/PR, Chocolatey a newly packed/uploaded version, and
Homebrew a formula update. Never change bytes behind an existing release URL.
Runtime requirements and the known Frequency List/category provenance gaps in
the bundled `SOURCES.md` continue to apply to every channel.
