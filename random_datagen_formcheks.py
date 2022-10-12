import re


def validate_exp(exp):
    check0 = True if exp.count(" ") != len(exp) else False
    if not check0:
        return False, "Received empty expression"

    check1 = re.findall(r"(?<!\\)[\(|\)\[|\]]", exp)
    check1_pass = True if len(check1) % 2 == 0 and len(check1)>=2 else False

    check2 = re.findall(r"(?<=:)\d,?\d*(?=\))", exp)
    square_braces_count = check1.count('[') + check1.count(']')
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
    check3_pass = True if largest_len <= 30 else False

    if not check3_pass:
        return False, "Word length is too long (max 15 characters)"

    return True, ""

# Test for validate expression
# print(validate_exp("(\\)\\ul\\(:2,4)[\\[\\]](-:3)"))
# print(validate_exp("(\\)\\ul\\(:2,4)[\\[\\]](-:3)"))
# print(validate_exp("    ABC "))
# print(validate_exp("(\\l:7,10)[@gmail.com,@yahoo.com]"))


def validate_forms(columns_details, no_of_rows):
    if no_of_rows > 100:
        return False, "Rows limit exceeded (Max 100 rows can be added)"
    if len(columns_details.keys())>10:
        return False, "Columns limit exceeded (Max 10 columns can be added)"
    for cols in columns_details.values():
        if cols[2] == "expression":
            validate_result, msg = validate_exp(cols[3]["expression"])
            if not validate_result:
                return False, f"{msg} for column '{cols[0]}'"
    return True, ""