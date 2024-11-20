Name: Brennan Chan
ID: 1219829962

Generative AI Acknowledgment: Portions of the code in this project were generated with assistance from ChatGPT, an AI tool developed by OpenAI. 
Reference: OpenAI. (2024). ChatGPT [Large language model]. openai.com/chatgpt

This program, written in Python, analyzes the Master Boot Record (MBR) and GUID Partition Table (GPT) of forensic disk images from raw files. 
It takes the file path and offset values as inputs and outputs detailed information about the partitions and the first 16 bytes of the boot 
record for each partition. 
The program also calculates MD5, SHA-256, and SHA-512 hashes of the raw image before performing the analysis to ensure file integrity.