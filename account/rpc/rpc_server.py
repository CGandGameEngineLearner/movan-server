
from common.movan_rpc import RPCServer
from account.config import CONFIG

ACCOUNT_RPC_SERVER = RPCServer(CONFIG['Network']['account_server_host'], CONFIG['Network']['account_server_port'])