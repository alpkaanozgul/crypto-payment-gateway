import requests

def getBalanceTRC20(wallet_address):
    """
    Get TRC20 token balance for a given wallet address using Shasta testnet
    
    Args:
        wallet_address (str): The TRON wallet address
        
    Returns:
        float: The wallet balance in TRX
    """
    api_key = "get the api key"
    base_url = "https://api.shasta.trongrid.io"
    
    # Set up headers with API key
    headers = {
        "Accept": "application/json",
        "TRON-PRO-API-KEY": api_key
    }
    
    try:
        # Get account information
        endpoint = f"/v1/accounts/{wallet_address}"
        response = requests.get(base_url + endpoint, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
              # Debugging line to inspect raw response
            
            # If data is empty, set balance_trx to 0
            if not data.get('data'):
                print(f"No balance data found for address: {wallet_address}")
                balance_trx = 0
            else:
                # Get balance in SUN (smallest TRON unit)
                balance_sun = int(data['data'][0].get('balance', 0))
                
                # If no balance is found
                if balance_sun == 0:
                    print(f"No TRX found for address: {wallet_address}")
                    balance_trx = 0
                else:
                    # Convert from SUN to TRX (1 TRX = 1,000,000 SUN)
                    balance_trx = balance_sun / 1_000_000
            
            return balance_trx
        else:
            print(f"Error: API request failed with status code {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None

# Example usage
if __name__ == "__main__":
    # Example wallet address (replace with actual address)
    wallet = "TVboCPcoakS9g92MfArip8yK4uNxLq6JD6"
    
    balance = getBalanceTRC20(wallet)
    if balance is not None:
        print(f"Wallet balance: {balance} TRX")
