# CLI7 package channels

The user requested WinGet → Scoop → Chocolatey → Homebrew on 2026-10-18.
Anonymous GitHub API and downloads now confirm the repository is public.
All six v0.2.0 assets match the frozen CLI6 publication byte identities.
No crate, tag or Release asset is replaced by this work.

## Verified result

[Native acceptance run 39126125352](https://github.com/englishword/lingose-rust/actions/runs/39126125352)
passed all three jobs on commit `d237147e5e0bf5b0042e1d11a714bde712d06dc6`.
The [receipt](cli-package-channels-verification.json) records the exact inputs,
job steps, downloaded service artifact digests, reports and earlier attempts.

| Channel | Accepted locally/on native runners | Public distribution status |
| --- | --- | --- |
| WinGet | Client validation, install, 8 command checks, notices, uninstall | Community PR/index pending |
| Scoop | Public bucket revision, install/shim, 8 checks, notices, checkver/autoupdate, uninstall/reinstall | This repository's custom bucket is available; Main/Extras not submitted |
| Chocolatey | Real pack, local-feed install with runtime dependency, 8 shim checks, notices, same-version reinstall, uninstall | Community upload/moderation pending |
| Homebrew | Public tap revision, install, formula tests, 8 checks per architecture, notices, reinstall/uninstall | This repository's custom macOS tap is available; core not submitted |

Windows Server 2022 x64 and macOS 15.7.9 Intel/Apple Silicon supplied five
installed instances and 40 command checks. The three downloaded evidence ZIPs
match the service SHA256 and byte sizes. Raw logs and reports are retained in
`.local/cli7-final-39126125352/`; service artifacts have 14-day retention.
Scoop's generated current-version URL/hash/extract directory match the source.

Six earlier runs are retained separately. Failures exposed an unsupported
portable Scope field, local WinGet registration matching, a shared-runner API
limit and incomplete/manual Scoop bootstrap assumptions. The final run uses
the official Scoop installer, public channel URLs and only an ephemeral
read-only token for WinGet bootstrap; the asset preflight remains anonymous.
No failed attempt is relabelled as successful.

Local checks also passed: official schemas, eight direct Release executable
checks, real Chocolatey pack/download-only payload inspection, present/missing
runtime guard checks (the missing case mocks the filesystem result), 15 existing
archive/publication guard tests, syntax/actionlint and whitespace checks.
All 247 existing files outside the four current workflow/doc-state exceptions
retain their CLI6 identity. Rust code, packaged data, Cargo.lock, Release
materials and historical receipts were not changed, so the full Rust,
differential, performance and MSRV suites were not repeated for CLI7.

## WinGet

Candidate ID: `Lingose.Lingose`, Windows x64 portable ZIP. Three manifests are
under `packaging/winget/manifests/l/Lingose/Lingose/0.2.0/`. They specify the
actual nested executable, a command alias and the Microsoft VC++
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
silently invoking its administrative installer. A pre-install guard fails with
an actionable message if the x64 runtime DLL is absent. The bundled notices remain.

Install [Microsoft's Visual C++ v14 x64 Runtime](https://aka.ms/vc14/vc_redist.x64.exe) first if it is absent (the
`extras/vcredist2022` installer may require administrator rights). Then use
this public bucket:

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

The formula is now on the public default branch:

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
never packages to a community registry. Scoop's checkver/autoupdate are exercised
on a temporary manifest copy at the current version, including checksum extraction.
Actual results are recorded separately. The Windows runner already provides
system runtimes; this does not prove installation on a runtime-free machine.

For each future release, review all URL/hash/version/directory fields; Scoop's
update metadata helps generate a change but does not approve it. WinGet needs
a new version directory/PR, Chocolatey a newly packed/uploaded version, and
Homebrew a formula update. Never change bytes behind an existing release URL.
Runtime requirements and the known Frequency List/category provenance gaps in
the bundled `SOURCES.md` continue to apply to every channel.

The final Windows Release executable reports `NotSigned` under
`Get-AuthenticodeSignature`. Fixed SHA256 verifies the chosen archive bytes;
it is not a publisher signature. No channel packaging adds Authenticode,
Developer ID signing or notarization. Community security scanning and OS
download/launch warnings remain separate from these command-line tests.
