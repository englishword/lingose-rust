# Independent development probe

This subtree is a separate, unpublished Cargo workspace, excluded from the
production crate. Prepare the guarded full-data inputs with
`python -I -B -X utf8 tools/prepare_layout_probe.py --write` from the project root
before compiling; its include_bytes inputs live under the ignored `.local/layout-020`.

Enable exactly one of `static`, `static-hash`, `gzip`, or `hash`. Do not run
`--all-features`: candidates are intentionally mutually exclusive. Use
`--manifest-path tools/layout-probe/Cargo.toml --no-default-features --features <candidate>`
for each check/build, and `--release` for measurements. Set CARGO_HOME and
CARGO_TARGET_DIR to this project's `.local/cargo-home` and `.local/layout-target`.

Preserve FORMAT.md and the Python encoder together when changing the protocol.
The measurements are exact-key owned projections and ASCII lookup workloads;
they do not implement or accept the public API or annotate_ips. Keep probe-only
dependencies and developer paths out of the production crate.
