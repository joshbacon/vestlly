from snaptrade_client import SnapTrade

from flask import Flask, jsonify
import pymysql
import pymysql.cursors
from flask_cors import CORS
from decimal import Decimal

client_id = "VESTLLY-TEST-UMIOD"
secret = "6box143NZlF341Wc1EMezbxPIhBZdzWiHbxHyANfv5y1Milek8"
user_id = "admin"
user_secret = "a7aed493-0979-4207-86eb-af7b2dd60832"

snaptrade = SnapTrade(
    client_id=client_id,
    consumer_key=secret
)

app = Flask(__name__)
CORS(app)

def get_connection():
    return pymysql.connect(
        host="localhost",
        database="vestlly",
        user="gambit",
        password="Joshnmdb123!45",
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/stocks", methods=["GET"])
def get_stocks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("select * from stocks")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)


def serialize(rows):
    if isinstance(rows, list):
        return [{k: float(v) if isinstance(v, Decimal) else v for k, v in row.items()} for row in rows]
    return {k: float(v) if isinstance(v, Decimal) else v for k, v in rows.items()}


@app.route("/staccount")
def getAccounts():

    accounts = []

    # Use this endpoint to get the general account info
    general_data = snaptrade.account_information.list_user_accounts(
        user_id=user_id,
        user_secret=user_secret
    )

    # Fill in the general info into the accounts array
    for a in general_data.body:
        if 'MSB' in a['name']:
            continue
        accounts.append({
            'id': a['id'],
            'type': a['raw_type'],
            'name': a['name'],
            'institution': a['institution_name']
        })

    # Fill in other necessary data points
    for acc in accounts:
        # Get all holdings for each account
        holding_data = snaptrade.account_information.get_user_holdings(
            account_id=acc['id'],
            user_id=user_id,
            user_secret=user_secret
        ).body

        acc['cash'] = holding_data['account']['balance']['total'] # assumes only one currency held (in this case CAD), >
        acc['holdings'] = holding_data['positions'] # filter this down later to only the required fields

        # Get open orders
        acc['orders'] = []
        for order in holding_data['orders']:
                if order['status'] == 'ACCEPTED' and order['time_executed'] == None:
                        acc['orders'].append(order)

        # Get the activity on each account to add up contributions (used to calculate growth)
        activity_data = snaptrade.account_information.get_account_activities(
            account_id=acc['id'],
            user_id=user_id,
            user_secret=user_secret
        ).body

        acc['transactions'] = activity_data['data']

        # get the performance from the db
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"select * from performance where account_id = '{acc['id']}'")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        values = [row['total_value'] for row in rows]
        contribs = [row['contributed'] for row in rows]
        withdraws = [row['withdrawals'] for row in rows]

        acc['performance'] = values
        acc['contributions'] = contribs
        acc['withdrawals'] = withdraws

    return {
        'status': general_data.status,
        'accounts': accounts
    }

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8997)