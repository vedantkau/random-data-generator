import streamlit as st
import datetime
import traceback
from libs.datagen import generate_data
from libs.form_checks import validate_forms
import libs.config as config

# initial setup
randomness_types = {
    'string': ['list', 'expression'],
    'integer': ['min_max', 'range', 'list', 'calculated'],
    'decimal': ['min_max', 'range', 'list', 'calculated'],
    'date': ['min_max', 'range', 'list'],
    'bool': ['list'],
    'faker': ['address', 'automotive', 'bank', 'barcode', 'color', 'company', 'credit_card', 'currency', 'file', 'geo', 'internet', 'isbn', 'job', 'lorem', 'misc', 'person', 'phone_number', 'profile', 'ssn', 'user_agent']
}
constraint_types = {
    'string': ['no constraint', 'unique'],
    'integer': ['no constraint', 'unique', 'between', 'greater than', 'greater than equal to', 'less than', 'less than equal to'],
    'decimal': ['no constraint', 'unique', 'between', 'greater than', 'greater than equal to', 'less than', 'less than equal to'],
    'date': ['no constraint', 'unique', 'between', 'greater than', 'greater than equal to', 'less than', 'less than equal to'],
    'faker': ['no constraint', 'unique']
}
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
st.set_page_config(
    page_title="Random DataGen",
    page_icon="",
    layout="wide",
)
if 'column_details' not in st.session_state:
    st.session_state["column_details"] = {'col1':['column_1', 'string', 'list', {}, {}]}
    st.session_state["i"] = [1]
    st.session_state["generated_data"] = ""
    st.session_state["is_there_data"] = False


@st.cache
def convert_df(df, df_type):
    if df_type == "csv":
        return df.to_csv(index=False).encode('utf-8')
    if df_type == "json":
        return df.to_json(orient="records").encode('utf-8')

st.header("Random data generator")
data_tab, setup_tab, docs_tab = st.tabs(["Data", "Setup", "Docs"])


