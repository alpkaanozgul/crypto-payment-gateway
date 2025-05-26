from web3 import Web3

# 1️⃣ Connect to the Avalanche Fuji Testnet RPC
fuji_rpc_url = 'https://api.avax-test.network/ext/bc/C/rpc'
web3 = Web3(Web3.HTTPProvider(fuji_rpc_url))

def sendAvax(sender_private_key,recipient_address,amount_in_avax):

    # Check if connected to the network
    if web3.is_connected():
        print("✅ Connected to the Avalanche Fuji Testnet")
    else:
        print("❌ Failed to connect to the Avalanche Fuji Testnet")

    # 2️⃣ Sender's Wallet Details
    account = web3.eth.account.from_key(sender_private_key)
    sender_address = account.address  # Corrected the sender's public address

   

    # 5️⃣ Convert AVAX to Wei (since AVAX follows the Ethereum standard)
    amount_in_wei = web3.to_wei(amount_in_avax, 'ether')

    # 6️⃣ Get the nonce (to keep track of transactions for the sender's wallet)
    nonce = web3.eth.get_transaction_count(sender_address)

    # 7️⃣ Create the transaction object
    transaction = {
        'nonce': nonce,  # unique transaction count for this sender's wallet
        'to': recipient_address,  # recipient address
        'value': amount_in_wei,  # amount of AVAX (in Wei)
        'gas': 21000,  # Standard gas limit for simple transfers
        'gasPrice': web3.to_wei('25', 'gwei'),  # Gas price (25 gwei is enough for the Fuji testnet)
        'chainId': 43113  # Chain ID for Fuji Testnet (Mainnet = 43114)
    }

    # 8️⃣ Sign the transaction with the sender's private key
    signed_txn = web3.eth.account.sign_transaction(transaction, sender_private_key)

    # 9️⃣ Send the raw signed transaction to the network
    txn_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)


    print(txn_hash)
    # 🔟 Print the transaction hash to track it on the block explorer
    return txn_hash.hex()
