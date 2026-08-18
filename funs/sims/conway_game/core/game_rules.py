def conway_rule(current_state: int, neighbors: int) -> int:
    """康威生命游戏核心规则[1,5](@ref)"""
    if current_state == 1:
        return 1 if 2 <= neighbors <= 3 else 0
    else:
        return 1 if neighbors == 3 else 0