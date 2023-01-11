import pandas as pd
import numpy as np
import libs.datagen_functions as dgf
import traceback


def generate_data(column_details, no_of_rows=5, cols_render_order=None):
    pd_data = {}
    column_details[cols_render_order[0]][4]["type"] = "no constraint" if column_details[cols_render_order[0]][4]["type"] != "unique" else "unique"

    #generate random data for columns
    for keys in cols_render_order:
        cols = column_details[keys]
        constraint_type = cols[4]["type"]
        constraint_col1 = pd_data.get(cols[4]["value1"], '')
        constraint_col2 = pd_data.get(cols[4]["value2"], '')
        if constraint_type == "less than" or constraint_type == "less than equal to":
            constraint_col2 = constraint_col1
            constraint_col1 = pd.Series([], dtype="float32")
        if constraint_type == "greater than" or constraint_type == "greater than equal to":
            constraint_col2 = pd.Series([], dtype="float32")
        if constraint_type == "unique" or constraint_type == "no constraint":
            constraint_col1 = pd.Series([], dtype="float32")
            constraint_col2 = pd.Series([], dtype="float32")
        if cols[1] == "string" and cols[2] == "list":
            exp = "["+cols[3]["list"]+"]"
            words_list = dgf.exp_parser(exp)
            pd_data[cols[0]] = dgf.random_word_gen(words_list, no_of_rows, constraint_type)
        elif cols[1] == "string" and cols[2] == "expression":
            exp = cols[3]["expression"]
            pd_data[cols[0]] = dgf.random_word_gen(dgf.exp_parser(exp), no_of_rows, constraint_type)
        elif (cols[1] == "integer" or cols[1] == "decimal") and cols[2] == "list":
            digits_range = list(map(float if cols[1] == "decimal" else int, cols[3]["list"].split(",")))
            pd_data[cols[0]] = dgf.random_digits_gen(digits_range, cols[2], cols[1], no_of_rows, constraint_type, constraint_col1, constraint_col2)
        elif (cols[1] == "integer" or cols[1] == "decimal") and cols[2] == "min_max":
            digits_range = [cols[3]["min"], cols[3]["max"]]
            pd_data[cols[0]] = dgf.random_digits_gen(digits_range, cols[2], cols[1], no_of_rows, constraint_type, constraint_col1, constraint_col2)
        elif (cols[1] == "integer" or cols[1] == "decimal") and cols[2] == "range":
            digits_range = [cols[3]["min"], cols[3]["increment"]]
            pd_data[cols[0]] = dgf.random_digits_gen(digits_range, cols[2], cols[1], no_of_rows, constraint_type, constraint_col1, constraint_col2)
        elif cols[1] == "date" and cols[2] == "list":
            dates_range = cols[3]["list"].split(",")
            pd_data[cols[0]] = dgf.random_dates_gen(dates_range, cols[2], no_of_rows, constraint_type, constraint_col1, constraint_col2)
        elif cols[1] == "date" and cols[2] == "min_max":
            dates_range = [cols[3]["datemin"], cols[3]["datemax"]]
            pd_data[cols[0]] = dgf.random_dates_gen(dates_range, cols[2], no_of_rows, constraint_type, constraint_col1, constraint_col2)
        elif cols[1] == "date" and cols[2] == "range":
            dates_range = [cols[3]["datemin"], cols[3]["increment"]]
            pd_data[cols[0]] = dgf.random_dates_gen(dates_range, cols[2], no_of_rows, constraint_type, constraint_col1, constraint_col2)
        elif cols[1] == "bool" and cols[2] == "list":
            opts_list = cols[3]["list"].split(",")[:2]
            pd_data[cols[0]] = dgf.random_bool_gen(opts_list, no_of_rows)
        elif cols[1] == "faker":
            pd_data[cols[0]] = dgf.faker_data_gen(cols[3]["provider"], constraint_type, no_of_rows)

    #add columns with randomness type as 'calculated'
    for keys, cols in column_details.items():
        if cols[1] == "date":
            try:
                pd_data[cols[0]] = pd.to_datetime(pd_data[cols[0]], format="%Y-%m-%d")
                pd_data[cols[0]] = pd_data[cols[0]].astype('str')
            except:
                pass

        if (cols[1] == "integer" or cols[1] == "decimal") and cols[2] == "calculated":
            try:
                exp = cols[3]["calculated"]
                pd_data[cols[0]] = pd_data.eval(exp)
            except Exception as e:
                return f"Calculated expression seems not correct for column '{cols[0]}'"

        if cols[1] == "integer":
            pd_data[cols[0]] = pd_data[cols[0]].round()
            pd_data[cols[0]] = pd_data[cols[0]].astype("Int64")
        if cols[1] == "decimal":
            pd_data[cols[0]] = pd_data[cols[0]].astype("float64")
    
    #concat columns mentioned in advanced expression
    for keys, cols in column_details.items():
        if cols[1] == "string":
            data = pd_data[cols[0]]
            pd_series = pd.Series(data[0]) if isinstance(data[0], list) else pd_data.get(data[0], pd.Series('', index=range(no_of_rows),  dtype="str"))
            for d in data[1:]:
                pd_series = pd_series.combine(pd.Series(d) if isinstance(d, list) else pd_data.get(d, pd.Series('', index=range(no_of_rows),  dtype="str")), lambda str1,str2: str(str1)+str(str2), fill_value="")
            pd_data[cols[0]] = pd_series

    pd_df = pd.DataFrame(pd_data)
    return pd_df
    
         

# Test for generate data
# column_details = {'col1': ['column_1', 'string', 'list', {'list': 'Abc,Xyz,Pqr', 'expression': '', 'min': 0.0, 'max': 0.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 0.0}], 'col2': ['column_2', 'string', 'expression', {'list': '', 'expression': '(\\ul:2,3)(-)(\\d:3)', 'min': 0.0, 'max': 0.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 0.0}], 'col3': ['column_3', 'integer', 'min_max', {'list': '', 'expression': '', 'min': 0.0, 'max': 20.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 0.0}], 'col4': ['column_4', 'integer', 'range', {'list': '', 'expression': '', 'min': 0.0, 'max': 0.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 1.0}], 'col5': ['column_5', 'decimal', 'min_max', {'list': '', 'expression': '', 'min': 0.0, 'max': 30.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 0.0}], 'col6': ['column_6', 'decimal', 'range', {'list': '', 'expression': '', 'min': 0.0, 'max': 0.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 0.5}], 'col7': ['column_7', 'date', 'min_max', {'list': '', 'expression': '', 'min': 0.0, 'max': 0.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 31), 'increment': 0.0}], 'col8': ['column_8', 'date', 'range', {'list': '', 'expression': '', 'min': 0.0, 'max': 0.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 1.0}]}
# column_details = {'col1': ['col1', 'decimal', 'min_max', {'list': '', 'expression': '', 'min': 10.0, 'max': 20.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 0.0, 'calculated': ''}], 'col2': ['col2', 'decimal', 'range', {'list': '', 'expression': '', 'min': 0.0, 'max': 0.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 10.0, 'calculated': ''}], 'col3': ['col3', 'decimal', 'calculated', {'list': '', 'expression': '', 'min': 0.0, 'max': 0.0, 'datemin': datetime.date(2022, 1, 1), 'datemax': datetime.date(2022, 1, 1), 'increment': 0.0, 'calculated': 'False'}]}
# time0 = time.time()
# print(generate_data(column_details))
# time1 = time.time()
# print(time1-time0)