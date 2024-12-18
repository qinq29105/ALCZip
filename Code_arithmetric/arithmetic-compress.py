# Usage: python arithmetic-compress.py GameofThrones.txt compress_out

import contextlib, sys
import arithmeticcoding
import time  # Import time module to measure execution time

# Command line main application function.
def main(args):
    # Handle command line arguments
    if len(args) != 2:
        sys.exit("Usage: python arithmetic-compress.py InputFile OutputFile")
    inputfile, outputfile = args
    
    # Start the timer for compression
    start_time = time.perf_counter()
    
    # Read input file once to compute symbol frequencies
    freqs = get_frequencies(inputfile)
    freqs.increment(256)  # EOF symbol gets a frequency of 1
    
    # Read input file again, compress with arithmetic coding, and write output file
    with open(inputfile, "rb") as inp, \
            contextlib.closing(arithmeticcoding.BitOutputStream(open(outputfile, "wb"))) as bitout:
        write_frequencies(bitout, freqs)
        compress(freqs, inp, bitout)
    
    # End the timer for compression and calculate the elapsed time
    end_time = time.perf_counter()
    compression_time = end_time - start_time
    print(f"Compression Time: {compression_time:.4f} seconds")  # Print the compression time

# Returns a frequency table based on the bytes in the given file.
# Also contains an extra entry for symbol 256, whose frequency is set to 0.
def get_frequencies(filepath):
    freqs = arithmeticcoding.SimpleFrequencyTable([0] * 257)
    with open(filepath, "rb") as input:
        while True:
            b = input.read(1)
            if len(b) == 0:
                break
            freqs.increment(b[0])
    return freqs


def write_frequencies(bitout, freqs):
    with open("frequencies.freq", "w") as freq_file:
        for i in range(256):
            freq = freqs.get(i)
            freq_file.write(f"{freq}\n")  # Save each frequency
            write_int(bitout, 32, freq)


def compress(freqs, inp, bitout):
    enc = arithmeticcoding.ArithmeticEncoder(32, bitout)
    while True:
        symbol = inp.read(1)
        if len(symbol) == 0:
            break
        enc.write(freqs, symbol[0])
    enc.write(freqs, 256)  # EOF
    enc.finish()  # Flush remaining code bits


# Writes an unsigned integer of the given bit width to the given stream.
def write_int(bitout, numbits, value):
    for i in reversed(range(numbits)):
        bitout.write((value >> i) & 1)  # Big endian


# Main launcher
if __name__ == "__main__":
    main(sys.argv[1:])

