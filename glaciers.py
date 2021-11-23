import csv
from datetime import datetime
from pathlib import PosixPath
from matplotlib import pyplot as plt
from os.path import splitext
from utils import haversine_distance


class Glacier:
    def __init__(self, glacier_id, name, unit, lat, lon, code):
        # check parameters are of the correct type
        if type(glacier_id) != str:
            raise TypeError("Glacier ID is not a string")

        if len(glacier_id) != 5:
            raise ValueError("Glacier ID is not the correct length (should be 5 digits)")

        if type(name) != str:
            raise TypeError("Glacier name is not a string")

        if type(unit) != str:
            raise TypeError("Glacier political unit is not a string")

        if len(unit) != 2:
            raise ValueError("Political unit code of incorrect length (should be length 2)")

        if unit != '99' and not unit.isupper():
            raise ValueError("Political unit code invalid (should either be capital letters or the unknown code '99')")

        if type(lat) != int and type(lat) != float:
            raise TypeError("Latitude of glacier is not of accepted numeric type")

        if not (-90 <= lat <= 90):
            raise ValueError("Invalid latitude of glacier given (should be in range -90 to 90)")

        if not (type(lon) == int or type(lon) == float):
            raise TypeError("Longitude of glacier is not of accepted numeric type")

        if not (-180 <= lon <= 180):
            raise ValueError("Invalid longitude of glacier given (should be in range -180 to 180)")

        if type(code) != int:
            raise TypeError("The glacier type code must be an integer")

        if len(str(code)) != 3:
            raise ValueError("The glacier type code must be 3-digits")

        self.id = glacier_id
        self.name = name
        self.unit = unit
        self.coordinates = (lat, lon)
        self.type = code
        self.mass_balances = {}

    def add_mass_balance_measurement(self, year, mass_balance, partial):
        # check parameters
        if not (type(year) == int or (type(year) == str and str(year).isnumeric())):
            raise TypeError("Year of mass-balance measurement not of supported type (integer or numeric string)")

        year = int(year)

        if not (0 <= year <= datetime.now().year):
            raise ValueError("Invalid year given of mass-balance reading (should be a positive and of maximum value the current year (not in future)")

        if not (type(mass_balance) == int or type(mass_balance) == float):
            raise TypeError("Mass-balance measurement not of supported numeric type")

        if not (type(partial) == bool):
            raise TypeError("Input mass-balance measurement does not indicate whether measurement is partial or full (through boolean type)")

        # update glacier with measurement
        if year in self.mass_balances.keys():
            # if partial measurement and already exists in dict, add to this value to get sum
            if partial:
                self.mass_balances[year] += mass_balance
        else:
            # if measurement doesnt exist yet, add it
            self.mass_balances.update({year: mass_balance})
        # N.B. if key exists but measurement isn't partial, this value is ignored

        return True

    def plot_mass_balance(self, output_path):
        # check parameters and glacier
        if not (type(output_path) == PosixPath):
            raise TypeError("Directory plot to be saved to not specified as a Path object")

        if not (len(self.mass_balances.keys()) > 0):
            raise ValueError("No mass balance data recorded for glacier trying to be plotted")

        # generate plot
        x_vals = self.mass_balances.keys()
        y_vals = self.mass_balances.values()

        plot, plot_axes = plt.subplots()
        plot_axes.plot(x_vals, y_vals, label=self.name)
        plot_axes.set_title("Graph of net mass-balance per year")
        plot_axes.set_xlabel("Year")
        plot_axes.set_ylabel("Mass-balance")
        plot_axes.legend()
        plot.tight_layout()
        plot.savefig(output_path)


