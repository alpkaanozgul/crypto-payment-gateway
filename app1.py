from flask import Flask, request, render_template, jsonify
import mysql.connector
import createWalletAvax
import getBalance
import sendAvax2
from decimal import Decimal
import time
import threading
import re
from datetime import datetime
import requests
import json

app = Flask(__name__)

transactions = {}

@app.route('/<api_key>/<float:wantAmmount>', methods=['GET'])
def main(api_key, wantAmmount):

    address, webhook_url, email = validateApi(api_key)
    if address is not None:
        pK, wA = createWallet()
        print(wA)
        transaction_status = "Waiting for transaction..."

        transaction_id = f"{api_key}_{wA}"  
        transactions[transaction_id] = {"status": transaction_status, "address": address}

        try:
            conn = mysql.connector.connect(
                host="localhost",  
                user="root",       
                password="Alp_O_07_Xd",       
                database="crypto_db"  
            )
            
            cursor = conn.cursor()

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            query = "INSERT INTO transactions (transaction_id, timestamp, address, amount, email) VALUES (%s, %s, %s, %s, %s)"
            values = (transaction_id, timestamp, address, wantAmmount, email)

            cursor.execute(query, values)

            conn.commit()

            print(f"Transaction {transaction_id} stored successfully.")
            
        except mysql.connector.Error as err:
            print(f"Error: {err}")
    
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

        threading.Thread(target=check_transaction, args=(transaction_id, wA, pK, address, wantAmmount, webhook_url)).start()

        transaction_link = f"/transaction/{transaction_id}"
        return jsonify({"transaction_link": transaction_link})

    return "API Key not valid", 400


from flask import Flask, render_template, jsonify
import mysql.connector
import re
from datetime import datetime, timedelta

@app.route('/transaction/<transaction_id>', methods=['GET'])
def transaction_page(transaction_id):
    # Check if the transaction ID exists in your transactions dictionary
    if transaction_id in transactions:
        amount = 0
        print(f"The transaction ID is ----> {transaction_id}")
        
        # Split the transaction ID
        split = re.split("_", transaction_id)

        # Connect to the database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Alp_O_07_Xd",
            database="crypto_db"
        )
        cursor = conn.cursor()

        # Execute the query using parameterized query to avoid SQL injection
        cursor.execute("SELECT amount, timestamp, status FROM transactions WHERE transaction_id = %s;", (transaction_id,))
        result = cursor.fetchone()

        # Close the connection
        conn.close()

        if result:
            amount = result[0]
            timestamp = result[1]
            status = result[2]
            print(f"The amount is here --->> {amount}")

            # Get current time
            current_time = datetime.now()

            # Check if the transaction's timestamp is older than 1 hour
            if current_time - timestamp <= timedelta(hours=1):
              return render_template('transaction_status.html', address1=split[1], data={'amount': amount}, transaction_id=transaction_id)
                
            else:
                # If more than 1 hour, render the template with the details
                
                # If within 1 hour, send status and transaction ID as JSON
                return jsonify({
                    'transaction_id': transaction_id,
                    'status': status,
                    'amount': amount
                })
        else:
            # Transaction not found in the database
            return jsonify({"error": "Transaction not found"}), 404
    else:
        # Transaction ID not in the transactions dictionary
        return jsonify({"error": "Transaction not found"}), 404



@app.route('/status/<transaction_id>', methods=['GET'])
def status(transaction_id):
    
    if transaction_id in transactions:
        return jsonify(transactions[transaction_id])
    else:
        return jsonify({"status": "Transaction not found", "address": ""}), 404


def check_transaction(transaction_id, wA, pK, your_address, wantAmmount, webhook_url):
    thread_event = threading.Event()  # Thread event to manage timeout and payment success
    
    validate = 0
    start_time = time.time()
    
    while not thread_event.is_set():
        # Check if the payment was successful
        validate = validateTransaction(wA, wantAmmount)
        
        if validate == 1:  # Payment was successful
            thread_event.set()  # Signal that payment was successful
            tx_hash = sendAvax2.sendAvax(pK, f"{your_address}", wantAmmount - 0.0007)
            time.sleep(5)
            if tx_hash is not None:
                transactions[transaction_id]["status"] = "Transaction Successful"
                update_transaction_status(transaction_id, 'success')
                send_webhook(transaction_id, wantAmmount, "success", webhook_url)
            else:
                transactions[transaction_id]["status"] = "Transaction Failed"
                update_transaction_status(transaction_id, 'failed')
                send_webhook(transaction_id, wantAmmount, "failed", webhook_url)
            break  # Exit the loop

        # Check if the 10-second timeout is reached
        if time.time() - start_time > 1800:
            transactions[transaction_id]["status"] = "Transaction Timeout"
            update_transaction_status(transaction_id, 'timeout')
            print(f"Transaction {transaction_id} timed out.")
            break  # Exit the loop

        time.sleep(5)  # Wait for 5 seconds before checking again


def update_transaction_status(transaction_id, status):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Alp_O_07_Xd",
        database="crypto_db"
    )
    cursor = conn.cursor()
    
    update_query = "UPDATE transactions SET status = %s WHERE transaction_id = %s"
    cursor.execute(update_query, (status, transaction_id))
    
    conn.commit()
    print(f"Transaction {transaction_id} status updated to {status}.")
    cursor.close()
    conn.close()


def send_webhook(transaction_id, amount, status, webhook_url):
    payload = {
        "event": "payment_completed",
        "data": {
            "transaction_id": f"{transaction_id}",
            "amount": f"{amount}",
            "currency": "AVAX",
            "status": status
        }
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        print("Webhook sent successfully!")
    else:
        print(f"Failed to send webhook. Status code: {response.status_code}")


def validateTransaction(wA, amount):
    balance = getBalance.getBalance(wA)
    amount = Decimal(amount)
    balance = Decimal(balance)
    epsilon = Decimal(1e-9)
    
    if abs(amount - balance) < epsilon:
        print(f"✅ The transaction sent {amount} AVAX as expected.")
        return 1
    else:
        print(f"❌ The transaction sent {balance} AVAX, but {amount} AVAX was expected.")
        return 0


def createWallet():
    wallet = createWalletAvax.createWalletAavax()
    pK, wA = wallet
    return [pK, wA]


def validateApi(api_key):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Alp_O_07_Xd",
        database="crypto_db"
    )
    cursor = conn.cursor()
    cursor.execute(f"SELECT address, webhook_url, email FROM crypto_addresses WHERE api_key = '{api_key}';")
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0], result[1], result[2]
    else:
        return None


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)  