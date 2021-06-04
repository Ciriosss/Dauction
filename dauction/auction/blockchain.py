from web3 import Web3


ganache_url = "HTTP://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

def newAccount(account,privateKey):

   ETHaccount = web3.eth.account.privateKeyToAccount(privateKey)
   account.address = ETHaccount.address
   account.encrypt = ETHaccount.encrypt('start2impact')

   account.save()

def transferETH(accountFrom,addressTo,amount):
    str = accountFrom.encrypt
    encrypt = str.replace("\'", "\"")
    privateKey = web3.eth.account.decrypt(encrypt, "start2impact")
    addressFrom = accountFrom.address



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
    return (web3.toHex(tx_hash))


def signedAuction(jsonHash):

    address = '0x6D5C772413f1E00C01F5803d970C72397a7A130b'
    privateKey = '72f178d89433fe470e10cbd16496b5485ffb5cf5695feba80d993606d7fde48e'
    nonce = web3.eth.getTransactionCount(address)
    gasPrice = web3.eth.gasPrice
    value = web3.toWei(0, 'ether')
    signedTx = web3.eth.account.signTransaction(dict(
        nonce = nonce,
        gasPrice = gasPrice,
        gas = 100000,
        to = '0x6D5C772413f1E00C01F5803d970C72397a7A130b',
        value = value,
        data = jsonHash.encode('utf-8')
    ),privateKey)
    tx = web3.eth.sendRawTransaction(signedTx.rawTransaction)
    txId = web3.toHex(tx)
    return(txId)

def getBalance(address):
    wei = web3.eth.getBalance(address)
    balance = web3.fromWei(wei, 'ether')
    return round(balance, 4)