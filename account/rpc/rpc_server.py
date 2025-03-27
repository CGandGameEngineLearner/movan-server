
from common.movan_rpc.server import RPCServer
from account.config import CONFIG

RPC_SERVER = RPCServer(CONFIG['Network']['account_server_host'], CONFIG['Network']['account_server_port'])