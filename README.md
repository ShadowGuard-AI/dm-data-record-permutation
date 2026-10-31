![Banner](banner.png)

# dm-data-record-permutation
Randomly reorders the rows (records) in a data file. This disrupts the original order, which may unintentionally reveal information or patterns, particularly when combined with other masking techniques. - Focused on Tools designed to generate or mask sensitive data with realistic-looking but meaningless values

## Install
`git clone https://github.com/ShadowGuardAI/dm-data-record-permutation`

## Usage
`./dm-data-record-permutation [params]`

## Parameters
- `--file_type`: No description provided
- `--header`: Specify if the input file has a header row. If not specified, assume header exists.
- `--delimiter`: Delimiter for CSV files. Default is
- `--seed`: Seed for a reproducible shuffle. If not specified, each run shuffles from fresh system randomness and produces a different order.

## Shuffle and output path

By default each run is a fresh random shuffle, so the permutation is not fixed and cannot be inverted from the row count alone. Pass --seed with an integer to make a run reproducible: two runs with the same seed and the same input produce identical output.

The output file must not be the input file. If the resolved output path equals the resolved input path, the run refuses at exit 1 before any write, including when the same file is named through a ./ alias or a symlink.

## License
Copyright (c) ShadowGuardAI
