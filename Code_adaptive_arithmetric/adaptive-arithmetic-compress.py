# Usage: python adaptive-arithmetic-compress.py GameofThrones.txt compress_out

import contextlib
import sys
import time  
import arithmeticcoding


# Command line main application function.
def main(args):
    # Handle command line arguments
    if len(args) != 2:
        sys.exit("Usage: python adaptive-arithmetic-compress.py InputFile OutputFile")
    inputfile, outputfile = args

    # Perform file compression and time the process
    start_time = time.time()  # Record the start time
    with open(inputfile, "rb") as inp, \
            contextlib.closing(arithmeticcoding.BitOutputStream(open(outputfile, "wb"))) as bitout:
        compress(inp, bitout)
    end_time = time.time()  # Record the end time

    # Output the elapsed time
    print(f"Compression completed in {end_time - start_time:.6f} seconds.")


def compress(inp, bitout):
    initfreqs = arithmeticcoding.FlatFrequencyTable(257)
    freqs = arithmeticcoding.SimpleFrequencyTable(initfreqs)
    enc = arithmeticcoding.ArithmeticEncoder(32, bitout)
    while True:
        # Read and encode one byte
        symbol = inp.read(1)
        if len(symbol) == 0:
            break
        enc.write(freqs, symbol[0])
        freqs.increment(symbol[0])
    enc.write(freqs, 256)  # EOF
    enc.finish()  # Flush remaining code bits


# Main launcher
if __name__ == "__main__":
    main(sys.argv[1:])
