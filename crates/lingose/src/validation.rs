use crate::{Error, Result};

pub(crate) fn word(word: &str) -> Result<()> {
    if word.is_empty()
        || word.contains('\0')
        || word.starts_with(python_whitespace)
        || word.ends_with(python_whitespace)
    {
        return Err(Error::InvalidArgument {
            parameter: "word",
            reason: "must be nonempty, without NUL or surrounding whitespace",
        });
    }
    Ok(())
}

// Python 3.12 / Unicode 15.0 str.isspace(), including U+001C..U+001F.
// Keep this explicit rather than relying on the compiler's Unicode version.
pub(crate) fn python_whitespace(character: char) -> bool {
    matches!(
        character,
        '\u{0009}'..='\u{000d}'
            | '\u{001c}'..='\u{0020}'
            | '\u{0085}'
            | '\u{00a0}'
            | '\u{1680}'
            | '\u{2000}'..='\u{200a}'
            | '\u{2028}'
            | '\u{2029}'
            | '\u{202f}'
            | '\u{205f}'
            | '\u{3000}'
    )
}

pub(crate) fn language(lang: &str) -> Result<()> {
    if !matches!(lang, "en" | "zh") {
        return Err(Error::InvalidArgument {
            parameter: "lang",
            reason: "must be exactly en or zh",
        });
    }
    Ok(())
}

pub(crate) fn annotation(text: &str, skip_top: i64) -> Result<()> {
    if skip_top < 0 {
        return Err(Error::InvalidArgument {
            parameter: "skip_top",
            reason: "must be nonnegative",
        });
    }
    if text.contains('\0') {
        return Err(Error::InvalidArgument {
            parameter: "text",
            reason: "must not contain NUL",
        });
    }
    Ok(())
}
