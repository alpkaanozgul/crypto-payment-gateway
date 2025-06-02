from flask import Flask, request, render_template, jsonify
import mysql.connector
import createWalletAvax
import getBalance
import sendAvax2
from decimal import Decimal
import time
import threading
import re
from datetime import datetime, timedelta
import requests
import json
import getBalanceTRC20
import createwalletTRC20
import sendTRC20

app = Flask(__name__)

@app.route('/<api_key>/<currency>/<float:wantAmmount>', methods=['GET'])
def main(api_key, currency, wantAmmount):

    address, webhook_url, email = validateApi(api_key,currency)
    
    print(f"webhook is ******** {webhook_url}")
    
    
    code = getCode(api_key)

    if currency ==  "AVAX":
        if address is not None:
            pK, wA = createWallet()
            print(f"wallet address = {wA}")
            print(f"private key = {pK}")

        transaction_id = f"{api_key}_{wA}"  

        try:
            conn = mysql.connector.connect(
                host="localhost",  
                user="root",       
                password="",       
                database="crypto_db"  
            )
            
            cursor = conn.cursor()

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            query = "INSERT INTO transactions (transaction_id, timestamp, address, amount, email, code, currency) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            values = (transaction_id, timestamp, address, wantAmmount, email, code, currency)



            cursor.execute(query, values)

            conn.commit()
            split = re.split("_", transaction_id)

            update_transaction_status_internal(transaction_id, "Waiting for transaction...")


            print(f"Transaction {transaction_id} stored successfully.")
            
        except mysql.connector.Error as err:
            print(f"Error: {err}")
    
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

        threading.Thread(target=check_transaction, args=(transaction_id, wA, pK, address, wantAmmount, webhook_url,currency)).start()

        transaction_link = f"https://api.coin-xpress.com/transaction/{transaction_id}/{currency}"
        return jsonify({"transaction_link": transaction_link})


    elif currency == "USDT":
        if address is not None:
            pK, wA = createwalletTRC20.createWalletTRC20()
            print(f"wallet address = {wA}")
            print(f"private key = {pK}")
        transaction_id = f"{api_key}_{wA}"  

        try:
            conn = mysql.connector.connect(
                host="localhost",  
                user="root",       
                password="",       
                database="crypto_db"  
            )
            
            cursor = conn.cursor()

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            query = "INSERT INTO transactions (transaction_id, timestamp, address, amount, email, code, currency) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            values = (transaction_id, timestamp, address, wantAmmount, email, code, currency)



            cursor.execute(query, values)

            conn.commit()
            split = re.split("_", transaction_id)

            update_transaction_status_internal(transaction_id, "Waiting for transaction...")


            print(f"Transaction {transaction_id} stored successfully.")
            
        except mysql.connector.Error as err:
            print(f"Error: {err}")
    
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

        threading.Thread(target=check_transaction, args=(transaction_id, wA, pK, address, wantAmmount, webhook_url,currency)).start()

        transaction_link = f"https://localhost:5000/transaction/{transaction_id}/{currency}"
        return jsonify({"transaction_link": transaction_link})







def getCode(api_key):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="crypto_db"
    )
    cursor = conn.cursor()
    cursor.execute(f"SELECT code, webhook_url, email FROM crypto_addresses WHERE api_key = '{api_key}';")
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        return None

@app.route('/num/detail/<transaction_id>', methods = ['GET'])
def detail(transaction_id):
        

        if if_transaction_exists(transaction_id):
            split = re.split("_", transaction_id)
            status = checkstatus(transaction_id)
            amount = checkamount(transaction_id)


            return jsonify({
                "send_address": split[1],
                "status": status,
                "amount": amount
            })
        else:
            # If transaction doesn't exist, return error
            return jsonify({"error": "Transaction not found"}), 404

def checkamount(transaction_id):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="crypto_db"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT amount FROM transactions WHERE transaction_id = %s", (transaction_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0]


@app.route('/transaction/<transaction_id>/<currency>', methods=['GET'])
def transaction_page(transaction_id,currency):
    # Check if the transaction ID exists in your transactions dictionary
    

    if if_transaction_exists(transaction_id):
        amount = 0
        print(f"The transaction ID is ----> {transaction_id}")
        
        # Split the transaction ID
        split = re.split("_", transaction_id)

        # Connect to the database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="crypto_db"
        )
        cursor = conn.cursor()

        # Execute the query using parameterized query to avoid SQL in                     jection
        cursor.execute("SELECT amount FROM transactions WHERE transaction_id = %s;", (transaction_id,))
        result = cursor.fetchone()

        # Close the connection
        conn.close()

        if result:
            amount = result[0]
            
            print(f"The amount is here --->> {amount}")

            
            return render_template('transaction_status.html', address1=split[1], data={'amount': amount}, transaction_id=transaction_id,currency=currency)
                
            
        else:
            # Transaction not found in the database
            return jsonify({"error": "Transaction not found"}), 404
    else:
        # Transaction ID not in the transactions dictionary
        return jsonify({"error": "Transaction not found"}), 404




@app.route('/status/<transaction_id>', methods=['GET'])
def status(transaction_id):
    
    if if_transaction_exists(transaction_id):
        status = checkstatus(transaction_id)
        return jsonify({"status": f"{status}"}), 200
    else:
        return jsonify({"status": "Transaction not found", "address": ""}), 404


def checkstatus(transaction_id):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="crypto_db"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM transactions WHERE transaction_id = %s", (transaction_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0]

