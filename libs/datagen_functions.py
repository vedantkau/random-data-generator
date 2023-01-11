import pandas as pd
import numpy as np
import random
import datetime
import math
import itertools
from faker import Faker
from faker.exceptions import UniquenessException


letters_up = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
letters_low = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
fake = Faker()

def list_search(ll, ul, digits_range):
    ll_index = 0
    ul_index = len(digits_range)
    if ((not pd.isnull(ll)) and ll > digits_range[-1]) or ((not pd.isnull(ul)) and ul < digits_range[0]):
        return []
    for i, ele in enumerate(digits_range):
        if (not pd.isnull(ll)) and ll_index == 0 and ele>=ll:
            ll_index = i
        if (not pd.isnull(ul)) and ul_index == len(digits_range) and ul<ele:
            ul_index = i
    return digits_range[ll_index:ul_index]


def exp_parser(exp):
    exp=exp.strip()

    random_chars_list = []
    esc_flag = False
    inside_list = False
    inside_col_braces = False
    inside_col_braces_start = 0
    inside_col_braces_end = 0
    inside_exp = False
    inside_exp_range = False
    inside_exp_range_start = 0
    inside_exp_range_end = 0
    outside_exp = False
    i = -1

    while i < len(exp)-1:
        i += 1

        if exp[i] == "[" and esc_flag == False and not (inside_list and inside_exp and inside_col_braces):
            inside_list = True
            random_chars_list.append([""])
            continue
        if exp[i] == "]" and inside_list == True and esc_flag == False:
            inside_list = False
            random_chars_list[-1] = random_chars_list[-1][0].split("__,__")
            continue
        if exp[i] == "\\" and inside_list == True and esc_flag == False:
            esc_flag = True
            continue
        if inside_list == True:
            if exp[i] == "," and esc_flag == False:
                random_chars_list[-1][0] += "__,__"
                continue
            esc_flag = False
            random_chars_list[-1][0] += exp[i]
            continue


        if exp[i] == "{" and esc_flag == False and not (inside_list and inside_exp and inside_col_braces):
            inside_col_braces = True
            inside_col_braces_start = i + 1
            continue
        if exp[i] == "}" and inside_col_braces == True and exp[i-1] != "\\":
            inside_col_braces = False
            inside_col_braces_end = i
            random_chars_list.append([exp[inside_col_braces_start:inside_col_braces_end], ["col_exp"]]) 
            continue
 
        if inside_col_braces or inside_list:
            continue

        if exp[i] == "(" and esc_flag == False and not (inside_list and inside_exp and inside_col_braces):
            inside_exp = True
            random_chars_list.append([])
            continue
        if exp[i] == ":" and esc_flag == False and inside_exp == True:
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

        if i == 0 or (exp[i-1] in ")}]" and not (inside_col_braces and inside_exp and inside_list)):
            outside_exp = True
            random_chars_list.append([''])
        if exp[i] == "\\" and outside_exp == True and esc_flag == False:
            esc_flag = True
            continue
        if (exp[i] in "({[" and esc_flag == False and outside_exp == True):
            outside_exp = False
            continue
        if outside_exp == True:
            esc_flag = False
            random_chars_list[-1][-1] += exp[i]
            continue

    if esc_flag or inside_list or inside_col_braces or inside_exp or inside_exp_range:
        return []
    return random_chars_list

# Test for exp_parser
# print(exp_parser("{cols_1}  \\ul:2,3)[a,b,c]ABC###"))
# print(exp_parser("    ABC "))
# print(exp_parser("[Abc,Xyz,Pqr](\':1)[C,Z,Q]"))
# print(exp_parser("(\\ul:2,3)(-)(\\d:3)"))
# print(exp_parser(" (._:2,3)"))
# print(exp_parser("abc\\("))
# print(exp_parser("{acd{abc}d}"))
# print(exp_parser("[abc,xyz\\{}]{col1}"))
# print(exp_parser("[abc,xyz\\{}\\,pqrs,lmn]"))


