import subprocess
import json
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy
from dotenv import load_dotenv
from bit import PrivateKeyTestnet 
from bit.network import NetworkAPI
from web3.eth import Account
from constants import *
import os 
import web3
load_dotenv()

menmonic  = os.getenv("MNEMONIC")
print(menmonic)

def derive_wallets(menmonic, coin, numderive):
    command = f'php ./hd-wallet-derive/hd-wallet-derive.php -g --format=json --coin={coin} --mnemonic={menmonic} --cols=path,address,privkey,pubkey --numderive={numderive}'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()

    keys = json.loads(output)
    return keys

def priv_key_to_account(coin, priv_key):
    if coin == 'ETH':
        return Account.privateKeyToAccount(priv_key)
    elif coin == 'BTCTEST':
        return PrivateKeyTestnet(priv_key)
    else:
        print('Cryptocoin is not valid')
    return None

def create_tx(coin, account, to, amount):
    if coin == 'ETH':
        transaction_obj = {
            'to': to,
            'from': account,
            'value':amount,
            'gas':web3.eth.estimate_gas({
                'to': to,
                'from': account,
                'value': amount
            }),
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(web3.eth.coinbase),
            'chainID': 577
        }
        return transaction_obj
    elif coin == 'BTCTEST':
        return PrivateKeyTestnet.prepare_transaction(account, [(to, amount, BTC)])
    else:
        print('Cryptocoin is not valid')
        return None
    
def sent_tx(coin, account, to, amount):
    raw_transaction = create_tx(coin, account, to, amount)
    if coin == 'ETH':
        signed_trans = web3.eth.sign_transaction(raw_transaction)
        return web3.eth.sendRawTransaction(signed_trans)
    elif coin == 'BTCTEST':
        signed_trans = PrivateKeyTestnet.sign_transaction(raw_transaction)
        return NetworkAPI.broadcast_tx_testnet(signed_trans)
    else:
        print('Cryptocoin is not valid')
        return None
    
coins = {
    'eth': derive_wallets(menmonic, ETH, 3),
    'btc-test': derive_wallets(menmonic, BTCTEST, 3)
}
