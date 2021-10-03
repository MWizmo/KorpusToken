from web3.auto import Web3
import time
privateKey = '3ec4440a4695f15f11fe9c48a764bc7df4783495d5096b6b4fe8ef33fb4cb147'
# _receiver = '0x4C580b20Fa1C4d46821421c3229A0287Ce989322'


def createKTD(value, receiver):
    #privateKey = "" импорт ключа из базы данных. Если он не подходит к кошельку владельца смарт-контракта, то эфириум отменит транзакцию в конце
    try:
        value = int(value)
    except ValueError:
        return 'Число токенов должно быть целым числом', False
    if value <= 0:
        return 'Число токенов должно быть положительным числом', False
    try:
        w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/35b77298442b49168bbe5a150071dd9f"))
        account = w3.eth.account.privateKeyToAccount(privateKey)
        nonce = w3.eth.getTransactionCount(account.address)
        abi_file = open("app/static/ABI/Contract_ABI.json", "r")
        KorpusContract = w3.eth.contract(
            Web3.toChecksumAddress("0x47ae9eFf852D74f05FA3cc2F67C4563Ca2600B4C"),
            abi=abi_file.read())
        abi_file.close()
        transaction = KorpusContract.functions.mintKTD(value, receiver).buildTransaction(
            {
                'nonce': nonce,
                'from': account.address,
                'gas': 75000,
                'gasPrice': w3.toWei('1.5', 'gwei'),
                'chainId': 3
            }
        )
        signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
        try:
            txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            transaction_hash = txn_hash.hex()
            return 'Транзакция проведена успешно.\nПодробности по ссылке:', transaction_hash
        except Exception:
            return "Некорректный адрес получателя", False
    except Exception as e:
        return str(e), False


def createKTI(value, receiver):
    try:
        value = int(value)
    except ValueError:
        return 'Число токенов должно быть целым числом', False
    if value <= 0:
        return "Число токенов должно быть больше нуля.", False
    #privateKey = "" импорт ключа из базы данных. Если он не подходит к кошельку владельца смарт-контракта, то эфириум отменит транзакцию в конце
    try:
        w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/35b77298442b49168bbe5a150071dd9f"))
        account = w3.eth.account.privateKeyToAccount(privateKey)
        nonce = w3.eth.getTransactionCount(account.address)
        abi_file = open("app/static/ABI/Contract_ABI.json", "r")
        KorpusContract = w3.eth.contract(
            Web3.toChecksumAddress("0x47ae9eFf852D74f05FA3cc2F67C4563Ca2600B4C"),
            abi=abi_file.read()
        )
        abi_file.close()
        transaction = KorpusContract.functions.mintKTI(value, receiver).buildTransaction(
            {
                'nonce': nonce,
                'from': account.address,
                'gas': 75000,
                'gasPrice': w3.toWei('1.5', 'gwei'),
                'chainId': 3
            }
        )
        signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
        try:
          txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
          transaction_hash = txn_hash.hex()
          return 'Транзакция проведена успешно.\nПодробности по ссылке:', transaction_hash
        except Exception:
          return "Некорректный адрес.", False
    except Exception as e:
        return str(e), False


def transferWEI(value, receiver):
    try:
        value = float(value)
    except ValueError:
        return 'Число эфира должно быть действительным числом', False
    if value <= 0:
        return "Число эфира должно быть больше нуля.", False
    try:
        _wei = int(value * 1000000000000000000)
        #privateKey = "" импорт ключа из базы данных. Если он не подходит к кошельку владельца смарт-контракта, то эфириум отменит транзакцию в конце
        w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/35b77298442b49168bbe5a150071dd9f"))
        account = w3.eth.account.privateKeyToAccount(privateKey)
        nonce = w3.eth.getTransactionCount(account.address)
        abi_file = open("app/static/ABI/Contract_ABI.json", "r")
        KorpusContract = w3.eth.contract(
            Web3.toChecksumAddress("0x47ae9eFf852D74f05FA3cc2F67C4563Ca2600B4C"),
            abi=abi_file.read()
        )
        transaction = KorpusContract.functions.transferWEI(receiver, _wei).buildTransaction(
            {
                'nonce': nonce,
                'from': account.address,
                'gas': 75000,
                'gasPrice': w3.toWei('1.5', 'gwei'),
                'chainId': 3
            }
        )
        abi_file.close()
        signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
        try:
          txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
          transaction_hash = txn_hash.hex()
          return 'Транзакция проведена успешно.\nПодробности по ссылке:', transaction_hash
        except Exception:
          return "Некорректный адрес или недостаточно прав.", False
    except Exception as e:
        return str(e), False


