# Merger

Script to let you merge two runs of the same campaign.

## How to use
```shell
python merge.py <run_1_dir> <run_2_dir>
```

## How does it work
- 1. Make a unique lists of all tests from both directories.
- 2. For each test:
    - 2.1. Find the test folder and test config item for both dirs.
    - 2.2. Pick the most recent punctual test folder and its config.
    - 2.3. Place this chosen test into a new dir called "merged" or something.