#
# AUTHOR:  enthusiast @ iotatangle.slack.com
# VERSION: 1.0
#
# LICENSE
#
# You may apply this tool to reconstruct your own private/personal IOTA seed
# You may share this tool as it is
#
# You may not abuse this tool
# You may not distribute this tool via your own channel
# You may not change this tool without permission
# You may not complain if this tool did not help you - sorry about that!
#
# You may assume that chances for success are low
# You may be happy if it saved your iotas
#

import sys
import os
import iota
import string
import time
import concurrent.futures
from itertools import product
from six import binary_type


# ####################################################
# CONFIGURATION
# ####################################################

# The seed to start brute-forcing with. Insert your seed as a string (surrounded by quotes, e.g. "SEED9")
SEED = ""

# The amount of addresses to check per seed. Generating addresses is very time consuming. Keep as low as possible.
# Set to zero if you don't want to generate addresses but just seeds and seed checksums.
ADDRESSES_PER_SEED = 2

# Known address you are looking for. None or empty string, if you just want to run until the end of the script. You
# can lookup the addresses in the output file later.
ABORT_AT_ADDRESS = "MY9KNOWN9ADDRESS9"

# If you can remember the checksum of your seed, you might want to search for seeds with a the same. None or empty
# string, if you just want to run until the end of the script. You can lookup the checksums in the output file later.
# It is recommended to leave this variable empty and manually search the output for your checksum, as there might be
# multiple seeds with your checksum!
# ATTENTION: You can speed up dramatically, if you set ADDRESSES_PER_SEED to 0 and skip address generation!
# ATTENTION: Due to recent exchange of the hashing algorithm used in IOTA, checksums differ between IRI 1.2 and 1.3!
ABORT_AT_SEED_CHECKSUM = ""

# Needs to be set to 1, 2 or 3 ACCORDING to what your wallet used!
ADDRESS_SECURITY_LEVEL = 2

# You can disable console status output during execution which will increase execution speed. Will make a huge
# difference if ADDRESSES_PER_SEED is set to 0.
STATUS_OUTPUT = True

# Characters to use for brute forcing. You can limit the character set if you don't want to go the full range for some
# reason.
BRUTE_FORCE_CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ9'  

# More processes than CPU/Cores does not make sense. Decrease, if you want to use the machine in parallel.
PARALLEL_PROCESSES = os.cpu_count() -1

# Output file to store addresses in. None or empty string, if you don't want to write output.
OUTPUT_FILE = "addresses.log"


# ####################################################
# EXECUTION
# ####################################################

def brute_force(length):
    for l in range(0, length+1):  # only do lengths of 1 + 2
        to_attempt = product(BRUTE_FORCE_CHARACTERS, repeat=l)
        for attempt in to_attempt:
            yield ''.join(attempt)


def check_seed(seed):
    """
    Checks addresses of input seed
    
    :param seed: 
    :return: 
    """
    print("=> Nothing to generate. Just checking the addresses of the given seed")
    print()
    yield seed


def brute_seed(seed):
    """
    Tries to brute-force missing characters by extending the seed up to 81 characters
    
    :param seed: 
    :return: 
    """
    missing_characters = 81 - len(seed)

    if missing_characters <= 0:
        print("ERROR: Your seed is already 81 characters or longer.")
        sys.exit(-1)
    else:
        print("=> Trying to extend and brute-force missing {} character(s) ({} possibilities)".format(
            missing_characters,
            (missing_characters ** len(BRUTE_FORCE_CHARACTERS))+1
        ))
        print()

        if missing_characters > 2:
            print("WARNING: You are missing more than 2 characters. Process might never finish.")
            print()

        # Give user time to read
        time.sleep(2)

        for sample in brute_force(missing_characters):
            yield seed + sample


def flip_seed(seed):
    """
    Tries to iterate single characters, one by one
    
    :param seed: 
    :return: 
    """
    print("=> Trying to flip {} character(s) ({} possibilities)".format(
        len(seed),
        (len(seed) ** (len(BRUTE_FORCE_CHARACTERS)-1))+1
    ))  # 26 possibilities, as the current character does not need to be checked
    print()

    # Give user time to read
    time.sleep(2)

    # Also test input itself
    yield seed

    # Flip characters position by position
    for char in BRUTE_FORCE_CHARACTERS:
        count = 0
        for position in range(0, len(seed)):

            # Yield if character wasn't already to one to use
            if list(seed)[position] != char:
                tmp = list(seed)
                tmp[position] = char
                yield "".join(tmp)

            # Increase position counter
            count += 1


