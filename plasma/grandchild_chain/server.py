import rlp
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher
from ethereum import utils
from plasma.grandchild_chain.child_chain import GrandChildChain
from plasma.root_chain.deployer import Deployer
from plasma_core.constants import CONTRACT_ADDRESS, AUTHORITY
from plasma_core.block import Block
from plasma_core.transaction import Transaction
from plasma_core.utils.transactions import encode_utxo_id

child_chain = GrandChildChain(AUTHORITY['address'], "0x4B3eC6c9dC67079E82152d6D55d8dd96a8e6AA26")


@Request.application
def application(request):
    # Dispatcher is dictionary {<method_name>: callable}
    dispatcher["submit_block"] = lambda block: child_chain.submit_block(rlp.decode(utils.decode_hex(block), Block))
    dispatcher["apply_transaction"] = lambda transaction: child_chain.apply_transaction(rlp.decode(utils.decode_hex(transaction), Transaction))
    dispatcher["get_transaction"] = lambda blknum, txindex: rlp.encode(child_chain.get_transaction(encode_utxo_id(blknum, txindex, 0)), Transaction).hex()
    dispatcher["get_current_block"] = lambda: rlp.encode(child_chain.get_current_block(), Block).hex()
    dispatcher["get_current_block_num"] = lambda: child_chain.get_current_block_num()
    dispatcher["get_block"] = lambda blknum: rlp.encode(child_chain.get_block(blknum), Block).hex()
    response = JSONRPCResponseManager.handle(
        request.data, dispatcher)
    return Response(response.json, mimetype='application/json')


if __name__ == '__main__':
    run_simple('localhost', 8547, application)