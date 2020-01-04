from vehicle import Vehicle

class Car(Vehicle):
    

    def brag(self):
        print('look how awesome is my car')

car1 = Car()
car1.drive()
car1.add_warning('new warning')
print(car1)

car2 = Car(200)
car2.drive()

car3 = Car(210)
car3.drive()
