#!/usr/bin/env python3
"""
Quick test to verify if the issue is with FTPS data channel
Let's try regular FTP after getting AUTH
"""
import ftplib
import logging

logging.basicConfig(level=logging.DEBUG)

try:
    # Try basic FTP connection to see what the server actually supports
    ftp = ftplib.FTP()
    print("Connecting...")
    ftp.connect('192.168.1.22', 21, timeout=10)
    print("Connected, getting features...")
    
    # Get server features
    try:
        features = ftp.sendcmd('FEAT')
        print("Server features:")
        print(features)
    except:
        print("FEAT command not supported")
    
    # Try to login without AUTH first to see what happens
    print("Trying login...")
    ftp.login('julien', '2004')
    print("Basic FTP login successful!")
    
    # Test upload
    with open('/tmp/test_basic_ftp.txt', 'w') as f:
        f.write("Basic FTP test")
    
    with open('/tmp/test_basic_ftp.txt', 'rb') as f:
        ftp.storbinary('STOR test_basic.txt', f)
    
    print("Upload successful!")
    
    ftp.quit()
    
except Exception as e:
    print(f"Error: {e}")
    try:
        ftp.quit()
    except:
        pass
