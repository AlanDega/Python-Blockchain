from vehicle import Vehicle
class Bus(Vehicle):
    def __init__(self, starting_top_speed=130):
        super().__init__(starting_top_speed)    
        self.passengers = []


    def add_group(self, passengers):
        self.passengers.extend(passengers)


bus1 = Bus(150)
bus1.add_group(['Vane','Claudia','torres','carla'])
print(bus1.passengers)
bus1.drive()