def inject_seed(seed):
    """
    Tries to inject a single character at each position, one by one
    
    :param seed: 
    :return: 
    """
    character_positions = len(seed) + 1
    print("=> Trying to inject characters at {} positions ({} possibilities)".format(
        character_positions,
        character_positions ** len(BRUTE_FORCE_CHARACTERS)
    ))
    print()

    # Give user time to read
    time.sleep(2)

    # Also test input itself
    yield seed

    # Inject characters position by position
    for char in BRUTE_FORCE_CHARACTERS:
        count = 0
        for position in range(0, len(seed)+1):
            tmp = list(seed)
            tmp.insert(position, char)

            # Yield if it isn't the same as in the previous loop cycle
            if position != 0 and tmp[position-1] == char:
                continue
            else:
                yield "".join(tmp)

            # Increase position counter
            count += 1


def sanitize_seed(seed):
    # Sanitize input
    seed = seed.strip().upper()[0:81]

    # Check if seed is valid
    if not set(seed) <= set(string.ascii_uppercase + '9'):
        print("ERROR: Please configure a valid seed in the configuration section of the script.")
        return None

    # Encode seed as required
    return seed


def print_configuration():
    print("CURRENT SETTINGS (change in script head):")

    if SEED:
        print("   - Offset seed is '{}{}'".format(SEED[0:55], "..." if len(SEED) > 55 else ""))
    else:
        print("   - Offset seed is an empty string")

    print("   - {} addresses will be generated per seed{}".format(
        ADDRESSES_PER_SEED,
        " (set to 0 if you are only looking for seed checksums)" if ADDRESSES_PER_SEED != 0 else ""
    ))

    if ABORT_AT_SEED_CHECKSUM:
        print("   - The script will abort once the SEED checksum '{}' was found".format(
            ABORT_AT_SEED_CHECKSUM
        ))
        print("     (Better don't stop at the first occurrence but search the output file!)")
    else:
        print("   - The script will run until all SEEDs were generated")

    if ADDRESSES_PER_SEED != 0:
        if ABORT_AT_ADDRESS:
            print("   - The script will abort once ADDRESS '{}{}' was found".format(
                ABORT_AT_ADDRESS[0:25],
                "..." if len(ABORT_AT_ADDRESS) > 25 else ""
            ))
        else:
            print("   - The script will run until all ADDRESSES were generated")

    print("   - Address security level is {} (adapt to the setting of your wallet)".format(ADDRESS_SECURITY_LEVEL))

    print()


def get_mode():

    # Mode/function mapping
    modes = {
        "1": check_seed,
        "2": brute_seed,
        "3": flip_seed,
        "4": inject_seed
    }

    # Ask for mode
    print("WHICH OPERATION MODE DO YOU WANT TO EXECUTE?")
    print("  1. Just check the addresses of the given seed")
    print("  2. Brute-force missing characters up to a 81 character seed")
    print("  3. Flip single characters to detect single typos")
    print("  4. Inject single characters at all positions to find single missing characters")

    # Query user input until it's a valid one
    a = ""
    while a.strip() not in modes:
        try:
            a = input("Please select option: ")
        except EOFError:  # Might get thrown on Ctrl+C
            print()  # Beauty fix
            print()  # Beauty fix
            return None

        if a == "":
            print()
            print("Execution aborted by user.")
            sys.exit(-1)

    # Print spacer
    print("")

    # Return mode (reference to function to execute)
    return modes[a]


def get_checksum(trytes):
    return iota.Address(trytes)._generate_checksum()[0:3]  # Using same checksum mechanism as used for addresses


def yield_addresses(seed):
    # Connect to IOTA
    api = iota.Iota("http://localhost:14265", seed.encode('ascii'))  # No real IOTA connection required.

    # Generate addresses of seed
    api_response = api.get_new_addresses(index=1, count=ADDRESSES_PER_SEED, security_level=ADDRESS_SECURITY_LEVEL)
    for address in api_response['addresses']:
        yield binary_type(address).decode('ascii')


