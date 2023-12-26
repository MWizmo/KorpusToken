from app import w3, contract_address, ktd_address, kti_address, infura_url, chain_id, db# admin_wallet_address, db
from app.models import TokenExchangeRate
from web3.auto import Web3
import time
import datetime

import os

def transfer_KTD(num, address, private_key):
    w3 = Web3(Web3.HTTPProvider(infura_url))
    account = w3.eth.account.privateKeyToAccount(private_key)
    nonce = w3.eth.getTransactionCount(account.address, "pending")
    file = open("app/static/ABI/KTD_ABI.json", "r")
    KorpusToken_Deposit = w3.eth.contract(
        Web3.toChecksumAddress(ktd_address),
        abi=file.read()
    )
    file.close()

    estimateGas = KorpusToken_Deposit.functions.transfer(address, num).estimateGas({
      'nonce': nonce, 'from': account.address, 'gasPrice': w3.toWei('35', 'gwei'), 'chainId': chain_id
    })

    transaction = KorpusToken_Deposit.functions.transfer(address, num).buildTransaction(
        {
            'nonce': nonce,
            'from': account.address,
            'gas': estimateGas,
            'gasPrice': w3.toWei('35', 'gwei'),
            'chainId': chain_id
        }
    )
    signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
    try:
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

        return txn_hash.hex(), False
    except Exception:
        return "Недопустимый адрес или недостаточно токенов.", True

def get_main_contract_KTI_balance():
    file = open("app/static/ABI/KTI_ABI.json", "r")
    Korpus_KTI = w3.eth.contract(
      Web3.toChecksumAddress(kti_address),
      abi=file.read()
    )
    file.close()

    return Korpus_KTI.functions.balanceOf(Web3.toChecksumAddress(contract_address)).call()

def get_main_contract_KTD_balance():
    file = open("app/static/ABI/KTD_ABI.json", "r")
    Korpus_KTD = w3.eth.contract(
      Web3.toChecksumAddress(ktd_address),
      abi=file.read()
    )
    file.close()

    return Korpus_KTD.functions.balanceOf(Web3.toChecksumAddress(contract_address)).call()

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

def set_KTI_buyer(address, limit, private_key):
    w3 = Web3(Web3.HTTPProvider(infura_url))
    account = w3.eth.account.privateKeyToAccount(private_key)
    nonce = w3.eth.getTransactionCount(account.address, "pending")
    file = open("app/static/ABI/Contract_ABI.json", "r")
    KorpusContract = w3.eth.contract(
        Web3.toChecksumAddress(contract_address),
        abi=file.read()
    )
    file.close()

    estimateGas = KorpusContract.functions.addAddressToBuyers(address, limit).estimateGas({
      'nonce': nonce, 'from': account.address, 'gasPrice': w3.toWei('35', 'gwei'), 'chainId': chain_id
    })

    transaction = KorpusContract.functions.addAddressToBuyers(address, limit).buildTransaction(
        {
            'nonce': nonce,
            'from': account.address,
            'gas': estimateGas,
            'gasPrice': w3.toWei('35', 'gwei'),
            'chainId': chain_id
        }
    )
    signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
    try:
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        return txn_hash.hex(), False
    except Exception:
        return "Недопустимый адрес или недостаточно средств.", True

def set_KTD_seller(address, limit, private_key):
    w3 = Web3(Web3.HTTPProvider(infura_url))
    account = w3.eth.account.privateKeyToAccount(private_key)
    nonce = w3.eth.getTransactionCount(account.address, "pending")
    file = open("app/static/ABI/Contract_ABI.json", "r")
    KorpusContract = w3.eth.contract(
        Web3.toChecksumAddress(contract_address),
        abi=file.read()
    )
    file.close()

    estimateGas = KorpusContract.functions.addAddressToSellers(address, limit).estimateGas({
      'nonce': nonce, 'from': account.address, 'gasPrice': w3.toWei('35', 'gwei'), 'chainId': chain_id
    })

    transaction = KorpusContract.functions.addAddressToSellers(address, limit).buildTransaction(
        {
            'nonce': nonce,
            'from': account.address,
            'gas': estimateGas,
            'gasPrice': w3.toWei('35', 'gwei'),
            'chainId': chain_id
        }
    )
    signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
    try:
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        return txn_hash.hex(), False
    except Exception:
        return "Недопустимый адрес или недостаточно средств.", True

