//! Command-line entry point; business commands are not implemented yet.

use std::process::ExitCode;

fn main() -> ExitCode {
    eprintln!(
        "lingose-cli {}: command-line interface is not implemented yet.",
        env!("CARGO_PKG_VERSION")
    );
    ExitCode::FAILURE
}