def check_addresses(seed, generated_seed_checksum=None):
    results = dict()
    if ADDRESSES_PER_SEED:
        count = 1
        for address in yield_addresses(seed):
            if address == ABORT_AT_ADDRESS:
                if ABORT_AT_ADDRESS:
                    print("SUCCESS! Address found in {} at position {}".format(seed, count))
                    sys.exit(0)
            results[count] = address
            count += 1
    return seed, generated_seed_checksum, results


def complete_task(task_sequence):
    # Wait for task completed signal
    concurrent.futures.wait(task_sequence, return_when="FIRST_COMPLETED")

    # Iterate tasks to find tasks to complete
    for task in task_sequence:

        # Check if task is completed
        if task.done():

            # Get task results
            seed, seed_checksum, addresses = task.result()

            # Save task output
            if OUTPUT_FILE:
                with open(OUTPUT_FILE, "a") as fh:
                    if addresses:
                        for address_index, address in addresses.items():
                            fh.write("{}\t{}\t{}\t{}\n".format(seed, seed_checksum, address_index, address))
                    else:
                        fh.write("{}\t{}\n".format(seed, seed_checksum))

            # Remove completed task
            task_sequence.remove(task)

    # Return sequence of remaining/running tasks
    return task_sequence


# ####################################################
# Start-up code
# ####################################################
if __name__ == '__main__':

    try:
        print()
        print("You wanted a miner? Here is your IOTA miner... mining your seed.")
        print("IOTA seed recovery tool to straighten your typos.", "Running on PyOTA vers.", iota.__version__)
        print()

        print("              ###################################################               ")
        print("              ## Donations appreciated if this tool helped you ##               ")
        print("              ## QPLGOG9PMIMUAW9UDMUNZQHPXZPXDNGLBEIHILXHWHIOF ##               ")
        print("              ## HLIHPDDERXAJQKUQDEORMHSUWVZQE9JYSHIWADIIPAOJD ##               ")
        print("              ###################################################               ")
        print()

        print("Please note, although the generation of seeds is quite fast, the calculation of")
        print("addresses takes very long slowing down the brute-force process significantly!")
        print()

        print("Please note, that all found addresses will be written to an output file. If you")
        print("know any of your previously used addresses, you can search the output file for.")
        print()

        # Check python version
        if sys.version_info.major < 3:
            print("ERROR: Python3 required!")
            print()
            sys.exit(-1)

        if SEED is None:
            print("ERROR: No seed configured!")
            print()
            sys.exit(-1)

        # Sanitize and encode seed
        seed_offset = sanitize_seed(SEED)

        # Continue if seed was legit
        if seed_offset is not None:

            # Prepare output file
            if OUTPUT_FILE:
                print("!! Make sure to have enough disk space for the output file or disable it !!")
                print()
                with open(OUTPUT_FILE, "w") as f:
                    pass

            # Print configuration
            print_configuration()

            # Query mode to execute from user
            brute_force_function = get_mode()

            # Initialize process pool executor to execute tasks in dedicated processes
            queued_tasks = []
            with concurrent.futures.ProcessPoolExecutor(max_workers=PARALLEL_PROCESSES) as executor:

                status_count = 0

                # Execute seed generation and launch address generation in parallel
                for generated_seed in brute_force_function(seed_offset):

                    # Calculate seed's checksum
                    generated_seed_checksum = get_checksum(generated_seed)

                    # Abort if user is looking for seed matching a given checksum
                    if ABORT_AT_SEED_CHECKSUM and ABORT_AT_SEED_CHECKSUM == generated_seed_checksum:
                        print("SUCCESS! Seed {} matching checksum {}".format(generated_seed, generated_seed_checksum))
                        print("Search for further seeds if this one was not the one you were looking for!")
                        sys.exit(0)

                    # If all workers are busy, wait for first task to complete
                    if len(queued_tasks) >= PARALLEL_PROCESSES:

                        # Update remaining tasks
                        queued_tasks = complete_task(queued_tasks)

                    # Print status
                    if STATUS_OUTPUT:
                        print("Working on", generated_seed)

                    # Submit address generation and verification task
                    new_task = executor.submit(check_addresses, generated_seed, generated_seed_checksum)

                    # Keep reference to active task
                    queued_tasks.append(new_task)

                # Wait and complete last tasks
                while queued_tasks:

                    # Update remaining tasks
                    queued_tasks = complete_task(queued_tasks)

    except KeyboardInterrupt:
        print("Execution interrupted by user.")
    finally:
        input("Please press >enter< to exit...")
