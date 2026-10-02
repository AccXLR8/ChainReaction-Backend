def matchmaking_queue_key(mode: str = "default") -> str:
    return f"matchmaking:queue:{mode}"


def game_lock_key(game_id: str) -> str:
    return f"game:{game_id}:lock"


def game_state_key(game_id: str) -> str:
    return f"game:{game_id}:state"


def connection_set_key(game_id: str) -> str:
    return f"game:{game_id}:connections"
