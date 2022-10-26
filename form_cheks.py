import re
import config

def validate_exp(exp, column_names, current_col):
    check0 = True if exp.count(" ") != len(exp) else False
    if not check0:
        return False, "Received empty expression"

    check1 = re.findall(r"(?<!\\)[\(|\)\[|\]\{|\}]", exp)
    check1_pass = True if len(check1) % 2 == 0 else False

    check2 = re.findall(r"(?<=:)\d,?\d*(?=\))", exp)
    square_braces_count = check1.count('[') + check1.count(']') + check1.count("{") + check1.count("}")
    check2_pass = True if len(check2) == (
        len(check1)-square_braces_count) // 2 else False

    if not check1_pass or not check2_pass:
        return False, "Expression is not correct"

    largest_len = 0
    for ranges in check2:
        largest_len += int(ranges.split(",")[-1])
    check3 = re.findall(r"(?<!\\)\[.*(?<!\\)\]", exp)
    for lists in check3:
        largest_len += len(max(lists[1:-1].split(","), key=len))
    check3_pass = True if largest_len <= 30 and config.STRING_LENGTH_LIMIT else False

    if not check3_pass:
        return False, "Word length is too long for random characters (max 30 characters)"

    inside_braces = False
    escape = False
    check4 = []
    split_pos = 0
    for i in range(len(exp) - 1):
        if escape == True:
            escape = False
            continue
        if exp[i] == "\\":
            escape = True
            continue
        if exp[i] == "(" or exp[i] == "[":
            inside_braces = True
            continue
        if exp[i] == ")" or exp[i] == "]":
            inside_braces = False
            continue
        if inside_braces == True:
            continue
        if exp[i] == "{":
            split_pos = i + 1
            continue
        if exp[i] == "}":
            check4.append(exp[split_pos:i])

    for cols in check4:
        if cols == current_col:
            return False, f"Same column cannot be added in expression"
        if cols not in column_names:
            return False, f"'{cols}' mentioned in expression does not exist, an error"

    return True, ""

# Test for validate expression
# print(validate_exp("(\\)\\ul\\(:2,4)[\\[\\]](-:3)"))
# print(validate_exp("(\\)\\ul\\(:2,4)[\\[\\]](-:3)"))
# print(validate_exp("    ABC "))
# print(validate_exp("(\\l:7,10)[@gmail.com,@yahoo.com]"))


def validate_forms(columns_details, no_of_rows):
    column_names = [cols[0] for cols in columns_details.values()]
    if no_of_rows > config.MAX_ROWS:
        return False, f"Rows limit exceeded (Max {config.MAX_ROWS} rows can be added)"
    if len(columns_details.keys())> config.MAX_COLUMNS:
        return False, f"Columns limit exceeded (Max {config.MAX_COLUMNS} columns can be added)"
    for cols in columns_details.values():
        if len(cols[0]) != len(re.findall(r"[\w+_*\s*]", cols[0])):
            return False, f"Invalid column name for column '{cols[0]}', only space, _, letters and digits are allowed" 
        if cols[2] == "expression":
            validate_result, msg = validate_exp(cols[3]["expression"], column_names, cols[0])
            if not validate_result:
                return False, f"{msg} for column '{cols[0]}'"
        if cols[2] == "list":
            list_elements = cols[3]["list"].split(",")
            if len(list_elements) > 20 and config.LIST_LENGTH_LIMIT:
                return False, f"Max 20 elements can be added in list for column '{cols[0]}'"
            if len(max(list_elements, key=len)) > 30 and config.LIST_LENGTH_LIMIT:
                return False, f"Max length for a list element must be less than 30 for column '{cols[0]}'"
    return True, ""