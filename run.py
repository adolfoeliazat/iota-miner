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
# You may be happy if it saved your IOTAs
#

import sys
import os
import iota
import string
import time
import random
import concurrent.futures
from itertools import product
from six import binary_type


# ####################################################
# CONFIGURATION
# ####################################################

# The seed to start brute-forcing with. Insert your seed as a string (surrounded by quotes, e.g. "SEED9").
# You can put a wildcard marker (*) to define the injection position for the brute-force mode.
# You can surround a portion of characters with wildcard markers (*SEEDPART*) to define start and end position for
# injection and character flipping mode
SEED = ""

# The amount of addresses to check per seed. Generating addresses is very time consuming. Keep as low as possible.
# Set to zero if you don't want to generate addresses but just seeds and seed checksums.
ADDRESSES_PER_SEED = 2  # INTEGER - No quotes!

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

# Needs to be set to 1, 2 or 3 ACCORDING to what your wallet used! 2 is the libraries default.
ADDRESS_SECURITY_LEVEL = 2  # INTEGER - No quotes!

# You can disable console status output during execution which will increase execution speed. Will make a huge
# difference if ADDRESSES_PER_SEED is set to 0.
STATUS_OUTPUT = True  # Boolean - No quotes!

# Characters to use for brute forcing. You can limit the character set if you don't want to go the full range for some
# reason.
BRUTE_FORCE_CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ9'

# More processes than CPU/Cores does not make sense. Decrease, if you want to use the machine in parallel.
PARALLEL_PROCESSES = os.cpu_count() - 1

# Output file to store addresses in. None or empty string, if you don't want to write output.
OUTPUT_FILE = "addresses.log"


# ####################################################
# ####################################################
# ####################################################
# EXECUTION
# DO NOT EDIT BELOW THIS LINE!
# ####################################################
# ####################################################
# ####################################################

def yield_systematic_character_sequences(char_min, char_max):
    for l in range(char_min, char_max+1):  # +1 as it is not doing the last character otherwise
        to_attempt = product(BRUTE_FORCE_CHARACTERS, repeat=l)
        for attempt in to_attempt:
            yield ''.join(attempt)


def yield_random_character_sequences(char_min, char_max):
    while True:
        random_seed_length = random.randint(char_min, char_max)
        if random_seed_length > 0:
            yield "".join([random.choice(BRUTE_FORCE_CHARACTERS) for i in range(0, random_seed_length)])


def check_seed(seed):
    """
    Checks addresses of input seed
    
    :param seed: 
    :yield: The seed itself
    """
    print("=> Nothing to generate. Just checking the addresses of the given seed")
    print()
    yield seed.replace("*", "")