def setBudget(date, budgetItem, cost):
    #privateKey = "" импорт ключа из базы данных. Если он не подходит к кошельку владельца смарт-контракта, то эфириум отменит транзакцию в конце
    try:
        cost = int(cost)
        date = int(date)
        w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/35b77298442b49168bbe5a150071dd9f"))
        account = w3.eth.account.privateKeyToAccount(privateKey)
        nonce = w3.eth.getTransactionCount(account.address)
        abi_file = open("app/static/ABI/Contract_ABI.json", "r")
        KorpusContract = w3.eth.contract(
            Web3.toChecksumAddress("0x47ae9eFf852D74f05FA3cc2F67C4563Ca2600B4C"),
            abi=abi_file.read()
        )
        transaction = KorpusContract.functions.setBudget(date, budgetItem, cost).buildTransaction(
            {
                'nonce': nonce,
                'from': account.address,
                'gas': 50000,
                'gasPrice': w3.toWei('1.5', 'gwei'),
                'chainId': 3
            }
        )
        abi_file.close()
        signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
        try:
          txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
          transaction_hash = txn_hash.hex()
          return 'Транзакция проведена успешно.\nПодробности по ссылке:', transaction_hash
        except Exception:
          return "Некорректные данные или недостаточно прав.", False
    except Exception as e:
        return str(e), False


def setStudentResult(project, student, date, axis, points):
    try:
        date = int(date)
        #privateKey = "" импорт ключа из базы данных. Если он не подходит к кошельку владельца смарт-контракта, то эфириум отменит транзакцию в конце
        w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/35b77298442b49168bbe5a150071dd9f"))
        account = w3.eth.account.privateKeyToAccount(privateKey)
        nonce = w3.eth.getTransactionCount(account.address)
        abi_file = open("app/static/ABI/Contract_ABI.json", "r")
        KorpusContract = w3.eth.contract(
            Web3.toChecksumAddress("0x47ae9eFf852D74f05FA3cc2F67C4563Ca2600B4C"),
            abi=abi_file.read()
        )
        abi_file.close()
        transaction = KorpusContract.functions.setStudentResult(project, student, date, axis, points).buildTransaction(
            {
                'nonce': nonce,
                'from': account.address,
                'gas': 70000,
                'gasPrice': w3.toWei('1.5', 'gwei'),
                'chainId': 3
            }
        )
        signed_txn = w3.eth.account.signTransaction(transaction, private_key=account.privateKey)
        try:
          txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
          transaction_hash = txn_hash.hex()
          return 'Транзакция проведена успешно.\nПодробности по ссылке:', transaction_hash
        except Exception:
          return "Некорректные данные или недостаточно прав.", False
    except Exception as e:
        return str(e), False


def getBudget(date, budgetItem):
    date = int(date)
    #privateKey = "" импорт ключа из базы данных
    w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/35b77298442b49168bbe5a150071dd9f"))
    account = w3.eth.account.privateKeyToAccount(privateKey)
    nonce = w3.eth.getTransactionCount(account.address)
    abi_file = open("app/static/ABI/Contract_ABI.json", "r")
    KorpusContract = w3.eth.contract(
        #вводим его адрес и ABI
        Web3.toChecksumAddress("0x47ae9eFf852D74f05FA3cc2F67C4563Ca2600B4C"),
        abi=abi_file.read()
    )
    abi_file.close()
    cost = KorpusContract.functions.budgetInformation(date, budgetItem).call()
    return cost