def random_word_gen(random_chars_list, no_of_rows=5, constraint_type = "no constraint"):
    random_words_list = []
    for lists in random_chars_list:
        part_gen_list = []

        if len(lists)>=1 and isinstance(lists[-1], list) and lists[-1][0] == "col_exp":
            part_gen_list = lists[0]
            random_words_list.append(part_gen_list)
            continue

        if len(lists)>=1 and isinstance(lists[-1], list):
            choice_chars = lists[:-1]
            if constraint_type == "unique":
                len_of_word = [int(lists[-1][0]), int(lists[-1][1])+1] if len(lists[-1]) == 2 else [int(lists[-1][0]), int(lists[-1][0])+1]
                word_permutations = []
                for i in range(*len_of_word):
                    word_permutations.extend(list(itertools.product(choice_chars, repeat=i)))
                part_gen_list = random.sample(word_permutations, k=min(len(word_permutations), no_of_rows))
                for i in range(len(part_gen_list)):
                    part_gen_list[i] = "".join(part_gen_list[i])
            else:
                len_of_word = [int(lists[-1][0]), int(lists[-1][1])] if len(lists[-1]) == 2 else [int(lists[-1][0]), int(lists[-1][0])]
                for _ in range(no_of_rows):
                    part_gen_list.append("".join(random.choices(choice_chars, k=random.randint(*len_of_word))))
       
        if len(lists)>=1 and not isinstance(lists[-1], list):
            if constraint_type == "unique":
                part_gen_list = random.sample(lists, k=min(len(lists), no_of_rows))
            else:
                for _ in range(no_of_rows):
                    part_gen_list.append(random.choice(lists))
        
        random_words_list.append(part_gen_list)

    if constraint_type == "unique" and len(random_words_list) > 1:
        continue_flag = False
        indices_to_delete = []
        for i in range(len(random_words_list)):
            if continue_flag:
                continue_flag = False
                continue
            if isinstance(random_words_list[i], list) and len(random_words_list[i]) < no_of_rows:
                if (i != 0 and isinstance(random_words_list[i-1], list)):
                    random_words_list[i] = list(itertools.product(random_words_list[i-1], random_words_list[i]))[:no_of_rows]
                    for j in range(len(random_words_list[i])):
                        random_words_list[i][j] = "".join(random_words_list[i][j])
                    indices_to_delete.append(i-1)
                elif (i != len(random_words_list)-1 and isinstance(random_words_list[i+1], list)):
                    random_words_list[i] = list(itertools.product(random_words_list[i], random_words_list[i+1]))[:no_of_rows]
                    for j in range(len(random_words_list[i])):
                        random_words_list[i][j] = "".join(random_words_list[i][j])
                    indices_to_delete.append(i+1)
                    continue_flag = True
        indices_to_delete = indices_to_delete[::-1]
        for i in indices_to_delete:
            random_words_list.pop(i)

    return random_words_list
           
# Test for random words
# print(random_word_gen(exp_parser("{cols_1}  \\ul:2,3)[a,b,c]ABC###")))
# print(random_word_gen(exp_parser("    ABC ")))
# print(random_word_gen(exp_parser("[Abc,Xyz,Pqr](\':1)[C,Z,Q]")))
# print(random_word_gen(exp_parser("(\\ul:2,3)(-)(\\d:3)")))
# print(random_word_gen(exp_parser("[a,b,c](._:2,3)")))
# print(random_word_gen(exp_parser("{colun_1##_##(\\ul:2,3)")))



def random_digits_gen(random_digits_range, random_gen_mode="list", random_gen_type="integer", no_of_rows=5, constraint_type="no constraint", constraint_col1=pd.Series([]), constraint_col2=pd.Series([])):
    random_digits_list = []
    random_digits_range[0] = math.floor(random_digits_range[0]) if random_gen_type == "integer" else float(random_digits_range[0])
    random_digits_range[1] = math.ceil(random_digits_range[1]) if random_gen_type == "integer" else float(random_digits_range[1])
    if constraint_type == "less than":
        constraint_col2 = constraint_col2 - 1
    if constraint_type == "greater than":
        constraint_col1 = constraint_col1 + 1
    if random_gen_mode == "min_max" and len(random_digits_range) == 2:
        min_ele = random_digits_range[0]
        max_ele = random_digits_range[1]
        if constraint_type != "unique":
            for i in range(no_of_rows):
                lower_limit = max(min_ele, min_ele if pd.isnull(constraint_col1.get(i, None)) else constraint_col1.get(i))
                upper_limit = min(max_ele, max_ele if pd.isnull(constraint_col2.get(i, None)) else constraint_col2.get(i))
                random_digits_list.append(None if (lower_limit > max_ele or upper_limit < min_ele) else random.uniform(lower_limit, upper_limit))
        if constraint_type == "unique":
            if random_gen_type == "integer":
                max_ele = max_ele + 1
                sample = range(min_ele, max_ele)
                sample_size = min(len(sample), no_of_rows)
                random_digits_list = random.sample(sample, k=sample_size)
            if random_gen_type == "decimal":
                seed_multlipier = random.random()
                for i in range(no_of_rows):
                    random.seed(i*seed_multlipier)
                    random_digits_list.append(random.uniform(min_ele, max_ele))
    elif random_gen_mode == "range" and len(random_digits_range) == 2:
        start_ele = random_digits_range[0]
        increment = random_digits_range[1] if random_digits_range[1] != 0 else random_digits_range[1] + 1
        random_digits_list = np.arange(start_ele, start_ele+(increment*no_of_rows), step=increment)
    else:
        if constraint_type != "unique" and constraint_type != "no constraint":
            random_digits_range.sort()
            for i in range(no_of_rows):
                filtered_list = list_search(constraint_col1.get(i, None), constraint_col2.get(i, None), random_digits_range)
                random_digits_list.append(None if filtered_list == [] else random.choice(filtered_list))
        if constraint_type == "no constraint":
            random_digits_list = np.random.choice(random_digits_range, size=no_of_rows)
        if constraint_type == "unique":
            random_digits_range = set(random_digits_range)
            random_digits_list = random.sample(random_digits_range, min(no_of_rows, len(random_digits_range)))

    return pd.Series(random_digits_list, dtype="float64")

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