def brute_seed(seed, random_choice=False):
    """
    Tries to brute-force missing characters by extending the seed systematically or randomly
    
    :param seed: 
    :param random_choice: Whether to systematically generate patterns or to pick random character sequences
    :yield: Generated seeds one by one
    """

    # Check conditions
    if seed.count('*') > 1:
        print("ERROR: Your seed contains more than one injection marker '*'.")
        print()
        sys.exit(-1)

    # Execute function
    else:

        # Warn user in case of random seed choices
        if random_choice is True:
            print("WARNING: The random generator can generate duplicates and will never stop itself")
            print()

        # Calculate range (offset + length) to brute-force
        seed_length = len(seed.replace("*", ""))

        # Ask min seed length from user
        min_seed_extension_length = None
        while min_seed_extension_length is None:
            response = input("What is the MINIMUM seed length to generate (>={})? ".format(seed_length))
            try:
                if response == "" or int(response) < seed_length:
                    min_seed_extension_length = 0
                elif int(response) > 81:
                    min_seed_extension_length = 81 - seed_length
                else:
                    min_seed_extension_length = int(response) - seed_length
            except ValueError:
                pass

        # Ask max seed length from user
        max_seed_extension_length = None
        while max_seed_extension_length is None:
            try:
                response = input("What is the MAXIMUM seed length to generate (<={})? ".format(81))
                if response == "" or int(response) > 81:
                    max_seed_extension_length = 81 - seed_length
                elif int(response) < seed_length:
                    max_seed_extension_length = 0
                else:
                    max_seed_extension_length = int(response) - seed_length

                # Do plausibility check
                if max_seed_extension_length < min_seed_extension_length:
                    print("INFO: Maximum seed length cannot be smaller than minimum seed length.")
                    max_seed_extension_length = None
            except ValueError:
                pass

        # Print spacer
        print()

        # Print warning on long brute-force tasks
        if max_seed_extension_length > 3:
            print("WARNING: You are missing more than 3 characters. Process might never finish.")
            print()

        if random_choice:
            possibilities_string = ""
        else:
            # Print settings and brute-force possibilities
            if max_seed_extension_length > min_seed_extension_length:
                brute_force_possibilities = round((len(BRUTE_FORCE_CHARACTERS) ** max_seed_extension_length) - (len(BRUTE_FORCE_CHARACTERS) ** min_seed_extension_length))
            else:
                brute_force_possibilities = (len(BRUTE_FORCE_CHARACTERS) ** max_seed_extension_length)
            print("=> Trying to {} missing {} character(s)".format("guess" if random_choice else "brute-force", max_seed_extension_length))
            possibilities_string = " ({} possibilities)".format(brute_force_possibilities)

        if min_seed_extension_length != max_seed_extension_length:
            print("=> Only generating seeds between {} and {} characters{}".format(seed_length + min_seed_extension_length, seed_length + max_seed_extension_length, possibilities_string))
        else:
            print("=> Only generating seeds with {} characters{}".format(seed_length + max_seed_extension_length, possibilities_string))
        print()

        # Give user time to read
        time.sleep(3)

        # Always yield input seed as first sample
        yield seed.replace("*", "")

        if random_choice is False:
            extension_generator = yield_systematic_character_sequences(min_seed_extension_length, max_seed_extension_length)
        else:
            extension_generator = yield_random_character_sequences(min_seed_extension_length, max_seed_extension_length)

        # Yield generated seeds
        for sample in extension_generator:
            if "*" in seed:
                yield seed.replace("*", sample)
            else:
                yield seed + sample


def brute_random_seed(seed):
    """
    Tries to brute-force missing characters by extending the seed randomly
    
    :param seed: 
    :yield: Generated random seed one by one
    """
    return brute_seed(seed, random_choice=True)


