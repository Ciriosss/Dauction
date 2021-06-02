from web3 import Web3



ganache_url = "HTTP://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

addressFrom ="0x89de550dc8371ED5ef99AE687BB98d37C342D89C"
addressTo = "0x6D5C772413f1E00C01F5803d970C72397a7A130b"
privateKey = "fad5e2a0697029ac188ee440a9f5ff71b579e1356515c39ed4ea906da3f179a2"
amount = 979

nonce = web3.eth.getTransactionCount(addressFrom)
tx = {
        'nonce': nonce,
        'to': addressTo,
        'value': web3.toWei(amount, 'ether'),
        'gas': 2000000,
        'gasPrice': web3.toWei('50', 'gwei')
}
signed_tx = web3.eth.account.signTransaction(tx, privateKey)
tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
print (web3.toHex(tx_hash))