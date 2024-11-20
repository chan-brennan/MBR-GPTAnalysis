#!/usr/bin/env python3
import hashlib
import os
import struct
import argparse

# Function to calculate hashes and write to files
def calculate_hashes(filename):
    # Ensure the directory exists for the output files
    base_filename = os.path.basename(filename)

    # Define file paths for hash output files
    md5_path = f"MD5-{base_filename}.txt"
    sha256_path = f"SHA-256-{base_filename}.txt"
    sha512_path = f"SHA-512-{base_filename}.txt"

    # Open files for writing hash values
    with open(md5_path, 'w') as f_md5, \
         open(sha256_path, 'w') as f_sha256, \
         open(sha512_path, 'w') as f_sha512:

        md5 = hashlib.md5()
        sha256 = hashlib.sha256()
        sha512 = hashlib.sha512()

        # Read the image file and calculate hashes
        with open(filename, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
                sha256.update(chunk)
                sha512.update(chunk)

        # Write the hash values to their respective files
        f_md5.write(md5.hexdigest())
        f_sha256.write(sha256.hexdigest())
        f_sha512.write(sha512.hexdigest())

# Function to convert GUID from GPT partition table
def convert_guid(raw_guid):
    """
    Convert the raw GUID from GPT partition entry to the little-endian format.
    The entire GUID is treated as little-endian and returned as a 16-byte string
    without dashes.
    """
    # Reverse the entire 16-byte GUID for little-endian interpretation
    little_endian_guid = raw_guid[::-1]
    
    # Return the GUID as a continuous hex string, without dashes
    return little_endian_guid.hex().lower()

# Function to read MBR and extract partition table
def read_mbr(filename, offsets):
    mbr_types = {
        0x07: "HPFS/NTFS/exFAT",
        0x06: "FAT16",
        0x0B: "FAT32",
        0x0C: "FAT32 LBA",
        0x83: "Linux",
        0xa9: "NetBSD",
    }

    partitions = []  # Store partition details for later printing
    boot_records = []  # Store boot record details for later printing

    try:
        with open(filename, 'rb') as f:
            mbr = f.read(512)  # Read the first 512 bytes (MBR)

            # Check the MBR signature
            signature = struct.unpack('<H', mbr[510:512])[0]
            if signature != 0xAA55:
                print("Not a valid MBR.")
                return

            # Check if the MBR contains a protective GPT partition type (0xEE)
            entry = mbr[446:446 + 16]
            partition_type = entry[4]
            if partition_type == 0xEE:
                read_gpt(filename)
                return

            # Read partition entries (16 bytes each, 4 partitions)
            for i in range(4):
                entry = mbr[446 + i * 16: 446 + (i + 1) * 16]
                partition_type = entry[4]
                start_sector = struct.unpack('<I', entry[8:12])[0]
                partition_size = struct.unpack('<I', entry[12:16])[0]

                if partition_type == 0x00:
                    continue  # Skip empty partition

                partition_name = mbr_types.get(partition_type, "Unknown")

                # Collect partition information
                partitions.append(
                    f"({partition_type:02x}), {partition_name}, {start_sector * 512}, {partition_size * 512}"
                )

                # Extract boot record if offsets are provided
                if i < len(offsets):
                    f.seek(start_sector * 512 + offsets[i])
                    boot_record = f.read(16)
                    ascii_repr = ''.join([chr(b) if 32 <= b < 127 else '.' for b in boot_record])

                    boot_records.append(
                        f"Partition number: {i + 1}\n"
                        f"16 bytes of boot record from offset {offsets[i]}: "
                        f"{' '.join(f'{b:02X}' for b in boot_record)}\n"
                        f"ASCII: {' '.join(ascii_repr)}"
                    )

            # Print partitions first
            for partition in partitions:
                print(partition)

            # Print boot records next
            for record in boot_records:
                print(record)

    except IOError:
        print(f"Error opening file: {filename}")

# Function to read GPT and extract partition entries
def read_gpt(filename):
    try:
        with open(filename, 'rb') as f:
            # Read GPT header (starts at sector 1, 512 bytes offset)
            f.seek(512)
            header = f.read(92)

            # Check if the signature matches "EFI PART"
            signature = header[:8].decode('utf-8')
            if signature != "EFI PART":
                print("Not a valid GPT.")
                return

            # Extract header values
            partition_entry_lba = struct.unpack('<Q', header[72:80])[0]
            num_partition_entries = struct.unpack('<I', header[80:84])[0]
            partition_entry_size = struct.unpack('<I', header[84:88])[0]

            # Read partition entries
            f.seek(partition_entry_lba * 512)  # Go to partition entries
            for i in range(num_partition_entries):
                entry = f.read(partition_entry_size)
                partition_type_guid = entry[:16]
                starting_lba = struct.unpack('<Q', entry[32:40])[0]
                ending_lba = struct.unpack('<Q', entry[40:48])[0]
                partition_name = entry[56:128].decode('utf-16').strip('\x00')

                # Skip unused entries
                if partition_type_guid == b'\x00' * 16:
                    continue

                # Convert GUID to little-endian format
                guid_string = convert_guid(partition_type_guid)

                # Print partition details in the desired format
                print(f"Partition number: {i + 1}")
                print(f"Partition Type GUID : {guid_string}")
                print(f"Starting LBA in hex: 0x{starting_lba:X}")
                print(f"Ending LBA in hex: 0x{ending_lba:X}")
                print(f"Starting LBA in Decimal: {starting_lba}")
                print(f"Ending LBA in Decimal: {ending_lba}")
                print(f"Partition name: {partition_name}")
                print()

    except IOError:
        print(f"Error opening file: {filename}")

# Main function to parse arguments and execute the appropriate functions
def main():
    parser = argparse.ArgumentParser(description='Analyze MBR and GPT of forensic disk images.')
    parser.add_argument('-f', '--file', required=True, help='Path to raw image file')
    parser.add_argument('-o', '--offsets', nargs='*', type=int, help='Offsets for MBR boot records')

    args = parser.parse_args()

    # Calculate and write hash values
    calculate_hashes(args.file)

    # Open and analyze raw image
    try:
        with open(args.file, 'rb') as f:
            first_sector = f.read(512)
            # Check if it's MBR or GPT by looking for the MBR signature
            mbr_signature = first_sector[0x1FE:0x200]  # MBR signature at the end of sector 0
            if mbr_signature == b'\x55\xAA':
                if args.offsets:
                    read_mbr(args.file, args.offsets)
                else:
                    read_mbr(args.file, [])  # No offsets provided, just read MBR partitions
            else:
                read_gpt(args.file)
    except IOError:
        print(f"Error opening file: {args.file}")

if __name__ == "__main__":
    main()