"""把起点终点和墙壁路径转换为int"""
def toInt(x):
  if x == 'S':
    return 2
  elif x == 'E':
    return 3
  else:
    return int(x)
"""将迷宫文件转换为int列表"""
def  Maze(filename):
  maze = []
  with open(filename, 'r', encoding='utf-8') as f:
    for line in f:
      maze.append([toInt(x) for x in line.strip()])
  for i in range(len(maze)):
    for j in range(len(maze[0])):
      if maze[i][j] == 2:
        start = (i, j)
      elif maze[i][j] == 3:
        goal = (i, j)
  return maze, start, goal
"""判断是否在迷宫内且未访问过"""
def is_valid(x, y, visited):
  return (x>=0 and x<height and y>=0 and y<width and maze[x][y] != 1 and not visited[x][y])

def dfs(x, y, path = []):
  if not is_valid(x, y, visited):
    return False
  if(maze[x][y] == 1):
    return False
  visited[x][y] = True

  path.append((x, y))
  if((x, y) == goal):
    return True
  for dx, dy in directions:
    if(dfs(x+dx, y+dy, path)):
      return True
  path.pop()
  
  return False

def bfs():
  visited = [[False for _ in range(width)] for _ in range(height)]
  visited[start[0]][start[1]] = True
  que = [(start, [start])]

  while(len(que) > 0):
    pos, state = que.pop(0)
    if pos == goal:
      state.append(pos)
      return state
    for dx, dy in directions:
        cur_state = state.copy()
        if not is_valid(pos[0]+dx, pos[1]+dy, visited):
          continue
        visited[pos[0]+dx][pos[1]+dy] = True
        cur_state.append((pos[0]+dx, pos[1]+dy))
        que.append(((pos[0]+dx, pos[1]+dy), cur_state))
  return [] 

filename = input("请输入文件名")
maze, start, goal = Maze(filename)
width, height = len(maze[0]), len(maze)

visited = [[False for _ in range(width)] for _ in range(height)]
directions = []

if(start[0]<goal[0]): 
  if(start[1]<goal[1]): directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
  else: directions = [(1, 0), (0, -1), (-1, 0), (0, 1)]
else:
  if(start[1]<goal[1]): directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
  else: directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]