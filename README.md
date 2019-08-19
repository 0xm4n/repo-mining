# Repo Mining
This program analyses all the commits in a repository and finds commits that have removed a parameter from an existing method. 

## Overview
To implement this functionality I do the following steps:
 1. Use PyDriller to extract commits and modifications information from a Git repository.
 2. Use regular expression to search all the modified methods in each commit.
 3. Consider the overload method in Java, and find those method have removed a parameter.
 4. Save the result to a CSV file.
 
Running this script on the following repositories and the result CSV file is in the result folder:
+ slf4j
+ mockito
+ jackson-databind

## Requirements
+ Python 3
+ Git
+ PyDriller

Installing PyDriller is easily done using pip. Assuming it is installed, run the following from the command-line:
```bash
$ pip install pydriller
```
## Quick Start
To mine a repo you can run this script using:
```bash
python3 repo_mining.py <path to repository>
```
