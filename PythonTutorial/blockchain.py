"""
Basic Blockchain built to understand some of the core concepts
Code from tutorial at http://ecomunsing.com/build-your-own-blockchain
"""
import hashlib, json

def hashMe(msg=""):
    # For convenience, this is a helper function that wraps our hashing algorithm
    if type(msg)!=str:
        msg = json.dumps(msg,sort_keys=True)  # If we don't sort keys, we can't guarantee repeatability!
        
    return hashlib.sha256(msg.encode('utf-8')).hexdigest()

"""
This will create valid transactions in the range of (1,maxValue)
"""
def makeTransaction(maxValue=3):
    import random
    # This will randomly choose -1 or 1
    sign = int(random.getrandbits(1)) * 2 - 1
    amount = random.randint(1,maxValue)
    alicePays = sign * amount
    bobPays = -1 * alicePays
    # By construction, this will always return transactions that respect the conservation of tokens.
    # However, note that we have not done anything to check whether these overdraft an account
    return {u'Alice':alicePays, u'Bob':bobPays}

"""
    Inputs: txn, state: dictionaries keyed with account names, holding numeric values for transfer amount (txn) or account balance (state)
    Returns: Updated state, with additional users added to state if necessary
    NOTE: This does not not validate the transaction- just updates the state!
"""
def updateState(txn, state):

    # If the transaction is valid, then update the state
    state = state.copy() # As dictionaries are mutable, let's avoid any confusion by creating a working copy of the data.
    for key in txn:
        if key in state.keys():
            state[key] += txn[key]
        else:
            state[key] = txn[key]
    return state

def isValidTxn(txn, state):
    # Assume that the transaction is a dictionary keyed by account names

    # Check that the sum of the deposits and withdrawals is 0
    if sum(txn.values()) is not 0:
        return False

    for key in txn.keys():
        if key in state.keys():
            acctBalance = state[key]
        else:
            acctBalance = 0
        if (acctBalance + txn[key]) < 0:
            return False

    return True

def makeBlock(txns, chain):
    parentBlock = chain[-1]
    parentHash = parentBlock[u'hash']
    blockNumber = parentBlock[u'contents'][u'blockNumber'] + 1
    txnCount = len(txns)
    blockContents = {u'blockNumber':blockNumber,u'parentHash':parentHash,
                     u'txnCount':len(txns),'txns':txns}
    blockHash = hashMe(blockContents)
    block = {u'hash':blockHash,u'contents':blockContents}

    return block

"""
    Raise an exception if the hash does not match the block contents
"""
def checkBlockHash(block):
    expectedHash = hashMe( block['contents'])
    if block['hash'] != expectedHash:
        raise Exception('Hash does not match contents of block {0}'.format(block['contents']['blockNumber']))
    return

"""
    We want to check the following conditions:
     - Each of the transactions are valid updates to the system state
     - Block hash is valid for the block contents
     - Block number increments the parent block number by 1
     - Accurately references the parent block's hash
"""
def checkBlockValidity(block, parent, state):
    parentNumber = parent['contents']['blockNumber']
    parentHash = parent['hash']
    blockNumber = block['contents']['blockNumber']

    for txn in block['contents']['txns']:
        if isValidTxn(txn, state):
            state = updateState(txn, state)
        else:
            raise Exception('Invalid transaction in block {0}: {1}'.format(blockNumber, txn))

    checkBlockHash(block)

    if blockNumber != (parentNumber+1):
        raise Exception("Block number is not inline with parent: {0}".format(blockNumber))

    if block['contents']['parentHash'] != parentHash:
        raise Exception('Parent hash not accurate for block {0}'.format(blockNumber))
    
    return state

"""
     Work through the chain from the genesis block (which gets special treatment), 
     checking that all transactions are internally valid,
     that the transactions do not cause an overdraft,
     and that the blocks are linked by their hashes.
     This returns the state as a dictionary of accounts and balances,
     or returns False if an error was detected
"""
def checkChain(chain):
    ## Data input processing: Make sure that our chain is a list of dicts
    if type(chain)==str:
        try:
            chain = json.loads(chain)
            assert(type(chain)==list)
        except:
            return False
    elif type(chain) != list:
        return False

    state = {}
    ## Prime the pump by checking the genesis block
    # We want to check the following conditions:
    # - Each of the transactions are valid updates to the system state
    # - Block hash is valid for the block contents
    for txn in chain[0]['contents']['txns']:
        state = updateState(txn, state)
    checkBlockHash(chain[0])
    parent = chain[0]

    ## Checking subsequent blocks: These additionally need to check
    #    - the reference to the parent block's hash
    #    - the validity of the block number
    for block in chain[1:]:
        state = checkBlockValidity(block, parent, state)
        parent = block

    return state



state = {u'Alice':50,u'Bob':50}
genesisBlockTxns = [state]
genesisBlockContents = {u'blockNumber':0, u'parentHash':None,u'txnCount':1,u'txns':genesisBlockTxns}
genesisHash = hashMe(genesisBlockContents)
genesisBlock = {u'hash':genesisHash, u'contents':genesisBlockContents}
genesisBlockStr = json.dumps(genesisBlock, sort_keys=True)


chain = [genesisBlock]

# make a bunch of dummy transactions
txnBuffer = [makeTransaction() for i in range(30)]

blockSizeLimit = 5  # Arbitrary number of transactions per block- 
               #  this is chosen by the block miner, and can vary between blocks!lockSizeLimit = 5  # Arbitrary number of transactions per block- 
               #  this is chosen by the block miner, and can vary between blocks!

while len(txnBuffer) > 0:
    bufferStartSize = len(txnBuffer)

    ## Gather a set of valid transactions for inclusion
    txnList = []
    while (len(txnBuffer) > 0) and (len(txnList) < blockSizeLimit):
        newTxn = txnBuffer.pop()
        validTxn = isValidTxn(newTxn, state)

        # if transaction is valid
        if validTxn:
            txnList.append(newTxn)
            state = updateState(newTxn, state)
        else:
            print("ignored transaction")
            sys.stdout.flush()
            continue

    myBlock = makeBlock(txnList, chain)
    chain.append(myBlock)

print(chain[0])
print(chain[1])

print(state)

print(checkChain(chain))