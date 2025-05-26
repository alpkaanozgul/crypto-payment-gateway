from eth_account import Account

# 1. Generate a new wallet (private key and address)

def createWalletAavax():
    
    account = Account.create()
    private_key = account.key.hex()  # Your private key (keep it safe, don't share it)
    public_address = account.address  # Your public wallet address


    return [private_key,public_address]