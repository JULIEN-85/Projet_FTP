#!/usr/bin/env python3
"""Test script to debug FTP upload issues"""

import json
import logging
from simple_transfer import SimpleTransfer

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

print("Config loaded:", config['ftp'])

# Create transfer object
transfer = SimpleTransfer(config)

# Test connection
print("Testing connection...")
if transfer.connect():
    print("✓ Connection successful")
    
    # Test creating test file
    test_content = "Hello FTP test"
    with open('/tmp/test_ftp_upload.txt', 'w') as f:
        f.write(test_content)
    
    # Test upload
    print("Testing upload...")
    result = transfer.upload_file('/tmp/test_ftp_upload.txt', 'test_upload.txt')
    print(f"Upload result: {result}")
    
    # Test directory listing
    print("Testing file listing...")
    files = transfer.list_files()
    print(f"Files on server: {files}")
    
    transfer.disconnect()
else:
    print("✗ Connection failed")
