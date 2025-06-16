# 🧠 Forensic Disk Image Analyzer

**Author:** Brennan Chan  
**Course:** CSE 469 – Computer and Network Forensics  
**Tool Acknowledgment:** Portions of the code were generated with assistance from ChatGPT by OpenAI  
**Reference:** OpenAI. (2024). *ChatGPT* [Large language model]. https://openai.com/chatgpt

---

## 📘 Overview

This project is a Python-based tool for analyzing Master Boot Record (MBR) and GUID Partition Table (GPT) data from raw forensic disk images. It performs low-level parsing of partition entries, extracts boot sector data, and verifies file integrity using cryptographic hash functions. This tool supports both MBR and GPT analysis and can distinguish between protective MBRs and valid GPT headers.

---

## 🛠 Features

- 🔍 **MBR Partition Table Analysis:**  
  Extracts up to 4 MBR partition entries and decodes types (e.g., FAT16, NTFS, Linux).
  
- 🧠 **GPT Partition Table Analysis:**  
  Identifies valid GPT headers, parses partition entries, and extracts GUIDs, names, and LBA ranges.

- 🧪 **Boot Record Inspection:**  
  Reads the first 16 bytes of each partition (given offset), presenting both hexadecimal and ASCII representations.

- 🔐 **Integrity Verification:**  
  Computes and saves the MD5, SHA-256, and SHA-512 hash values of the raw disk image.

---

## 📂 Project Structure
```
ForensicDiskAnalyzer/
├── boot_info.py # Main script for MBR/GPT parsing and hashing
├── gpt_sample.raw # Sample GPT-based raw disk image
├── mbr_sample.raw # Sample MBR-based raw disk image
├── MD5-gpt_sample.raw.txt # MD5 hash of gpt_sample.raw
├── MD5-mbr_sample.raw.txt # MD5 hash of mbr_sample.raw
├── PartitionTypes.csv # Optional CSV listing partition type codes
├── PartitionTypes.json # JSON version of partition type codes
├── Makefile # Compilation helper (optional)
└── README.md # This file
```
---

## 🧪 Sample Usage

### CLI Example

```bash
python3 boot_info.py -f mbr_sample.raw -o 0 0 0 0
```
-f: Path to the raw disk image file

-o: List of byte offsets for reading the first 16 bytes of each partition’s boot record

Output Example (MBR)
```
(07), HPFS/NTFS/exFAT, 1048576, 2097152
Partition number: 1
16 bytes of boot record from offset 0: 45 52 52 4F 52 00 00 00 00 00 00 00 00 00 00 00
ASCII: E R R O R . . . . . . . . .
```

Output Example (GPT)
```
Partition number: 1
Partition Type GUID : a2a0d0eb-e5b9-3344-87c0-68b6b72699c7
Starting LBA in hex: 0x22
Ending LBA in hex: 0x1F1
Starting LBA in Decimal: 34
Ending LBA in Decimal: 497
Partition name: EFI system partition
```

## 🔄 Execution Model
The raw image file is hashed using MD5, SHA-256, and SHA-512.

The script inspects the first 512 bytes to determine whether it's an MBR or GPT disk.

If MBR:

1. Reads up to 4 partition entries (16 bytes each)

2. Classifies partition types using a hardcoded dictionary

3. Optionally reads 16 boot-record bytes from given offsets

If GPT:

1. Validates "EFI PART" signature

2. Parses the GPT header for partition layout

3. Extracts and formats partition GUIDs, names, and LBAs

## 🧰 Supported Partition Types (MBR)
A few commonly supported types:

0x07 – HPFS/NTFS/exFAT

0x06 – FAT16

0x0B – FAT32

0x83 – Linux

0xEE – GPT Protective MBR

Full list available in: PartitionTypes.csv or PartitionTypes.json.

## 📦 Hash Output Files
For each raw image, the following files will be generated:

MD5-<filename>.txt

SHA-256-<filename>.txt

SHA-512-<filename>.txt

These ensure the forensic integrity of the disk images prior to analysis.

## ⚙️ Requirements
Python 3.x

No external libraries required

Works on Linux, macOS, or Windows with Python
