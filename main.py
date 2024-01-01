import os
from dotenv import load_dotenv
import requests
from datetime import datetime

#Connecting to ENV file
os.chdir('C:/Users/jeron/OneDrive/Desktop/Inter/DecentDAO/DecentDAO_Accounting') #Your CWD
load_dotenv()

chain = input("What chain would you like to have the accounting done for (Eth or Gnosis) ?")
init_bal = float(input("What is the initial balance in USDC for the Treasury ?"))

decent_adrs = '0xD26c85D435F02DaB8B220cd4D2d398f6f646e235'

if chain.lower() == 'eth':
    credential = 'ETHERSCAN_API_KEY'
    base_url = "http://api.etherscan.io"
    start_block = 18472175 #2 months back
else:
    credential = 'GNOSISSCAN_API_KEY'
    base_url = "https://api.gnosisscan.io"
    start_block = 31224790 #2 months back


api_key =  os.environ.get(credential)


response = requests.get(f"{base_url}/api?module=proxy&action=eth_blockNumber&apikey={api_key}").json()
block_height = int(response['result'], 16)


print("Fetching all ERC-20 token transactions from the Decent DAO Treasury for the last 2 Months...")
print()
response = requests.get(
    f"{base_url}/api",
    params={
        "module": "account",
        "action": "tokentx",
        "address": decent_adrs,
        "sort": "asc",
        "startblock":start_block,
        "endblock":block_height, #two months back untill today...
        "apikey": api_key,
    },
).json()



with open("ledger.txt", "a", encoding="utf-8") as ledger:

    ledger.write("; -*- ledger -*-\n")
    ledger.write("2023/12/01 * Initial Treasury Balance\n")
    ledger.write(f"  Assets:Treasury:USDC                      ${f'{round(init_bal, 1):,}'}\n")
    ledger.write("  Equity:SeriesA\n\n\n")


    for txn in response['result']:

        date = datetime.fromtimestamp(int(txn['timeStamp'])).strftime("%Y/%m/%d")
        value = round(int(txn['value']) / 10 ** int(txn['tokenDecimal']), 2)

        token = txn['tokenName']

        if "USDC" in token or "USD" in token:
            token = "USDC"
        else:
            token = "USDT"

        txn_fee = round(int(txn['gasPrice']) * int(txn['gasUsed']) / 10**18, 10)

        if txn['from'] == decent_adrs.lower():

            txn_type = "Output"
            to_adrs = f"Providers: {txn['from'][:5]}...{txn['from'][38:]}"

            if value > 1000:
                ledger.write(f"{date} Payroll\n")
                ledger.write(f"   Expenses:Payroll   ${f'{value:,}'}\n")
            elif value > 500:
                ledger.write(F"{date} Providers\n")
                ledger.write(f"   Expenses:{to_adrs}   ${f'{value:,}'}\n")
            elif value < 500:
                ledger.write(F"{date} Other Expenses\n")
                ledger.write(f"   Expenses:Deductible Business Exp.   ${f'{value:,}'}\n")
            ledger.write(f"   Assets:Treasury:{token}   -${f'{value:,}'}\n\n\n")


        else:
            txn_type = "Input"
            from_adrs = f"Client {txn['from'][:5]}...{txn['from'][38:]}"

            if value > 50:
                ledger.write(f"{date} Financial Service Fees\n")
                ledger.write(f"   Assets:Treasury:{token}   ${f'{value:,}'}\n")
                ledger.write(f"   Invoices:{from_adrs}   -${f'{value:,}'}\n\n\n")
            else:
                ledger.write(f"{date} Unknown Input Trxn\n")
                ledger.write(f"   Assets:Treasury:{token}   ${f'{value:,}'}\n")
                ledger.write(f"   Invoices:{from_adrs}   -${f'{value:,}'}\n\n\n")


print("Writing all txns into a ledger.txt file...")
print()
print("Done !")
print("Run comands:\n")
print("     ledger -f ledger.txt balance -> Checking final balances.\n")
print("     ledger -w -f ledger.txt bal ^Assets ^Expenses ^Invoices -> Checking balances of specific accounts.\n")
print("     ledger r -M -f ledger.txt -- period-sort total Expenses:Payroll -> Checking Payroll.")
ledger.close()