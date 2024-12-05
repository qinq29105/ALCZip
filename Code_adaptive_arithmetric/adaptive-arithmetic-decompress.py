# Usage: python adaptive-arithmetic-decompress.py compress_out decompress_out.txt

import sys
import time  
import arithmeticcoding


# Command line main application function.
def main(args):
    # Handle command line arguments
    if len(args) != 2:
        sys.exit("Usage: python adaptive-arithmetic-decompress.py InputFile OutputFile")
    inputfile, outputfile = args

    # Perform file decompression and time the process
    start_time = time.time()  # Record the start time
    with open(inputfile, "rb") as inp, open(outputfile, "wb") as out:
        bitin = arithmeticcoding.BitInputStream(inp)
        decompress(bitin, out)
    end_time = time.time()  # Record the end time

    # Output the elapsed time
    print(f"Decompression completed in {end_time - start_time:.6f} seconds.")


def decompress(bitin, out):
    initfreqs = arithmeticcoding.FlatFrequencyTable(257)
    freqs = arithmeticcoding.SimpleFrequencyTable(initfreqs)
    dec = arithmeticcoding.ArithmeticDecoder(32, bitin)
    while True:
        # Decode and write one byte
        symbol = dec.read(freqs)
        if symbol == 256:  # EOF symbol
            break
        out.write(bytes((symbol,)))
        freqs.increment(symbol)


# Main launcher
if __name__ == "__main__":
    main(sys.argv[1:])
