import csv
from pathlib import Path


class Glacier:
    def __init__(self, glacier_id, name, unit, lat, lon, code):

        if (type(glacier_id) != str) or (type(name) != str) or (type(unit) != str):
            raise TypeError

        if (type(lat) != int and type(lat) != float) or (type(lon) != int and type(lon) != float) or (type(code) != int):
            raise TypeError

        self.id = glacier_id
        self.name = name
        self.unit = unit
        self.coordinates = (lat, lon)
        self.type = code

    def add_mass_balance_measurement(self, year, mass_balance):
        raise NotImplementedError

    def plot_mass_balance(self, output_path):
        raise NotImplementedError

        
class GlacierCollection:

    def __init__(self, file_path):

        with open(file_path, 'r') as file:
            file.seek(0)
            header = file.readline()
            self.header = header[:-1].split(',')
            reader = csv.reader(file)
            body = list(reader)

        self.glaciers = {}
        id_index = self.header.index('WGMS_ID')
        name_index = self.header.index('NAME')
        unit_index = self.header.index('POLITICAL_UNIT')
        lat_index = self.header.index('LATITUDE')
        lon_index = self.header.index('LONGITUDE')
        type1_index = self.header.index('PRIM_CLASSIFIC')
        type2_index = self.header.index('FORM')
        type3_index = self.header.index('FRONTAL_CHARS')

        for row in body:
            gid = row[id_index]
            name = row[name_index]
            unit = row[unit_index]
            lat = float(row[lat_index])
            lon = float(row[lon_index])
            code = int(row[type1_index] + row[type2_index] + row[type3_index])

            self.glaciers.update({gid: Glacier(gid, name, unit, lat, lon, code)})

    def read_mass_balance_data(self, file_path):
        raise NotImplementedError

    def find_nearest(self, lat, lon, n):
        """Get the n glaciers closest to the given coordinates."""
        raise NotImplementedError
    
    def filter_by_code(self, code_pattern):
        """Return the names of glaciers whose codes match the given pattern."""
        raise NotImplementedError

    def sort_by_latest_mass_balance(self, n, reverse):
        """Return the N glaciers with the highest area accumulated in the last measurement."""
        raise NotImplementedError

    def summary(self):
        raise NotImplementedError

    def plot_extremes(self, output_path):
        raise NotImplementedError


# Test
file_path = Path("sheet-A.csv")
collection = GlacierCollection(file_path)