def getStudentResults(_project, _student, _date, _axis):
    _date = int(_date)
    #privateKey = "" импорт ключа из базы данных
    w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/35b77298442b49168bbe5a150071dd9f"))
    account = w3.eth.account.privateKeyToAccount(privateKey)
    nonce = w3.eth.getTransactionCount(account.address)
    #интерфейс контракта
    abi_file = open("app/static/ABI/Contract_ABI.json", "r")
    KorpusToken_Deposit = w3.eth.contract(
        Web3.toChecksumAddress("0x19Fcb1b2286f178C6070Dfb309bB5324Ac8823c9"),
        abi = [ { "constant": "true", "inputs": [], "name": "name", "outputs": [ { "name": "", "type": "string" } ], "payable": "false", "stateMutability": "view", "type": "function" }, { "constant": "false", "inputs": [ { "name": "_spender", "type": "address" }, { "name": "_value", "type": "uint256" } ], "name": "approve", "outputs": [ { "name": "", "type": "bool" } ], "payable": "false", "stateMutability": "nonpayable", "type": "function" }, { "constant": "true", "inputs": [], "name": "totalSupply", "outputs": [ { "name": "", "type": "uint256" } ], "payable": "false", "stateMutability": "view", "type": "function" }, { "constant": "false", "inputs": [ { "name": "_from", "type": "address" }, { "name": "_to", "type": "address" }, { "name": "_value", "type": "uint256" } ], "name": "transferFrom", "outputs": [ { "name": "", "type": "bool" } ], "payable": "false", "stateMutability": "nonpayable", "type": "function" }, { "constant": "true", "inputs": [], "name": "burner", "outputs": [ { "name": "", "type": "address" } ], "payable": "false", "stateMutability": "view", "type": "function" }, { "constant": "false", "inputs": [ { "name": "_to", "type": "address" }, { "name": "_amount", "type": "uint256" } ], "name": "mint", "outputs": [ { "name": "", "type": "bool" } ], "payable": "false", "stateMutability": "nonpayable", "type": "function" }, { "constant": "false", "inputs": [ { "name": "newBurner", "type": "address" } ], "name": "transferBurnership", "outputs": [], "payable": "false", "stateMutability": "nonpayable", "type": "function" }, { "constant": "false", "inputs": [ { "name": "_spender", "type": "address" }, { "name": "_subtractedValue", "type": "uint256" } ], "name": "decreaseApproval", "outputs": [ { "name": "success", "type": "bool" } ], "payable": "false", "stateMutability": "nonpayable", "type": "function" }, { "constant": "true", "inputs": [ { "name": "_owner", "type": "address" } ], "name": "balanceOf", "outputs": [ { "name": "balance", "type": "uint256" } ], "payable": "false", "stateMutability": "view", "type": "function" }, { "constant": "false", "inputs": [ { "name": "burner", "type": "address" }, { "name": "_value", "type": "uint256" } ], "name": "burnFrom", "outputs": [], "payable": "false", "stateMutability": "nonpayable", "type": "function" }, { "constant": "false", "inputs": [ { "name": "_project", "type": "string" }, { "name": "_student", "type": "string" }, { "name": "_date", "type": "uint256" }, { "name": "_axis", "type": "string" }, { "name": "_points", "type": "uint256" } ], "name": "addStudentResult", "outputs": [], "payable": "false", "stateMutability": "nonpayable", "type": "function" }, { "constant": "true", "inputs": [], "name": "owner", "outputs": [ { "name": "", "type": "address" } ], "payable": "false", "stateMutability": "view", "type": "function" }, { "constant": "true", "inputs": [], "name": "symbol", "outputs": [ { "name": "", "type": "string" } ], "payable": "false", "stateMutability": "view", "type": "function" }, { "constant": "false", "inputs": [ { "name": "_to", "type": "address" }, { "name": "_value", "type": "uint256" } ], "name": "transfer", "outputs": [ { "name": "", "type": "bool" } ], "payable": "false", "stateMutability": "nonpayable", "type": "function" }, { "constant": "true", "inputs": [ { "name": "_project", "type": "string" }, { "name": "_student", "type": "string" }, { "name": "_date", "type": "uint256" }, { "name": "_axis", "type": "string" } ], "name": "studentResults", "outputs": [ { "name": "_result", "type": "uint256" } ], "payable": "false", "stateMutability": "view", "type": "function" }, { "constant": "false", "inputs": [ { "name": "_spender", "type": "address" }, { "name": "_addedValue", "type": "uint256" } ], "name": "increaseApproval", "outputs": [ { "name": "success", "type": "bool" } ], "payable": "false", "stateMutability": "nonpayable", "type": "function" }, { "constant": "true", "inputs": [ { "name": "_owner", "type": "address" }, { "name": "_spender", "type": "address" } ], "name": "allowance", "outputs": [ { "name": "remaining", "type": "uint256" } ], "payable": "false", "stateMutability": "view", "type": "function" }, { "constant": "false", "inputs": [ { "name": "newOwner", "type": "address" } ], "name": "transferOwnership", "outputs": [], "payable": "false", "stateMutability": "nonpayable", "type": "function" }, { "inputs": [], "payable": "false", "stateMutability": "nonpayable", "type": "constructor" }, { "anonymous": "false", "inputs": [ { "indexed": "true", "name": "from", "type": "address" }, { "indexed": "true", "name": "to", "type": "address" }, { "indexed": "false", "name": "value", "type": "uint256" } ], "name": "Transfer", "type": "event" }, { "anonymous": "false", "inputs": [ { "indexed": "true", "name": "owner", "type": "address" }, { "indexed": "true", "name": "spender", "type": "address" }, { "indexed": "false", "name": "value", "type": "uint256" } ], "name": "Approval", "type": "event" }, { "anonymous": "false", "inputs": [ { "indexed": "true", "name": "previousBurner", "type": "address" }, { "indexed": "true", "name": "newBurner", "type": "address" } ], "name": "BurnershipTransferred", "type": "event" }, { "anonymous": "false", "inputs": [ { "indexed": "true", "name": "previousOwner", "type": "address" }, { "indexed": "true", "name": "newOwner", "type": "address" } ], "name": "OwnershipTransferred", "type": "event" } ]
    )
    abi_file.close()
    points = KorpusToken_Deposit.functions.studentResults(_project, _student, _date, _axis).call()
    return points


