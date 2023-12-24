import os
from dotenv import load_dotenv
from web3 import Web3

#Connecting to ENV file
os.chdir('C:/Users/jeron/OneDrive/Desktop/Inter/DecentDAO/DecentDAO_Accounting') #Your CWD
load_dotenv()

CHAINSTACK_HTTPS_PROVIDER = os.environ.get('CHAINSTACK_HTTPS_PROVIDER')

#Creating Web3 instance
w3 = Web3(Web3.HTTPProvider(CHAINSTACK_HTTPS_PROVIDER))

if w3.eth.chain_id == 100:
    print("Connected to Gnosis chain!")

    decent_addrs = '0xd26c85d435f02dab8b220cd4d2d398f6f646e235'[2:].lower() #Skip over 0x to check input data.
    current_block = 31282934 # w3.eth.block_number => if you need to monitor latest txns.
    untill_block = 31224790 #Block height from two months back.

    for height in reversed(range(untill_block, current_block)):
        block = w3.eth.get_block(height, True)

        """   DOES NOT WORK !   """
        #if transaction['to'] == decent_addrs or transaction['from'] == decent_addrs:

        for txn in block.transactions:
            if decent_addrs in str(txn['input'].hex()):
                print()
                print("Found a Gnosis Safe transaction from the address.")
                print(txn)










else:
    print("Failed to connect to Gnosis chain.")

