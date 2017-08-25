# iota-miner
You wanted an IOTA miner? Here is your IOTA miner... mining your seed. IOTA seed recovery tool to straighten your typos.


# Prerequisite
- Python3
- PyOpenSSL
- Pyota + dependencies

# Important
This tool ships with a copy of the Pyota libary (v1.2.0b1), because:
- It is the latest version and newer than the one available via PIP (at the time of writing)
- It is the last version still supporting CURL, which is going to be replaced with KERL due to an UPDATE in the IOTA protocol

# Installation
1) Install Python3
2) Install required Python 3 modules
    > pip3 install pyota
    
    > pip3 install pyopenssl

# Execution
1) Configure settings at the top section in run.py
2) Launch run.py
    > python3 run.py
