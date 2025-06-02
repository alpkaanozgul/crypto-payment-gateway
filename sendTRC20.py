from tronpy import Tron
from tronpy.keys import PrivateKey

def sendTRC20(private_key, to_address, amount):
    print("sende girdi")

    
# Connect to Shasta testnet
    client = Tron(network="shasta")

    # Your private key and destination address
    

    # Create private key instance
    # Create private key instance - handle both string and PrivateKey inputs
    if isinstance(private_key, str):
        priv_key = PrivateKey(bytes.fromhex(private_key))
    else:
        priv_key = private_key

    # Get the account address from private key
    from_address = priv_key.public_key.to_base58check_address()
    print(f"from address: {from_address}")

    print(f"*-*-*-*-*- before amount: {amount}")
    # Amount to send (in SUN - 1 TRX = 1,000,000 SUN)
    amount = amount *1000000  # This will send 1 TRX
    print(f"*-*-*-*-*- after amount: {amount}")
    
   

    try:
        # Create and sign the transaction
        print(f"before txn")
        txn = (
            client.trx.transfer(from_address, to_address, amount)
            .build()
            .sign(priv_key)
        )
        

        # Broadcast the transaction
        result = txn.broadcast()
        print(f"result: {result}")

        # Print the transaction result
        print(f"Transaction successful!")
        print(f"Transaction ID: {result['txid']}")
        print(f"From: {from_address}")
        print(f"To: {to_address}")
        print(f"Amount: {amount/1000000} TRX")
        return result['txid']

    except Exception as e:

        print(f"An error occurred: {str(e)}, send address is {to_address}")
        return None

if __name__ == "__main__":
    sendTRC20("", "", 5)
