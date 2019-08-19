__author__ = "Zhenyi Tang"
__license__ = 'MIT License.'
__email__ = "zhenyit@outlook.com"
__version__ = "0.1"

'''
# This program analyses all the commits in a repository and
  finds commits that have removed a parameter from an existing method
# Input the path to the repository through command line arguments
# Output is a CSV file contain the methods' infomation
'''

import re
import csv
import sys
from pydriller import GitRepository

# Get methods' infomation from the commit
def get_func_info(diffs, mod_type):
    func_name, func_sig, func_modifier, func_mod_row, func_params = [], [], [], [], []
    for idx in range(len(diffs[mod_type])):
        method = re.search("^[\s]*(public |private ){1}.*\(*\)[\s]*{$", diffs[mod_type][idx][1])
        if (method):
            method_decl = diffs[mod_type][idx][1].lstrip()
            sig_left_idx = method_decl.find('(')
            sig_right_idx = method_decl.rfind(')')
            name_left_idx = method_decl.rfind(' ', 0, sig_left_idx)
            func_name.append( method_decl[ name_left_idx+1:sig_left_idx ] )
            func_sig.append( method_decl[ sig_left_idx:sig_right_idx+1] )
            func_modifier.append( method_decl[:sig_left_idx] )
            func_mod_row.append( diffs[mod_type][idx][0] )
            params = re.sub("\<[^<>]*\>","", method_decl[ sig_left_idx:sig_right_idx+1] )
            params = params.replace('(', '').replace(')', '').split(", ")
            while("" in params) : 
                params.remove("") 
            func_params.append(params)
    return func_name, func_sig, func_modifier, func_mod_row, func_params

# Due to overload, there may have some methods with the same name are modified in the same commit
def find_mod_func_pair(line_num, func_name, pair_func_name, pair_func_mod_row):
    diff = 99999
    pair_line = 0
    for idx,pair_func in enumerate(pair_func_name):
        if (pair_func == func_name):
            pair_line_num = pair_func_mod_row[idx]
            if (abs(pair_line_num-line_num)<diff):
                diff = abs(pair_line_num-line_num)
                pair_line = idx
    return pair_line

def main():
    print('Running...')
    # Report_data: a list uses to store the result data
    report_data = []
    # Get the repo path from command line arguments
    path = sys.argv[1]

    # Analyse the commit in the repo
    git_repo = GitRepository(path)
    commits = git_repo.get_list_commits()
    for i,commit in enumerate(commits):
        for j,mod in enumerate(commit.modifications):
            diffs = git_repo.parse_diff(mod.diff)
            # Get Method Info From Modification Detail
            add_func_name,add_func_sig,add_func_modifier,add_func_mod_row,add_func_params = get_func_info(diffs, 'added')
            del_func_name,del_func_sig,del_func_modifier,del_func_mod_row,del_func_params = get_func_info(diffs, 'deleted')
            # Find method that have removed a parameter
            # Consider the Overloading in Java method
            # 1 - added method number <= deleted method number
            for add_idx,add_func in enumerate(add_func_name):
                if add_func in del_func_name:
                    add_override_count = add_func_name.count(add_func)
                    del_override_count = del_func_name.count(add_func)
                    if (add_override_count <= del_override_count):
                        # Find the deleted method that near the added method 
                        line_num = add_func_mod_row[add_idx]
                        del_idx = find_mod_func_pair(line_num, add_func, del_func_name, del_func_mod_row)
                        if ( del_func_modifier[del_idx] == add_func_modifier[add_idx]):
                            if ( len(del_func_params[del_idx]) == len(add_func_params[add_idx])+1):
                                if (all(elem in del_func_params[del_idx]  for elem in add_func_params[add_idx])):
                                    new_sig = add_func + add_func_sig[add_idx]
                                    old_sig = add_func + del_func_sig[del_idx]  
                                    report_data.append([commit.hash,mod.filename,old_sig,new_sig])
            # 2 - added method number > deleted method number
            for del_idx,del_func in enumerate(del_func_name):
                if del_func in add_func_name:
                    add_override_count = add_func_name.count(del_func)
                    del_override_count = del_func_name.count(del_func)
                    if (add_override_count > del_override_count):
                        line_num = del_func_mod_row[del_idx]
                        add_idx = find_mod_func_pair(line_num, del_func, add_func_name, add_func_mod_row)
                        if ( del_func_modifier[del_idx] == add_func_modifier[add_idx]):
                            if ( len(del_func_params[del_idx]) == len(add_func_params[add_idx])+1):
                                if (all(elem in del_func_params[del_idx]  for elem in add_func_params[add_idx])):
                                    new_sig = del_func + add_func_sig[add_idx]
                                    old_sig = del_func + del_func_sig[del_idx]  
                                    report_data.append([commit.hash,mod.filename,old_sig,new_sig])
    # Save the report data to a CSV
    report_data = list(set(tuple(element) for element in report_data))
    header = ['Commit SHA', 'Java File', 'Old function signature', 'New function signature']
    report_data.insert(0,header)
    with open('report.csv', 'w', newline='') as resultFile:  
        wr = csv.writer(resultFile, dialect='excel')
        wr.writerows(report_data)
    print('Finish!')
main()