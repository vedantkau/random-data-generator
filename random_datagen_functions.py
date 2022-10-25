import random
import pandas as pd
import datetime
import numpy as np
import time

letters_up = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
letters_low = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']


def exp_parser(exp):
    exp=exp.strip()

    random_chars_list = []
    esc_flag = False
    inside_list = False
    inside_list_start = 0
    inside_list_end = 0
    inside_col_braces = False
    inside_col_braces_start = 0
    inside_col_braces_end = 0
    inside_exp = False
    inside_exp_range = False
    inside_exp_range_start = 0
    inside_exp_range_end = 0
    outside_exp_start = 0
    outside_exp_end = 0
    i = -1

    while i < len(exp)-1:
        i += 1

        if exp[i] == "[" and esc_flag == False:
            inside_list = True
            inside_list_start = i + 1
            continue
        if exp[i] == "]" and inside_list == True:
            inside_list = False
            inside_list_end = i
            random_chars_list.append(exp[inside_list_start:inside_list_end].split(","))
            continue
        
        if exp[i] == "{" and esc_flag == False:
            inside_col_braces = True
            inside_col_braces_start = i + 1
            continue
        if exp[i] == "}" and inside_col_braces == True:
            inside_col_braces = False
            inside_col_braces_end = i
            random_chars_list.append([exp[inside_col_braces_start:inside_col_braces_end], ["col_exp"]]) 
            continue
 
        if inside_col_braces or inside_list:
            continue

        if exp[i] == "(" and esc_flag == False:
            inside_exp = True
            random_chars_list.append([])
            continue
        if exp[i] == ":" and inside_exp == True and esc_flag == False:
            inside_exp_range = True
            inside_exp_range_start = i + 1
            continue
        if exp[i] == ")" and inside_exp == True and inside_exp_range == True:
            inside_exp_range = False
            inside_exp = False
            inside_exp_range_end = i
            random_chars_list[-1].append(exp[inside_exp_range_start:inside_exp_range_end].split(","))
            continue
        if inside_exp and inside_exp_range:
            continue
        if exp[i] == "\\" and inside_exp == True and esc_flag == False:
            esc_flag = True
            continue
        if esc_flag == True and inside_exp == True:
            esc_flag = False
            if exp[i] == "u" and exp[i+1] == "l":
                random_chars_list[-1] = random_chars_list[-1] + letters_up
                i = i+1
                continue
            if exp[i] == "l" and exp[i+1] == "l":
                random_chars_list[-1] = random_chars_list[-1] + letters_low
                i = i+1
                continue
            if exp[i] == "l":
                random_chars_list[-1] = random_chars_list[-1] + letters_low + letters_up
                continue
            if exp[i] == "d":
                random_chars_list[-1] = random_chars_list[-1] + digits
                continue
            random_chars_list[-1].append(exp[i])
            continue
        if inside_exp == True and esc_flag == False:
            if exp[i] in "{}[]()\\\"\':":
                return []
            random_chars_list[-1].append(exp[i])
            continue
        
        if i == 0 or exp[i-1] in ")}]":
            outside_exp_start = i
        if i == len(exp)-1 or exp[i+1] in "({[":
            outside_exp_end = i + 1
            random_chars_list.append([exp[outside_exp_start:outside_exp_end]])

    if esc_flag or inside_list or inside_col_braces or inside_exp or inside_exp_range:
        return []
    return random_chars_list

# Test for exp_parser
# print(exp_parser("{cols_1}  \\ul:2,3)[a,b,c]ABC###"))
# print(exp_parser("    ABC "))
# print(exp_parser("[Abc,Xyz,Pqr](\':1)[C,Z,Q]"))
# print(exp_parser("(\\ul:2,3)(-)(\\d:3)"))
# print(exp_parser(" (._:2,3)"))


def random_word_gen(random_chars_list, no_of_rows=5):
    random_words_list = []

    for lists in random_chars_list:
        part_gen_list = []

        if len(lists)>=1 and isinstance(lists[-1], list) and lists[-1][0] == "col_exp":
            part_gen_list = lists[0]
            random_words_list.append(part_gen_list)
            continue

        if len(lists)>=1 and isinstance(lists[-1], list):
            choice_chars = lists[:-1]
            len_of_word = [int(lists[-1][0]), int(lists[-1][1])] if len(lists[-1]) == 2 else [int(lists[-1][0]), int(lists[-1][0])]

            for _ in range(no_of_rows):
                part_gen_list.append("".join(random.choices(choice_chars, k=random.randint(*len_of_word))))
       
        if len(lists)>=1 and not isinstance(lists[-1], list):
            for _ in range(no_of_rows):
                part_gen_list.append(random.choice(lists))
       
        random_words_list.append(part_gen_list)

    return random_words_list
           
