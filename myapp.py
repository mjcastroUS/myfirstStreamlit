import streamlit as st
import autogen
import sqlite3
import os

# Ruta relativa al archivo de la base de datos SQLite
db_path = os.path.join(os.path.dirname(__file__), 'contactcenter.db')

query_maker_gpt_system_prompt = '''
You are an SQL query generator for a SQLite database. 
Generate the SQL query using only the specified columns in the schema provided below. 
Do not add any columns on your own.

Below is the Schema of the available tables for making SQL queries. 
Create and return only one query.

Table name: CALL_DATA

Columns: YR_MO, CALL_DATE, AGENT_KEY, CALLS, HANDLE_TIME, 
CALL_REGEN, CALLS_WITH_OFFER, CALLS_WITH_ACCEPT, CALLS_OFFER_APPLIED, TRANSFERS

Provide a SQL query example:
SELECT CALLS, AGENT_KEY FROM Call_Data WHERE AGENT_KEY = '12465';

Always use the exact table name and columns as provided. 
Match the right agent against the AGENT_KEY column using the
 LIKE operator with '%' when necessary.

User Input:
'''

def query_maker(user_input, customization_params, api_key):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Configura Autogen para generar y personalizar consultas SQL
    autogen_config = {
        "model": "gpt-3.5-turbo",
        "api_key": api_key,
        "template": query_maker_gpt_system_prompt,
        "customization": {
            "verbosity": customization_params.get("verbosity", 0.5),
            "detail": customization_params.get("detail_level", "standard")
        }
    }

    # Utiliza Autogen para crear la consulta SQL
    query = autogen.generate_sql_query(user_input, autogen_config)
    
    # Ejecutar la consulta en la base de datos
    cursor.execute(query)
    results = cursor.fetchall()
    
    # Personalizar la salida basada en la configuración de Autogen
    if autogen_config["customization"]["detail"] == "high":
        results = autogen.enhance_details(results)

    conn.close()
    return results

# Streamlit app
st.title('SQL Query Generator with OpenAI')

openai_api_key = st.sidebar.text_input('OpenAI API Key', type='password')
if not openai_api_key.startswith('sk-'):
    st.warning('Please enter your OpenAI API key!', icon='⚠')

customization_params = {
    "verbosity": st.sidebar.slider('Verbosity', 0.0, 1.0, 0.5),
    "detail_level": st.sidebar.selectbox('Detail Level', ['standard', 'high'])
}

user_input = st.text_area('Enter your SQL query prompt:', '')

if st.button('Generate and Execute SQL Query'):
    if openai_api_key.startswith('sk-'):
        result = query_maker(user_input, customization_params, openai_api_key)
        st.write(result)
    else:
        st.warning('Please enter a valid OpenAI API key!', icon='⚠')
