import heapq
import time
import os
import struct
from collections import defaultdict
from compute import average_codeword_length, source_entropy, encoding_efficiency, compression_ratio


# Node in the Huffman tree, containing the frequency of a character, the character itself, and pointers to left and right children.
class TreeNode:
    def __init__(self, character=None, frequency=0):
        self.character = character
        self.frequency = frequency
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.frequency < other.frequency


# Build the Huffman tree from a frequency table.
def build_huffman_tree(freq_table):
    priority_queue = [TreeNode(char, freq) for char, freq in freq_table.items()]
    heapq.heapify(priority_queue)

    while len(priority_queue) > 1:
        left = heapq.heappop(priority_queue)
        right = heapq.heappop(priority_queue)

        internal_node = TreeNode(frequency=left.frequency + right.frequency)
        internal_node.left = left
        internal_node.right = right

        heapq.heappush(priority_queue, internal_node)

    return priority_queue[0]  # root of the Huffman tree


# Convert a character to its binary representation
def to_binary(byte):
    return format(byte, '08b')


# Traverse the Huffman tree and create the codebook (map) for each character.
def traverse_huffman_tree(root, current_code, codebook):
    if root is not None:
        if root.character is not None:  # Leaf node
            codebook[root.character] = current_code
        traverse_huffman_tree(root.left, current_code + '0', codebook)
        traverse_huffman_tree(root.right, current_code + '1', codebook)


# Read a file and return its contents as a byte array.
def read_file_into_buffer(path):
    with open(path, 'rb') as file:
        return file.read()


# Write data from a buffer to a file.
def write_file_from_buffer(path, buffer, mode='wb'):
    with open(path, mode) as file:
        file.write(buffer)


# Get the Huffman bitstring for the file content based on the character codebook.
def get_huffman_bitstring(buffer, codebook):
    bitstring = ''.join([codebook[byte] for byte in buffer])
    return bitstring


# Convert a bitstring to bytes (grouping every 8 bits).
def get_buffer_from_bitstring(bitstring):
    byte_array = bytearray()
    for i in range(0, len(bitstring), 8):
        byte_array.append(int(bitstring[i:i+8], 2))
    return bytes(byte_array)


# Read the header (metadata) from the compressed file and return the extracted information.
def read_header(buffer):
    padded_bits = struct.unpack('I', buffer[:4])[0]
    size = struct.unpack('I', buffer[4:8])[0]

    codebook = {}
    offset = 8
    for _ in range(size):
        char = buffer[offset]
        offset += 1
        code_len = struct.unpack('I', buffer[offset:offset+4])[0]
        offset += 4
        code = buffer[offset:offset+code_len].decode('utf-8')
        offset += code_len
        codebook[char] = code

    return padded_bits, codebook, buffer[offset:]


# Decompress the file by decoding the Huffman bitstring using the codebook.
def decompress_file(input_path, output_path):
    start_time = time.time()  # Start timing the decompression process
    buffer = read_file_into_buffer(input_path)
    padded_bits, codebook, file_data = read_header(buffer)

    reverse_codebook = {code: char for char, code in codebook.items()}
    bitstring = ''.join([to_binary(byte) for byte in file_data])
    bitstring = bitstring[:-padded_bits]  # Remove padding

    decoded_buffer = []
    current_code = ''
    for bit in bitstring:
        current_code += bit
        if current_code in reverse_codebook:
            decoded_buffer.append(reverse_codebook[current_code])
            current_code = ''

    write_file_from_buffer(output_path, bytes(decoded_buffer))

    end_time = time.time()  # End timing the decompression process
    print(f"Decompression time: {end_time - start_time:.4f} seconds")


# Compress the file using Huffman coding and write to the output file.
def compress_file(input_path, output_path):
    start_time = time.time()  # Start timing the compression process
    buffer = read_file_into_buffer(input_path)
    freq_table = defaultdict(int)
    for byte in buffer:
        freq_table[byte] += 1

    # Build Huffman tree
    root = build_huffman_tree(freq_table)
    
    # Create the Huffman codebook
    codebook = {}
    traverse_huffman_tree(root, '', codebook)

    # Get the Huffman bitstring
    bitstring = get_huffman_bitstring(buffer, codebook)

    # Calculate padding bits
    padded_bits = (8 - len(bitstring) % 8) % 8
    bitstring = bitstring + '0' * padded_bits  # Add padding

    # Convert bitstring to bytes
    compressed_data = get_buffer_from_bitstring(bitstring)

    # Write the header and the compressed data to the output file
    write_file_from_buffer(output_path, struct.pack('I', padded_bits), mode='wb')  # Write padded bits
    write_file_from_buffer(output_path, struct.pack('I', len(codebook)), mode='ab')  # Write codebook size
    for char, code in codebook.items():
        write_file_from_buffer(output_path, bytes([char]), mode='ab')  # Write character
        write_file_from_buffer(output_path, struct.pack('I', len(code)), mode='ab')  # Write code length
        write_file_from_buffer(output_path, code.encode('utf-8'), mode='ab')  # Write code

    write_file_from_buffer(output_path, compressed_data, mode='ab')  # Write compressed data

    end_time = time.time()  # End timing the compression process
    print(f"Compression time: {end_time - start_time:.4f} seconds")

    # Compute compression metrics
    original_size = os.path.getsize(input_file)
    encoded_size = os.path.getsize(compressed_file)
    
    avg_codeword_len = average_codeword_length(codebook, freq_table)
    entropy = source_entropy(freq_table)
    encoding_eff = encoding_efficiency(codebook, freq_table, entropy)
    redun = 1 - encoding_eff
    comp_ratio = compression_ratio(encoded_size, original_size)
    
    print(f"Average codeword length: {avg_codeword_len:.4f} ")
    print(f"Source entropy: {entropy:.4f} ")
    print(f"Encoding efficiency: {encoding_eff:.4f}")
    print(f"Redundancy: {redun:.4f} ")
    print(f"original file size: {original_size:.4f}")
    print(f"compressed file size: {encoded_size:.4f}")
    print(f"Compression ratio: {comp_ratio:.4f}")


if __name__ == "__main__":
    input_file = 'GameofThrones.txt'
    compressed_file = 'compressed.huff'
    decompressed_file = 'decoded.txt'

    # Perform compression
    compress_file(input_file, compressed_file)

    # Perform decompression
    decompress_file(compressed_file, decompressed_file)

    print("Compression and decompression completed successfully!")
