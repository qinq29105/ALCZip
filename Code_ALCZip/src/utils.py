import os
import math
import chardet
from typing import Dict, Tuple, List

def detect_encoding(file_path: str) -> str:
    """检测文件编码"""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    result = chardet.detect(raw_data)
    return result['encoding']

def chunk_text(text: str, max_length: int = 1024) -> List[str]:
    """将文本分块"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        word_length = len(word)
        if current_length + word_length + 1 <= max_length:
            current_chunk.append(word)
            current_length += word_length + 1
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = word_length
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def ensure_dir(directory: str) -> None:
    """确保目录存在"""
    if not os.path.exists(directory):
        os.makedirs(directory)

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

def calculate_average_length(text: str, dictionary: Dict[str, str]) -> float:
    total_len = 0
    total_chars = 0
    for char, code in dictionary.items():
        char_freq = sum(1 for c in text if c == char)
        total_len += len(code) * char_freq
        total_chars += char_freq
    return total_len / total_chars if total_chars > 0 else 0

def calculate_compression_metrics(input_path: str, encoded_data: str,
                               dictionary: Dict[str, str]) -> Tuple[float, float, float, float]:
    entropy = calculate_entropy_from_file(input_path)
    avg_length = calculate_average_length(encoded_data, dictionary)
    efficiency = entropy / avg_length if avg_length > 0 else 0
    redundancy = 1 - efficiency
    return efficiency, redundancy, entropy, avg_length

def save_compressed_data(output_path: str, 
                        encoded_data: str, 
                        dictionary: Dict[str, str],
                        original_encoding: str) -> None:
    padding_length = (8 - len(encoded_data) % 8) % 8
    encoded_data += '0' * padding_length
    
    bytes_data = bytearray()
    for i in range(0, len(encoded_data), 8):
        byte = encoded_data[i:i+8]
        bytes_data.append(int(byte, 2))
    
    with open(output_path + '.compressed', 'wb') as f:
        # 写入原始文件编码
        encoding_bytes = original_encoding.encode('utf-8')
        f.write(len(encoding_bytes).to_bytes(1, byteorder='big'))
        f.write(encoding_bytes)
        # 写入填充长度
        f.write(padding_length.to_bytes(1, byteorder='big'))
        # 写入字典
        dict_str = str(dictionary)
        dict_bytes = dict_str.encode('utf-8')
        f.write(len(dict_bytes).to_bytes(4, byteorder='big'))
        f.write(dict_bytes)
        # 写入压缩数据
        f.write(bytes_data)

def load_compressed_data(input_path: str) -> Tuple[str, Dict[str, str], str]:
    """读取压缩文件，返回编码数据、字典和原始编码方式"""
    with open(input_path, 'rb') as f:
        # 读取原始文件编码
        encoding_len = int.from_bytes(f.read(1), byteorder='big')
        original_encoding = f.read(encoding_len).decode('utf-8')
        # 读取填充长度
        padding_length = int.from_bytes(f.read(1), byteorder='big')
        # 读取字典
        dict_len = int.from_bytes(f.read(4), byteorder='big')
        dict_bytes = f.read(dict_len)
        dictionary = eval(dict_bytes.decode('utf-8'))
        # 读取压缩数据
        bytes_data = f.read()
        
    # 转换为二进制字符串
    binary_str = ''.join(format(byte, '08b') for byte in bytes_data)
    if padding_length > 0:
        binary_str = binary_str[:-padding_length]
        
    return binary_str, dictionary, original_encoding