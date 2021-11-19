import csv
from pathlib import Path
from utils import haversine_distance


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
        self.mass_balances = {}

    def add_mass_balance_measurement(self, year, mass_balance, partial):
        if year in self.mass_balances.keys():
            # if partial measurement and already exists in dict, add to this value to get sum
            if partial:
                self.mass_balances[year] += mass_balance
        else:
            # if measurement doesnt exist yet, add it
            self.mass_balances.update({year: mass_balance})
        # N.B. if key exists but measurement isn't partial, this value is ignored

    def plot_mass_balance(self, output_path):
        raise NotImplementedError

        
class GlacierCollection:

    def __init__(self, file_path):

        with open(file_path, 'r') as file:
            file.seek(0)
            header = file.readline()
            header = header[:-1].split(',')
            reader = csv.reader(file)
            body = list(reader)

        self.glaciers = {}
        id_index = header.index('WGMS_ID')
        name_index = header.index('NAME')
        unit_index = header.index('POLITICAL_UNIT')
        lat_index = header.index('LATITUDE')
        lon_index = header.index('LONGITUDE')
        type1_index = header.index('PRIM_CLASSIFIC')
        type2_index = header.index('FORM')
        type3_index = header.index('FRONTAL_CHARS')

        for row in body:
            gid = row[id_index]
            name = row[name_index]
            unit = row[unit_index]
            lat = float(row[lat_index])
            lon = float(row[lon_index])
            code = int(row[type1_index] + row[type2_index] + row[type3_index])

            self.glaciers.update({gid: Glacier(gid, name, unit, lat, lon, code)})

    def read_mass_balance_data(self, file_path):

        with open(file_path, 'r') as file:
            file.seek(0)
            header = file.readline()
            header = header[:-1].split(',')
            reader = csv.reader(file)
            body = list(reader)

        id_index = header.index('WGMS_ID')
        year_index = header.index('YEAR')
        mass_balance_index = header.index('ANNUAL_BALANCE')
        lb_index = header.index('LOWER_BOUND')
        ub_index = header.index('UPPER_BOUND')

        for row in body:
            gid = row[id_index]
            year = row[year_index]
            mass_balance = row[mass_balance_index]
            l_bound = int(row[lb_index])
            u_bound = int(row[ub_index])

            if l_bound == 9999 and u_bound == 9999:
                is_partial = False
            else:
                is_partial = True

            if mass_balance != '':
                self.glaciers[gid].add_mass_balance_measurement(int(year), float(mass_balance), is_partial)

    def find_nearest(self, lat, lon, n=5):
        """Get the n glaciers closest to the given coordinates."""
        nearest = {}

        for k, v in self.glaciers.items():
            lat2, lon2 = v.coordinates
            dist = haversine_distance(lat, lon, lat2, lon2)

            if len(nearest.keys()) < n:
                nearest.update({v.name: dist})
            elif dist < max(nearest.values()):
                maxi = max(nearest, key=nearest.get)
                nearest.pop(maxi)
                nearest.update({v.name: dist})

        return list(nearest.keys())

    
    def filter_by_code(self, code_pattern):
        """Return the names of glaciers whose codes match the given pattern."""
        if type(code_pattern) != str and type(code_pattern) != int:
            raise TypeError

        names = []
        code_pattern = str(code_pattern)
        codes = [code_pattern]

        while True:
            new_codes = []
            for code in codes:
                if '?' in code:
                    ind = code.index('?')
                    new_codes.extend([code[:ind] + str(x) + code[ind+1:] for x in range(10)])
                else:
                    new_codes.append(code)

            if new_codes == codes:
                codes = list(map(int, codes))
                break
            else:
                codes = new_codes.copy()

        for k,v in self.glaciers.items():
            if v.type in codes:
                names.append(v.name)

        return names

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
mass_balance_file = Path("sheet-EE.csv")
collection.read_mass_balance_data(mass_balance_file)
res = collection.find_nearest(-30.16490, -69.80940)
print(res)