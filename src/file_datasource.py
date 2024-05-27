from csv import reader
from datetime import datetime
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.aggregated_data import AggregatedData
from domain.parking import Parking
import config

class FileDatasource:
    def __init__(self, accelerometer_filename: str, gps_filename: str, parking_filename: str) -> None:
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename
        self.parking_filename = parking_filename

    def read(self) -> AggregatedData:
        if self._position == len(self._data):
            self._position = 0
        data = self._data[self._position]
        data = AggregatedData(data.accelerometer, data.gps, data.parking, datetime.now(), config.USER_ID)
        self._position += 1
        return data

    def startReading(self, *args, **kwargs):
        self._position = 0
        self._data = []

        with open(self.accelerometer_filename, "r") as accelerometer_file, \
                open(self.gps_filename, "r") as gps_file, \
                open(self.parking_filename, "r") as parking_file:

            accelerometer_data_reader = reader(accelerometer_file)
            gps_data_reader = reader(gps_file)
            parking_data_reader = reader(parking_file)

            for _ in range(3):
                next(accelerometer_data_reader)
                next(gps_data_reader)
                next(parking_data_reader)

            for accelerometer_row, gps_row, parking_row in zip(
                    accelerometer_data_reader, gps_data_reader, parking_data_reader
            ):
                if not all((accelerometer_row, gps_row, parking_row)):
                    continue

                x, y, z = map(int, accelerometer_row)
                longitude, latitude = map(float, gps_row)
                empty_count = float(parking_row[0])
                p_longitude, p_latitude = map(float, parking_row[1:3])

                aggregated_data = AggregatedData(
                    Accelerometer(x, y, z),
                    Gps(longitude, latitude),
                    Parking(empty_count, Gps(p_longitude, p_latitude)),
                    datetime.now(),
                    config.USER_ID
                )

                self._data.append(aggregated_data)
        
    def stopReading(self, *args, **kwargs):
        if self.accelerometer_file:
            self.accelerometer_file.close()
        if self.gps_file:
            self.gps_file.close()
        if self.parking_file:
            self.parking_file.close()