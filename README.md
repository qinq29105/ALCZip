# ALCZip: Fully Exploitation of Large models in Lossless Text Compression

**ALCZip** is a novel compression method that integrates large language models (LLMs) with traditional techniques to enhance the compression of semantically complex data. ALCZip employs an adaptive approach to incorporate LLMs into Huffman coding, significantly improving compression speed compared to other LLM-based methods, such as LLMZip and FineZip. It is among the first to use LLMs for constructing adaptive dictionaries of letter combinations of varying lengths, resulting in more efficient compression. Additionally, ALCZip successfully applies semantic simplification to text compression, marking a first in lossless text compression. Through experiments on the Game of Thrones text, we demonstrate that ALCZip achieves superior compression ratios. While it incurs higher computational costs, ALCZip outperforms other LLM-based methods in both compression and decompression times, advancing the application of LLMs in compression. The trade-off between compression efficiency and computational time is discussed, with ALCZip being particularly suited for scenarios requiring substantial data reduction.

## Key Features
- **Adaptive LLM Integration:** Combines the power of large language models with traditional compression methods like Huffman coding for improved efficiency.
- **Semantic Simplification:** Introduces semantic simplification in lossless text compression, the first of its kind, enabling better handling of complex data structures.
- **High Compression Ratios:** Achieves substantial data reduction while maintaining high-quality output, suitable for long-term storage and bandwidth optimization.
- **Adaptability:** Can be applied to diverse datasets, particularly those involving intricate structures or specialized terminology (e.g., legal, scientific documents).

## Installation

To use ALCZip, please refer to the readme in that folder. Simply clone the repository to your local machine to access **ALCZip**:

```bash
git clone https://github.com/qinq29105/ALCZip.git
cd ALCZip
