import streamlit as st
import streamlit.components.v1 as components

import datetime

from random_datagen_functions import generate_data
from random_datagen_formcheks import validate_forms

# initial setup
randomness_types = {
    'string': ['list', 'expression'],
    'integer': ['min_max', 'range', 'list'],
    'decimal': ['min_max', 'range', 'list'],
    'date': ['min_max', 'range', 'list'],
    'bool': ['list']
}
st.set_page_config(
    page_title="Data Generator",
    page_icon="",
    layout="wide",
)
if 'column_details' not in st.session_state:
    st.session_state['column_details'] = {'col1':['column_1', 'string', 'list', {}]}
    st.session_state['i'] = [1]
    st.session_state["generated_data"] = None
    st.session_state["is_there_data"] = False
# components.html(
#             '''
#             <script>
#             btns_list = document.getElementsByClassName("css-6kekos edgvbvh9");
#             for (var i=0; i<btns_list.length; i++){
#                 if (btns_list[i].innerText == 'Generate data!'){
#                     btns_list[i].addEventListener("click", () => {document.getElementById("tabs-1-tab-0").click();});
#                 }
#             }
#             </script>
#             '''
#         )

@st.cache
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

st.markdown("# Random data generator")
data_tab, setup_tab = st.tabs(["Data", "Setup"])

with setup_tab:
    st.write("**No of rows required (max 100):**")
    st.number_input("a", value=5, key="no_of_rows", label_visibility="collapsed")
    st.write("")
    st.write("**Configure the columns:**")
    col1, col2, col3 = st.columns([1,1,5], gap="small")
    add_btn = col1.button("Add column")
    remove_btn = col2.button("Remove columns")

    if add_btn:
        i = st.session_state['i'][-1] + 1
        st.session_state['column_details'][f'col{i}']=[f'column_{i}', 'string', 'list', {}]
        st.session_state['i'].append(i)
    if remove_btn:
        column_details = list(st.session_state["column_details"].keys())
        for keys in column_details:
            if st.session_state.get(keys) and st.session_state[keys]:
                del st.session_state["column_details"][keys]

    col1, col2, col3, col4, col5 = st.columns([0.5,3,2,2,3], gap="small")
    col1.write("**#**")
    col2.write("**Column name**")
    col3.write("**Data type**")
    col4.write("**Pattern type**")
    col5.write("**Pattern**")

    for keys,cols in st.session_state['column_details'].items():
        cols[0] = st.session_state.get(f"{keys}_name", f"column_{keys.replace('col', '')}")
        cols[1] = st.session_state.get(f"{keys}_datatype", "string")
        cols[2] = st.session_state.get(f"{keys}_patternselect", "list")
        for types in ("list", "expression", "min", "max", "datemin", "datemax", "increment"):
            if types in ("min", "max", "increment"):
                cols[3][types] = st.session_state.get(f"{keys}_{types}", 0.0)
            elif types in ("datemin", "datemax"):
                cols[3][types] = st.session_state.get(f"{keys}_{types}", datetime.date(2022, 1, 1))
            else:
                cols[3][types] = st.session_state.get(f"{keys}_{types}", "")
            

        with st.container():
            col1, col2, col3, col4, col5 = st.columns([0.5,3,2,2,3], gap="small")
            col1.checkbox("", key=keys)
            col2.text_input("a", value=f"{cols[0]}", key=f"{keys}_name", label_visibility="collapsed")
            col3.selectbox("a", randomness_types.keys(), index=list(randomness_types.keys()).index(cols[1]), key=f"{keys}_datatype", label_visibility="collapsed")
            current_randomness_index = randomness_types[cols[1]].index(cols[2]) if cols[2] in randomness_types[cols[1]] else 0
            col4.selectbox("a", randomness_types[cols[1]], index=current_randomness_index, key=f"{keys}_patternselect", label_visibility="collapsed")
            current_randomness_type = randomness_types[cols[1]][current_randomness_index]
            if current_randomness_type == "list":
                col5.text_input("a", placeholder="Comma (,) separated", key=f"{keys}_list", value=cols[3]["list"], label_visibility="collapsed")
            elif current_randomness_type == "expression":
                col5.text_input("a", placeholder="See expression docs", key=f"{keys}_expression", value=cols[3]["expression"], label_visibility="collapsed")
            elif current_randomness_type == "min_max":
                if cols[1] == "date":
                    col5.date_input("Min date", key=f"{keys}_datemin", value=cols[3]["datemin"], label_visibility="visible")
                    col5.date_input("Max date", key=f"{keys}_datemax", value=cols[3]["datemax"], label_visibility="visible")
                else:
                    col5.number_input("Min", key=f"{keys}_min", value=cols[3]["min"], label_visibility="visible")
                    col5.number_input("Max", key=f"{keys}_max", value=cols[3]["max"], label_visibility="visible")
            elif current_randomness_type == "range":
                if cols[1] == "date":
                    col5.date_input("Min date", key=f"{keys}_datemin", value=cols[3]["datemin"], label_visibility="visible")
                    col5.number_input("Increment (in days)", key=f"{keys}_increment", value=cols[3]["increment"], label_visibility="visible")
                else:
                    col5.number_input("Min", key=f"{keys}_min", value=cols[3]["min"], label_visibility="visible")
                    col5.number_input("Increment", key=f"{keys}_increment", value=cols[3]["increment"], label_visibility="visible")

    msg_box = st.container()
    msg_box.write("")
    generate_btn = st.button("Generate data!", key="generate_btn")
    if generate_btn:
        print(st.session_state["column_details"])
        checks_result, msg = validate_forms(st.session_state["column_details"], st.session_state["no_of_rows"])

        if checks_result:
            try:
                st.session_state["generated_data"] = generate_data(st.session_state["column_details"], st.session_state["no_of_rows"])
                st.session_state["is_there_data"] = True
                msg_box.success("Dataset created! Please go to Data tab.")
            except:
                msg_box.error("Something went wrong, sorry :(")
        else:
            msg_box.error(msg)


with data_tab:
    if st.session_state["is_there_data"]:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        st.download_button("Download as csv", convert_df(st.session_state["generated_data"]), 
            f"random_data_{timestamp}.csv", "text/csv", key="download_csv")
        st.dataframe(st.session_state["generated_data"], use_container_width=True) 
    else:
        st.write("Go create dataset in setup!")

