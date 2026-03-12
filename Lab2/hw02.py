

class StuData():
  
  def __init__(self, filename):
    self.properties = {"name": 0, "stu_num": 1, "gender": 2, "age": 3}
    self.data = []
    with open(filename, 'r', encoding='utf-8') as f:
      for line in f:
          self.data.append(line.split())

  def AddData(self, name, stu_num, gender, age):
     self.data.append([name, stu_num, gender, age])

  def SortData(self, property):
     self.data.sort(key = lambda x: x[self.properties[property]])

  def ExportFile(self, savename):
     with open(savename, "x") as f:
        for line in self.data:
           f.write(" ".join(line) + "\n")