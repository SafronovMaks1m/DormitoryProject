from src.models.sensors import Sensors
from .generating_values_exception import GeneratingValuesSensorsException
import random

class GeneratingValuesSensors:
    def __init__(self, sensors: list[Sensors], probability: int = 20):
        self.sensors = sensors
        self.probability = probability
        self.res = {
            'normal' : {},
            'violations':{}
        }
        
    @property
    def probability(self):
        return self._probability
    
    @probability.setter
    def probability(self, value):
        if value < 0:
            raise GeneratingValuesSensorsException("The probability cannot be less than 0")
        self._probability = value
    
    def formation_result(self, name_sen, new_value, normal = True):
        self.res.get(['violations', 'normal'][normal]).update({name_sen: new_value})
    
    def generation(self) -> dict:
        for sensor in self.sensors:
            norm_violate = random.randint(0, 100)
            normal = True
            if norm_violate <= self.probability:
                normal = False
                lt_gt = random.randint(1, 2)
                if lt_gt == 1 and sensor.min_normal - 0.1 > 0:
                    value = random.randint(
                        0, 
                        int(sensor.min_normal * 10 - 1)
                    ) / 10
                else:
                    value = random.randint(
                        int(sensor.max_normal * 10 + 1),
                        int((sensor.max_normal + 20) * 10)
                    ) / 10
            else:
                value = random.randint(
                    int(sensor.min_normal * 10),
                    int(sensor.max_normal * 10)
                ) / 10
            self.formation_result(sensor.name, value, normal)
        return self.res