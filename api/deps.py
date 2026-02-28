from functools import lru_cache
from clients.aturiya import AturiyaClient
from clients.pipe0 import Pipe0Client


@lru_cache
def get_aturiya_client() -> AturiyaClient:
    return AturiyaClient()


@lru_cache
def get_pipe0_client() -> Pipe0Client:
    return Pipe0Client()
