from app import w3, contract_address, ktd_address
from web3.auto import Web3
import time

def transfer_KTD(num, address, private_key):
    w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/35b77298442b49168bbe5a150071dd9f"))
    account = w3.eth.account.privateKeyToAccount(private_key)
    nonce = w3.eth.getTransactionCount(account.address, "pending")
    file = open("app/static/ABI/KTD_ABI.json", "r")
    KorpusToken_Deposit = w3.eth.contract(
        Web3.toChecksumAddress(ktd_address),
        abi=file.read()
    )
    file.close()

    estimateGas = KorpusToken_Deposit.functions.transfer(address, num).estimateGas({
      'nonce': nonce, 'from': account.address, 'gasPrice': w3.toWei('2', 'gwei'), 'chainId': 3
    })

    transaction = KorpusToken_Deposit.functions.transfer(address, num).buildTransaction(
        {
            'nonce': nonce,
            'from': account.address,
            'gas': estimateGas,
            'gasPrice': w3.toWei('2', 'gwei'),
            'chainId': 3
        }
    )
    signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
    try:
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

        return txn_hash.hex(), True
    except Exception:
        return "Недопустимый адрес или недостаточно токенов.", False

def get_KTI_total(kti_address):
    file = open("app/static/ABI/KTI_ABI.json", "r")
    Korpus_KTI = w3.eth.contract(
      Web3.toChecksumAddress(kti_address),
      abi=file.read()
    )
    file.close()

    return Korpus_KTI.functions.totalSupply().call()

def get_KTD_total(ktd_address):
    file = open("app/static/ABI/KTD_ABI.json", "r")
    Korpus_KTD = w3.eth.contract(
      Web3.toChecksumAddress(ktd_address),
      abi=file.read()
    )
    file.close()

    return Korpus_KTD.functions.totalSupply().call()

def set_KTI_buyer(address, private_key):
    w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/35b77298442b49168bbe5a150071dd9f"))
    account = w3.eth.account.privateKeyToAccount(private_key)
    nonce = w3.eth.getTransactionCount(account.address, "pending")
    file = open("app/static/ABI/Contract_ABI.json", "r")
    KorpusContract = w3.eth.contract(
        Web3.toChecksumAddress(contract_address),
        abi=file.read()
    )
    file.close()

    estimateGas = KorpusContract.functions.addAddressToBuyers(address).estimateGas({
      'nonce': nonce, 'from': account.address, 'gasPrice': w3.toWei('2', 'gwei'), 'chainId': 3
    })

    transaction = KorpusContract.functions.addAddressToBuyers(address).buildTransaction(
        {
            'nonce': nonce,
            'from': account.address,
            'gas': estimateGas,
            'gasPrice': w3.toWei('2', 'gwei'),
            'chainId': 3
        }
    )
    signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
    try:
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        return txn_hash.hex(), True
    except Exception:
        return "Недопустимый адрес или недостаточно средств.", False

def set_KTD_seller(address, private_key):
    w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/35b77298442b49168bbe5a150071dd9f"))
    account = w3.eth.account.privateKeyToAccount(private_key)
    nonce = w3.eth.getTransactionCount(account.address)
    file = open("app/static/ABI/Contract_ABI.json", "r")
    KorpusContract = w3.eth.contract(
        Web3.toChecksumAddress(contract_address),
        abi=file.read()
    )
    file.close()

    estimateGas = KorpusContract.functions.addAddressToSellers(address).estimateGas({
      'nonce': nonce, 'from': account.address, 'gasPrice': w3.toWei('2', 'gwei'), 'chainId': 3
    })

    transaction = KorpusContract.functions.addAddressToSellers(address).buildTransaction(
        {
            'nonce': nonce,
            'from': account.address,
            'gas': estimateGas,
            'gasPrice': w3.toWei('2', 'gwei'),
            'chainId': 3
        }
    )
    signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
    try:
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        return txn_hash.hex(), True
    except Exception:
        return "Недопустимый адрес или недостаточно средств.", False

def sell_KTD(amount, private_key):
    try:
        value = int(amount)
    except ValueError:
        return 'Число токенов должно быть целым числом'
    if value > 0:
        w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/35b77298442b49168bbe5a150071dd9f"))
        account = w3.eth.account.privateKeyToAccount(private_key)
        nonce = w3.eth.getTransactionCount(account.address, "pending")
        file = open("app/static/ABI/KTD_ABI.json", "r")
        KorpusToken_Deposit = w3.eth.contract(
            Web3.toChecksumAddress(ktd_address),
            abi=file.read()
        )
        file.close()
        estimateGas = KorpusToken_Deposit.functions.approve(Web3.toChecksumAddress(contract_address), value).estimateGas({
          'nonce': nonce, 'from': account.address, 'gasPrice': w3.toWei('2', 'gwei'), 'chainId': 3
        })

        transaction = KorpusToken_Deposit.functions.approve(Web3.toChecksumAddress(contract_address), value).buildTransaction(
            {
                'nonce': nonce,
                'from': account.address,
                'gas': estimateGas,
                'gasPrice': w3.toWei('2', 'gwei'),
                'chainId': 3
            }
        )
        signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
        try:
            txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            transaction_hash = txn_hash.hex()
            while True:
                try:
                    receipt = w3.eth.getTransactionReceipt(transaction_hash)
                    if receipt is not None:
                        break
                except:
                    time.sleep(5)

            if receipt.status == 1:
                file = open("app/static/ABI/Contract_ABI.json", "r")
                KorpusContract = w3.eth.contract(
                    Web3.toChecksumAddress(contract_address),
                    abi=file.read()
                )
                file.close()
                nonce = w3.eth.getTransactionCount(account.address, "pending")
                estimateGas = KorpusContract.functions.sellKTD(value).estimateGas(
                    {'nonce': nonce, 'from': account.address, 'gasPrice': w3.toWei('2', 'gwei'), 'chainId': 3})
                transaction = KorpusContract.functions.sellKTD(value).buildTransaction(
                    {
                        'nonce': nonce,
                        'from': account.address,
                        'gas': estimateGas,
                        'gasPrice': w3.toWei('2', 'gwei'),
                        'chainId': 3
                    }
                )
                signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
                txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
                transaction_hash = txn_hash.hex()

                return transaction_hash, False
        except Exception as e:
            print(e)
            return "Недостаточно токенов на вашем счёте или на балансе смарт-контракта недостаточно эфира.", False
    else:
        return "Число токенов не должно быть меньше или равно нулю.", False

