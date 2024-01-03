import os
from dotenv import load_dotenv
import requests
from datetime import datetime

#Connecting to ENV file
os.chdir('C:/Users/jeron/OneDrive/Desktop/Inter/DecentDAO/DecentDAO_Accounting') #Your CWD
load_dotenv()


init_bal = 1097499 + 741571

decent_adrs = '0xD26c85D435F02DaB8B220cd4D2d398f6f646e235'

credential = 'ETHERSCAN_API_KEY'
base_url = "http://api.etherscan.io"
start_block = 18493528  #2 months back



api_key =  os.environ.get(credential)


response = requests.get(f"{base_url}/api?module=proxy&action=eth_blockNumber&apikey={api_key}").json()
block_height = int(response['result'], 16)

print()
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


tot_value = 0

with open("ledger.txt", "r+", encoding="utf-8") as ledger:
    lines = ledger.readlines()
    line = lines[0]
    if "ledger" in line:
        #print("CONTENTS TO ERASE.....")
        ledger.truncate(0)
        ledger.close()

with open("ledger.txt", "r+", encoding="utf-8") as ledger:
    ledger.write("; -*- ledger -*-\n")
    ledger.write("2023/12/01 * Treasury Balance\n")
    ledger.write(f"  Assets:Treasury:USDC                      ${f'{round(init_bal, 1):,}'}\n")
    ledger.write(f"  Assets:Treasury:PAX                       $2,315,692\n")
    ledger.write(f"  Assets:Treasury:DAI                       $823,409\n")
    ledger.write(f"  Assets:Treasury:WBTC:6.954                $313,729\n")
    ledger.write(f"  Assets:Treasury:USDT                      $88,231\n")

    ledger.write("  Equity:InitialBalance\n\n\n")


    for txn in response['result']:

        date = datetime.fromtimestamp(int(txn['timeStamp'])).strftime("%Y/%m/%d")
        value = round(int(txn['value']) / 10 ** int(txn['tokenDecimal']), 2)

        tot_value += value
        token = txn['tokenName']

        if "gift" in token or "𝐔𝐒𝐃 𝐂𝐨𝐢𝐧" in token:
            pass #Fake tokens
        else:
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
                elif value < 300:
                    ledger.write(F"{date} Other Expenses\n")
                    ledger.write(f"   Expenses:Deductible Business Exp.   ${f'{value:,}'}\n")
                elif value < 500:
                    ledger.write(F"{date} Team meet 2023.\n")
                    ledger.write(f"   Expenses:Travel   ${f'{value:,}'}\n")
                ledger.write(f"   Assets:Treasury:{token}   -${f'{value:,}'}\n\n\n")


            else:
                txn_type = "Input"
                from_adrs = f"Client {txn['from'][:5]}...{txn['from'][38:]}"

                if value > 50:
                    ledger.write(f"{date} Financial Service Fees\n")
                    ledger.write(f"   Assets:Treasury:{token}   ${f'{value:,}'}\n")
                    ledger.write(f"   Income:Services:{from_adrs}   -${f'{value:,}'}\n\n\n")
                else:
                    ledger.write(f"{date} Unknown Input Trxn\n")
                    ledger.write(f"   Assets:Treasury:{token}   ${f'{value:,}'}\n")
                    ledger.write(f"   Income:{from_adrs}   -${f'{value:,}'}\n\n\n")

print("---")
print(f"Final USDC balance in Safe: ${f'{round(init_bal - tot_value, 2):,}'}")
print("---")
print()
print("Writing all txns into a ledger.txt file...")
print()
print("Done !")
print("Run comands on Ledger-CLI:\n")
print("     ledger -f ledger.txt balance -> Checking final balances.\n")
print("     ledger -w -f ledger.txt bal ^Assets ^Expenses -> Checking balances of specific accounts.\n")
print("     ledger r -M -f ledger.txt -- period-sort total Expenses:Payroll -> Checking Payroll.")
ledger.close()

