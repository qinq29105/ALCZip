import os
import logging
import torch
from transformers import GPT2Tokenizer, GPT2Model
from tqdm import tqdm
from .utils import chunk_text, ensure_dir

logger = logging.getLogger(__name__)

class TextSimplifier:
    def __init__(self, model_name='gpt2'):
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2Model.from_pretrained(model_name)
        self.max_length = 1024
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
    def process_chunk(self, text):
        try:
            encoded = self.tokenizer.encode(text, max_length=self.max_length, truncation=True)
            padded = self.tokenizer.pad_token_id * torch.ones((1, self.max_length), dtype=torch.long)
            padded[0, :len(encoded)] = torch.tensor(encoded)
            
            attention_mask = torch.zeros((1, self.max_length), dtype=torch.long)
            attention_mask[0, :len(encoded)] = 1
            
            inputs = {
                'input_ids': padded,
                'attention_mask': attention_mask
            }
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                
            decoded_text = self.tokenizer.decode(padded[0][attention_mask[0] == 1], 
                                               skip_special_tokens=True)
            return decoded_text
            
        except Exception as e:
            logger.error(f"Error processing chunk: {str(e)}")
            raise

    def save_batch(self, results, output_path, batch_idx, encoding):
        batch_path = f"{output_path}.batch_{batch_idx}.txt"
        with open(batch_path, 'w', encoding=encoding) as f:
            f.write('\n'.join(results))
        return batch_path

    def process_file(self, input_path, output_dir, encoding):
        logger.info(f"Processing file: {input_path}")
        
        try:
            with open(input_path, 'r', encoding=encoding) as f:
                text = f.read()

            chunks = chunk_text(text, max_length=self.max_length)
            
            results = []
            batch_size = 50
            batch_files = []
            batch_idx = 0
            
            for i, chunk in enumerate(tqdm(chunks, desc="Processing text")):
                if not chunk.strip():
                    continue
                
                processed_text = self.process_chunk(chunk)
                results.append(processed_text)
                
                if len(results) >= batch_size or i == len(chunks) - 1:
                    if results:
                        ensure_dir(output_dir)
                        output_path = os.path.join(
                            output_dir,
                            os.path.basename(input_path)
                        )
                        batch_file = self.save_batch(results, output_path, batch_idx, encoding)
                        batch_files.append(batch_file)
                        batch_idx += 1
                        results = []
            
            with open(os.path.join(output_dir, 'batch_info.txt'), 'w', encoding=encoding) as f:
                for batch_file in batch_files:
                    f.write(f"{batch_file}\n")
            
            logger.info(f"Processing complete. Results saved in {output_dir}")
            logger.info(f"Total batches: {batch_idx}")
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            raise

    def merge_batches(self, output_dir, final_output_path, encoding):
        try:
            with open(os.path.join(output_dir, 'batch_info.txt'), 'r', encoding=encoding) as f:
                batch_files = f.readlines()
            
            simplified_path = final_output_path + '.simplified'
            with open(simplified_path, 'w', encoding=encoding) as out_file:
                for batch_file in tqdm(batch_files, desc="Merging batches"):
                    batch_file = batch_file.strip()
                    if os.path.exists(batch_file):
                        with open(batch_file, 'r', encoding=encoding) as f:
                            out_file.write(f.read())
                            out_file.write('\n')
                        os.remove(batch_file)
            
            os.remove(os.path.join(output_dir, 'batch_info.txt'))
            logger.info(f"Merged results saved to {simplified_path}")
            
        except Exception as e:
            logger.error(f"Error merging batches: {str(e)}")
            raise