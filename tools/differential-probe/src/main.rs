//! Development-only bridge: invoke public APIs and preserve complete results.

use std::fs::File;
use std::io::{self, BufReader, BufWriter, Read, Write};

const MAGIC: &[u8; 8] = b"LNGDIFF1";

fn number(input: &mut impl Read) -> io::Result<u32> {
    let mut bytes = [0; 4];
    input.read_exact(&mut bytes)?;
    Ok(u32::from_le_bytes(bytes))
}

fn string(input: &mut impl Read) -> io::Result<String> {
    let mut bytes = vec![0; number(input)? as usize];
    input.read_exact(&mut bytes)?;
    String::from_utf8(bytes).map_err(io::Error::other)
}

fn write_number(output: &mut impl Write, value: usize) -> io::Result<()> {
    output.write_all(
        &u32::try_from(value)
            .map_err(io::Error::other)?
            .to_le_bytes(),
    )
}

fn write_string(output: &mut impl Write, value: &str) -> io::Result<()> {
    write_number(output, value.len())?;
    output.write_all(value.as_bytes())
}

enum Value {
    Optional(Option<String>),
    Text(String),
    Strings(Vec<String>),
    Bool(bool),
}

fn write_value(output: &mut impl Write, result: lingose::Result<Value>) -> io::Result<()> {
    match result {
        Ok(Value::Optional(None)) => output.write_all(&[0]),
        Ok(Value::Text(value) | Value::Optional(Some(value))) => {
            output.write_all(&[1])?;
            write_string(output, &value)
        }
        Ok(Value::Strings(values)) => {
            output.write_all(&[2])?;
            write_number(output, values.len())?;
            for value in values {
                write_string(output, &value)?;
            }
            Ok(())
        }
        Ok(Value::Bool(value)) => output.write_all(&[3, u8::from(value)]),
        Err(error) => {
            let class = match error {
                lingose::Error::InvalidArgument { .. } => "InvalidArgument",
                lingose::Error::Data { .. } => "Data",
                lingose::Error::IncompatibleDataVersion { .. } => "IncompatibleDataVersion",
                _ => return Err(io::Error::other("unmapped public error")),
            };
            output.write_all(&[4])?;
            write_string(output, class)
        }
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let arguments: Vec<_> = std::env::args_os().collect();
    if arguments.len() != 3 {
        return Err("expected request and output paths".into());
    }
    let mut input = BufReader::new(File::open(&arguments[1])?);
    let mut output = BufWriter::new(File::create_new(&arguments[2])?);
    let mut magic = [0; 8];
    input.read_exact(&mut magic)?;
    if &magic != MAGIC {
        return Err("unsupported differential protocol".into());
    }
    let count = number(&mut input)?;
    output.write_all(MAGIC)?;
    write_number(&mut output, count as usize)?;
    for _ in 0..count {
        let mut opcode = [0];
        input.read_exact(&mut opcode)?;
        let word = string(&mut input)?;
        let option = string(&mut input)?;
        let mut threshold = [0; 8];
        input.read_exact(&mut threshold)?;
        let result = match opcode[0] {
            0 => lingose::ipa(&word).map(Value::Strings),
            1 => lingose::IPA(&word).map(Value::Strings),
            2 => lingose::ips(&word).map(Value::Strings),
            3 => lingose::IPS(&word).map(Value::Strings),
            4 => lingose::ism(&word).map(Value::Optional),
            5 => lingose::ISM(&word).map(Value::Optional),
            6 => lingose::ipsm(&word).map(Value::Strings),
            7 => lingose::IPSM(&word).map(Value::Strings),
            8 => lingose::root_lemma(&word).map(Value::Optional),
            9 => lingose::meaning(&word).map(Value::Optional),
            10 => lingose::meaning_with_lang(&word, &option).map(Value::Optional),
            11 => lingose::kind(&word).map(Value::Bool),
            12 => lingose::kind_with_label(&word, &option).map(Value::Bool),
            13 => lingose::kind_list().map(Value::Strings),
            14 => lingose::kind_list_with_label(&option).map(Value::Strings),
            15 => lingose::labels().map(Value::Strings),
            16 => lingose::annotate_ips(&word).map(Value::Text),
            17 => lingose::annotate_ips_with_skip_top(&word, i64::from_le_bytes(threshold))
                .map(Value::Text),
            _ => return Err("unknown differential opcode".into()),
        };
        write_value(&mut output, result)?;
    }
    if input.read(&mut [0])? != 0 {
        return Err("trailing request bytes".into());
    }
    output.flush()?;
    Ok(())
}
