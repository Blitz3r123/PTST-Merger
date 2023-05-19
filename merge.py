# 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

import os 
import sys
import json
import shutil

from pprint import pprint

from rich.console import Console
from rich.table import Table

console = Console()

# Take in 3 arguments:
# 1. The path to the first folder containing tests
# 2. The path to the second folder containing tests
# 3. The path to the folder to store the merged tests
if len(sys.argv) != 4:
    print("Usage: python3 merge.py <run_1_dir> <run_2_dir> <merged_dir>")
    sys.exit(1)
    
# Get the paths to the folders
run1dir = sys.argv[1]
run2dir = sys.argv[2]
mergedir = sys.argv[3]

# Verify that the first two folders exists
if not os.path.isdir(run1dir):
    console.print(f"Error: {run1dir} is not a directory", style="bold red")
    sys.exit(1)
if not os.path.isdir(run2dir):
    console.print(f"Error: {run2dir} is not a directory", style="bold red")
    sys.exit(1)

# Verify that the first two folders have contents
if len(os.listdir(run1dir)) == 0:
    console.print(f"Error: {run1dir} is empty", style="bold red")
    sys.exit(1)
if len(os.listdir(run2dir)) == 0:
    console.print(f"Error: {run2dir} is empty", style="bold red")
    sys.exit(1)
    
def get_test_info(test):
    # Get folder of test
    test_folder = os.path.dirname(test)
    
    all_test_info = []
    
    # Get json files in test folder
    json_files = [os.path.join(test_folder, file) for file in os.listdir(test_folder) if file.endswith(".json")]
    
    if len(json_files) > 1:
        for file in json_files:
            with open(file, "r") as f:
                all_test_info.append(json.load(f))
        
        # Flatten the list of lists
        all_test_info = [item for sublist in all_test_info for item in sublist]
    else:
        with open(json_files[0], "r") as f:
            all_test_info = json.load(f)
    
    testname = os.path.basename(test)
    
    test_info = [item for item in all_test_info if item["test"].lower() == testname.lower()]
    
    assert(len(test_info) == 1)
    
    return test_info[0]
    
def create_table(list1, list2, title1, title2, transfer_history):
    table = Table(show_header=True, show_lines=True)
    table.add_column(title1)
    table.add_column(title2)

    # trim and lower all items in list1 and list2
    list1 = [x.strip().lower() for x in list1]
    list2 = [x.strip().lower() for x in list2]

    # Get intersection of list1 and list2
    intersection = list(set(list1) & set(list2))
    # Get items in list1 but not in list2
    list1_only = list(set(list1) - set(list2))
    # Get items in list2 but not in list1
    list2_only = list(set(list2) - set(list1))
    
    # Add the items in the intersection to the table
    for item in intersection:
        # Check if the item was transferred
        matching_history_items = [x for x in transfer_history if item.lower() in x["test"].lower()]
        
        if len(matching_history_items) == 0:
            table.add_row(item, item)
        else:
            matching_history_item = matching_history_items[0]
            parent_dir = os.path.dirname(matching_history_item['from'])

            if parent_dir == os.path.basename(title1):
                table.add_row(f"[bold blue]{item}[/bold blue]", item)
            else:
                table.add_row(item, f"[bold blue]{item}[/bold blue]")
    
    # Add the items in list1_only to the table
    for item in list1_only:
        table.add_row(item, "")
    
    # Add the items in list2_only to the table
    for item in list2_only:
        table.add_row("", item)

    return table
    
def create_merged_folder_if_not_exists(mergedir):
    if not os.path.isdir(mergedir):
        os.mkdir(mergedir)

# Get all tests from the folders
run1tests = [x for x in os.listdir(run1dir) if os.path.isdir( os.path.join(run1dir, x) )]
run2tests = [x for x in os.listdir(run2dir) if os.path.isdir( os.path.join(run2dir, x) )]

# Get the test statuses from the json files

