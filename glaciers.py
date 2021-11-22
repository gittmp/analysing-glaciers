import csv
from datetime import datetime
from pathlib import Path, PosixPath
from matplotlib import pyplot as plt
from utils import haversine_distance


class Glacier:
    def __init__(self, glacier_id, name, unit, lat, lon, code):
        # check parameters are of the correct type
        assert (type(glacier_id) == str), "Glacier ID is not a string"
        assert (len(glacier_id) == 5), "Glacier ID is not the correct length (should be 5 digits)"
        assert (type(name) == str), "Glacier name is not a string"
        assert (type(unit) == str), "Glacier political unit is not a string"
        assert (len(unit) == 2), "Political unit code of incorrect length (should be length 2)"
        assert (unit == '99' or unit.isupper()), "Political unit code invalid (should either be capital letters or the unknown code '99')"

        assert (type(lat) == int or type(lat) == float), "Latitude of glacier is not of accepted numeric type"
        assert (-90 <= lat <= 90), "Invalid latitude of glacier given (should be in range -90 to 90)"
        assert (type(lon) == int or type(lon) == float), "Longitude of glacier is not of accepted numeric type"
        assert (-180 <= lon <= 180), "Invalid longitude of glacier given (should be in range -180 to 180)"
        assert (type(code) == int and len(str(code)) == 3), "The glacier type code is not a 3-digit integer"

        self.id = glacier_id
        self.name = name
        self.unit = unit
        self.coordinates = (lat, lon)
        self.type = code
        self.mass_balances = {}

    def add_mass_balance_measurement(self, year, mass_balance, partial):
        # check parameters
        assert (type(year) == int or type(year) == str), "Year of mass-balance measurement not of supported type (integer or string)"
        year = int(year)
        assert (0 <= year <= datetime.now().year), "Invalid year given of mass-balance reading (should be a positive and of maximum value the current year (not in future)"
        assert (type(mass_balance) == int or type(mass_balance) == float), "Mass-balance measurement not of supported numeric type"
        assert (type(partial) == bool), "Input mass-balance measurement does not indicate whether measurement is partial or full (through boolean type)"

        # update glacier with measurement
        if year in self.mass_balances.keys():
            # if partial measurement and already exists in dict, add to this value to get sum
            if partial:
                self.mass_balances[year] += mass_balance
        else:
            # if measurement doesnt exist yet, add it
            self.mass_balances.update({year: mass_balance})
        # N.B. if key exists but measurement isn't partial, this value is ignored

    def plot_mass_balance(self, output_path):
        # check parameters and glacier
        assert (type(output_path) == PosixPath), "Directory plot to be saved to not specified as a Path object"
        assert (len(self.mass_balances.keys()) > 0), "No mass balance data recorded for glacier trying to be plotted"

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
        assert (type(file_path) == PosixPath), "File loading glacier data from not specified as a Path object"
        assert file_path.is_file(), "Specified glacier data file does not exist"

        # load glacier data from file
        with open(file_path, 'r') as file:
            file.seek(0)
            header = file.readline()
            header = header[:-1].split(',')
            reader = csv.reader(file)
            body = list(reader)

        assert (len(body) > 0), "No glaciers specified in the input data file"

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
            assert lat.replace('.', '', 1).replace('-', '', 1).isnumeric(), f"Specified latitude on row {i} of data file is not numeric"
            assert lon.replace('.', '', 1).replace('-', '', 1).isnumeric(), f"Specified longitude on row {i} of data file is not numeric"
            assert (len(type1) == 1 and type1.isdigit()), f"Primary classification on row {i} of data file is not a single digit"
            assert (len(type2) == 1 and type2.isdigit()), f"Form on row {i} of data file is not a single digit"
            assert (len(type3) == 1 and type3.isdigit()), f"Frontal characteristics on row {i} of data file is not a single digit"

            lat = float(lat)
            lon = float(lon)
            code = int(type1 + type2 + type3)

            assert (gid not in self.glaciers.keys()), f"Glacier ID on row {i} of data file not unique (or glacier specified multiple times)"

            self.glaciers.update({gid: Glacier(gid, name, unit, lat, lon, code)})

    def read_mass_balance_data(self, file_path):
        # check paramaters
        assert (type(file_path) == PosixPath), "File holding mass-balance data not specified as a Path object"
        assert file_path.is_file(), "Specified glacier mass-balance data file does not exist"

        # load mass balance data from file
        with open(file_path, 'r') as file:
            file.seek(0)
            header = file.readline()
            header = header[:-1].split(',')
            reader = csv.reader(file)
            body = list(reader)

        assert (len(body) > 0), "No mass-balance data specified in the input file"

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
                assert (gid in self.glaciers.keys()), "Glacier trying to be populated with mass-balance data not present in collection"
                self.glaciers[gid].add_mass_balance_measurement(int(year), float(mass_balance), is_partial)

    def find_nearest(self, lat, lon, n=5):
        """Get the n glaciers closest to the given coordinates."""
        # check parameters
        assert (type(lat) == int or type(lat) == float), "Latitude is not of accepted numeric type"
        assert (-90 <= lat <= 90), "Invalid latitude given (should be in range -90 to 90)"
        assert (type(lon) == int or type(lon) == float), "Longitude is not of accepted numeric type"
        assert (-180 <= lon <= 180), "Invalid longitude given (should be in range -180 to 180)"
        assert (type(n) == int), "The number of glaciers to return 'n' is not an integer"

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
        assert (type(code_pattern) == str or type(code_pattern) == int), "Input code pattern not a string or an integer"
        assert (len(code_pattern) == 3), "Input code pattern must be of length 3"

        if type(code_pattern) == str:
            assert code_pattern.isnumeric(), "Input code pattern must be all numeric characters"

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

        for k,v in self.glaciers.items():
            if v.type in codes:
                names.append(v.name)

        return names

    def sort_by_latest_mass_balance(self, n=5, reverse=False):
        """Return the N glaciers with the highest area accumulated in the last measurement."""
        # check parameters
        assert (type(n) == int), "Input number of glaciers n not an integer"
        assert (type(reverse) == bool), "Input parameter 'reverse' must be of boolean type"

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

        assert (len(changes) > 0), "No glaciers have mass-balance data, so cannot return highest/lowest changes"

        result = [changes[k] for k in sorted(changes.keys(), reverse=(not reverse))]

        assert (len(result) == n), "There are not 'n' glaciers in the collection with mass-balance data to sort"

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

        assert (glaciers_with_measurements != 0), "No glaciers in collection have mass-balance data"
        percent_shrunk = round((shrinkers / glaciers_with_measurements) * 100)

        print(f"This collection has {no_glaciers} glaciers.")
        print(f"The earliest measurement was in {earliest_year}.")
        print(f"{percent_shrunk}% of glaciers shrunk in their last measurement.")

    def plot_extremes(self, output_path):
        # check parameters
        assert (type(output_path) == PosixPath), "Directory plot to be saved to not specified as a Path object"

        # retrieve growth extreme data
        grow_extreme = self.sort_by_latest_mass_balance(n=1)
        grow_extreme_glacier = grow_extreme[0]

        growth = grow_extreme_glacier.mass_balances[max(grow_extreme_glacier.mass_balances.keys())]
        assert (growth > 0), "No glacier grew in latest measurements"

        # plot growth extreme
        x_vals_grow = grow_extreme_glacier.mass_balances.keys()
        y_vals_grow = grow_extreme_glacier.mass_balances.values()

        plot, plot_axes = plt.subplots()
        plot_axes.plot(x_vals_grow, y_vals_grow, label=grow_extreme_glacier.name)

        # retrieve shrinking extreme data
        shrunk_extreme = self.sort_by_latest_mass_balance(n=1, reverse=True)
        shrunk_extreme_glacier = shrunk_extreme[0]

        shrinkage = shrunk_extreme_glacier.mass_balances[max(shrunk_extreme_glacier.mass_balances.keys())]
        assert (shrinkage < 0), "No glacier shrunk in latest measurements"

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


# Test
file_path = Path("sheet-A.csv")
collection = GlacierCollection(file_path)
mass_balance_file = Path("sheet-EE.csv")
collection.read_mass_balance_data(mass_balance_file)
collection.find_nearest(32.38517, 77.86855, n=5)
collection.filter_by_code('555')
collection.sort_by_latest_mass_balance()
collection.sort_by_latest_mass_balance(reverse=True)
collection.summary()
plot_file = Path("figure.png")
collection.plot_extremes(plot_file)
