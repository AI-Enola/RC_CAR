"""
Modifié par : LA
Source VL53L0X : https://github.com/johnbryanmoore/VL53L0X_rasp_python
Titre : Capteur de distance ToF
Description : Utilisation de Ctypes pour effectuer la communication entre Python et l'API en C
Version : 1.0
OS : Raspbian (Linux/GNU)
Mise à jour : 2022-03-02
Langue : FRANÇAIS
"""


from ctypes import *
import smbus


"""
Différent mode de précision
"""
VL53L0X_GOOD_ACCURACY_MODE = int(0)   # Good Accuracy mode
VL53L0X_BETTER_ACCURACY_MODE = int(1)   # Better Accuracy mode
VL53L0X_BEST_ACCURACY_MODE = int(2)   # Best Accuracy mode
VL53L0X_LONG_RANGE_MODE = int(3)   # Longe Range mode
VL53L0X_HIGH_SPEED_MODE = int(4)   # High Speed mode

"""
On appel le SMBUS au niveau du I2C
"""
I2CBUS = smbus.SMBus(1)

"""
Fichier source en C convertit en .so
"""
# Load VL53L0X shared lib 
TOF_LIB = CDLL("VL53L0X_ToF/vl53l0x_python.so")


"""
Lecture des données du capteur en I2C
"""
def i2c_read(i2c_address, register, data_pointer, length):

    check_block_data = 0
    bytes_data = []
 
    try: bytes_data = I2CBUS.read_i2c_block_data(i2c_address, register, length)
    except IOError: check_block_data = -1

    if check_block_data == 0:

        for index in range(length):
            data_pointer[index] = bytes_data[index]

    return check_block_data


"""
Écriture des données vers le capteur I2C
"""
def i2c_write(i2c_address, register, data_pointer, length):

    check_block_data = 0
    data = []

    for index in range(length):
        data.append(data_pointer[index])

    try: I2CBUS.write_i2c_block_data(i2c_address, register, data)
    except IOError: check_block_data = -1

    return check_block_data

"""
Interaction avec les fonctions en type de langage C avec les pointeurs au niveau de l'API
"""
# Create read function pointer
READ_FUNCTION_C = CFUNCTYPE(c_int, c_ubyte, c_ubyte, POINTER(c_ubyte), c_ubyte)
READ_FUNCTION = READ_FUNCTION_C(i2c_read)

# Create write function pointer
WRITE_FUNCTION_C = CFUNCTYPE(c_int, c_ubyte, c_ubyte, POINTER(c_ubyte), c_ubyte)
WRITE_FUNCTION = WRITE_FUNCTION_C(i2c_write)

# pass i2c read and write function pointers to VL53L0X library
TOF_LIB.VL53L0X_set_i2c(READ_FUNCTION, WRITE_FUNCTION)



class VL53L0X(object):
    """
    Initialisation de l'adresse du capteur I2C
    Utilisation des fonctions de l'API en C
    Fonction de démarrage de la récupération de donnée et de la fonction d'arrêt
    Récupération de la distance
    Récupération du temps de la mesure entre l'envoi du signal et de la reception du signal.
    """

    def __init__(self, i2c_address=int, TCA9548A_Number=255, TCA9548A_Address=0):

        """Initialize the VL53L0X ToF Sensor from ST"""
        self.DEVICE_ADDRESS = i2c_address
        self.TCA9548A_Device = TCA9548A_Number
        self.TCA9548A_Address = TCA9548A_Address
        self.DEVICE_NUMBER = 1


    def start_ranging(self, mode=int):
        """
        Démarrage de la mesure du capteur ToF VL53L0X
        """
        TOF_LIB.startRanging(self.DEVICE_NUMBER, mode, self.DEVICE_ADDRESS, self.TCA9548A_Device, self.TCA9548A_Address)
        

    def stop_ranging(self):
        """
        Arrêt de la mesure du capteur ToF VL53L0X
        """
        TOF_LIB.stopRanging(self.DEVICE_NUMBER)


    def get_distance(self):
        """
        Récupération de la distance receuilli par le capteur
        """
        return TOF_LIB.getDistance(self.DEVICE_NUMBER)


    def get_timing(self):
        """
        Récupération du temps de la mesure de la distance
        """
        
        device = POINTER(c_void_p)
        device = TOF_LIB.getDev(self.DEVICE_NUMBER)

        budget = c_uint(0)
        budget_pointer = pointer(budget)

        status =  TOF_LIB.VL53L0X_GetMeasurementTimingBudgetMicroSeconds(device, budget_pointer)
        
        if status == 0: return (budget.value + 1000)
        else: return 0