def sellKTD(value):   # обмен токенов вклада на эфир
    # _value = 0 число, задаваемое пользователем. Количество токенов, которое он хочет разрешить использовать
    try:
        value = int(value)
    except ValueError:
        return 'Число токенов должно быть целым числом', False
    if value > 0:
        # privateKey = "" импорт ключа из базы данных
        w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/35b77298442b49168bbe5a150071dd9f"))
        account = w3.eth.account.privateKeyToAccount(privateKey)
        nonce = w3.eth.getTransactionCount(account.address)
        file = open("app/static/ABI/KTD_ABI.json", "r")
        KorpusToken_Deposit = w3.eth.contract(
            # вводим его адрес и ABI
            Web3.toChecksumAddress("0x19Fcb1b2286f178C6070Dfb309bB5324Ac8823c9"),
            abi=file.read()
        )
        file.close()
        estimateGas = KorpusToken_Deposit.functions.approve(Web3.toChecksumAddress("0x47ae9eFf852D74f05FA3cc2F67C4563Ca2600B4C"), value).estimateGas({'nonce': nonce, 'from': account.address, 'gasPrice': w3.toWei('2', 'gwei'), 'chainId': 3})

        transaction = KorpusToken_Deposit.functions.approve(Web3.toChecksumAddress("0x47ae9eFf852D74f05FA3cc2F67C4563Ca2600B4C"), value).buildTransaction(
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
                    Web3.toChecksumAddress("0x47ae9eFf852D74f05FA3cc2F67C4563Ca2600B4C"),
                    abi=file.read()
                )
                file.close()
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
                return 'Транзакция проведена успешно.\nПодробности по ссылке:', transaction_hash
        except Exception as e:
            print(e)
            return "Недостаточно токенов.", False
    else:
        return "Число токенов не должно быть меньше или равно нулю.", False