class GlacierCollection:

    def __init__(self, file_path):
        # check parameters
        if not (type(file_path) == PosixPath):
            raise TypeError("File loading glacier data from not specified as a Path object")

        if not file_path.is_file():
            raise FileNotFoundError("Specified glacier data file does not exist")

        _, extension = splitext(file_path)
        if extension != '.csv':
            raise ValueError(f"Glacier data file must be '.csv' not '{extension}'")

        # load glacier data from file
        with open(file_path, 'r') as file:
            file.seek(0)
            header = file.readline()
            header = header[:-1].split(',')
            reader = csv.reader(file)
            body = list(reader)

        if not (len(body) > 0):
            raise EOFError("No glaciers specified in the input data file")

        self.glaciers = {}
        id_index = header.index('WGMS_ID')
        name_index = header.index('NAME')
        unit_index = header.index('POLITICAL_UNIT')
        lat_index = header.index('LATITUDE')
        lon_index = header.index('LONGITUDE')
        type1_index = header.index('PRIM_CLASSIFIC')
        type2_index = header.index('FORM')
        type3_index = header.index('FRONTAL_CHARS')

        for i in range(len(body)):
            row = body[i]
            gid = row[id_index]
            name = row[name_index]
            unit = row[unit_index]
            lat = row[lat_index]
            lon = row[lon_index]
            type1 = row[type1_index]
            type2 = row[type2_index]
            type3 = row[type3_index]

            # validity checks
            if not lat.replace('.', '', 1).replace('-', '', 1).isnumeric():
                raise ValueError(f"Specified latitude on row {i} of data file is not numeric")

            if not lon.replace('.', '', 1).replace('-', '', 1).isnumeric():
                raise ValueError(f"Specified longitude on row {i} of data file is not numeric")

            if not (len(type1) == 1 and type1.isdigit()):
                raise ValueError(f"Primary classification on row {i} of data file is not a single digit")

            if not (len(type2) == 1 and type2.isdigit()):
                raise ValueError(f"Form on row {i} of data file is not a single digit")

            if not (len(type3) == 1 and type3.isdigit()):
                raise ValueError(f"Frontal characteristics on row {i} of data file is not a single digit")

            lat = float(lat)
            lon = float(lon)
            code = int(type1 + type2 + type3)

            if gid in self.glaciers.keys():
                raise KeyError(f"Glacier ID on row {i} of data file not unique (or glacier specified multiple times)")

            self.glaciers.update({gid: Glacier(gid, name, unit, lat, lon, code)})

    def read_mass_balance_data(self, file_path):
        # check parameters
        if type(file_path) != PosixPath:
            raise TypeError("File holding mass-balance data not specified as a Path object")

        if not file_path.is_file():
            raise FileNotFoundError("Specified glacier mass-balance data file does not exist")

        _, extension = splitext(file_path)
        if extension != '.csv':
            raise ValueError(f"Glacier mass-balance file must be '.csv' not '{extension}'")

        # load mass balance data from file
        with open(file_path, 'r') as file:
            file.seek(0)
            header = file.readline()
            header = header[:-1].split(',')
            reader = csv.reader(file)
            body = list(reader)

        if len(body) == 0:
            raise EOFError("No mass-balance data specified in the input file")

        id_index = header.index('WGMS_ID')
        year_index = header.index('YEAR')
        mass_balance_index = header.index('ANNUAL_BALANCE')
        lb_index = header.index('LOWER_BOUND')
        ub_index = header.index('UPPER_BOUND')

        for row in body:
            gid = row[id_index]
            year = int(row[year_index])
            mass_balance = row[mass_balance_index]

            if mass_balance == '':
                continue
            else:
                mass_balance = float(mass_balance)

            l_bound = int(row[lb_index])
            u_bound = int(row[ub_index])

            if l_bound == 9999 and u_bound == 9999:
                is_partial = False
            else:
                is_partial = True

            if mass_balance != '':
                if gid not in self.glaciers.keys():
                    raise KeyError("Glacier trying to be populated with mass-balance data not present in collection")

                self.glaciers[gid].add_mass_balance_measurement(int(year), float(mass_balance), is_partial)

        return True

    def find_nearest(self, lat, lon, n=5):
        """Get the n glaciers closest to the given coordinates."""
        # check parameters
        if not (type(lat) == int or type(lat) == float):
            raise TypeError("Latitude is not of accepted numeric type")

        if not (-90 <= lat <= 90):
            raise ValueError("Invalid latitude given (should be in range -90 to 90)")

        if not (type(lon) == int or type(lon) == float):
            raise TypeError("Longitude is not of accepted numeric type")

        if not (-180 <= lon <= 180):
            raise ValueError("Invalid longitude given (should be in range -180 to 180)")

        if type(n) != int:
            raise TypeError("The number of glaciers to return 'n' is not an integer")

        if n < 0:
            raise ValueError("The number of glaciers to return 'n' must be non-negative")

        if len(self.glaciers.keys()) < n:
            raise ValueError(f"There are not 'n={n}' glaciers in the dataset to return")

        # calculate nearest glaciers
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
        # check parameters
        if not (type(code_pattern) == str or type(code_pattern) == int):
            raise TypeError("Input code pattern not a string or an integer")

        code_pattern = str(code_pattern)

        if not (len(code_pattern) == 3):
            raise ValueError("Input code pattern must be of length 3")

        numeric_pattern = code_pattern.replace("?", "", 3)

        if type(code_pattern) == str and len(numeric_pattern) > 0 and not numeric_pattern.isnumeric():
            raise ValueError("Input code pattern must be all numeric characters")

        # filter all glaciers by pattern
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

        for k, v in self.glaciers.items():
            if v.type in codes:
                names.append(v.name)

        return names

    def sort_by_latest_mass_balance(self, n=5, reverse=False):
        """Return the N glaciers with the highest area accumulated in the last measurement."""
        # check parameters
        if not (type(n) == int):
            raise TypeError("Input number of glaciers 'n' is not an integer")

        if n < 0:
            raise ValueError("Input number of glaciers 'n' must be non-negative")

        if not (type(reverse) == bool):
            raise TypeError("Input parameter 'reverse' must be of boolean type")

        # find greatest/smallest change and return result
        changes = {}

        for k, v in self.glaciers.items():
            if len(v.mass_balances.keys()) > 0:
                latest_change = v.mass_balances[max(v.mass_balances.keys())]

                if not reverse:
                    if len(changes.keys()) < n:
                        changes.update({latest_change: v})
                    elif latest_change > min(changes.keys()):
                        changes.pop(min(changes.keys()))
                        changes.update({latest_change: v})
                else:
                    if len(changes.keys()) < n:
                        changes.update({latest_change: v})
                    elif latest_change < max(changes.keys()):
                        changes.pop(max(changes.keys()))
                        changes.update({latest_change: v})

        if len(changes) == 0:
            raise ValueError("No glaciers have mass-balance data, so cannot return highest/lowest changes")

        result = [changes[k] for k in sorted(changes.keys(), reverse=(not reverse))]

        if not (len(result) == n):
            raise ValueError("There are not 'n' glaciers in the collection with mass-balance data to sort")

        return result

    def summary(self):
        # number of glaciers
        no_glaciers = len(self.glaciers.keys())

        # earliest mass-balance measurement year
        earliest_year = datetime.now().year
        for k, v in self.glaciers.items():
            if len(v.mass_balances.keys()) > 0:
                min_year_k = min(v.mass_balances.keys())

                if min_year_k < earliest_year:
                    earliest_year = min_year_k

        # % of glaciers that shrunk at last measurement
        glaciers_with_measurements = 0
        shrinkers = 0

        for k, v in self.glaciers.items():
            if len(v.mass_balances.keys()) > 0:
                glaciers_with_measurements += 1
                latest_change = v.mass_balances[max(v.mass_balances.keys())]
                if latest_change < 0:
                    shrinkers += 1

        if glaciers_with_measurements == 0:
            raise ZeroDivisionError("No glaciers in collection have mass-balance data")

        percent_shrunk = round((shrinkers / glaciers_with_measurements) * 100)

        print(f"This collection has {no_glaciers} glaciers.")
        print(f"The earliest measurement was in {earliest_year}.")
        print(f"{percent_shrunk}% of glaciers shrunk in their last measurement.")

        return True

    def plot_extremes(self, output_path, latest_=None):
        # check parameters
        if not (type(output_path) == PosixPath):
            raise TypeError("Directory plot to be saved to not specified as a Path object")

        # retrieve growth extreme data
        grow_extreme = self.sort_by_latest_mass_balance(n=1)
        grow_extreme_glacier = grow_extreme[0]
        latest_year = max(grow_extreme_glacier.mass_balances.keys())
        growth = grow_extreme_glacier.mass_balances[latest_year]

        if growth <= 0:
            raise ValueError("No glacier grew in latest measurements")

        # plot growth extreme
        x_vals_grow = grow_extreme_glacier.mass_balances.keys()
        y_vals_grow = grow_extreme_glacier.mass_balances.values()

        plot, plot_axes = plt.subplots()
        plot_axes.plot(x_vals_grow, y_vals_grow, label=grow_extreme_glacier.name)

        # retrieve shrinking extreme data
        shrunk_extreme = self.sort_by_latest_mass_balance(n=1, reverse=True)
        shrunk_extreme_glacier = shrunk_extreme[0]
        latest_year = max(shrunk_extreme_glacier.mass_balances.keys())
        shrinkage = shrunk_extreme_glacier.mass_balances[latest_year]

        if shrinkage >= 0:
            raise ValueError("No glacier shrunk in latest measurements")

        # plot shrinking extreme
        x_vals_shrunk = shrunk_extreme_glacier.mass_balances.keys()
        y_vals_shrunk = shrunk_extreme_glacier.mass_balances.values()

        plot_axes.plot(x_vals_shrunk, y_vals_shrunk, label=shrunk_extreme_glacier.name)

        # add detail to plot
        plot_axes.set_title("Net mass-balance per year for extreme glaciers of collection")
        plot_axes.set_xlabel("Year")
        plot_axes.set_ylabel("Mass-balance")
        plot_axes.legend()
        plot.tight_layout()
        plot.savefig(output_path)
