# Crypto Payment Gateway

## Overview

This project is a **Crypto Payment Gateway** that enables secure and seamless cryptocurrency transactions using AVAX and USDT. The gateway allows merchants and users to create wallets, check balances, and send cryptocurrency. The system also supports webhook notifications for transaction status updates.

---

## Disclaimer
 Important Notice: This project is for Testnet . While the functionality may be adapted for the Mainnet, please be aware that engaging with real currency on the Mainnet carries inherent financial risks.

Use at Your Own Risk:

This software is provided "as-is," without warranty of any kind, express or implied.

The creators, contributors, and maintainers of this project do not assume any responsibility for:

Financial losses or damages incurred while using this software.

Emotional distress or psychological harm resulting from its use.

Any activities conducted with this software, whether intentional or accidental, that violate legal or ethical standards.

Legal and Ethical Compliance:
Users are responsible for ensuring compliance with all relevant laws and regulations in their jurisdiction. Engaging in illegal activities, including but not limited to money laundering, fraud, or unauthorized access to systems, is strictly prohibited.

Acknowledgment of Risk:
By using this software, you acknowledge that you understand the potential risks involved and agree that the developers are not liable for any consequences arising from your use of the project.

## Features

* **Wallet Creation**: Generate new wallets for AVAX and USDT.
* **Balance Check**: Retrieve wallet balances for AVAX and TRC20 tokens (USDT).
* **Transaction Management**: Record, monitor, and update transaction statuses.
* **Webhook Support**: Notify users or systems about transaction status changes.
* **API Key Validation**: Ensure secure access with API keys.
* **Real-Time Monitoring**: Background process to check transaction statuses and manage timeouts.

---

## Prerequisites

* **Software/Technologies:**

  * Python 3.8+
  * Flask
  * MySQL
  * Requests library
  * A valid webhook URL for notifications (optional)

* **Blockchain Requirements:**

  * AVAX RPC Endpoint
  * TRC20 (USDT) blockchain connection

* **Packages Required**:
  Install the necessary Python packages:

  ```bash
  pip install flask mysql-connector-python requests
  ```

* **Database**:
  Set up a MySQL database and create a `crypto_db` database with the following table:

  ```sql
  CREATE TABLE transactions (
      transaction_id VARCHAR(255) PRIMARY KEY,
      timestamp DATETIME,
      address VARCHAR(255),
      amount DECIMAL(18, 8),
      email VARCHAR(255),
      code VARCHAR(10),
      currency VARCHAR(10),
      status VARCHAR(50)
  );

  CREATE TABLE crypto_addresses (
      api_key VARCHAR(255) PRIMARY KEY,
      code VARCHAR(10),
      webhook_url VARCHAR(255),
      email VARCHAR(255)
  );
  ```

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/alpkaanozgul/crypto-payment-gateway.git
   ```

2. Navigate to the project directory:

   ```bash
   cd crypto-payment-gateway
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:

   * Update the database connection credentials in the code (if required).
   * Run the provided SQL commands to create necessary tables.

5. Run the Flask application:

   ```bash
   python main.py
   ```

---

## API Endpoints

### 1. **Create Transaction**

**GET** `/api_key/<currency>/<float:wantAmmount>`

* Creates a new transaction for the specified currency and amount.

### 2. **Transaction Details**

**GET** `/num/detail/<transaction_id>`

* Returns details of a specific transaction.

### 3. **Transaction Status**

**GET** `/status/<transaction_id>`

* Retrieves the status of a transaction.

### 4. **Update Transaction Status**

**GET** `/update_status/<api_key>/<transaction_id>/<currency>/<status>`

* Updates the transaction status.

---

## Workflow

1. **Create Wallet**: Generates a wallet address and private key.
2. **Initiate Transaction**: Stores transaction details in the database and starts monitoring for payments.
3. **Check Payment**: A background thread checks the wallet for the expected amount. If received, the system transfers funds to the recipient's address.
4. **Webhook Notification**: Sends a webhook with the transaction status to the configured URL.
5. **Timeout Handling**: Cancels the transaction if the payment is not completed within 10 minutes.

---

## Example Usage

### Check Wallet Balance

```python
from getBalanceTRC20 import getBalanceTRC20

wallet = "TVboCPcoakS9g92MfArip8yK4uNxLq6JD6"
balance = getBalanceTRC20(wallet)
print(f"Wallet balance: {balance} USDT")
```

### Initiate a Transaction

Send a `GET` request to:

```bash
http://127.0.0.1:5000/<api_key>/AVAX/0.5
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact

For any issues or support, please contact:

* **Name**: Your Name
* **Email**: [your-email@example.com](mailto:your-email@example.com)
* **GitHub**: [https://github.com/your-username](https://github.com/your-username)
