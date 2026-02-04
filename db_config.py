import psycopg2
import streamlit as st


def get_connection():
    return psycopg2.connect(
        host=st.secrets['DB_HOST'],
        port=int(st.secrets['DB_PORT']),
        dbname=st.secrets['DB_NAME'],
        user=st.secrets['DB_USER'],
        password=st.secrets['DB_PASSWORD'],
        connect_timeout=10,
        sslmode='require'  # Most cloud providers require this
    )
