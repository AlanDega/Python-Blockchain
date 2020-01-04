class Car:
    top_speed = 100 
    warnings = []

    def drive(self):
        print('i am driving but cetsinly not faster than{}'.format(self.top_speed))

car1 = Car()
car1.drive()

# 
car1.warnings.append('New Warning')

car2 = Car()
car2.drive()
print(car2.warnings)

car3 = Car()
car3.drive()
print(car3.warnings)
