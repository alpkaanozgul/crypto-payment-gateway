from eth_account import Account

from web3 import Web3



# 1️⃣ Connect to Avalanche Fuji Testnet RPC
fuji_rpc_url = 'https://api.avax-test.network/ext/bc/C/rpc'
web3 = Web3(Web3.HTTPProvider(fuji_rpc_url))

def getBalance(address):
    # Check if connected
    if web3.is_connected():
        print("✅ Connected to the Avalanche Fuji Testnet")
    else:
        print("❌ Failed to connect to the Avalanche Fuji Testnet")

    # 2️⃣ Specify the wallet address you want to check (replace with your actual public address)
    wallet_address = f"{address}"  # Example address

    # 3️⃣ Get the balance of the wallet (in Wei)
    balance_wei = web3.eth.get_balance(wallet_address)

    # 4️⃣ Convert Wei to AVAX (1 AVAX = 10^18 Wei)
    balance_avax = web3.from_wei(balance_wei, 'ether')

    # Print the wallet balance
    return balance_avax