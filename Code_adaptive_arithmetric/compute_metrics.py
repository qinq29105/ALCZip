import arithmeticcoding
import os
import math


# Function to get symbol frequencies from the file
def get_frequencies(filepath):
    """
    Retrieve the frequency table of symbols from the file, used for subsequent entropy and encoding analysis.
    """
    # Initialize a frequency table, assuming symbol space is 0-255 (byte values)
    freqs = arithmeticcoding.SimpleFrequencyTable([0] * 256)
    
    with open(filepath, "rb") as input_file:
        while True:
            b = input_file.read(1)  # Read one byte at a time
            if not b:
                break  # End of file
            symbol = b[0]  # Convert byte to symbol (0-255)
            freqs.increment(symbol)  # Update the frequency of this symbol

    return freqs


# Calculate source entropy directly from the file
def calculate_entropy_from_file(filepath):
    """
    Read the file and calculate source entropy: H(X) = - ∑ p(x_i) * log2(p(x_i))
    """
    # Count symbol frequencies in the file
    frequencies = [0] * 256
    total_symbols = 0

    with open(filepath, "rb") as input_file:
        while True:
            b = input_file.read(1)
            if not b:
                break
            symbol = b[0]
            frequencies[symbol] += 1
            total_symbols += 1

    # Calculate source entropy
    entropy = 0.0
    for freq in frequencies:
        if freq > 0:  # Exclude symbols with zero frequency
            prob = freq / total_symbols  # Probability of the symbol
            entropy -= prob * math.log2(prob)  # Calculate entropy

    return entropy


# Calculate average code length (based on the actual size of the compressed file)
def calculate_average_code_length_from_encoded_file(encoded_file, total_symbols):
    """
    Calculate the actual average code length based on the compressed bitstream.
    """
    compressed_file_size = os.path.getsize(encoded_file) * 8  # File size in bits (bytes to bits)
    return compressed_file_size / total_symbols


# Compute encoding efficiency, redundancy, and compression ratio
def compute_metrics(input_file, encoded_file, frequencies):
    """
    Calculate source entropy, average code length, encoding efficiency, redundancy, compression ratio, and other metrics.

    Parameters:
        input_file (str): Path to the original input file.
        encoded_file (str): Path to the compressed file.
        frequencies (list): Symbol frequency list (used for entropy and average code length calculations).

    Returns:
        dict: A dictionary containing the calculated metrics.
    """
    # Calculate source entropy (directly from the file)
    entropy = calculate_entropy_from_file(input_file)

    # Get the total number of symbols in the file
    total_symbols = sum(frequencies)

    # Calculate the actual average code length
    average_codeword_length = calculate_average_code_length_from_encoded_file(encoded_file, total_symbols)

    # Calculate encoding efficiency and redundancy
    efficiency = entropy / average_codeword_length
    redundancy = 1 - efficiency

    # Calculate compression ratio
    original_file_size = os.path.getsize(input_file)  # Original file size (in bytes)
    compressed_file_size = os.path.getsize(encoded_file)  # Compressed file size (in bytes)
    compression_ratio = compressed_file_size / original_file_size 

    # Return the calculated metrics
    return {
        "Average Codeword Length": average_codeword_length,
        "Source Entropy": entropy,
        "Encoding Efficiency": efficiency,
        "Redundancy": redundancy,
        "original file size": original_file_size,
        "compressed file size": compressed_file_size,
        "Compression Ratio": compression_ratio,
    }


# Main code to execute the analysis
def main(input_file, encoded_file):
    # Get symbol frequencies from the input file
    freqs = get_frequencies(input_file)

    # Compute and print the various metrics
    metrics = compute_metrics(input_file, encoded_file, freqs.frequencies)

    print("Source Entropy: ", metrics["Source Entropy"])
    print("Average Codeword Length: ", metrics["Average Codeword Length"])
    print("Encoding Efficiency: ", metrics["Encoding Efficiency"])
    print("Redundancy: ", metrics["Redundancy"])
    print("original file size: ", metrics["original file size"])
    print("compressed file size: ", metrics["compressed file size"])
    print("Compression Ratio: ", metrics["Compression Ratio"])


if __name__ == "__main__":
    input_file = "GameofThrones.txt"  # Replace with the actual input file path
    encoded_file = "compress_out"  # Replace with the actual compressed file path
    
    main(input_file, encoded_file)