# Test for random words
# print(random_word_gen(exp_parser("{cols_1}  \\ul:2,3)[a,b,c]ABC###")))
# print(random_word_gen(exp_parser("    ABC ")))
# print(random_word_gen(exp_parser("[Abc,Xyz,Pqr](\':1)[C,Z,Q]")))
# print(random_word_gen(exp_parser("(\\ul:2,3)(-)(\\d:3)")))
# print(random_word_gen(exp_parser("[a,b,c](._:2,3)")))
# print(random_word_gen(exp_parser("{colun_1##_##(\\ul:2,3)")))



def random_digits_gen(random_digits_range, random_gen_mode="list", random_gen_type="integer", no_of_rows=5):
    random_digits_list = []
    if random_gen_mode == "min_max" and len(random_digits_range) == 2:
        min_ele = int(random_digits_range[0])
        max_ele = int(random_digits_range[1])
        random_digits_list = min_ele + (max_ele-min_ele) * np.random.rand(no_of_rows)
    elif random_gen_mode == "range" and len(random_digits_range) == 2:
        start_ele = int(random_digits_range[0])
        increment = round(random_digits_range[1]) if random_gen_type == "integer" else float(random_digits_range[1])
        random_digits_list = np.arange(start_ele, start_ele+(increment*no_of_rows), step=increment)
    else:
        random_digits_list = np.random.choice(random_digits_range, size=no_of_rows)
        random_digits_list = list(map(float, random_digits_list))

    if random_gen_type == "integer":
        random_digits_list = list(map(int, random_digits_list))
   
    return pd.Series(random_digits_list)

# Test for random digits
# print(random_digits_gen([1,5], "min_max", "float", 5))
# print(random_digits_gen([1,5.5], "range", "float", 5))
# print(random_digits_gen([95,100], "min_max", "integer", 5))
# print(random_digits_gen([1,5.5], "range", "integer", 5))


def random_bool_gen(opts_list, no_of_rows=5):
    random_bool_list = np.random.choice(opts_list, size=no_of_rows)
    return pd.Series(random_bool_list)

# Test for random boolean
# print(random_bool_gen(['true', 'false']))
# print(random_bool_gen([0, 1]))
# print(random_bool_gen(['M', 'F']))


def random_dates_gen(random_dates_range, random_gen_mode="list", no_of_rows=5):
    random_dates_list = []
    if random_gen_mode == "min_max" and len(random_dates_range) == 2:
        min_date = random_dates_range[0]
        max_date = random_dates_range[1]
        date_diff = (max_date - min_date).days
        for _ in range(no_of_rows):
            random_dates_list.append(min_date+datetime.timedelta(random.randint(0, date_diff)))
    elif random_gen_mode == "range" and len(random_dates_range) == 2:
        start_date = random_dates_range[0]
        increment = round(random_dates_range[1])
        random_dates_list = np.arange(start_date, start_date+datetime.timedelta(no_of_rows*increment), step=increment)
    else:
        for _ in range(no_of_rows):
            try:
                select_date = datetime.datetime.strptime(random.choice(random_dates_range), "%Y-%m-%d")
            except ValueError:
                select_date = datetime.date(2022, 1, 1)
            random_dates_list.append(select_date)
   
    return pd.Series(random_dates_list)

# Test for random dates
# print(random_dates_gen(['2022-01-01', '2022-01-31'], "min_max", 5))
# print(random_dates_gen(['2022-01-01',5], "range", 5))
# print(random_dates_gen(['2022-01-01', '2022-01-12', '2022-01-15', '2022-01-26', '2022-01-31'], "list", 5))


