import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path)


def get_connection():
    return mysql.connector.connect(
        host=os.environ["s_host"],
        port=os.environ["s_port"],
        user=os.environ["s_user"],
        password=os.environ["s_pass"],
        database="taxi",
        # ssl_ca="ca.pem",
    )


def execute_query(query, params=None):
    db = get_connection()
    cursor = db.cursor()

    cursor.execute(query, params)
    db.commit()

    affected = cursor.rowcount

    cursor.close()
    db.close()
    return affected


def fetch_query(query, params=None):
    db = get_connection()
    cursor = db.cursor(dictionary=True)  # returns rows as dict

    cursor.execute(query, params)
    result = cursor.fetchall()

    cursor.close()
    db.close()
    return result


def call_procedure(proc_name, params=None):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    cursor.callproc(proc_name, params or [])

    results = []
    for result in cursor.stored_results():
        results = result.fetchall()

    cursor.close()
    db.close()
    return results