run1jsons = [file for file in os.listdir(run1dir) if file.endswith(".json")]
if len(run1jsons) == 0:
    console.print(f"Error: {run1dir} does not contain any json files", style="bold red")
    sys.exit(1)

run2jsons = [file for file in os.listdir(run2dir) if file.endswith(".json")]
if len(run2jsons) == 0:
    console.print(f"Error: {run2dir} does not contain any json files", style="bold red")
    sys.exit(1)    


# Merge the json files if there is more than 1
run1statuses = []
if len(run1jsons) > 1:
    for file in run1jsons:
        with open(os.path.join(run1dir, file), "r") as f:
            run1statuses.append(json.load(f))
     
    # Flatten the list of lists
    run1statuses = [item for sublist in run1statuses for item in sublist]
else:
    with open(os.path.join(run1dir, run1jsons[0]), "r") as f:
        run1statuses = json.load(f)
        
# Merge the json files if there is more than 1
run2statuses = []
if len(run1jsons) > 1:
    for file in run1jsons:
        with open(os.path.join(run1dir, file), "r") as f:
            run2statuses.append(json.load(f))
     
    # Flatten the list of lists
    run2statuses = [item for sublist in run2statuses for item in sublist]
else:
    with open(os.path.join(run1dir, run1jsons[0]), "r") as f:
        run2statuses = json.load(f)

# Get the intersection of the tests
tests = list(set(run1tests) & set(run2tests))

unmerged_count = 0

new_test_info = []

transfer_history = []
for test in tests:
    chosendir = None
    
    # Get the status of the test from both runs
    run1_info = [x for x in run1statuses if x["test"] == test][0]
    run2_info = [x for x in run2statuses if x["test"] == test][0]
    
    run1status = run1_info["status"]
    run2status = run2_info["status"]
    
    run1status = "punctual" if run1status in ["punctual", "success", "pass"] else "prolonged"
    run2status = "punctual" if run2status in ["punctual", "success", "pass"] else "prolonged"
    
    if run1status == "punctual" and run2status == "punctual":
        if run1_info['end_time'] > run2_info['end_time']:
            chosendir = os.path.join(run1dir, test)
        else:
            chosendir = os.path.join(run2dir, test)
    
    elif run1status == "prolonged" and run2status == "prolonged":
        shutil.copytree(os.path.join(run1dir, test), os.path.join(mergedir, test))
        new_test_info.append(get_test_info( os.path.join(run1dir, test) ))
        unmerged_count += 1
        continue
    
    else:
        if run1status == "punctual":
            chosendir = os.path.join(run1dir, test)
        else:        
            chosendir = os.path.join(run2dir, test)
            
    create_merged_folder_if_not_exists(mergedir)
    # # Copy the test to the merged folder
    shutil.copytree(chosendir, os.path.join(mergedir, test))
    new_test_info.append(get_test_info(chosendir))

    transfer_history.append({
        "test": test,
        "from": chosendir,
        "to": os.path.join(mergedir, test)
    })
    
# Create list of tests that are not in the intersection
non_intersection_tests = list(set(run1tests) ^ set(run2tests))
for test in non_intersection_tests:
    shutil.copytree(os.path.join(run1dir, test), os.path.join(mergedir, test))
    new_test_info.append(get_test_info( os.path.join(run1dir, test) ))
    
# Write the new test info to a json file
with open(os.path.join(mergedir, "merged_progress.json"), "w") as f:
    json.dump(new_test_info, f, indent=4)
    
assert(len(new_test_info) == ( len(transfer_history) + len(non_intersection_tests) + unmerged_count ))
    
console.print(f"Merged {len(transfer_history)} tests.", style="bold green")
console.print(f"Copied over {len(non_intersection_tests) + unmerged_count} tests.", style="bold green")
console.print(create_table(run1tests, run2tests, run1dir, run2dir, transfer_history), style="bold white")