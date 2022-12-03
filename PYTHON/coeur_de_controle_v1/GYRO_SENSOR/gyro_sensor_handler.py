"""
Autheur : LA
Titre : Capteur Gyroscope
Description : Initalisation et récupération des données avec le protocole I2C
Version : 1.0
OS : Raspbian (Linux/GNU)
Mise à jour : 2022-04-12
"""

# Python Libraries
import smbus


class GyroSensor:
    """
    Initialise les données pour établir une connexion I2C et récupérer les données du capteur.
    """
    def __init__(self, logger=object) -> None :
        """
        Initialise les données pour établir une connexion I2C
        """
        self.logger = logger

        self.logger.info("[GPIO CORE - GyroSensor] - Init Gyro...")
        #Device address
        self.DEVICE_ADDRESS = 0X68

        #some MPU6050 Registers and their Address
        self.PWR_MGMT_1   = 0x6B
        self.SMPLRT_DIV   = 0x19
        self.CONFIG       = 0x1A
        self.GYRO_CONFIG  = 0x1B
        self.INT_ENABLE   = 0x38
        self.ACCEL_XOUT_H = 0x3B
        self.ACCEL_YOUT_H = 0x3D
        self.ACCEL_ZOUT_H = 0x3F
        self.GYRO_XOUT_H  = 0x43
        self.GYRO_YOUT_H  = 0x45
        self.GYRO_ZOUT_H  = 0x47

        self.SMBUS = smbus.SMBus(1)

        #write to sample rate register
        self.SMBUS.write_byte_data(self.DEVICE_ADDRESS, self.SMPLRT_DIV, 7)
        #Write to power management register
        self.SMBUS.write_byte_data(self.DEVICE_ADDRESS, self.PWR_MGMT_1, 1)
        #Write to Configuration register
        self.SMBUS.write_byte_data(self.DEVICE_ADDRESS, self.CONFIG, 0)
        #Write to Gyro configuration register
        self.SMBUS.write_byte_data(self.DEVICE_ADDRESS, self.GYRO_CONFIG, 24)
        #Write to interrupt enable register
        self.SMBUS.write_byte_data(self.DEVICE_ADDRESS, self.INT_ENABLE, 1)


    def read_raw_data(self, address):
        """
        Lecture des données sur le bus I2C
        """
	    # Accelero and Gyro value are 16-bit
        high = self.SMBUS.read_byte_data(self.DEVICE_ADDRESS, address)
        low = self.SMBUS.read_byte_data(self.DEVICE_ADDRESS, address + 1)
    
        # concatenate higher and lower value
        value = ((high << 8) | low)
        
        # to get signed value from mpu6050
        if(value > 32768):
            value = value - 65536

        return value


    def get_data(self) -> str :
        """
        Récupére les données du capteur.
        Retourne : Données du capteur en type string
        """
        #Read Accelerometer raw value
        acc_x = self.read_raw_data(self.ACCEL_XOUT_H)
        acc_y = self.read_raw_data(self.ACCEL_YOUT_H)
        acc_z = self.read_raw_data(self.ACCEL_ZOUT_H)
        
        #Read Gyroscope raw value
        gyro_x = self.read_raw_data(self.GYRO_XOUT_H)
        gyro_y = self.read_raw_data(self.GYRO_YOUT_H)
        gyro_z = self.read_raw_data(self.GYRO_ZOUT_H)
        
        #Full scale range +/- 250 degree/C as per sensitivity scale factor
        Ax = acc_x / 16384.0
        Ay = acc_y / 16384.0
        Az = acc_z / 16384.0
        
        Gx = gyro_x / 131.0
        Gy = gyro_y / 131.0
        Gz = gyro_z / 131.0
        
        # self.logger.info(f"[GPIO CORE - GyroSensor] - Gx = {Gx: .2f}°/s |Gy = {Gy: .2f} °/s |Gz = {Gz: .2f} °/s |Ax={Ax:.2f} g |Ay={Ay:.2f} g | Az={Az:.2f} g")
        return str(f"Gx = {Gx: .2f}°/s |Gy = {Gy: .2f} °/s |Gz = {Gz: .2f} °/s |Ax={Ax:.2f} g |Ay={Ay:.2f} g | Az={Az:.2f} g")