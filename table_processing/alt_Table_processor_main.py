from PyPDF2 import PdfReader
import logging
import pandas as pd
import os
import math
import statistics

logging.basicConfig(filename='alt_table_detection.log', filemode='a', datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO, format='[%(asctime)s][%(levelname)s] %(message)s\n')
logging.getLogger().addHandler(logging.StreamHandler())

def Average(lst):
    return math.ceil(sum(lst) / len(lst)) # int(statistics.median(lst))

def get_tbl(txt):
    dir = os.path.dirname(txt)
    df = ""
    with open(txt, 'r') as r:
        for line in r:
            if len(line.strip()) > 5:
                df+= line
    tbls = df.strip().split("Tab")
    for count, value in enumerate(tbls):
        output_txt = dir + '\output' + str(count) + '.txt'
        output_xl = dir + '\output' + str(count) + '.xlsx'
        with open(output_txt, "w") as txt_file:
            txt_file.write(value.strip())
            txt_file.close()
        with open(output_txt, "r") as txt_file:
            num_words_total = []
            num_spaces_total = []
            for line in txt_file:
                print(line.split())
                num_spaces = len(line.split())
                num_words = 0
                for letter in line:
                    num_words += 1
                num_words_total.append(num_words)
                num_spaces_total.append(num_spaces)
            txt_file.close()
        
        num_col = Average(num_spaces_total) 
        col_width = math.ceil((Average(num_words_total))/num_col)
        print(num_col)

        col_specs = []
        start = 0
        end = col_width
        for i in range(num_col):
            tup = (start, end)
            col_specs.append(tup)
            start += col_width
            end += col_width
        tbl = pd.read_fwf(output_txt, colspecs=col_specs, skipfooter=1)
        tbl.to_excel(output_xl, index=None)

    # read_file = pd.read_csv(txt, encoding= 'unicode_escape')


    # read_file.to_excel(xl, index=None)

get_tbl('C:\\Users\\EFUNG\\Downloads\\PMRA TABLES_Redacted (provided by Martin L).txt')
# get_tbl('C:\\Users\\EFUNG\\Downloads\\PMRA Table 7.txt')


