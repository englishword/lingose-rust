# Lingose 0.2.0

Offline English word queries and IPS text annotation by ZHAN Xianjue.
Learn the IPSM Approach at https://lingose.com/.
Source: https://github.com/englishword/lingose-rust.

## Install and run

Choose the archive for your operating system and CPU. Check its SHA-256 against
the accompanying SHA256SUMS, then extract the entire archive. All files are
inside a single folder named after the archive. Keep the notices with copies
you distribute. The executable contains the dictionary; no Python, Node, Cargo,
configuration or extra dictionary download is needed to use it.

On Windows PowerShell, inside the extracted folder:

```powershell
.\lingose.exe --version
.\lingose.exe word apple --json
.\lingose.exe annotate --text "Abandon the book."
.\lingose.exe annotate --input article.txt -o annotated.txt
```

On Linux/macOS, inside the extracted folder:

```sh
./lingose --version
./lingose word apple --json
./lingose annotate --text "Abandon the book."
printf 'the\napple' | ./lingose annotate --json
./lingose annotate --input article.txt -o annotated.txt
```

You can put the executable in a directory on your PATH. Use `lingose --help`,
`lingose word --help` or `lingose annotate --help` for all options. Input files
and stdin must be UTF-8. Plain annotation preserves input bytes outside the
annotations and adds no newline. JSON annotation has only `text` and `annotate`.
`--skip-top N` defaults to 0; 5062 is the effective upper limit.

Results go to stdout, diagnostics to stderr. `-o PATH` writes the selected format
to a file without repeating it on stdout. Exit codes: 0 success (including an
unknown word), 2 invalid arguments/text parameters, 1 I/O/resource/runtime error.

## Platform requirements and validation scope

- Windows x86_64: validated on Windows Server 2022. This MSVC binary imports
  VCRUNTIME140.dll and requires a compatible Microsoft Visual C++ v14 x64 Runtime
  in addition to Windows/UCRT system components. If that runtime is absent, use
  Microsoft's official installer: https://aka.ms/vc14/vc_redist.x64.exe.
  Runtime guidance: https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist.
- Linux x86_64/aarch64 GNU: validated on Ubuntu 24.04 (glibc 2.39), with the normal
  system dynamic loader, glibc and libgcc_s. ELF symbol requirements and loader
  paths are recorded in manifest.json; metadata is not older-distro execution
  acceptance. System libraries are not bundled.
- macOS Intel/Apple Silicon: validated on macOS 15.7.9. No Developer ID signing or
  notarization is provided. CI download/extraction tests do not establish browser
  quarantine/Gatekeeper acceptance on a user's Mac.

Test results apply to the recorded native runner environments. Archive creation,
CI artifact downloads and an eventual public GitHub Release are separate steps.
These 0.2.0 candidates are not evidence of crates.io publication.

## Attribution and licenses

Project license: LICENSE (CC BY 4.0). Read SOURCES.md and the included source,
Unicode, Rust standard-library and per-crate notices. Third-party works retain
their own licenses. The preserved Frequency List/category provenance gaps are
listed in SOURCES.md; inclusion of notices is not a new permission grant.
