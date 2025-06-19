#!/usr/bin/env python3
"""Test script to try active mode FTP"""

import json
import logging
from simple_transfer import SimpleTransfer

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

# Modify config to use active mode
config['ftp']['passive_mode'] = False
print("Testing with active mode FTP")
print("Config:", config['ftp'])

# Create transfer object
transfer = SimpleTransfer(config)

# Test connection
print("Testing connection...")
if transfer.connect():
    print("✓ Connection successful")
    
    # Test creating test file
    test_content = "Hello FTP active mode test"
    with open('/tmp/test_ftp_active.txt', 'w') as f:
        f.write(test_content)
    
    # Test upload
    print("Testing upload...")
    result = transfer.upload_file('/tmp/test_ftp_active.txt', 'test_active.txt')
    print(f"Upload result: {result}")
    
    transfer.disconnect()
else:
    print("✗ Connection failed")
