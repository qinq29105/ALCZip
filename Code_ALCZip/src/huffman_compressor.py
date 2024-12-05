from typing import Dict
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from heapq import heapify, heappush, heappop
from tqdm import tqdm

class HuffmanCompressor:
    def __init__(self, max_dict_size=1000, max_substring_len=6, model_name="gpt2"):
        self.dictionary: Dict[str, str] = {}
        self.max_substring_len = max_substring_len
        self.max_dict_size = max_dict_size
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        self.model.eval()
        self.chars = set()

    def generate_dictionary(self, sample_text: str) -> Dict[str, int]:
        # Split sample text into chunks of max 1024 tokens
        chunk_size = 1024
        chunks = [sample_text[i:i + chunk_size * 4] for i in range(0, len(sample_text), chunk_size * 4)]
        
        freq = {}
        
        # Process each chunk with progress bar
        with tqdm(chunks, desc="生成字典") as pbar:
            for chunk in pbar:
                tokens = self.tokenizer.encode(chunk, truncation=True, max_length=chunk_size)
                token_words = self.tokenizer.convert_ids_to_tokens(tokens)
                
                # Add single characters first
                for c in chunk:
                    self.chars.add(c)
                    freq[c] = freq.get(c, 0) + 1
                
                # Process GPT-2 tokens
                for token in token_words:
                    if token.startswith('Ġ'):
                        token = token[1:]
                    if token.startswith('â'):
                        continue
                        
                    word = self.tokenizer.convert_tokens_to_string([token])
                    if len(word) > 1 and len(word) <= self.max_substring_len:
                        if word in chunk:
                            count = chunk.count(word)
                            freq[word] = freq.get(word, 0) + count * 2

        # Ensure all characters are in the dictionary
        for c in sample_text:
            if c not in freq:
                freq[c] = 1
        
        # Limit dictionary size
        sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_freq[:self.max_dict_size])
    

    def build_huffman_tree(self, freq: Dict[str, int]) -> None:
        heap = [[weight, [char, ""]] for char, weight in freq.items()]
        heapify(heap)
        
        with tqdm(total=len(heap)-1, desc="Building Huffman Tree") as pbar:
            while len(heap) > 1:
                lo = heappop(heap)
                hi = heappop(heap)
                for pair in lo[1:]:
                    pair[1] = '0' + pair[1]
                for pair in hi[1:]:
                    pair[1] = '1' + pair[1]
                heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
                pbar.update(1)
            
        if heap:
            for char, code in heap[0][1:]:
                self.dictionary[char] = code

    def encode(self, text: str, pbar=None) -> str:
        encoded = ""
        i = 0
        while i < len(text):
            best_match = ""
            best_len = 0
            
            for j in range(min(self.max_substring_len, len(text) - i), 0, -1):
                substr = text[i:i+j]
                if substr in self.dictionary:
                    best_match = substr
                    best_len = j
                    break
            
            if best_len > 0:
                encoded += self.dictionary[best_match]
                i += best_len
            else:
                if text[i] not in self.dictionary:
                    self.dictionary[text[i]] = format(len(self.dictionary), 'b').zfill(8)
                encoded += self.dictionary[text[i]]
                i += 1
            
            if pbar:
                pbar.update(best_len if best_len > 0 else 1)
        
        return encoded

    def decode(self, encoded_text: str, pbar=None) -> str:
        reverse_dict = {v: k for k, v in self.dictionary.items()}
        result = ""
        current = ""
        
        with tqdm(total=len(encoded_text), desc="Decoding") as pbar:
            for bit in encoded_text:
                current += bit
                if current in reverse_dict:
                    result += reverse_dict[current]
                    current = ""
                pbar.update(1)
        
        return result