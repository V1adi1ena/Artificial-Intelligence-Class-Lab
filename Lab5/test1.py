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


# --- 3. 执行 DLS ---
print("\n--- 执行 DLS ---")
path = []
for i in range(height):
    for j in range(width):
        visited[i][j] = False
if dls(start[0], start[1], path, limit=40):
    res = maze.copy()
    for (x, y) in path[1:-1]:
        res[x][y] = 7
    for x in res:
        print(x)
    print(f"DLS 路径为：{path}")
else:
    print("DLS 未找到路径")

# --- 4. 执行 IDDFS ---
print("\n--- 执行 IDDFS ---")
path = []
max_limit = 40
for i in range(height):
    for j in range(width):
        visited[i][j] = False
if iddfs(start[0], start[1], max_limit, path=path):
    res = maze.copy()
    for (x, y) in path[1:-1]:
        res[x][y] = 7
    for x in res:
        print(x)
    print(f"IDDFS 路径为：{path}")
else:
    print(f"IDDFS 未找到路径")

# --- 5. 执行 DDFS ---
print("\n--- 执行 DDFS ---")
result_dedfs = dedfs()

if result_dedfs:
    res = maze.copy()
    for (x, y) in result_dedfs[1:-1]:
        res[x][y] = 7
    for x in res:
        print(x)
    print(f"DDFS 路径为：{result_dedfs}")
else:
    print("DDFS 未找到路径")