from common.movan_rpc import RPCServer
from sync.config import CONFIG
SYNC_RPC_SERVER = RPCServer(CONFIG["Network"]["rpc_host"], CONFIG["Network"]["rpc_port"])