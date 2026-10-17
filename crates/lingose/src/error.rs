use std::fmt;

/// The result of a Lingose query or annotation operation.
pub type Result<T> = std::result::Result<T, Error>;

/// A failure distinct from a valid unknown word or unavailable field.
///
/// Both [`Error::Data`] and [`Error::IncompatibleDataVersion`] correspond to
/// Python's `LexiconDataError`; the latter corresponds to its
/// `SchemaVersionError` subclass. Error messages are diagnostic text, not a
/// stable part of the API.
#[derive(Clone, Debug, Eq, PartialEq)]
#[non_exhaustive]
pub enum Error {
    /// An argument has the correct Rust type but invalid contents.
    InvalidArgument {
        /// The argument name, such as `word`, `lang`, `label`, or `skip_top`.
        parameter: &'static str,
        /// Why the value is invalid.
        reason: &'static str,
    },
    /// A required bundled resource is missing, unreadable, or corrupt.
    Data {
        /// The logical resource name, never a required development path.
        resource: &'static str,
        /// Details of the resource failure.
        message: String,
    },
    /// A resource uses an unsupported or inconsistent data format version.
    IncompatibleDataVersion {
        /// The logical resource name.
        resource: &'static str,
        /// The version required by this crate.
        expected: String,
        /// The version found in the resource.
        found: String,
    },
}

impl fmt::Display for Error {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidArgument { parameter, reason } => {
                write!(formatter, "invalid {parameter}: {reason}")
            }
            Self::Data { resource, message } => {
                write!(formatter, "cannot read {resource}: {message}")
            }
            Self::IncompatibleDataVersion {
                resource,
                expected,
                found,
            } => write!(
                formatter,
                "incompatible {resource} data version: expected {expected}, found {found}"
            ),
        }
    }
}

impl std::error::Error for Error {}
