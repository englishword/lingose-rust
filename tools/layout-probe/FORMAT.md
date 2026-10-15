# P1.2 layout probe interchange, version 1

Development-only experiment; not the production exporter or public Rust API.
Every candidate contains the same full projected record stream. A gzip stream
contains exactly one complete image; all integer fields are little-endian u32.
Missing string references use `0xffffffff`, distinct from an empty string.

Header (112 bytes): 8-byte magic `LNGIDX01`, then ten u32 fields:
`format_version=1`, `string_count`, `entry_count`, `label_count`, `member_count`,
`frequency_count`, `pool_bytes`, `lexicon_schema=2`, `frequency_schema=1`,
`ipsm_algorithm=1`; then 32 raw bytes of lexicon data_version and 32 raw bytes
of frequency data_version. SHA-256 of the complete image is provided in the
experiment manifest, not included in this image.

Sections, contiguous with no padding or trailing bytes:

1. `string_count + 1` pool offsets, beginning at zero and ending at pool_bytes.
   Distinct strings are sorted by their original UTF-8 bytes. No normalization.
2. entry_count records of ten u32 fields:
   `word, ipa, ips, ism, ipsm, root_lemma, meaning_en, meaning_zh, kind_bits,
   annotation_state`. The first eight values are string IDs; only word is
   non-nullable. Each pronunciation reference represents the selected zero/one
   result independently, matching the fixed Python baseline. annotation_state:
   0 blocked, 1 allows missing-source rule fallback, 2 has an available nonempty
   IPS. Actual entry existence is never discarded. Entries sorted by word UTF-8.
3. label_count records: `label_string_id, members_start, members_length`.
   Labels retain configuration order; label_count <= 32. Membership bitmap bit
   position is the label ordinal in this array, not the source field ordinal.
4. member_count entry indices, preserving the full Python category business
   ordering within each label; no rank field is needed at runtime.
5. frequency_count records: `word_string_id, original_number`, sorted by word
   UTF-8. Keys retain Python-lowercase spelling, phrases and punctuation. Numbers
   are minimum original NUMBER values, 1..5062, with original gaps preserved.
6. UTF-8 string pool, concatenating original text without separators.

Two independent resources use this format: `image.bin` contains the lexicon and
categories, with frequency_count=0; `frequency.bin` contains only frequency keys,
with entry_count=label_count=member_count=0 and its own string pool. This permits
production to initialize and validate frequency data only for skip_top > 0.
The preparation tool writes both raw resources, deterministic `.bin.gz` files,
and separate `.sha256` files under `.local/layout/`, plus manifest and complete
benchmark corpora. Each build embeds exactly one representation of each resource,
avoiding a raw+compressed combined binary comparison. The probe loads both to
measure all workloads, reporting their initialization times separately.

Candidate modes: `static` (raw image + sorted index), `static-hash` (raw image
+ runtime HashMap word indices), `gzip` (decompressed image + sorted index),
`hash` (decompressed image + runtime HashMap word indices).
All candidates validate the SHA-256, schema/version identifiers, section bounds,
UTF-8 and index invariants once before exposing borrowed internal views.
The benchmark copies outputs into the planned owned Rust result types.
All candidates use the same full category lists and frequency data.

P2.1 will implement the final guarded exporter, explicit metadata and provenance;
P2.2 will implement production validation/error paths and OnceLock reuse.
