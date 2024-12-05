import os
from .text_simplifier import TextSimplifier
from .huffman_compressor import HuffmanCompressor
from .utils import (calculate_compression_metrics, save_compressed_data, 
                   detect_encoding, load_compressed_data)
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self, model_name='gpt2', max_dict_size=1000, max_substring_len=6):
        self.simplifier = TextSimplifier(model_name)
        self.compressor = HuffmanCompressor(max_dict_size, max_substring_len)

    def process(self, input_path: str, output_dir: str, final_output_path: str) -> tuple:
        # 检测输入文件编码
        original_encoding = detect_encoding(input_path)
        original_encoding = 'utf-8'
        logger.info(f"Detected input file encoding: {original_encoding}")

        # 简化文本
        logger.info("Simplifying text...")
        self.simplifier.process_file(input_path, output_dir, original_encoding)
        self.simplifier.merge_batches(output_dir, final_output_path, original_encoding)
        
        # 读取简化后的文本
        simplified_text_path = final_output_path + '.simplified'
        with open(simplified_text_path, 'r', encoding=original_encoding) as f:
            simplified_text = f.read()
        
        # 生成字典并构建Huffman树
        logger.info("Generating dictionary...")
        freq = self.compressor.generate_dictionary(simplified_text)
        logger.info("Building Huffman tree...")
        self.compressor.build_huffman_tree(freq)
        
        # 编码
        logger.info("Encoding text...")
        with tqdm(total=len(simplified_text), desc="Compression progress") as pbar:
            encoded = self.compressor.encode(simplified_text, pbar)
        
        return (encoded, 
                self.compressor.dictionary,
                calculate_compression_metrics(input_path, encoded, self.compressor.dictionary),
                original_encoding)

    def decode(self, input_path: str, output_path: str) -> None:
        """解码压缩文件"""
        logger.info(f"Decoding file: {input_path}")
        
        # 读取压缩文件
        encoded_data, dictionary, original_encoding = load_compressed_data(input_path)
        
        # 解码
        logger.info("Decoding data...")
        decoded_text = self.compressor.decode(encoded_data, dictionary)
        
        # 保存解码后的文件
        with open(output_path, 'w', encoding=original_encoding) as f:
            f.write(decoded_text)
        
        logger.info(f"Decoded file saved to: {output_path}")