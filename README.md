# Studying Glaciers: Reading and analysing historical datasets

This project investigates historical measurements of glacier size, implementing code to make it easier to load glacier data and perform analyses.

## Glacier information

For each glacier, we record some basic pieces of information:
- its name
- a unique identifier (ID) for referring to it
- the country or other political unit it belongs to
- its type, composed of three aspects (primary classification, form, frontal characteristics)
- its location (latitude and longitude)

Additionally, we care about how the “health” of the glacier changes over time. Glaciers can grow and decrease in size. This is measured through a quantity called mass-balance. In its simplest form, it is a single number which measures the net growth or loss in a given time period. If it is positive, it means that the glacier has grown. If it is negative, it has shrunk.

## Structure of the data

The data you are working has been compiled over a number of years. It is split across multiple files in CSV format. For the purposes of the project, we will look at two files, `sheet-A.csv` and `sheet-EE.csv`.

The first file (`sheet-A.csv`) has the basic information for each glacier. It contains one row per glacier. The of interest columns are, in order:
- political unit
- name
- identifier (WGMS_ID), made up of 5 digits
- latitude, in degrees
- longitude, in degrees
- primary classification, encoded as a digit
- form, encoded as a digit
- frontal characteristics, encoded as a digit

<img width="1415" alt="Screenshot 2023-01-28 at 17 04 31" src="https://user-images.githubusercontent.com/44398472/215279330-5f0590b5-dc31-458b-83ba-e07283acd27c.png">

The second file (`sheet-EE.csv`) contains the mass-balance measurements taken across the years. It has one row per measurement. Each glacier can have data for multiple years. There can also be multiple measurements per year for some glaciers: sometimes, the mass-balance is recorded for different parts of the glacier, contained within specific altitudes. In those cases, these lower and upper bounds are recorded in that row. However, if the measurement refers to the entire glacier, then the lower and upper altitudes are recorded as 9999.

<img width="1284" alt="Screenshot 2023-01-28 at 17 05 38" src="https://user-images.githubusercontent.com/44398472/215279384-35cd78ae-5014-425b-ae2d-0250cd01dfd7.png">

The columns named POLITICAL_UNIT, NAME, and WGMS_ID are the same as in the first file. The other columns of interest are:
- YEAR: the year the measurement refers to
- LOWER_BOUND and UPPER_BOUND: the range of altitudes the measurement refers to (as described
above), in meters above sea level (m.a.s.l.)
- ANNUAL_BALANCE: the net value for the mass-balance, in millimeters water equivalent (mm.w.e.)

The data files used by the project are a simplified version of the datasets of the World Glacier Monitoring Service. Those datasets are released as open access under condition of attribution:
Zemp, Michael, Samuel U Nussbaumer, Isabelle Gärtner-Roer, Jacqueline Bannwart, Philipp Rastner, Frank
Paul, and Martin Hoelzle, eds. 2021. Global Glacier Change Bulletin No. 4 (2018-2019). Zürich, Switzerland: ISC(WDS)/IUGG(IACS)/UNEP/UNESCO/WMO, World Glacier Monitoring Service. https://doi.org/10.5904/wgms-fog-2021-05.

## Program

The implemented projram reads in, validates, and analyses this data.

The code is split over two files. `glaciers.py` contains the definition of two classes, `Glacier` and `GlacierCollection`. The first represents a single glacier, while the second brings together all the glaciers from a dataset. The second file, `utilities.py`, is a place to put useful functions.

Users can create `Glacier` objects and call methods on them. However, the user will likely interact primarily through the `GlacierCollection`, by creating it, adding data and retrieving some analysis results.

### Reading in data

To create a `Glacier` object, one must know some basic properties: its unique identifier, name, political unit, coordinates, and the 3-digit code describing its type. These are passed to the class’s constructor: `my_glacier = Glacier(”01657”, ”DE LOS TRES”, ”AR”, -49.33, -73.0, 544)`

Alternatively, users can create an entire collection by passing in the file containing basic information (`sheet-A.csv`). The argument to the constructor should be a `Path` object from Python’s `pathlib` module. For example: 
`
from pathlib import Path
file_path = Path(”../sheet-A.csv”)
collection = GlacierCollection(file_path)
`

Once the `GlacierCollection` is available, it should be possible to read in the mass-balance data through its `read_mass_balance_data` method, which should take as input another `Path` object pointing to the relevant sheet. This method should, in turn, call the `add_mass_balance_measurement` method of `Glacier`, which takes 3 arguments: the year, the value, and a boolean value indicating whether this is a partial (sub-region) measurement or not.

### Analysis

Given a `GlacierCollection` object, the `filter_by_code` method should take a 3-digit code as an integer or string, and return the names of all the glaciers with that code. For more flexibility, we may want to match several codes at once. To do this, the method should allow matching an incomplete code using the character "?". For example, if we want to find glaciers with codes where the first digit is 4 and the third digit is 9, but the second digit could be anything, we should be able to pass in the argument "4?9".

The `find_nearest` method should take as arguments a latitude, a longitude, and a number of results "n", and return a list of the names of the "n" glaciers which are closest to those coordinates.

The `sort_by_latest_mass_balance` method should accept an optional argument "n" (default: 5) and return a list of "n" `Glacier` objects, representing the glaciers with the greatest change in mass-balance at the time they were last recorded (the year of those measurements may differ across the glaciers).

The summary method should compute and display the following:
- number of glaciers in the collection
- earliest year of recorded mass-balance change (for any single glacier)
- percentage of the glaciers that shrunk at their last measurement, rounded to the nearest integer

### Plotting

`Glacier` objects also have a `plot_mass_balance` which plots the mass balance measurements on the Y-axis against the years the measurements were taken on the X-axis.

`GlacierCollection` objects also have a visualisation method called `plot_extremes`. This method should plot the mass balance measurements against the years for the two extreme glaciers in the collection.

Both plotting methods should also label the axes appropriately and save the plot to a file. They should therefore take a file path (a `Path` object, as above) as an argument.
