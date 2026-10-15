from flask import Flask, jsonify, request
from dotenv import load_dotenv
import mysql.connector

app = Flask(__name__)
load_dotenv()
client_id = os.getenv("CLIENT_ID")
secret = os.getenv("SECRET")
user_id = os.getenv("USER_ID")
user_secret = os.getenv("USER_SECRET")
account_id = os.getenv("ACCOUNT_ID")
db_name = os.getnev("DB_NAME")
db_user = os.getnev("DB_USER")
db_password = os.getenv("DB_PASSWORD")


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        database=db_name,
        user=db_user,
        password=db_password
    )

@app.route("/stocks", methods=["GET"])
def get_stocks():
    conn = get_connection()
    cursor = cursor.cursor(dictionar=True)
    cursor.execute("select * from stocks")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8998)
