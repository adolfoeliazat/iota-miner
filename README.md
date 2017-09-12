# IOTA miner
You wanted an IOTA miner? Here is your IOTA miner... mining your seed. IOTA seed recovery tool to straighten your typos. Please note that if you are missing or got wrong more than a very few characters, chances of discovering your seed decrease rapidly to zero.

This tool is (currently) not connecting to the IOTA network. Addresses are not checked online for actual balances. The use case of this tool is to discover a seed for a known seed checksum or an address you still remember (e.g. from browser history after using an IOTA explorer, Bitfinex withdrawal log,...). If you cannot remember any of this data, you need to implement an online validation mechanism and might want to spawn your own full node for best performance.

##### Operation Modes:
    
    - Just check the addresses of the given seed
    - Systematically brute-force missing characters
    - Randomly choose missing characters to brute-force seed
    - Flip single characters to detect single typos
    - Inject single characters at all positions to find a missing one
    
    You can set injection markers (* / **) to guide the tool at a certain section of your seed

## Important
This tool ships with a copy of the Pyota libary (v1.2.0b1), because:
- It is the latest version and newer than the one available via PIP (at the time of writing)
- It is the last version still supporting CURL, which is going to be replaced with KERL due to an UPDATE in the IOTA protocol

## Execution
1) (Follow installation steps below)
2) Edit configuration section in "run.py"
    1) Configure your seed to offset with
    2) Adapt some default configuration values to your specific needs
3) Open a command line window, traverse to the tool's folder and launch "run.py" with your Python3 interpreter
4) Follow the dialogue
  
## Installation
1) Install Python3
2) Install required Python 3 modules
    > pip3 install pyota
    
    > pip3 install pyopenssl
    
## Prerequisites (coming with the installation steps above)
- Python3
- PyOpenSSL
- Pyota + dependencies

