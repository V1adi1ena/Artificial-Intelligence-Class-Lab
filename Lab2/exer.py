class Car():
  def __init__(self, make, model, year):
    self.make = make
    self.model = model
    self.year = year
    self.odometer = 0

  def get_name(self):
    long_name = str(self.year) + " " + self.make + " " +self.model
    return long_name.title()
  
  def read_odometer(self):
    print("This car has" + str(self.odometer) + "miles on it")

  def update_odometer(self, mileage):
    if(mileage >= self.odometer):
      self.odometer = mileage
    else:
      print("You can't roll back an odometer!")
    
  def increment_odomter(self, miles):
    self.odometer += miles

class Book():
  def __init__(self, title, author, price):
    self.title = title
    self.author = author
    self.price = price

  def get_info(self):
    print(f"This book's title is { self.title }  written by { self.author } for { self.price } dollars.")

class PrintedBook(Book):
  def __init__(self, title, author, price, pages, weight):
    super().__init__(title, author, price)
    self.pages = pages
    self.weight = weight
  
  def get_info(self):
    super().get_info()
    print(f"And it has {self.pages} pages of {self.weight} grams")
