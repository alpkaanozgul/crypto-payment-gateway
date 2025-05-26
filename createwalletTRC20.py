from tronpy import Tron
from tronpy.keys import PrivateKey

def createWalletTRC20():
    # Step 1: Connect to Tron Testnet
    client = Tron(network='shasta')  # 'nile' is the name of Tron's testnet

    # Step 2: Generate a Wallet
    private_key = PrivateKey.random()
    public_key = private_key.public_key.to_base58check_address()
    address = private_key.public_key.to_base58check_address()

    print("New Wallet Created:")
    print(f"Address: {address}")
    print(f"Private Key: {private_key}")
    return private_key, address


if __name__ == "__main__":
    createWalletTRC20()
