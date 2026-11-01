import argparse
import logging
import random
import pandas as pd
import os
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    """
    parser = argparse.ArgumentParser(description="Randomly reorders the rows in a data file.")
    parser.add_argument("input_file", help="Path to the input data file (e.g., CSV, Excel).")
    parser.add_argument("output_file", help="Path to the output data file with permuted rows.")
    parser.add_argument("--file_type", choices=['csv', 'excel'], default='csv',
                        help="Type of the input file (csv or excel). Default is csv.")
    # BooleanOptionalAction keeps the documented default honest: the file is
    # assumed to have a header unless --no-header is passed. The old store_true
    # flag defaulted to False, so a plain run read the header as a data row,
    # shuffled it into the output, and wrote integer column names instead.
    parser.add_argument("--header", action=argparse.BooleanOptionalAction, default=True, help="Specify if the input file has a header row. If not specified, assume header exists (use --no-header for headerless files).")
    parser.add_argument("--delimiter", type=str, default=",", help="Delimiter for CSV files. Default is ','.") # Added delimiter option
    parser.add_argument("--seed", type=int, default=None, help="Seed for a reproducible shuffle. If not specified, each run shuffles from fresh system randomness and produces a different order.")

    return parser.parse_args()


def permute_data(input_file, output_file, file_type, header=True, delimiter=",", seed=None):
    """
    Randomly reorders the rows of the input data file and saves the result to the output file.

    Args:
        input_file (str): Path to the input data file.
        output_file (str): Path to the output data file.
        file_type (str): Type of the input file (csv or excel).
        header (bool): Indicates whether the input file has a header row.  Defaults to True.
        delimiter (str): Delimiter used in CSV files. Defaults to ","
        seed (int, optional): Seed for a reproducible shuffle. Defaults to None, which shuffles from fresh system randomness.
    """
    try:
        # I run the same path refusal before the existence check, so a call
        # that names one file twice hears about that first, even when the
        # file does not exist at all. The order of the errors is deliberate.
        if Path(input_file).resolve() == Path(output_file).resolve():
            raise ValueError("Output file is the same file as the input file. Refusing to overwrite the input in place.")

        # Input validation: Check if the input file exists
        if not os.path.isfile(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

        # Load the data based on the file type
        if file_type == 'csv':
            try:
                #Detect if there is a header row
                if header:
                    df = pd.read_csv(input_file, delimiter=delimiter)
                else:
                    df = pd.read_csv(input_file, header=None, delimiter=delimiter)
            except Exception as e:
                raise ValueError(f"Error reading CSV file: {e}")

        elif file_type == 'excel':
            try:
                # The excel branch takes neither the delimiter nor the
                # header flag. With an excel input, --no-header is silently
                # ignored and the first row is treated as the header anyway.
                df = pd.read_excel(input_file)
            except Exception as e:
                 raise ValueError(f"Error reading Excel file: {e}")
        else:
            raise ValueError("Invalid file type. Choose 'csv' or 'excel'.")


        # Permute the rows using pandas sample() with frac=1. With no seed,
        # random_state is None and each run shuffles from system randomness;
        # a seed passed with --seed makes the run reproducible.
        # Sampling without replacement at frac=1 is the invariant I want:
        # every row comes out exactly once, nothing dropped and nothing
        # duplicated, and each record stays whole while it moves. Dropping
        # the old index is part of the point: the output carries no trace
        # of where a row started, so the order cannot be undone from the
        # output alone. Without the seed, it cannot be undone at all.
        df_shuffled = df.sample(frac=1, random_state=seed).reset_index(drop=True)

        # Save the permuted data to the output file
        if file_type == 'csv':
            try:
                df_shuffled.to_csv(output_file, index=False, sep=delimiter)
            except Exception as e:
                raise ValueError(f"Error writing CSV file: {e}")
        elif file_type == 'excel':
            try:
                df_shuffled.to_excel(output_file, index=False)
            except Exception as e:
                raise ValueError(f"Error writing Excel file: {e}")


        logging.info(f"Successfully permuted data from {input_file} to {output_file}")

    except FileNotFoundError as e:
        logging.error(str(e))
        raise
    except ValueError as e:
        logging.error(str(e))
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise

def main():
    """
    Main function to execute the data permutation process.
    """
    try:
        args = setup_argparse()
        permute_data(args.input_file, args.output_file, args.file_type, args.header, args.delimiter, args.seed)

        # Example usage upon successful execution:
        print(f"Successfully permuted data from {args.input_file} to {args.output_file}")
        print("Example Usage:")
        print(f"To permute the data in {args.input_file} using the same settings, run:")
        print(f"python main.py {args.input_file} {args.output_file} --file_type {args.file_type} {'--header' if args.header else ''} --delimiter '{args.delimiter}'")

    except Exception as e:
        logging.error(f"Data permutation failed: {e}")
        print(f"Data permutation failed. See logs for details.") # Inform user that an error occurred.
        sys.exit(1)


if __name__ == "__main__":
    main()