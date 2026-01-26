import psycopg
import streamlit as st


def get_connection():
    return psycopg.connect(
        host=str(st.secrets['DB_HOST']).strip(),  # .strip() removes hidden spaces
        port=int(st.secrets['DB_PORT']),
        dbname=str(st.secrets['DB_NAME']),
        user=str(st.secrets['DB_USER']),
        password=str(st.secrets['DB_PASSWORD']),
        connect_timeout=10,
        sslmode='require'  # Most cloud DBs (Supabase, Aiven, Neon) require this
    )