def sell_KTD(amount, private_key):
    try:
        value = int(amount)
    except ValueError:
        return 'Число токенов должно быть целым числом'
    if value > 0:
        w3 = Web3(Web3.HTTPProvider(infura_url))
        account = w3.eth.account.privateKeyToAccount(private_key)
        nonce = w3.eth.getTransactionCount(account.address, "pending")
        file = open("app/static/ABI/KTD_ABI.json", "r")
        KorpusToken_Deposit = w3.eth.contract(
            Web3.toChecksumAddress(ktd_address),
            abi=file.read()
        )
        file.close()
        estimateGas = KorpusToken_Deposit.functions.increaseAllowance(Web3.toChecksumAddress(contract_address), value).estimateGas({
          'nonce': nonce, 'from': account.address, 'gasPrice': w3.toWei('35', 'gwei'), 'chainId': chain_id
        })

        transaction = KorpusToken_Deposit.functions.increaseAllowance(Web3.toChecksumAddress(contract_address), value).buildTransaction(
            {
                'nonce': nonce,
                'from': account.address,
                'gas': estimateGas,
                'gasPrice': w3.toWei('35', 'gwei'),
                'chainId': chain_id
            }
        )
        signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
        try:
            txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            transaction_hash = txn_hash.hex()
            file = open("app/static/ABI/Contract_ABI.json", "r")
            KorpusContract = w3.eth.contract(
                Web3.toChecksumAddress(contract_address),
                abi=file.read()
            )
            file.close()
            nonce = w3.eth.getTransactionCount(account.address, "pending")
            estimateGas = KorpusContract.functions.sellKTD(value).estimateGas(
                {'nonce': nonce, 'from': account.address, 'gasPrice': w3.toWei('35', 'gwei'), 'chainId': chain_id})
            transaction = KorpusContract.functions.sellKTD(value).buildTransaction(
                {
                    'nonce': nonce,
                    'from': account.address,
                    'gas': estimateGas,
                    'gasPrice': w3.toWei('35', 'gwei'),
                    'chainId': chain_id
                }
            )
            signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
            txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            transaction_hash = txn_hash.hex()

            return transaction_hash, False
        except Exception as e:
            print(e)
            return "Что-то пошло не так. Попробуйте позже.", True
    else:
        return "Число токенов не должно быть меньше или равно нулю.", True

def set_KTD_price(price, private_key):
    w3 = Web3(Web3.HTTPProvider(infura_url))
    account = w3.eth.account.privateKeyToAccount(private_key)
    nonce = w3.eth.getTransactionCount(account.address, "pending")
    file = open("app/static/ABI/Contract_ABI.json", "r")
    KorpusContract = w3.eth.contract(
        Web3.toChecksumAddress(contract_address),
        abi=file.read()
    )
    file.close()

    estimateGas = KorpusContract.functions.setSellPriceKTD(price).estimateGas(
      {'nonce': nonce, 'from': account.address, 'gasPrice': w3.toWei('35', 'gwei'), 'chainId': chain_id}
    )

    transaction = KorpusContract.functions.setSellPriceKTD(price).buildTransaction(
        {
            'nonce': nonce,
            'from': account.address,
            'gas': estimateGas,
            'gasPrice': w3.toWei('35', 'gwei'),
            'chainId': chain_id
        }
    )
    signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
    try:
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        transaction_hash = txn_hash.hex()

        return transaction_hash, False
    except Exception:
        eth_error = "Недопустимый адрес, цена или недостаточно средств."
        return eth_error, True

def set_KTI_price(price, private_key):
    w3 = Web3(Web3.HTTPProvider(infura_url))
    account = w3.eth.account.privateKeyToAccount(private_key)
    nonce = w3.eth.getTransactionCount(account.address, "pending")
    file = open("app/static/ABI/Contract_ABI.json", "r")
    KorpusContract = w3.eth.contract(
        Web3.toChecksumAddress(contract_address),
        abi=file.read()
    )
    file.close()

    estimateGas = KorpusContract.functions.setBuyPriceKTI(price).estimateGas(
      {'nonce': nonce, 'from': account.address, 'gasPrice': w3.toWei('35', 'gwei'), 'chainId': chain_id}
    )

    transaction = KorpusContract.functions.setBuyPriceKTI(price).buildTransaction(
        {
            'nonce': nonce,
            'from': account.address,
            'gas': estimateGas,
            'gasPrice': w3.toWei('35', 'gwei'),
            'chainId': chain_id
        }
    )
    signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
    try:
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        transaction_hash = txn_hash.hex()

        return transaction_hash, False
    except Exception:
        eth_error = "Недопустимый адрес, цена или недостаточно средств."
        return eth_error, True

