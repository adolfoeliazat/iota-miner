# IOTA miner
You wanted an IOTA miner? Here is your IOTA miner... mining your seed. IOTA seed recovery tool to straighten your typos. Please note that if you are missing or got wrong more than a very few characters, chances of discovering your seed decrease rapidly to zero.

##### Operation Modes:

    - Just check the addresses of the given seed  
    - Brute-force missing characters up to a 81 character seed  
    - Flip single characters to detect single typos  
    - Inject single characters at all positions to find single missing characters
  
##### Upcoming features:

     - Injection marker (wildcard) telling the tool where to inject characters
     - Option to only test 81 character seeds
   

## Prerequisite
- Python3
- PyOpenSSL
- Pyota + dependencies

## Important
This tool ships with a copy of the Pyota libary (v1.2.0b1), because:
- It is the latest version and newer than the one available via PIP (at the time of writing)
- It is the last version still supporting CURL, which is going to be replaced with KERL due to an UPDATE in the IOTA protocol

## Installation
1) Install Python3
2) Install required Python 3 modules
    > pip3 install pyota
    
    > pip3 install pyopenssl

## Execution
1) Configure settings at the top section in run.py
2) Launch run.py
    > python3 run.py
