import math

# calculate the average codeword length
def average_codeword_length(codes, freq_table):
    total_length = 0
    total_freq = sum(freq_table.values())
    
    for char, code in codes.items():
        total_length += len(code) * freq_table[char]
    
    return total_length / total_freq

# calculate the source_entropy
def source_entropy(freq_table):
    total_freq = sum(freq_table.values())
    entropy = 0
    for freq in freq_table.values():
        probability = freq / total_freq
        entropy -= probability * math.log2(probability)  
    return entropy

# calculate the encoding efficiency
def encoding_efficiency(codes, freq_table, entropy):
    avg_codeword_len = average_codeword_length(codes, freq_table)
    return entropy / avg_codeword_len

# 计calculate the compression ratio
def compression_ratio(encoded_size, original_size):
    return  encoded_size / original_size