def generate_data(column_details, no_of_rows=5):
    pd_data = {}
    for keys, cols in column_details.items():
        if cols[1] == "string" and cols[2] == "list":
            exp = "["+cols[3]["list"]+"]"
            pd_data[cols[0]] = random_word_gen(exp_parser(exp), no_of_rows)
        elif cols[1] == "string" and cols[2] == "expression":
            exp = cols[3]["expression"]
            pd_data[cols[0]] = random_word_gen(exp_parser(exp), no_of_rows)
        elif (cols[1] == "integer" or cols[1] == "decimal") and cols[2] == "list":
            digits_range = cols[3]["list"].split(",")
            pd_data[cols[0]] = random_digits_gen(digits_range, cols[2], cols[1], no_of_rows)
        elif (cols[1] == "integer" or cols[1] == "decimal") and cols[2] == "min_max":
            digits_range = [cols[3]["min"], cols[3]["max"]]
            pd_data[cols[0]] = random_digits_gen(digits_range, cols[2], cols[1], no_of_rows)
        elif (cols[1] == "integer" or cols[1] == "decimal") and cols[2] == "range":
            digits_range = [cols[3]["min"], cols[3]["increment"]]
            pd_data[cols[0]] = random_digits_gen(digits_range, cols[2], cols[1], no_of_rows)
        elif cols[1] == "date" and cols[2] == "list":
            dates_range = cols[3]["list"].split(",")
            pd_data[cols[0]] = random_dates_gen(dates_range, cols[2], no_of_rows)
        elif cols[1] == "date" and cols[2] == "min_max":
            dates_range = [cols[3]["datemin"], cols[3]["datemax"]]
            pd_data[cols[0]] = random_dates_gen(dates_range, cols[2], no_of_rows)
        elif cols[1] == "date" and cols[2] == "range":
            dates_range = [cols[3]["datemin"], cols[3]["increment"]]
            pd_data[cols[0]] = random_dates_gen(dates_range, cols[2], no_of_rows)
        elif cols[1] == "bool" and cols[2] == "list":
            opts_list = cols[3]["list"].split(",")[:2]
            pd_data[cols[0]] = random_bool_gen(opts_list, no_of_rows)

    for keys, data in pd_data.items():
        if isinstance(data, list):
            pd_series = pd.Series(data[0]) if isinstance(data[0], list) else pd_data.get(data[0], pd.Series('', index=range(no_of_rows),  dtype="str"))
            for d in data[1:]:
                pd_series = pd_series.combine(pd.Series(d) if isinstance(d, list) else pd_data.get(d, pd.Series('', index=range(no_of_rows),  dtype="str")), lambda str1,str2: str(str1)+str(str2), fill_value=None)
            pd_data[keys] = pd_series

    pd_df = pd.DataFrame(pd_data)
    for keys, cols in column_details.items():
        try:
            if (cols[1] == "integer" or cols[1] == "decimal") and cols[2] == "calculated":
                exp = cols[3]["calculated"]
                pd_df[cols[0]] = pd_df.eval(exp)
                if cols[1] == "integer":
                    pd_df[cols[0]] = pd_df[cols[0]].astype("int64")
                else:
                    pd_df[cols[0]] = pd_df[cols[0]].astype("float")
        except:
            return f"Calculated expression seems not correct for column '{cols[0]}'"

    return pd_df
    
         

# Test for generate data
# column_details = {'col1': ['column_1', 'string', 'list', {'list': 'Abc,Xyz,Pqr', 'expression': '', 'min': 0.0, 'max': 0.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 0.0}], 'col2': ['column_2', 'string', 'expression', {'list': '', 'expression': '(\\ul:2,3)(-)(\\d:3)', 'min': 0.0, 'max': 0.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 0.0}], 'col3': ['column_3', 'integer', 'min_max', {'list': '', 'expression': '', 'min': 0.0, 'max': 20.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 0.0}], 'col4': ['column_4', 'integer', 'range', {'list': '', 'expression': '', 'min': 0.0, 'max': 0.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 1.0}], 'col5': ['column_5', 'decimal', 'min_max', {'list': '', 'expression': '', 'min': 0.0, 'max': 30.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 0.0}], 'col6': ['column_6', 'decimal', 'range', {'list': '', 'expression': '', 'min': 0.0, 'max': 0.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 0.5}], 'col7': ['column_7', 'date', 'min_max', {'list': '', 'expression': '', 'min': 0.0, 'max': 0.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 31), 'increment': 0.0}], 'col8': ['column_8', 'date', 'range', {'list': '', 'expression': '', 'min': 0.0, 'max': 0.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 1.0}]}
# column_details = {'col1': ['col1', 'decimal', 'min_max', {'list': '', 'expression': '', 'min': 10.0, 'max': 20.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 0.0, 'calculated': ''}], 'col2': ['col2', 'decimal', 'range', {'list': '', 'expression': '', 'min': 0.0, 'max': 0.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 10.0, 'calculated': ''}], 'col3': ['col3', 'decimal', 'calculated', {'list': '', 'expression': '', 'min': 0.0, 'max': 0.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 0.0, 'calculated': 'False'}]}
# time0 = time.time()
# print(generate_data(column_details))
# time1 = time.time()
# print(time1-time0)