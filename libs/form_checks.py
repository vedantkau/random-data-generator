import re
import libs.config as config

faker_classes = {
"address" : ['address', 'city', 'city_prefix', 'city_suffix', 'country', 'country_code', 'postcode', 'street_name', 'street_address', 'street_suffix'],
"automotive" : ['license_plate'],
"bank" : ['bban', 'iban', 'swift', 'swift11', 'swift8'],
"barcode" : ['ean', 'ean13', 'ean8', 'localized_ean', 'localized_ean13', 'localized_ean8'],
"color" : ['color', 'color_name', 'hex_color', 'rgb_color', 'rgb_css_color', 'safe_color_name', 'safe_hex_color'],
"company" : ['bs', 'catch_phrase', 'company', 'company_suffix'],
"credit_card" : ['credit_card_expire', 'credit_card_full', 'credit_card_number', 'credit_card_provider', 'credit_card_security_code'],
"currency" : ['cryptocurrency', 'cryptocurrency_code', 'cryptocurrency_name', 'currency', 'currency_code', 'currency_name', 'currency_symbol', 'pricetag'],
"file" : ['file_extension', 'file_name', 'file_path', 'mime_type', 'unix_device', 'unix_partition'],
"geo" : ['coordinate', 'latitude', 'latlng', 'local_latlng', 'location_on_land', 'longitude'],
"internet" : ['ascii_company_email', 'ascii_email', 'ascii_free_email', 'ascii_safe_email', 'company_email', 'email', 'free_email', 'free_email_domain', 'dga', 'domain_name', 'domain_word', 'hostname', 'http_method', 'iana_id', 'image_url', 'ipv4', 'ipv4_network_class', 'ipv4_private', 'ipv4_public', 'ipv6', 'mac_address', 'nic_handle', 'nic_handles', 'port_number', 'ripe_id', 'safe_domain_name', 'safe_email', 'slug', 'tld', 'uri', 'uri_extension', 'uri_page', 'uri_path', 'url', 'user_name'],
"isbn" : ['isbn10', 'isbn13'],
"job" : ['job'],
"lorem" : ['paragraph', 'paragraphs', 'sentence', 'sentences', 'text', 'texts', 'word', 'words'],
"misc" : ['md5', 'password', 'sha1', 'sha256', 'uuid4'],
"person" : ['first_name', 'first_name_female', 'first_name_male', 'first_name_nonbinary', 'language_name', 'last_name', 'last_name_female', 'last_name_male', 'last_name_nonbinary', 'name', 'name_female', 'name_male', 'name_nonbinary', 'prefix', 'prefix_female', 'prefix_male', 'prefix_nonbinary', 'suffix', 'suffix_female', 'suffix_male', 'suffix_nonbinary'],
"phone_number" : ['country_calling_code', 'msisdn', 'phone_number'], 
"profile" : ['profile', 'simple_profile'],
"ssn" : ['ssn'],
"user_agent" : ['android_platform_token', 'ios_platform_token', 'linux_platform_token', 'mac_platform_token', 'windows_platform_token', 'chrome', 'firefox', 'opera', 'safari', 'internet_explorer', 'linux_processor', 'mac_processor', 'user_agent']
}

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
    check3 = re.findall(r"(?<!\\)\[.*?(?<!\\)\]", exp)
    for lists in check3:
        largest_len += len(max(lists[1:-1].split(","), key=len))
    check3_pass = True if largest_len <= 30 or not config.STRING_LENGTH_LIMIT else False

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


def col_mapper(columns_details):
    col_keyname_map = {v[0] :k for k, v in columns_details.items()}
    col_stack = {}
    for keys, values in columns_details.items():
        if col_stack.get(keys):
            del col_stack[keys]
        col_stack[keys] = 1
        if values[4]['type'] != "no constraint" and values[4]['type'] != "unique":
            value1 = col_keyname_map.get(values[4]['value1'], '')
            value2 = col_keyname_map.get(values[4]['value2'], '')
            if value1 + value2 != '' and value1 == value2:
                return []
            if value1 != '':
                if col_stack.get(value1):
                    del col_stack[value1]
                col_stack[value1] = 1
            if value2 != '':
                if col_stack.get(value2):
                    del col_stack[value2]
                col_stack[value2] = 1
        
    return list(col_stack.keys())[::-1]


def validate_forms(columns_details, no_of_rows):
    column_names = [cols[0] for cols in columns_details.values()]
    if no_of_rows > config.MAX_ROWS and config.MAX_ROWS_LIMIT:
        return False, f"Rows limit exceeded (Max {config.MAX_ROWS} rows can be added)"
    if len(columns_details.keys()) > config.MAX_COLUMNS and config.MAX_COLUMNS_LIMIT:
        return False, f"Columns limit exceeded (Max {config.MAX_COLUMNS} columns can be added)"
    if len(set(column_names)) < len(column_names):
        return False, f"Duplicate column names cannot be allowed"
    for cols in columns_details.values():
        if len(cols[0]) != len(re.findall(r"[\w+_*\s*]", cols[0])):
            return False, f"Invalid column name for column '{cols[0]}', only space, _(underscore), letters and digits are allowed" 
        if cols[2] == "expression":
            validate_result, msg = validate_exp(cols[3]["expression"], column_names, cols[0])
            if not validate_result:
                return False, f"{msg} for column '{cols[0]}'"
        if cols[2] == "list":
            list_elements = cols[3]["list"].split(",")
            if cols[1] == "integer" or cols[1] == "decimal":
                try: 
                    list(map(float if cols[1] == "decimal" else int, list_elements))
                except ValueError:
                    return False, f"String element is not allowed in list for column '{cols[0]}'"
            if len(list_elements) > 20 and config.LIST_LENGTH_LIMIT:
                return False, f"Max 20 elements can be added in list for column '{cols[0]}'"
            if len(max(list_elements, key=len)) > 30 and config.LIST_LENGTH_LIMIT:
                return False, f"Max length for a list element must be less than 30 for column '{cols[0]}'"
        if cols[1] == "faker":
            if cols[3]['provider'] not in faker_classes.get(cols[2], []):
                return False, f"Invalid faker class for column '{cols[0]}'"
    cols_render_order = col_mapper(columns_details)
    if cols_render_order == []:
        return False, f"Same column cannot be allowed for both upper and lower limit in data constraints"

    return True, cols_render_order