def mint_KTD(amount, receiver, private_key):
  if amount > 0:
    w3 = Web3(Web3.HTTPProvider(infura_url))
    account = w3.eth.account.privateKeyToAccount(private_key)
    nonce = w3.eth.getTransactionCount(account.address, "pending")
    file = open("app/static/ABI/KTD_ABI.json", "r")
    KorpusToken_Deposit = w3.eth.contract(
      Web3.toChecksumAddress(ktd_address),
      abi=file.read()
    )
    file.close()

    estimateGas = KorpusToken_Deposit.functions.mint(receiver, amount).estimateGas(
      {'nonce': nonce, 'from': account.address, 'gasPrice': w3.toWei('35', 'gwei'), 'chainId': chain_id}
    )

    transaction = KorpusToken_Deposit.functions.mint(receiver, amount).buildTransaction(
      {
        'nonce': nonce,
        'from': account.address,
        'gas': estimateGas,
        'gasPrice': w3.toWei('35', 'gwei'),
        'chainId': chain_id
      }
    )
    signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
    try:
      txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
      transaction_hash = txn_hash.hex()

      return transaction_hash, False
    except Exception as e:
      return "Некорректный адрес.", True
  else:
    return "Число токенов должно быть больше нуля.", True

def mint_KTI(amount, receiver, private_key):
  print(private_key)
  if amount > 0:
    w3 = Web3(Web3.HTTPProvider(infura_url))
    account = w3.eth.account.privateKeyToAccount(private_key)
    nonce = w3.eth.getTransactionCount(account.address, "pending")
    file = open("app/static/ABI/KTI_ABI.json", "r")
    KorpusToken_Investment = w3.eth.contract(
      Web3.toChecksumAddress(kti_address),
      abi=file.read()
    )
    file.close()

    estimateGas = KorpusToken_Investment.functions.mint(receiver, amount).estimateGas(
      {'nonce': nonce, 'from': account.address, 'gasPrice': w3.toWei('35', 'gwei'), 'chainId': chain_id}
    )

    transaction = KorpusToken_Investment.functions.mint(receiver, amount).buildTransaction(
      {
        'nonce': nonce,
        'from': account.address,
        'gas': estimateGas,
        'gasPrice': w3.toWei('35', 'gwei'),
        'chainId': chain_id
      }
    )
    signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
    try:
      txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
      transaction_hash = txn_hash.hex()

      return transaction_hash, False
    except Exception:
      return "Некорректный адрес.", True
  else:
    return "Число токенов должно быть больше нуля.", True


def save_voting_to_blockchain(team, student, date, axis, points, private_key):
    w3 = Web3(Web3.HTTPProvider(infura_url))
    account = w3.eth.account.privateKeyToAccount(private_key)
    nonce = w3.eth.getTransactionCount(account.address, "pending")
    file = open("app/static/ABI/KTD_ABI.json", "r")
    KorpusToken_Deposit = w3.eth.contract(
      Web3.toChecksumAddress(ktd_address),
      abi=file.read()
    )
    file.close()

    estimateGas = KorpusToken_Deposit.functions.setStudentResult(team, student, date, axis, points).estimateGas(
      {'nonce': nonce, 'from': account.address, 'gasPrice': w3.toWei('35', 'gwei'), 'chainId': chain_id}
    )

    transaction = KorpusToken_Deposit.functions.setStudentResult(team, student, date, axis, points).buildTransaction(
      {
          'nonce': nonce,
          'from': account.address,
          'gas': estimateGas,
          'gasPrice': w3.toWei('35', 'gwei'),
          'chainId': chain_id
      }
    )
    signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
    try:
      txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
      transaction_hash = txn_hash.hex()
      
      return transaction_hash, False
    except Exception:
      return 'Некорректный адрес.', True

