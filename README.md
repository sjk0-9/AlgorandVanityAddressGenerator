# Algorand Vanity Address Generator

A simple vanity address generator for the Algorand blockchain.

Computes thousands of addresses every second and searches them for a desired set of starting characters.
On my 6 year old MacBook Pro I was able to compute 60-70k addresses a second.

For example:

```
$ python generate.py TEST output.json -n 5
Using 8 process(es) to search for 5 Algorand address(es) starting with TEST
Searched addresses:             0 (~0/sec)
Found! TESTRPP2VOXSYHT5CZNH6DNFVMXEBR7453BFOKOPRLYTAIDNESFQZZMLRQ
Searched addresses:       120,000 (~60,000/sec)
Found! TESTUUJESXXWADGAOGC5BKNHQUYUOM7GSGWKQWGRL7UMAJ2ZQ73JVA3H3U
Searched addresses:       462,000 (~64,500/sec)
Found! TESTMRP6P5WVHLI6Y6QE57FBGY3KNF36GMBWCFSNE5P7RHNYRQKYBFU76E
Searched addresses:     2,866,000 (~68,500/sec)
Found! TESTYQQE6PNYYZCARF5E2MM4IVRGN7B7YJQTUITCPOAHDKBB7P74HRQC5U
Searched addresses:     3,973,000 (~66,500/sec)
Found! TESTISIAY3G2HQOI5MSGUOMEEDUL45E5VF7DABGKAY3XO3E3VGEEDHQ4XY
```

With the output being a JSON file `output.json`

```json
[
  {
    "address": "TESTRPP2VOXSYHT5CZNH6DNFVMXEBR7453BFOKOPRLYTAIDNESFQZZMLRQ",
    "mnemonic": "word word word..."
  },
  {
    "address": "TESTUUJESXXWADGAOGC5BKNHQUYUOM7GSGWKQWGRL7UMAJ2ZQ73JVA3H3U",
    "mnemonic": "word word word..."
  },
  {
    "address": "TESTMRP6P5WVHLI6Y6QE57FBGY3KNF36GMBWCFSNE5P7RHNYRQKYBFU76E",
    "mnemonic": "word word word..."
  },
  {
    "address": "TESTYQQE6PNYYZCARF5E2MM4IVRGN7B7YJQTUITCPOAHDKBB7P74HRQC5U",
    "mnemonic": "word word word..."
  },
  {
    "address": "TESTISIAY3G2HQOI5MSGUOMEEDUL45E5VF7DABGKAY3XO3E3VGEEDHQ4XY",
    "mnemonic": "word word word..."
  }
]
```

## How to get started

> Note: I've only tested this on a single Intel MacBook Pro.
> If anyone wants to tell me how it works on other machines
> I'd really appreciate it.

Prerequisites:

* Git
* Python 3
* Some terminal

Open your terminal and clone this repository

```bash
git clone https://github.com/sjk0-9/AlgorandVanityAddressGenerator.git
```

Enter it, create the required local environment and install the required libraries:

```bash
cd AlgorandVanityAddressGenerator
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Now you're good to go.

If you ever want to leave the environment you can just call

```bash
disconnect
```

And to join the environment again (or if you open a new terminal), all you need this time is

```bash
source env/bin/activate
```

## Running the generator

To run the generator use the following command while in the correct environment

```bash
python generate.py [START] [output-file]
```

Replace [START] with the characters you want at the beginning of your address.
Replace [output-file] with the location you want to save the addresses and corresponding mnemonics (the 25 words to access your account).

There are a few optional parameters:

* `-n` or `--number` (e.g. `-n 5`):
  Stop after we've found this many addresses.
  If not provided, will continue until the user manually interrupts using `ctrl+c`.
* `-c` or `--cpu` (e.g. `-c 4` or `-c -2`):
  Use the given number of cpu cores to process.
  The more CPU cores the faster it will compute.
  If none is provided, will use all cores.
  If a negative number will provided, will use all but that number of cores
* `-h` or `--help`:
  Print out the instructions.

As it runs, it will display the total number of addresses checked and a rough estimate of how many addresses it's processing per second.
It will print the address as each is discovered.

It writes to the output file as it goes (occasionally producing temporary files to reduce risk of file corruption).

## How long does it take to find a given address?

It depends on the number of CPU cores you use and their speed.
The longer the START you're looking for is, the longer it takes to find.

The following is a rough calculation of the average number of addresses that need to be searched depending on the length of the address.

| Length | Addresses to search | Rough time on my laptop |
| ------:| -------------------:| ----------------------- |
|   1    |   16                |      < 1 seconds        |
|   2    |   512               |      < 1 seconds        |
|   3    |   16,384            |      < 1 seconds        |
|   4    |   524,288           |      ~ 9 seconds        |
|   5    |   16,777,216        |      ~ 4.5 minutes      |
|   6    |   536,870,912       |      ~ 2.5 hours        |
|   7    |   17 billion        |      ~ 80 hours         |
|   8    |   549 billion       |      ~ 106 days         |
|  54    |   948 quinvigintillion^ | ~ 38 octodecillion^ lifetimes of the universe |

^That's the name for these numbers according to https://decimal.info/, so that's what I'll go with.
## How trustworthy is this

Good question.
This code deals with private keys for algorand wallets.

For the sake of clarity surrounding something that is quite security critical, I have kept the code very simple, have avoided all but one external dependency (the official Algorand SDK) and gratuitously over-commented.
Every chunk of code has corresponding comments describing what it does with the idea being that even someone without much skill in python, or programming in general, can verify my intention.

What I have written is not malicious.
However I cannot guarantee the libraries I use,
the python runtime you use or anything on your system.
This is licensed under the MIT license as such:

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## I still don't trust you

Good.

If you want to keep the address, but not use the private key the generator made for you, you can re-key the address.

This can easily be performed via the "Rekey Account" option in the official Algorand wallet, though it only works if you have a ledger device you want to Rekey to.

If you have a little bit of developer know-how, you can also re-key using `goal` as described in the [Algorand developer docs](https://developer.algorand.org/docs/get-details/accounts/rekey/).

## Contact details

Twitter: [SJK](https://twitter.com/sjk0_9)

Tips: `TIPSHMFBDAOOKNCUO2GW6HFONVUWXCZKCGDNU3JINHQL2UWPIOOOARAVKE`