with setup_tab:
    
    st.write(f"**No of rows required (max {config.MAX_ROWS}):**" if config.MAX_ROWS_LIMIT else "**No of rows required:**")
    st.number_input("a", value=5, key="no_of_rows", label_visibility="collapsed")
    st.write("")
    st.write(f"**Configure the columns (max {config.MAX_COLUMNS}):**" if config.MAX_COLUMNS_LIMIT else "**Configure the columns:**")
    col1, col2, col3 = st.columns([1,1,5], gap="small")
    add_btn = col1.button("Add column")
    remove_btn = col2.button("Remove columns")

    if add_btn:
        i = st.session_state['i'][-1] + 1
        st.session_state['column_details'][f'col{i}']=[f'column_{i}', 'string', 'list', {}, {}]
        st.session_state['i'].append(i)
    if remove_btn:
        column_details = list(st.session_state["column_details"].keys())
        for keys in column_details:
            if st.session_state.get(keys) and st.session_state[keys]:
                del st.session_state["column_details"][keys]

    col1, col2, col3, col4, col5 = st.columns([0.5,3,2,2,3], gap="small")
    available_intcolumns = []
    available_datecolumns = []
    for keys, cols in st.session_state['column_details'].items():
        cols[1] = st.session_state.get(f"{keys}_datatype", "string")
        if (cols[1] == "integer" or cols[1] == "decimal"):
            available_intcolumns.append(cols[0])
        if cols[1] == "date":
            available_datecolumns.append(cols[0])
    iter_index = 0
    for keys,cols in st.session_state['column_details'].items():
        cols[0] = st.session_state.get(f"{keys}_name", f"column_{keys.replace('col', '')}")
        cols[1] = st.session_state.get(f"{keys}_datatype", "string")
        cols[2] = st.session_state.get(f"{keys}_patternselect", "list")
        for types in ("list", "expression", "min", "max", "datemin", "datemax", "increment", "calculated", "provider"):
            if types in ("min", "max", "increment"):
                cols[3][types] = st.session_state.get(f"{keys}_{types}", 0.0)
            elif types in ("datemin", "datemax"):
                cols[3][types] = st.session_state.get(f"{keys}_{types}", datetime.date(datetime.date.today().year, 1, 1))
            else:
                cols[3][types] = st.session_state.get(f"{keys}_{types}", "")
        cols[4] = {"type": st.session_state.get(f"{keys}_constrainttype", ""), "value1": st.session_state.get(f"{keys}_constraintvalue1", ""), "value2": st.session_state.get(f"{keys}_constraintvalue2", "")}

        with st.container():
            col1, col2, col3, col4, col5 = st.columns([0.5,3,2,2,3], gap="small")
            col1.checkbox("", key=keys)
            col2.text_input("Column name:", value=f"{cols[0]}", key=f"{keys}_name")
            col3.selectbox("Data type:", randomness_types.keys(), index=list(randomness_types.keys()).index(cols[1]), key=f"{keys}_datatype")
            current_randomness_index = randomness_types[cols[1]].index(cols[2]) if cols[2] in randomness_types[cols[1]] else 0
            col4.selectbox("Pattern type", randomness_types[cols[1]], index=current_randomness_index, key=f"{keys}_patternselect")
            current_randomness_type = randomness_types[cols[1]][current_randomness_index]
            if current_randomness_type == "list":
                col5.text_area("List", placeholder="Comma (,) separated", key=f"{keys}_list", value=cols[3]["list"])
            elif current_randomness_type == "expression" or current_randomness_type == "calculated":
                col5.text_input("Expression", placeholder="See pattern docs", key=f"{keys}_{current_randomness_type}", value=cols[3][current_randomness_type])
            elif current_randomness_type == "min_max":
                if cols[1] == "date":
                    col5.date_input("Min date", key=f"{keys}_datemin", value=cols[3]["datemin"])
                    col5.date_input("Max date", key=f"{keys}_datemax", value=cols[3]["datemax"])
                else:
                    col5.number_input("Min", key=f"{keys}_min", value=cols[3]["min"])
                    col5.number_input("Max", key=f"{keys}_max", value=cols[3]["max"])
            elif current_randomness_type == "range":
                if cols[1] == "date":
                    col5.date_input("Min date", key=f"{keys}_datemin", value=cols[3]["datemin"])
                    col5.number_input("Increment (in days)", key=f"{keys}_increment", value=cols[3]["increment"])
                else:
                    col5.number_input("Min", key=f"{keys}_min", value=cols[3]["min"])
                    col5.number_input("Increment", key=f"{keys}_increment", value=cols[3]["increment"])
            elif cols[1] == "faker":
                col5.selectbox("Faker class:", faker_classes.get(cols[2], faker_classes['address']), index=0, key=f"{keys}_provider")
            if cols[1] != "bool" and cols[2] != "calculated" and cols[2] != "range":
                current_constraint_index = constraint_types[cols[1]].index(cols[4]["type"]) if cols[4]["type"] in constraint_types[cols[1]] else 0
                col2.selectbox("Constraint type:", constraint_types[cols[1]], key=f"{keys}_constrainttype", index=current_constraint_index)
                if cols[4]["type"] in ['greater than', 'greater than equal to', 'less than', 'less than equal to']:
                    available_columns = available_datecolumns[:iter_index] + available_datecolumns[iter_index+1:] if cols[1] == "date" else available_intcolumns[:iter_index] + available_intcolumns[iter_index+1:]
                    col3.selectbox("Column:", available_columns, key=f"{keys}_constraintvalue1")
                if cols[4]["type"] == "between":
                    available_columns = available_datecolumns[:iter_index] + available_datecolumns[iter_index+1:] if cols[1] == "date" else available_intcolumns[:iter_index] + available_intcolumns[iter_index+1:]
                    col3.selectbox("Column 1:", available_columns, key=f"{keys}_constraintvalue1")
                    col4.selectbox("Column 2:", available_columns, key=f"{keys}_constraintvalue2")
        iter_index += 1

    msg_box = st.container()
    msg_box.write("")
    generate_btn = st.button("Generate data!", key="generate_btn")
    if generate_btn:
        print(st.session_state["column_details"])
        checks_result, checks_returnobj = validate_forms(st.session_state["column_details"], st.session_state["no_of_rows"])

        if checks_result:
            try:
                st.session_state["generated_data"] = generate_data(st.session_state["column_details"], st.session_state["no_of_rows"], checks_returnobj)
                if isinstance(st.session_state["generated_data"], str):
                    msg_box.error(st.session_state["generated_data"])
                    st.session_state["generated_data"] = ""
                    st.session_state["is_there_data"] = False
                else:
                    msg_box.success("Dataset created! Please go to Data tab.")
                    st.session_state["is_there_data"] = True
            except Exception as e:
                msg_box.error("Something went wrong, sorry :(")
        else:
            msg_box.error(str(checks_returnobj))


with data_tab:
    if st.session_state["is_there_data"]:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        col1, col2, col3 = st.columns([1,1,5], gap="small")
        col1.download_button("Download as csv", convert_df(st.session_state["generated_data"], "csv"), 
            f"random_data_{timestamp}.csv", "text/csv", key="download_csv")
        col2.download_button("Download as json", convert_df(st.session_state["generated_data"], "json"), 
            f"random_data_{timestamp}.json", "text/json", key="download_json")
        st.dataframe(st.session_state["generated_data"], use_container_width=True) 
    else:
        st.write("Go create dataset in setup!")


with docs_tab:
    st.markdown("#### Random data generator")
    st.caption("Version 2.0")
    index, content = st.columns([1, 5], gap="small")
    st.markdown("")
    index.markdown("[About](#random-data-generator)")
    index.markdown("[Getting started](#getting-started)")
    index.markdown("[Limitations](#limitations)")
    index.markdown("[View source](#view-source)")
    index.markdown("[Pattern documentation](#pattern-documentation)")
    index.markdown("[Data constraints](#data-constraints)")

    with open("./docs/docs.md", "r") as about_file:
        content.markdown(about_file.read())
