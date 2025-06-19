#!/usr/bin/env python3
"""Test script with plain FTP (no TLS)"""

import json
import logging
from simple_transfer import SimpleTransfer

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

# Modify config to use plain FTP
config['ftp']['use_ftps'] = False
config['ftp']['passive_mode'] = True
print("Testing with plain FTP (no TLS)")
print("Config:", config['ftp'])

# Create transfer object
transfer = SimpleTransfer(config)

# Test connection
print("Testing connection...")
if transfer.connect():
    print("✓ Connection successful")
    
    # Test creating test file
    test_content = "Hello plain FTP test"
    with open('/tmp/test_ftp_plain.txt', 'w') as f:
        f.write(test_content)
    
    # Test upload
    print("Testing upload...")
    result = transfer.upload_file('/tmp/test_ftp_plain.txt', 'test_plain.txt')
    print(f"Upload result: {result}")
    
    transfer.disconnect()
else:
    print("✗ Connection failed")