def increase_token_balance(address, amount):
    w3 = Web3(Web3.HTTPProvider(infura_url))
    private_key = os.environ.get('ADMIN_PRIVATE_KEY') or \
                  '56bc1794435c17242faddf14c51c2385537e4b1a047c9c49c46d5eddaff61a66'
    account = w3.eth.account.privateKeyToAccount(private_key)
    nonce = w3.eth.getTransactionCount(account.address, "pending")
    file = open("app/static/ABI/Contract_ABI.json", "r")
    KorpusContract = w3.eth.contract(
        Web3.toChecksumAddress(contract_address),
        abi=file.read()
    )
    file.close()

    estimateGas = KorpusContract.functions.increaseVirtualBalance(address, amount).estimateGas(
        {'nonce': nonce, 'from': account.address, 'gasPrice': w3.toWei('35', 'gwei'), 'chainId': chain_id}
    )

    transaction = KorpusContract.functions.increaseVirtualBalance(address, amount).buildTransaction(
        {
            'nonce': nonce,
            'from': account.address,
            'gas': estimateGas,
            'gasPrice': w3.toWei('35', 'gwei'),
            'chainId': chain_id
        }
    )
    signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
    try:
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        transaction_hash = txn_hash.hex()

        return transaction_hash, False
    except Exception:
        return 'Некорректный адрес.', True

def decrease_token_balance(address, amount):
    w3 = Web3(Web3.HTTPProvider(infura_url))
    private_key = os.environ.get('ADMIN_PRIVATE_KEY') or \
                  '56bc1794435c17242faddf14c51c2385537e4b1a047c9c49c46d5eddaff61a66'
    account = w3.eth.account.privateKeyToAccount(private_key)
    nonce = w3.eth.getTransactionCount(account.address, "pending")
    file = open("app/static/ABI/Contract_ABI.json", "r")
    KorpusContract = w3.eth.contract(
        Web3.toChecksumAddress(contract_address),
        abi=file.read()
    )
    file.close()

    estimateGas = KorpusContract.functions.decreaseVirtualBalance(address, amount).estimateGas(
        {'nonce': nonce, 'from': account.address, 'gasPrice': w3.toWei('35', 'gwei'), 'chainId': chain_id}
    )

    transaction = KorpusContract.functions.decreaseVirtualBalance(address, amount).buildTransaction(
        {
            'nonce': nonce,
            'from': account.address,
            'gas': estimateGas,
            'gasPrice': w3.toWei('35', 'gwei'),
            'chainId': chain_id
        }
    )
    signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
    try:
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        transaction_hash = txn_hash.hex()

        return transaction_hash, False
    except Exception:
        return 'Некорректный адрес.', True


def output_token(address, amount):
    w3 = Web3(Web3.HTTPProvider(infura_url))
    private_key = os.environ.get('ADMIN_PRIVATE_KEY') or \
                  '56bc1794435c17242faddf14c51c2385537e4b1a047c9c49c46d5eddaff61a66'
    account = w3.eth.account.privateKeyToAccount(private_key)
    nonce = w3.eth.getTransactionCount(account.address, "pending")
    file = open("app/static/ABI/Contract_ABI.json", "r")
    KorpusContract = w3.eth.contract(
        Web3.toChecksumAddress(contract_address),
        abi=file.read()
    )
    file.close()

    estimateGas = KorpusContract.functions.outputVirtualBalance(address, amount).estimateGas(
        {'nonce': nonce, 'from': account.address, 'gasPrice': w3.toWei('35', 'gwei'), 'chainId': chain_id}
    )

    transaction = KorpusContract.functions.outputVirtualBalance(address, amount).buildTransaction(
        {
            'nonce': nonce,
            'from': account.address,
            'gas': estimateGas,
            'gasPrice': w3.toWei('35', 'gwei'),
            'chainId': chain_id
        }
    )
    signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
    try:
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        transaction_hash = txn_hash.hex()

        return transaction_hash, False
    except Exception:
        return 'Некорректный адрес.', True


def set_token_price():
    private_key = os.environ.get('ADMIN_PRIVATE_KEY') or '56bc1794435c17242faddf14c51c2385537e4b1a047c9c49c46d5eddaff61a66'
    last_exchange_rate = TokenExchangeRate.query.order_by(TokenExchangeRate.date.desc()).first()
    if not last_exchange_rate.is_default_calculation_method:
        return
    new_exchange_rate = int(int(last_exchange_rate.exchange_rate_in_wei) * 1.05)
    ktd_message, is_ktd_error = set_KTD_price(new_exchange_rate, private_key)
    kti_message, is_kti_error = set_KTI_price(new_exchange_rate, private_key)
    if (not is_ktd_error) and (not is_kti_error):
        token_exchange_rate = TokenExchangeRate(date=datetime.datetime.now(), exchange_rate_in_wei=str(new_exchange_rate), is_default_calculation_method=True)
        db.session.add(token_exchange_rate)
        db.session.commit()
