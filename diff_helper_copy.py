'''The functions and code created in this file were written by John Allen'''

'''
This file is set up to be a "diff" helper file for analysing the differences between strings. 
It is probably best to edit and create helper functions here before integrating them into another file
'''
import sqlite3
from sqlite3 import Error
import numpy as np
from PIL import Image
import json
import difflib 
import pandas as pd

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def load_df_from_db(database):
    """ loads pandas dataframe from database filename string
    :param database: string of database filename
    :return: pandas dataframe of database
    """
    conn = create_connection(database)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM CodingEvents")
        rows = cur.fetchall()

        column_names = ["eventID", "videoID", "timed_url", "time","img_file","text_file", "notes", "code_text","coords"]
        
        df = pd.DataFrame(rows, columns=column_names).sort_values(by="time")
        return df

def get_file_entries(df, filename):
    '''returns the code entries in a database relevant to a given filename'''
    file_df = df[df.notes.str.startswith("code: "+filename)]
    return file_df.reindex()


def print_modified_lines_by_row(df):
    ''' This function prints the line numbers that have been modified between e'''
    for i in range(1, df.shape[0]):
            curr_row = df.iloc[i]
            prev_row = df.iloc[i-1]
            begin_code = prev_row.code_text
            end_code = curr_row.code_text
            diff = get_diff(begin_code,end_code)
            modified_lines = get_modified_lineNums(diff)
            print("Time:",curr_row.time, "| modified lines:", modified_lines)

def get_diff(before_code, after_code):
    """this function calculates the diff between two code strings, and returns a list of all the lines in the code,
      as well as indicators ('+', '-', '?') if the line has changed"""
    differ = difflib.Differ()
    diff = differ.compare(before_code.split('\n'), after_code.split('\n'))
    return list(diff)


def get_modified_lineNums(diff):
    """
    this function takes a diff object (returned by get_diff) and returns an array of the line numbers modified between the two files
    it's likely that you may modify this logic, or use this function structure to create similar functions you may find helpful
    """
    changed_lines = []
    i_offset = 0 # we do not want to add lines that start with - or ? to linecount
    for i in range(len(diff)):
        if diff[i].startswith("+"):
            changed_lines.append(i-i_offset) #should we do i+1? we will see
        elif diff[i].startswith('-'):
            if i < len(diff)-1:
                if not diff[i+1].startswith('+'): #we dont care about the 'deleted' lines that accompany changes -- we care about modified, deleted, or added lines precisely
                    changed_lines.append(i-i_offset)
                else:
                    i_offset += 1
        elif diff[i].startswith('?'):
            i_offset += 1
            continue # adding this if for potential changes later
    return changed_lines

def printDiff(diff):
  """prints a diff line by line"""
  for line in diff:
    print(line)

def get_all_code_files(df):
    """gets a list of all the unique code files in the dataframe"""
    df = load_df_from_db(database)
    code_df = df[df.notes.str.startswith("code:")]
    filenames = code_df.notes.str.split(" ").str[1].str.split(";").str[0].unique()
    return filenames


def get_code_states_on_output(df):
    """
    Take a dataframe and get the code state of each file every time the user tests the code (output produced)
    Returns: DataFrame with a column for Time and a column for each file in a database. Every row is the time and code state for each time the code is tested 
    """
    code_files = get_all_code_files(df)

    code_state = {x:"" for x in code_files} # set to empty
    output_indexes = df[df.notes.str.startswith("output:")].index

    all_rows = [] #going to append rows of data to this
    for i in output_indexes:
        df_slice = df.iloc[:i]
        row_data = [] # going to append rows to this
        row_data.append(df_slice.iloc[-1].time)
        for codeFile in code_files:
            file_slice = df_slice[df_slice.notes.str.startswith("code: "+codeFile+";")]
            if file_slice.shape[0] > 0: #file has occurred
                curr_code_state = file_slice.iloc[-1].code_text
                #print(codeFile, curr_code_state)
            else:
                curr_code_state = ""
            row_data.append(curr_code_state)
        all_rows.append(row_data)
    return pd.DataFrame(all_rows, columns= ["Time"]+code_files.tolist())

if __name__ == "__main__":
    database = "wordle_polished.db"
    df = load_df_from_db(database)
    output_df = get_code_states_on_output(df)
    print(output_df)

