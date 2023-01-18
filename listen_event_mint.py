from web3 import Web3
import asyncio
import json
import os
from pymongo import MongoClient

from dotenv import load_dotenv

load_dotenv()

provider = Web3.HTTPProvider(os.getenv('PROVIDER'))
web3 = Web3(provider)
print(web3.isConnected())
print(os.getenv('MONGO_URI'))
mdb = MongoClient(os.getenv('MONGO_URI_SPEC'))



# this contract has been deployed on the goerli net
# contract_address_saturn_box = os.getenv('ADDRESS_SATURN_BOX')
contract_address_saturn_mkp = os.getenv('ADDRESS_SATURN_MKP')
# with open("./src/abi/abiSaturnBox.json", "r") as f:
#     contract_abi_saturn_box = json.loads(f.read())
with open("./src/abi/abiSaturnMKP.json", "r") as f:
    contract_abi_saturn_mkp = json.loads(f.read())

# contract_saturn_box = web3.eth.contract(address=contract_address_saturn_box, abi=contract_abi_saturn_box)
contract_saturn_mkp = web3.eth.contract(address=contract_address_saturn_mkp, abi=contract_abi_saturn_mkp)

def handle_mint(event):
    args = event.get('args')
    tokenDetail = args.get('tokenDetail')
    agentDetail = tokenDetail[0]
    mdb["marketplace"]["token_info"].update_one(filter={
        "address": args.get('requester')
        },
        update ={
            "$set":{
                f"tokens.{agentDetail[0]}":{
                    "tokenId": agentDetail[0],
                    "agentId": agentDetail[1],
                    "isOnchain": agentDetail[2],
                    "baseRarity": agentDetail[3],
                    "rarity": agentDetail[4],
                    "level": agentDetail[5],
                    "damage": agentDetail[6],
                    "hp": agentDetail[7],
                    "evasion": agentDetail[8],
                    "armor": agentDetail[9],
                    "combo": agentDetail[10],
                    "precision": agentDetail[11],
                    "accuracy": agentDetail[12],
                    "counter": agentDetail[13],
                    "reversal": agentDetail[14],
                    "lock": agentDetail[15],
                    "disarm": agentDetail[16],
                    "speed": agentDetail[17]
                }
            }
        },
        upsert=True
        )

def handle_event(event):
    event_data = Web3.toJSON(event)
    print(event_data)
    handle_mint(json.loads(event_data))


async def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
        await asyncio.sleep(poll_interval)

def main():
    # event_doPurchaseBox = contract_saturn_box.events.doPurchaseBox.createFilter(fromBlock='latest')
    # event_requestOnChain = contract_saturn_mkp.events.requestOnChain.createFilter(fromBlock='latest')
    # event_toOffChain = contract_saturn_mkp.events.toOffChain.createFilter(fromBlock='latest')
    # event_toOnChain = contract_saturn_mkp.events.toOnChain.createFilter(fromBlock='latest')
    # event_doSellNFT = contract_saturn_mkp.events.doSellNFT.createFilter(fromBlock='latest')
    # event_doPurchaseNFT = contract_saturn_mkp.events.doPurchaseNFT.createFilter(fromBlock='latest')
    event_mintToken = contract_saturn_mkp.events.mintToken.createFilter(fromBlock='latest')


    loop = asyncio.get_event_loop()
    try:
        # loop.run_until_complete(asyncio.gather(log_loop(event_doPurchaseBox, 2)))
        # loop.run_until_complete(asyncio.gather(log_loop(event_requestOnChain, 2)))
        # loop.run_until_complete(asyncio.gather(log_loop(event_toOffChain, 2)))
        # loop.run_until_complete(asyncio.gather(log_loop(event_toOnChain, 2)))
        # loop.run_until_complete(asyncio.gather(log_loop(event_doSellNFT, 2)))
        # loop.run_until_complete(asyncio.gather(log_loop(event_doPurchaseNFT, 2)))
        loop.run_until_complete(asyncio.gather(log_loop(event_mintToken, 2)))
    finally:
        loop.close()

if __name__ == "__main__":
    main()