def flip_seed(seed):
    """
    Tries to flip single characters, one by one
    
    :param seed: 
    :yield: Generated seeds one by one
    """

    # Check and retrieve for injection markers
    start_pos = 0
    end_pos = len(seed)
    if seed.count('*') == 0:
        marker_valid = True
    elif seed.count('*') != 2:
        marker_valid = False
    elif seed.rfind("*") - seed.find("*") <= 1:  # No character(s) in between markers
        marker_valid = False
    else:
        marker_valid = True
        start_pos = seed.find("*")
        end_pos = seed.rfind("*") - 1  # -1 as we are removing the markers next, shifting everything
        seed = seed.replace("*", "")

    # Check conditions
    if not marker_valid:
        print("ERROR: Your position markers are not set correctly! Start & end marker required.")
        print()
        sys.exit(-1)

    else:
        character_steps = end_pos - start_pos
        print("=> Trying to flip {} character(s) ({} possibilities)".format(
            character_steps,
            ((len(BRUTE_FORCE_CHARACTERS)-1) * character_steps)
        ))  # -1 possibilities, as the current character does not need to be checked
        print()

        # Give user time to read
        time.sleep(3)

        # Always yield input seed as first sample
        yield seed.replace("*", "")

        # Flip characters position by position
        for char in BRUTE_FORCE_CHARACTERS:

            count = 0
            for position in range(start_pos, end_pos):

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
    :yield: Generated seeds one by one 
    """

    # Check and retrieve for injection markers
    start_pos = 0
    end_pos = len(seed) + 1  # +1 as we also want to inject at the very end of the seed
    if seed.count('*') == 0:
        marker_valid = True
    elif seed.count('*') != 2:
        marker_valid = False
    elif seed.rfind("*") - seed.find("*") <= 1:  # No character(s) in between markers
        marker_valid = False
    else:
        marker_valid = True
        start_pos = seed.find("*")
        end_pos = seed.rfind("*")  # Though by removing wildcards in the next step and shifting characters, NOT -1 as we also want to inject at the very end of the seed
        seed = seed.replace("*", "")

    # Check conditions
    if not marker_valid:
        print("ERROR: Your position markers are not set correctly! Start & end marker required.")
        print()
        sys.exit(-1)

    else:
        character_positions = end_pos - start_pos
        print("=> Trying to inject characters at {} positions ({} possibilities)".format(
            character_positions,
            len(BRUTE_FORCE_CHARACTERS) * character_positions
        ))
        print()

        # Give user time to read
        time.sleep(3)

        # Always yield input seed as first sample
        yield seed.replace("*", "")

        # Inject characters position by position
        for char in BRUTE_FORCE_CHARACTERS:
            count = 0

            for position in range(start_pos, end_pos):  # +1 as we also want to inject at the end
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
    seed = seed.strip().upper()

    # Chop seed if too long
    if len(seed) > 81:
        print("WARNING: Seed longer than 81 characters. Discarding exceeding characters.")
        seed = seed[0:81]

    # Check if seed is valid
    if not set(seed) <= set(string.ascii_uppercase + '9*'):
        print("ERROR: Please configure a valid seed in the configuration section of the script.")
        print()
        return None

    # Check if injection markers are not more than two, as it would be an invalid configuration
    if seed.count("*") > 2:
        print("ERROR: Invalid amount of injection markers. Use one to define the brute-force")
        print("       position or two to mark the section of the seed to flip or inject at.")
        print()
        return None

    # Encode seed as required
    return seed


def print_configuration():
    print("CURRENT SETTINGS (change in script head):")

    if SEED:
        print("   - Offset seed configuration is '{}{}'".format(SEED[0:55], "..." if len(SEED) > 55 else ""))
    else:
        print("   - Offset seed configuration is an empty string")

    if "*" in SEED:
        print("   - Seed contains injection marker ('{}').".format("*" if SEED.count("*") == 1 else "**"))
    else:
        print("   - Seed does not contain an injection marker ('*'/'**')")

    print("   - {} addresses will be generated per seed{}".format(
        ADDRESSES_PER_SEED,
        " (set 0 to calculate checksums only)" if ADDRESSES_PER_SEED != 0 else ""
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
        "3": brute_random_seed,
        "4": flip_seed,
        "5": inject_seed
    }

    # Ask for mode
    print("WHICH OPERATION MODE DO YOU WANT TO EXECUTE?")
    print("  1. Just check the addresses of the given seed")
    print("  2. Systematically brute-force missing characters")
    print("  3. Randomly choose missing characters to brute-force seed")
    print("  4. Flip single characters to detect single typos")
    print("  5. Inject single characters at all positions to find a missing one")

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


def check_addresses(seed, seed_checksum=None):
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
    return seed, seed_checksum, results


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


def check_configuration():
    assert isinstance(SEED, str)
    assert isinstance(ABORT_AT_ADDRESS, str)
    assert isinstance(ABORT_AT_SEED_CHECKSUM, str)
    assert isinstance(BRUTE_FORCE_CHARACTERS, str)
    assert isinstance(SEED, str)
    assert isinstance(OUTPUT_FILE, str)
    assert isinstance(ADDRESSES_PER_SEED, int)
    assert isinstance(ADDRESS_SECURITY_LEVEL, int)
    assert isinstance(PARALLEL_PROCESSES, int)
    assert isinstance(STATUS_OUTPUT, bool)


def main():
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

    print("Please note that all found addresses will be written to an output file. If you")
    print("know any of your previously used addresses, you can search the output file for.")
    print()

    # Check configuration variables
    check_configuration()

    # Check python version
    if sys.version_info.major < 3:
        print("ERROR: Python3 required!")
        print()
        sys.exit(-1)

    if SEED is None:
        print("ERROR: No seed configured!")
        print()
        sys.exit(-1)

    # Check configuration

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


# ####################################################
# Start-up code
# ####################################################
if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        print("Execution interrupted by user.")
    finally:
        print()
        input("Please press >enter< to exit...")
