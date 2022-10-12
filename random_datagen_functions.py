import random
import pandas as pd
import datetime
import time

letters_up = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
letters_low = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']


def exp_parser(exp):
    exp=exp.strip()
    random_chars_list = []
    esc_flag = False
    exp_end_flag = False
    exp_end_pos = 0
    list_start_pos = 0
    list_end_pos = 0
    i = -1

    while i < len(exp)-1:
        i += 1

        if exp[i] == "[" and esc_flag == False:
            list_start_pos = i+1
            while exp[i] != "]" or exp[i-1] == "\\":
                i += 1
            list_end_pos = i
            random_chars_list.append(exp[list_start_pos:list_end_pos].split(","))
            continue

        if exp[i] == "(" and esc_flag == False:
            random_chars_list.append([])
            continue
        if exp[i] == ")" and esc_flag == False:
            if exp_end_flag:
                random_len_exp = exp[exp_end_pos:i].split(",")
                random_chars_list[-1].append(random_len_exp)
                exp_end_flag = False
            else:
                random_chars_list[-1].append(['1'])
            continue

        if exp[i] == ":" and esc_flag == False:
            exp_end_pos = i+1
            exp_end_flag = True
            continue
        if exp_end_flag == False:
            if exp[i] == "\\":
                esc_flag = True
                continue
            if esc_flag == True:
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
            if esc_flag == False:
                random_chars_list[-1].append(exp[i])
   
    return random_chars_list


def random_word_gen(random_chars_list, no_of_rows=5):
    random_words_list = []
    for lists in random_chars_list:
        part_gen_list = []

        if len(lists)>=1 and isinstance(lists[-1], list):
            choice_chars = lists[:-1]
            len_of_word = [int(lists[-1][0]), int(lists[-1][1])] if len(lists[-1]) == 2 else [int(lists[-1][0]), int(lists[-1][0])]

            for _ in range(no_of_rows):
                part_gen_list.append("".join(random.choices(choice_chars, k=random.randint(*len_of_word))))
       
        if len(lists)>=1 and not isinstance(lists[-1], list):
            for _ in range(no_of_rows):
                part_gen_list.append(random.choice(lists))
       
        random_words_list.append(part_gen_list)
   
    random_words_series = pd.Series(random_words_list[0])
    for series in random_words_list[1:]:
        random_words_series = random_words_series.combine(pd.Series(series), lambda str1, str2:str1+str2)

    return random_words_series
           
# Test for random words
# exp1 = "(\\ul:2,3)(-)(\\d:3)"
# exp2 = "[Abc,Xyz,Pqr](\')[C,Z,Q]"
# exp3 = "    ABC "
# print(exp_parser(exp3))
# print(random_word_gen(exp_parser(exp3), 5))
# print(exp_parser(" (._:2,3)"))


def random_digits_gen(random_digits_range, random_gen_mode="list", random_gen_type="integer", no_of_rows=5):
    random_digits_list = []
    if random_gen_mode == "min_max" and len(random_digits_range) == 2:
        min_ele = int(random_digits_range[0])
        max_ele = int(random_digits_range[1])
        for _ in range(no_of_rows):
            random_digits_list.append(round(random.uniform(min_ele, max_ele), 3))
    elif random_gen_mode == "range" and len(random_digits_range) == 2:
        start_ele = int(random_digits_range[0])
        increment = round(random_digits_range[1]) if random_gen_type == "integer" else float(random_digits_range[1])
        for _ in range(no_of_rows):
            random_digits_list.append(start_ele)
            start_ele += increment
    else:
        for _ in range(no_of_rows):
            random_digits_list.append(random.choice(random_digits_range))

    if random_gen_type == "integer":
        random_digits_list = list(map(int, random_digits_list))
   
    return pd.Series(random_digits_list)

# Test for random digits
# print(random_digits_gen([1,5], "min_max", "float", 5))
# print(random_digits_gen([1,5.5], "range", "float", 5))
# print(random_digits_gen([1,5.5], "min_max", "int", 5))
# print(random_digits_gen([1,5.5], "range", "int", 5))


def random_bool_gen(opts_list, no_of_rows=5):
    random_bool_list = []
    for _ in range(no_of_rows):
        random_bool_list.append(random.choice(opts_list))
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
        for _ in range(no_of_rows):
            random_dates_list.append(start_date)
            start_date = start_date + datetime.timedelta(increment)
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


def generate_data(column_details, no_of_rows=100):
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
    
    return pd.DataFrame(pd_data)     

# Test for generate data
# column_details = {'col1': ['column_1', 'string', 'list', {'list': 'Abc,Xyz,Pqr', 'expression': '', 'min': 0.0, 'max': 0.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 0.0}], 'col2': ['column_2', 'string', 'expression', {'list': '', 'expression': '(\\ul:2,3)(-)(\\d:3)', 'min': 0.0, 'max': 0.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 0.0}], 'col3': ['column_3', 'integer', 'min_max', {'list': '', 'expression': '', 'min': 0.0, 'max': 20.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 0.0}], 'col4': ['column_4', 'integer', 'range', {'list': '', 'expression': '', 'min': 0.0, 'max': 0.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 1.0}], 'col5': ['column_5', 'decimal', 'min_max', {'list': '', 'expression': '', 'min': 0.0, 'max': 30.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 0.0}], 'col6': ['column_6', 'decimal', 'range', {'list': '', 'expression': '', 'min': 0.0, 'max': 0.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 0.5}], 'col7': ['column_7', 'date', 'min_max', {'list': '', 'expression': '', 'min': 0.0, 'max': 0.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 31), 'increment': 0.0}], 'col8': ['column_8', 'date', 'range', {'list': '', 'expression': '', 'min': 0.0, 'max': 0.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 1.0}]}
# time0 = time.time()
# print(generate_data(column_details))
# time1 = time.time()
# print(time1-time0)