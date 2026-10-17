//! Pinned scanner properties and the restricted IPS normalization/casing domain.

#[path = "annotation_unicode_tables.rs"]
mod tables;

pub(crate) fn flags(character: char) -> u8 {
    let cp = u32::from(character);
    let past = tables::FLAGS.partition_point(|&(first, _, _)| first <= cp);
    if past != 0 && cp <= tables::FLAGS[past - 1].1 {
        tables::FLAGS[past - 1].2
    } else {
        0
    }
}

pub(crate) fn is_mark(character: char) -> bool {
    flags(character) & 4 != 0
}

fn row(character: char) -> Option<&'static (u32, u8, &'static str, &'static str)> {
    tables::BASES
        .binary_search_by_key(&u32::from(character), |row| row.0)
        .ok()
        .map(|index| &tables::BASES[index])
}

fn special(cluster: &str) -> Option<&'static (&'static str, u8, &'static str, &'static str)> {
    tables::SPECIAL
        .binary_search_by_key(&cluster, |row| row.0)
        .ok()
        .map(|index| &tables::SPECIAL[index])
}

/// Equivalent to the reference's NFD base predicate, not an NFD output API.
pub(crate) fn base(cluster: &str) -> Option<char> {
    if let Some(row) = special(cluster) {
        return Some(char::from(row.1));
    }
    if matches!(cluster, "-" | "'" | "’") {
        return Some(if cluster == "-" { '-' } else { '\'' });
    }
    let mut chars = cluster.chars();
    let first = row(chars.next()?)?;
    chars
        .all(|c| tables::MARKS.binary_search(&u32::from(c)).is_ok())
        .then_some(char::from(first.1))
}

// Only called after base() accepts the complete cluster. Accepted trailing
// marks have identity casing; full first-scalar mappings preserve original form.
pub(crate) fn push_case(output: &mut String, cluster: &str, uppercase: bool) {
    if let Some(row) = special(cluster) {
        output.push_str(if uppercase { row.3 } else { row.2 });
    } else {
        let first = cluster.chars().next().expect("accepted nonempty cluster");
        let row = row(first).expect("accepted NFD base");
        output.push_str(if uppercase { row.3 } else { row.2 });
        output.push_str(&cluster[first.len_utf8()..]);
    }
}

#[cfg(test)]
mod tests {
    use sha2::{Digest, Sha256};

    use super::*;

    #[test]
    fn every_scalar_matches_python_scanning_nfd_predicate_and_accepted_casing() {
        let mut digest = Sha256::new();
        for cp in 0..=0x10ffff_u32 {
            let Some(c) = char::from_u32(cp) else {
                continue;
            };
            let row = row(c);
            let cluster = c.to_string();
            // Double-struck forms are exact special overrides, outside the
            // NFD table digest; generated oracle vectors cover every override.
            let nfd_base = if special(&cluster).is_some() {
                0
            } else {
                base(&cluster).map_or(0, |base| u8::try_from(u32::from(base)).unwrap())
            };
            // Separators have a literal override too, outside the NFD domain.
            let nfd_base = if matches!(c, '-' | '\'' | '’') {
                0
            } else {
                nfd_base
            };
            let mark = tables::MARKS.binary_search(&cp).is_ok();
            digest.update(cp.to_le_bytes());
            digest.update([flags(c), nfd_base, u8::from(mark)]);
            if row.is_some() {
                for uppercase in [false, true] {
                    let mut value = String::new();
                    push_case(&mut value, &cluster, uppercase);
                    digest.update(u32::try_from(value.len()).unwrap().to_le_bytes());
                    digest.update(value.as_bytes());
                }
            }
        }
        assert_eq!(format!("{:x}", digest.finalize()), tables::SCALAR_SHA256);
    }
}
