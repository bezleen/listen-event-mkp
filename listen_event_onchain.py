from web3 import Web3
import asyncio
import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# provider = Web3.HTTPProvider(os.getenv('PROVIDER'))
web3 = Web3(Web3.HTTPProvider(os.getenv('PROVIDER')))
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

def encode(token_detail):
    bit_index = 30
    value = 0
    value = value | token_detail.get("tokenId")
    value = value | (token_detail.get("agentId") << bit_index)
    bit_index += 4
    value = value | (token_detail.get("isOnchain") << bit_index)
    bit_index += 1
    value = value | (token_detail.get("baseRarity") << bit_index)
    bit_index += 3
    value = value | (token_detail.get("rarity") << bit_index)
    bit_index += 3
    value = value | (token_detail.get("level") << bit_index)
    bit_index += 9
    value = value | (token_detail.get("damage") << bit_index)
    bit_index += 10
    value = value | (token_detail.get("hp") << bit_index)
    bit_index += 12
    value = value | (token_detail.get("evasion") << bit_index)
    bit_index += 12
    value = value | (token_detail.get("armor") << bit_index)
    bit_index += 10
    value = value | (token_detail.get("combo") << bit_index)
    bit_index += 10
    value = value | (token_detail.get("precision") << bit_index)
    bit_index += 12
    value = value | (token_detail.get("accuracy") << bit_index)
    bit_index += 12
    value = value | (token_detail.get("counter") << bit_index)
    bit_index += 10
    value = value | (token_detail.get("reversal") << bit_index)
    bit_index += 10
    value = value | (token_detail.get("lock") << bit_index)
    bit_index += 10
    value = value | (token_detail.get("disarm") << bit_index)
    bit_index += 10
    value = value | (token_detail.get("speed") << bit_index)
    # bit_index += 10
    return value

def transact(token_id,detail_encoded):
    print("sendding...")
    abi = contract_abi_saturn_mkp
    address = os.getenv("ADMIN_ADDRESS")
    private_key = os.getenv("PRIVATE_KEY")
    nonce = web3.eth.get_transaction_count(address)
    chain_id = os.getenv("CHAIN_ID")
    # web3 = Web3(Web3.HTTPProvider(os.getenv('PROVIDER')))
    contract = web3.eth.contract(address=address, abi=abi)
    onchain_transaction = contract.functions.onChain(token_id,detail_encoded).buildTransaction(
        {"chainId":web3.eth.chain_id,"gasPrice": web3.eth.gas_price, "from":address, "nonce": nonce})
    sign_transaction = web3.eth.account.sign_transaction(onchain_transaction, private_key = private_key)
    send_transaction = web3.eth.send_raw_transaction(sign_transaction.rawTransaction)
    
    result = web3.eth.wait_for_transaction_receipt(send_transaction)
    print(result)


def handle_onchain(event):
    # event = {"args":{"requester":"0x727bEd465442B29A6F8b79AC872a46a315A90552", "tokenId":4}}
    args = event.get('args')
    requester = args.get('requester')
    tokenId = args.get('tokenId')
    meta_data = mdb["marketplace"]["token_info"].find_one({"address":requester})
    detail = meta_data.get("tokens").get(f"{tokenId}")
    token_detail_encode = encode(detail)
    print(token_detail_encode)
    # request contract
    print("adadasd")
    transact(tokenId,token_detail_encode)

def handle_event(event):
    event_data = Web3.toJSON(event)
    print(event_data)
    handle_onchain(json.loads(event_data))


async def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
        await asyncio.sleep(poll_interval)

def main():
    # event_doPurchaseBox = contract_saturn_box.events.doPurchaseBox.createFilter(fromBlock='latest')
    event_requestOnChain = contract_saturn_mkp.events.requestOnChain.createFilter(fromBlock='latest')
    # event_toOffChain = contract_saturn_mkp.events.toOffChain.createFilter(fromBlock='latest')
    # event_toOnChain = contract_saturn_mkp.events.toOnChain.createFilter(fromBlock='latest')
    # event_doSellNFT = contract_saturn_mkp.events.doSellNFT.createFilter(fromBlock='latest')
    # event_doPurchaseNFT = contract_saturn_mkp.events.doPurchaseNFT.createFilter(fromBlock='latest')
    # event_mintToken = contract_saturn_mkp.events.mintToken.createFilter(fromBlock='latest')


    loop = asyncio.get_event_loop()
    try:
        # loop.run_until_complete(asyncio.gather(log_loop(event_doPurchaseBox, 2)))
        loop.run_until_complete(asyncio.gather(log_loop(event_requestOnChain, 2)))
        # loop.run_until_complete(asyncio.gather(log_loop(event_toOffChain, 2)))
        # loop.run_until_complete(asyncio.gather(log_loop(event_toOnChain, 2)))
        # loop.run_until_complete(asyncio.gather(log_loop(event_doSellNFT, 2)))
        # loop.run_until_complete(asyncio.gather(log_loop(event_doPurchaseNFT, 2)))
        # loop.run_until_complete(asyncio.gather(log_loop(event_mintToken, 2)))
    finally:
        loop.close()

if __name__ == "__main__":
    # handle_onchain(1)
    main()