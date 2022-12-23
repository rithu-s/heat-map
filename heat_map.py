import difflib
from diff_helper_copy import get_diff, get_modified_lineNums, load_df_from_db, get_file_entries, print_modified_lines_by_row, printDiff
import pandas as pd
import sqlite3
from sqlite3 import Error
import numpy as np
from PIL import Image
import json
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.transforms

# follow progression of one line of code

a = 'console.log(data[0]);'
b = 'console.log(data[0].join(' '));'
seq=difflib.SequenceMatcher(a=a.lower(), b=b.lower())
# print(seq.ratio())


if __name__ == '__main__':
    database = "nodejsApp_pers.db" 
    # database = "wordle_polished.db" 
    df = load_df_from_db(database) # load database
    
    script_df = get_file_entries(df, "script.js") # getting only script.js file entries
    index_df = get_file_entries(df, "index.js") # getting only index.js file entries
    html_df = get_file_entries(df, "index.html") # getting only index.html file entries
    css_df = get_file_entries(df, "style.css") # getting only style.css file entries

    boilerplate_df = get_file_entries(df, "boilerplate.scss")

    file_df = script_df # code file name that we are collecting number of changes data on 
    entry_init = file_df['code_text'].iloc[len(file_df)-1] # getting last code_text entry out of all script.js file entries
    
    # line_init = entry_init.split("\n")[2] # getting the first line of code (can be applied to any line of code from the first entry by using a different array index) from the first code_text entry
    # comparing the first line of script.js code from the first entry of script.js to all lines of script.js from the second entry of script.js
    # whichever line comparison has the greatest seq.ratio is the matching line 
    
    num_changes = [0 for i in range(len(entry_init.split("\n")))] 
    all_lines = [0 for i in range(len(file_df))] 
    changes_made = [0 for i in range(len(file_df))] 
    all_last_entry = [0 for i in range(len(entry_init.split("\n")))] # array where each array value is each line of code from the last entry

    for line in range(len(entry_init.split("\n"))):
        line_init = entry_init.split("\n")[line]
        all_last_entry[line] = entry_init.split("\n")[line]
        for i in range(len(file_df)):
        # for i in range(1, 2):
            entry_following = file_df['code_text'].iloc[i] 
            all_seq = [0 for k in range(len(entry_following.splitlines()))] # initializing array of all sequence ratios 
            for j in range(len(entry_following.splitlines())):
                line_following = entry_following.split("\n")[j]
                seq=difflib.SequenceMatcher(a = line_init.lower(), b = line_following.lower()) # comparing the particular line from the first entry of script.js to every line in a different entry of script.js using Sequence Matcher
                curr_seq = seq.ratio() # getting the ratio of the . This is a value between 0.0 (no match at all) and 1.0 (identical match)
                all_seq[j] = curr_seq   # putting the ratio into an array
            matched_seqval = max(all_seq) # getting the maximum 
            matched_line = all_seq.index(max(all_seq)) # 
            if matched_seqval < 0.70:
                matched_line = -1
            else:
                if matched_seqval < 1.0:
                    changes_made[i] = 1
                else:
                    changes_made[i] = 0
            all_lines[i] = matched_line

            # print(matched_line)
        #print(all_lines)
        for ele in range(0, len(changes_made)):
            num_changes[line] = num_changes[line] + changes_made[ele] # adding up all the changes made 
        #print(changes_made)
    # print(num_changes)

    df_scriptjs_lastentry = pd.DataFrame(num_changes, columns=['Number of Changes'])
    # df_scriptjs_lastentry = pd.DataFrame(list(zip(num_changes, all_last_entry)), columns=['Number of Changes', 'Code Text'])
    df_scriptjs_lastentry.index += 1
    df_scriptjs_lastentry.index.name = 'Line Number'
    #print(df_scriptjs_lastentry)


    # converting dataframe to csv file 
    # df_scriptjs_lastentry.to_csv('nodejs.csv')

    # creating the heatmap from the df_scriptjs_lastentry dataframe
    fig, ax = plt.subplots(figsize=(7,9))
    cmap = sns.light_palette("red", as_cmap=True)
    heatmap = sns.heatmap(df_scriptjs_lastentry,  xticklabels=True, yticklabels=True,  annot= np.asarray(all_last_entry).reshape(len(df_scriptjs_lastentry),1), fmt = '', annot_kws = {"ha": 'left'}, cmap = cmap, ax=ax)
    for t in heatmap.texts:
        trans = t.get_transform()
        offs = matplotlib.transforms.ScaledTranslation(-0.48, 0, 
                        matplotlib.transforms.IdentityTransform())
        t.set_transform( offs + trans )
    # plt.savefig('heatmap.png')
    plt.show()

