import sys

def read_input(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f]
    n = int(lines[0])
    rows = [tuple(int(x.strip()) for x in line.split(',')) for line in lines[1:]]
    return n, rows


def solve(filename):
    n, rows = read_input(filename)
    total_sum = n * (n + 1) // 2

    # state_list: list of [l, r] pairs，l 为左指针，r 为右指针（不含）
    init_state = [[0, len(row)] for row in rows]

    memo = {}

    def minimax(state_list, is_max):
        """返回值 = 从当前状态开始，当前玩家行动后的 (小红总分 - 小蓝总分) 最优差值"""
        # 用 tuple of tuples 作为 memo key（hashable）
        key = tuple((l, r) for l, r in state_list)
        full_key = (key, is_max)
        if full_key in memo:
            return memo[full_key]

        # 检查终局
        if all(l == r for l, r in state_list):
            memo[full_key] = 0
            return 0

        if is_max:
            best = -float('inf')
            for i, (l, r) in enumerate(state_list):
                if l >= r:
                    continue
                old_l, old_r = l, r

                # 取左端
                val = rows[i][l]
                state_list[i] = [l + 1, r]
                child = minimax(state_list, False)
                state_list[i] = [old_l, old_r]
                if val + child > best:
                    best = val + child

                # 取右端
                if r - l > 1:
                    val = rows[i][r - 1]
                    state_list[i] = [l, r - 1]
                    child = minimax(state_list, False)
                    state_list[i] = [old_l, old_r]
                    if val + child > best:
                        best = val + child
            memo[full_key] = best
            return best
        else:
            best = float('inf')
            for i, (l, r) in enumerate(state_list):
                if l >= r:
                    continue
                old_l, old_r = l, r

                # 取左端
                val = rows[i][l]
                state_list[i] = [l + 1, r]
                child = minimax(state_list, True)
                state_list[i] = [old_l, old_r]
                if -val + child < best:
                    best = -val + child

                # 取右端
                if r - l > 1:
                    val = rows[i][r - 1]
                    state_list[i] = [l, r - 1]
                    child = minimax(state_list, True)
                    state_list[i] = [old_l, old_r]
                    if -val + child < best:
                        best = -val + child
            memo[full_key] = best
            return best

    # 第一步先手搜索
    best_diff = -float('inf')
    best_action = None
    for i in range(len(rows)):
        l, r = 0, len(rows[i])
        # 取左端
        val = rows[i][0]
        init_state[i] = [1, r]
        diff = val + minimax(init_state, False)
        init_state[i] = [0, r]
        print(f"row: {i+1}, side: L, val: {val}, diff: {diff}")
        if diff > best_diff:
            best_diff = diff
            best_action = (i, 'L', val)

        # 取右端
        if r > 1:
            val = rows[i][r - 1]
            init_state[i] = [l, r - 1]
            diff = val + minimax(init_state, False)
            init_state[i] = [0, r]
            print(f"row: {i+1}, side: R, val: {val}, diff: {diff}")
            if diff > best_diff:
                best_diff = diff
                best_action = (i, 'R', val)

    row_idx, side, val = best_action
    print(f"第{row_idx+1}行 {'左' if side == 'L' else '右'}端 牌点数{val}")

    red = (total_sum + best_diff) / 2
    blue = (total_sum - best_diff) / 2
    print(f"小红: {red:.0f} 小蓝: {blue:.0f}")
