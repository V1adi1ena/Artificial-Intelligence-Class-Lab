import puzzle
from puzzle import *


"""puzzle1"""
print("--------------puzzle1:---------------")
res1 = A_star('puzzle1.txt')
for x in res1:
  print(x)
print("-------------------------------------")

"""puzzle2"""
print("--------------puzzle2:---------------")
res2 = A_star('puzzle2.txt')
for x in res2:
  print(x)
print("-------------------------------------")