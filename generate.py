# Each of these imports, besides the AlgoSDK are part of the Python Standard Library
import argparse                         # Handles the command line inputs
from multiprocessing import \
    Process, Queue, Value, cpu_count    # For running on multiple CPU cores
from queue import Empty                 # For helping read from the queue
import itertools                        # To help us count the number of addresses we're generating
import os                               # For managing the files we are writing to
import json                             # For compiling the JSON we're writing
import re                               # To check that the requested value is possible
from algosdk import account, mnemonic   # For generating the accounts

def main(**kwargs):
    """
    The core process of the generator.
    Spins up each subprocess (which does the actual computational work).
    And retrieves and saves valid addresses while updating the commandline.
    """
    start = kwargs['start']
    output = kwargs['output']
    number = kwargs['number']
    cpu = kwargs['cpu']

    # Not all letters are valid. An Algorand Address is made up of upper case
    # letters A-Z and the numbers 2-7. 0 and 1 are ommited because they look too
    # similar to O and I. 8 and 9 are uneccessary because it's a 32 bit encoding
    # so we only need 32 possible characters.
    # If we've got a character that doesn't match, lets fail before we start
    # looking, otherwise we'll be here searching forever.
    if re.match('^[A-Z2-7]+$', start) is None:
        raise ValueError('Invalid start. Can only contain upper case letters A-Z and numbers 2-7.')

    # Each CPU core will communicate back to the main process via this queue
    queue = Queue()
    # The counter will be shared by each subprocess so we can tell how fast
    # We're generating accounts
    counter = Value('i', 0)

    # Parse number of CPU cores to use based on user input or default values
    if cpu < 0:
        cpu = max(get_max_cpus() + cpu, 1)
    if cpu == 0:
        raise ValueError('Cannot have CPU set to 0')

    # Output to let the user know what we're doing
    if number:
        print('Using {} process(es) to search for {} Algorand address(es) starting with {}'.format(cpu, number, start))
    else:
        print('Using {} process(es) to search for Algorand addresses starting with {}'.format(cpu, start))

    # For each core we can use, start a new python Process, which will run the
    # code to generate and check addresses in the subprocess method below.
    processes = []
    for _ in range(cpu):
        p = Process(target=subprocess, args=(start, queue, counter))
        p.start()
        processes.append(p)

    number_found = 0
    previous_counted = 0
    num_counted = 0
    # Now the processes are underway, keep checking if we've found anything in
    # the queue
    try:
        while True:
            # Compute and print out the number of addresses we've found and
            # the rate we're progressing
            previous_counted = num_counted
            num_counted = counter.value
            rate = (num_counted-previous_counted)//2
            print('\rSearched addresses: {:13,} (~{:,}/sec)'.format(num_counted, rate), end="")
            try:
                # Check the queue for 2 seconds at a time, if we don't find anything
                # start the loop again so we can refresh our counter display
                item = queue.get(timeout=2)
            except Empty:
                continue

            # If we've made it here, it means we've found a matching address!
            # print the address and add the full details to the JSON file
            print()
            print('Found!', item['address'])
            write_to_json(item, output)

            number_found += 1
            # If we have a limit on the number we want to return, and we've reached
            # that limit, break out of this loop
            if number_found == number:
                break
    except KeyboardInterrupt:
        # In the case that we try to stop early by sending an interrupt, we should
        # still tidy up, so catch the exception and continue to the cleanup
        pass

    # Stop and cleanup all of the previous processes
    for p in processes:
        p.terminate()
        p.join()

def subprocess(start, queue, counter):
    """
    Each instance of subprocess will continuously generate random accounts
    and check if they meet our criteria.
    """
    for i in itertools.count():
        try:
            # Generates a new random private key and the corresponding address
            private_key, address = account.generate_account()
            # If the start of the random address matches the phrase we're searching
            # for we should return it.
            if address.startswith(start):
                # Produce the mnemonic (key phrase) and send it back to the main
                # process along with the address
                queue.put({
                    'address': address,
                    'mnemonic': mnemonic.from_private_key(private_key),
                })

            # Increment the counter every 1000 cycles
            # (Any more regularly would cause needless delay)
            if (i % 1000 == 0):
                counter.value += 1000
        except KeyboardInterrupt:
            # Ignore interrupts when closing, because we are handling them and
            # the requisite cleanup in the main process
            pass

def write_to_json(item, output):
    """
    Append a given item to an array in a JSON file.
    If need be, creates the file.
    Has some fancy stuff in there to reduce risk of file corruption in event of
    a crash or interrupt.
    """
    try:
        # If the file doesn't exist, just fill it with the first item
        with open(output, 'x') as f:
            json.dump([item], f, indent=2)
    except FileExistsError:
        # If the file does exist retrieve the list of everything we've found
        # so far
        with open(output, 'r') as f:
            all_items = json.load(f)
        # Add the new item to that list
        all_items.append(item)

        # Write the new list to a temporarty file so we don't corrupt the
        # original in the event of a crash or interrupt
        directory, file = os.path.split(output)
        temp_output = os.path.join(directory, 'temp-{}'.format(file))
        with open(temp_output, 'w') as f:
            json.dump(all_items, f, indent=2)

        # Replace the original file with its updated version
        os.replace(temp_output, output)

def get_max_cpus():
    """
    Returns the maximum number of CPU cores available for us to use
    """
    try:
        return cpu_count()
    except NotImplementedError:
        # If we can't figure out how many CPU cores we have... well there's got
        # to be at least 1 right?
        return 1

# Run the following code only when we directly call this script from commandline
if __name__ == "__main__":
    # The following is what parses the commandline input to determine how to run
    # the remainder of the script
    parser = argparse.ArgumentParser(
        description="""
        Produces valid Algorand Addresses which begin with a set series of characters.
        Prints the addresses and writes the addresses and mnemonics in the JSON file format."""
        )
    parser.add_argument(
        'start',
        type=str,
        help="The characters you want at the start of your address."
        )
    parser.add_argument(
        'output',
        help="The file in which to write the mnemonics. If the file already exists, will attempt to read and append to it."
        )
    parser.add_argument(
        '--number',
        '-n',
        type=int,
        help="The number of addresses to produce. If not provided, will continue until manually stopped by the user."
        )
    parser.add_argument(
        '--cpu',
        '-c',
        default=get_max_cpus(),
        type=int,
        help="The number of CPU cores to use. Default is maximum available. Use negative numbers to define number of CPU cores not to use."
        )

    args = parser.parse_args()
    try:
        main(**vars(args))
    except Exception as e:
        print(e)
