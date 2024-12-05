import argparse
import logging
from src.text_processor import TextProcessor
from src.utils import save_compressed_data

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                   level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Text simplification and compression tool')
    parser.add_argument('-i', '--input', required=True, help='Input file path')
    parser.add_argument('-o', '--output', required=True, help='Output file path')
    parser.add_argument('-d', '--work_dir', required=True, help='Working directory for temporary files')
    parser.add_argument('--dict_size', type=int, default=1000, help='Maximum dictionary size')
    parser.add_argument('--substring_len', type=int, default=6, help='Maximum substring length')
    parser.add_argument('--decode', action='store_true', help='Decode mode')
    args = parser.parse_args()

    processor = TextProcessor(max_dict_size=args.dict_size, 
                            max_substring_len=args.substring_len)

    if args.decode:
        # 解码模式
        processor.decode(args.input, args.output)
    else:
        # 编码模式
        encoded_data, dictionary, metrics, original_encoding = processor.process(
            args.input, args.work_dir, args.output)
        
        # 保存压缩文件
        logger.info("Saving compressed file...")
        save_compressed_data(args.output, encoded_data, dictionary, original_encoding)
        
        # 输出统计信息
        efficiency, redundancy, entropy, avg_length = metrics
        logger.info(f'\nCompression completed:')
        logger.info(f'Entropy (H(X)): {entropy:.4f} bits')
        logger.info(f'Average Length (L): {avg_length:.4f} bits')
        logger.info(f'Encoding Efficiency: {efficiency:.4f}')
        logger.info(f'Redundancy: {redundancy:.4f}')

if __name__ == "__main__":
    main()