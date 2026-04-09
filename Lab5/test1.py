import maze
from maze import *

# --- 1. 执行 DFS ---
print("--- 执行 DFS ---")
path = []
for i in range(height):
    for j in range(width):
        visited[i][j] = False
if dfs(start[0], start[1], path):
    res = maze.copy()
    for (x, y) in path[1:-1]:
        res[x][y] = 7
    for x in res:
        print(x)
    print(f"DFS 路径为：{path}")
else:
    print("DFS 未找到路径")


# --- 2. 执行 BFS ---
print("\n--- 执行 BFS ---")
result_bfs = bfs()

if result_bfs:
    res = maze.copy()
    for (x, y) in result_bfs[1:-1]:
        res[x][y] = 7
    for x in res:
        print(x)
    print(f"BFS 路径为：{result_bfs}")
else:
    print("BFS 未找到路径")
