# Usage: python arithmetic-decompress.py compress_out decompress_out.txt

import sys
import arithmeticcoding
import time  # Import time module to measure execution time

# Command line main application function.
def main(args):
    # Handle command line arguments
    if len(args) != 2:
        sys.exit("Usage: python arithmetic-decompress.py InputFile OutputFile")
    inputfile, outputfile = args
    
    # Start the timer for decompression
    start_time = time.perf_counter()
    
    # Perform file decompression
    with open(outputfile, "wb") as out, open(inputfile, "rb") as inp:
        bitin = arithmeticcoding.BitInputStream(inp)
        freqs = read_frequencies(bitin)
        decompress(freqs, bitin, out)
    
    # End the timer for decompression and calculate the elapsed time
    end_time = time.perf_counter()
    decompression_time = end_time - start_time
    print(f"Decompression Time: {decompression_time:.4f} seconds")  # Print the decompression time

def read_frequencies(bitin):
    def read_int(n):
        result = 0
        for _ in range(n):
            result = (result << 1) | bitin.read_no_eof()  # Big endian
        return result
    
    freqs = [read_int(32) for _ in range(256)]
    freqs.append(1)  # EOF symbol
    return arithmeticcoding.SimpleFrequencyTable(freqs)


def decompress(freqs, bitin, out):
    dec = arithmeticcoding.ArithmeticDecoder(32, bitin)
    while True:
        symbol = dec.read(freqs)
        if symbol == 256:  # EOF symbol
            break
        out.write(bytes((symbol,)))


# Main launcher
if __name__ == "__main__":
    main(sys.argv[1:])