def random_dates_gen(random_dates_range, random_gen_mode="list", no_of_rows=5, constraint_type="no constraint", constraint_col1=pd.Series([]), constraint_col2=pd.Series([])):
    random_dates_list = pd.Series(np.nan, index=range(no_of_rows))
    if constraint_type == "less than":
        constraint_col2 = (constraint_col2 - datetime.timedelta(1))
    if constraint_type == "greater than":
        constraint_col1 = (constraint_col1 + datetime.timedelta(1))
    if random_gen_mode == "min_max" and len(random_dates_range) == 2:
        min_date = datetime.datetime.strptime(datetime.date.strftime(random_dates_range[0], "%Y-%m-%d"), "%Y-%m-%d")
        max_date = datetime.datetime.strptime(datetime.date.strftime(random_dates_range[1], "%Y-%m-%d"), "%Y-%m-%d")
        if constraint_type != "unique":
            for i in range(no_of_rows):
                min_date2 = max(min_date, min_date if pd.isnull(constraint_col1.get(i, None)) else constraint_col1.get(i))
                max_date2 = min(max_date, max_date if pd.isnull(constraint_col2.get(i, None)) else constraint_col2.get(i))
                if max_date2 < min_date or min_date2 > max_date:
                    random_dates_list[i] = None
                else:
                    date_diff = (max_date2 - min_date2).days
                    random_dates_list[i] = min_date2+datetime.timedelta(random.randint(0, date_diff))
        if constraint_type == "unique":
            date_diff = (max_date - min_date).days + 1
            sample = range(date_diff)
            sample_size = min(len(sample), no_of_rows)
            random_dates_list = random.sample(list(map(lambda d:min_date+datetime.timedelta(d), sample)), k=sample_size)
    elif random_gen_mode == "range" and len(random_dates_range) == 2:
        start_date = random_dates_range[0]
        increment = round(random_dates_range[1])
        random_dates_list = np.arange(start_date, start_date+datetime.timedelta(days = no_of_rows*increment), step=increment)
    else:
        for i in range(len(random_dates_range)):
            try:
                random_dates_range[i] = datetime.datetime.strptime(random_dates_range[i].strip(), "%Y-%m-%d")
            except ValueError:
                random_dates_range[i] = None
        if constraint_type != "unique" and constraint_type != "no constraint":
            random_dates_range.sort()
            for i in range(no_of_rows):
                filtered_list = list_search(constraint_col1.get(i, None), constraint_col2.get(i, None), random_dates_range)
                random_dates_list[i] = None if filtered_list == [] else random.choice(filtered_list)
        if constraint_type == "no constraint":
            random_dates_list = np.random.choice(random_dates_range, size=no_of_rows)
        if constraint_type == "unique":
            random_dates_range = set(random_dates_range)
            random_dates_list = random.sample(random_dates_range, min(no_of_rows, len(random_dates_range)))

    return pd.Series(random_dates_list)

# Test for random dates
# print(random_dates_gen(['2022-01-01', '2022-01-31'], "min_max", 5))
# print(random_dates_gen(['2022-01-01',5], "range", 5))
# print(random_dates_gen(['2022-01-01', '2022-01-12', '2022-01-15', '2022-01-26', '2022-01-31'], "list", 5))


def faker_data_gen(faker_provider="", constraint_type="no constraint", no_of_rows=5):
    faker_data_list = pd.Series(np.nan, index=range(no_of_rows))
    if faker_provider == "":
        return faker_data_list
    try:
        if constraint_type == "unique":
            faker_class = eval(f"fake.unique.{faker_provider}")
        else:
            faker_class = eval(f"fake.{faker_provider}")
    except AttributeError:
        return faker_data_list
    for i in range(no_of_rows):
        try:
            faker_data_list[i] = faker_class()
        except UniquenessException:
            break
    return faker_data_list