def check_transaction(transaction_id, wA, pK, your_address, wantAmmount, webhook_url,currency):
    
    thread_event = threading.Event()  # Thread event to manage timeout and payment success
    
    validate = 0
    start_time = time.time()
    print(f"webhook url = {webhook_url}")
    
    while not thread_event.is_set():
        # Check if the payment was successful
        print(f"3 webhook url = {webhook_url}")
        
        validate = validateTransaction(wA, wantAmmount,currency)
        
        split = re.split("_", transaction_id)
        
        if validate == 1:  # Payment was successful


            
            thread_event.set()  # Signal that payment was successful
            if currency == "AVAX":
                tx_hash = sendAvax2.sendAvax(pK, f"{your_address}")
            elif currency == "USDT":
                print(f"*********** {pK} {wantAmmount}")
                tx_hash = sendTRC20.sendTRC20(pK, your_address,int(wantAmmount))
            
            if tx_hash is not None:
                print("empty degil")
                update_transaction_status_internal(transaction_id,'success')
                
                if webhook_url is not None:
                  print(f"4 webhook url = {webhook_url}")
                  send_webhook(transaction_id, wantAmmount, "success", webhook_url)
            else:
                update_transaction_status_internal(transaction_id,'failed')
                if webhook_url is not None:
                  send_webhook(transaction_id, wantAmmount, "failed", webhook_url)
                break  # Exit the loop        
            
                

        print("time once")        

        if time.time() - start_time > 600:  # 30 minutes timeout
            update_transaction_status_internal(transaction_id, 'timeout')  # Fixed syntax error
            send_webhook(transaction_id, wantAmmount, "timeout", webhook_url)
            
            break  # Exit the loop
            
        print("time sonra")        

        time.sleep(5)
        
@app.route('/update_status/<api_key>/<transaction_id>/<currency>/<status>', methods=['GET'])
def update_transaction_status(api_key, transaction_id,currency, status):
    if validateApi(api_key,currency) and if_transaction_exists(transaction_id):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="crypto_db"
            )
            cursor = conn.cursor()
            
            update_query = "UPDATE transactions SET status = %s WHERE transaction_id = %s"
            cursor.execute(update_query, (status, transaction_id))
            
            conn.commit()
            print(f"Transaction {transaction_id} status updated to {status}.")
            return jsonify({"status": "Transaction status updated"}), 200

        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return jsonify({"status": "Database error", "error": str(err)}), 500
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()
    else:
        return jsonify({"status": "Invalid API key or transaction not found"}), 400


def update_transaction_status_internal(transaction_id, status):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="crypto_db"
        )
        cursor = conn.cursor()
        
        update_query = "UPDATE transactions SET status = %s WHERE transaction_id = %s"
        cursor.execute(update_query, (status, transaction_id))
        
        conn.commit()
        print(f"Transaction {transaction_id} status updated to {status}.")
        return True

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return False
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()


def send_webhook(transaction_id, amount, status, webhook_url):
    print(f"webhook url is {webhook_url}")
    payload = {
        "event": "payment_completed", 
        "data": {
            "transaction_id": f"{transaction_id}",
            "amount": f"{amount}",
            "currency": "USDT",
            "status": status
        }
    }
    headers = {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true' # Add ngrok header if test
    }
    try:
        response = requests.post(webhook_url, data=json.dumps(payload), headers=headers, verify=False) # Disable SSL verification test purpose
        if response.status_code == 200:
            print("Webhook sent successfully!")
        else:
            print(f"Failed to send webhook. Status code: {response.status_code}")
            print(f"Response content: {response.text}") # Print response content for debugging
    except requests.exceptions.RequestException as e:
        print(f"Error sending webhook: {str(e)}")


def validateTransaction(wA, amount,currency):
    # Get the balance of the wallet
    if currency == "AVAX":
        balance = getBalance.getBalance(wA)
    elif currency == "USDT":
        print(f"burda ---------- {wA}")
        balance = getBalanceTRC20.getBalanceTRC20(wA)
        print(f"balance----- {balance}")
    amount = Decimal(amount)
    balance = Decimal(balance)
    
    # Configurable fee tolerance (percentage) — change this as needed
    tolerance_percentage = Decimal('0.004')  
    
    print(f" Expected: {amount} AVAX, Received: {balance} AVAX")
    print(f" Valid range: [{amount- Decimal(0.004)}, {amount+Decimal(0.004)}]")

    # Check if the balance is within the acceptable range
    if abs(amount-balance)<=tolerance_percentage:
        print(f"✅ The transaction sent approximately {amount} {currency} as expected.")
        return 1
    else:
        print(f"❌ The transaction sent {balance} {currency}, but {amount} {currency} was expected (accounting for fees).")
        return 0




def createWallet():
    wallet = createWalletAvax.createWalletAavax()
    pK, wA = wallet
    return [pK, wA]


def validateApi(api_key,currency):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="crypto_db"
    )
    cursor = conn.cursor()
    if currency == "AVAX":
        cursor.execute(f"SELECT address, webhook_url, email FROM crypto_addresses WHERE api_key = '{api_key}';")
    elif currency == "USDT":
        cursor.execute(f"SELECT address_USDT_TRC20, webhook_url, email FROM crypto_addresses WHERE api_key = '{api_key}';")
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0], result[1], result[2]
    else:
        return None

def if_transaction_exists(transaction_id):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="crypto_db"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE transaction_id = %s", (transaction_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        return True
    else:
        return False

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)  
