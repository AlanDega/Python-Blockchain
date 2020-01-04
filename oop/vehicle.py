class Vehicle:
    def __init__(self, starting_top_speed=130):
        self.top_speed = starting_top_speed
        self.__warnings = []


    def __repr__(self):
        print('printing ...')
        return 'wazza Top_speed: {},  __warnings: {}'.format(self.top_speed, len(self.__warnings))    

    
    def add_warning(self, warning_text):
        if len(warning_text) > 0:
            self.__warnings.append(warning_text)


    def get_warnings(self):
        return self.__warnings
       

    def drive(self):
        print('i am driving but cetsinly not faster than{}'.format(self.top_speed))
    