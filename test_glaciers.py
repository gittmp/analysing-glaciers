from glaciers import Glacier, GlacierCollection
import pytest
from pytest import raises
from pathlib import Path


# correct creation of a glacier should raise no errors
def test_correct_glacier_creation():
    assert Glacier(glacier_id='04532',
                   name='AGUA NEGRA',
                   unit='AR',
                   lat=-30.16490,
                   lon=-69.80940,
                   code=638)

    assert Glacier(glacier_id='53192',
                   name='SKAFTAFELLSJOKULL',
                   unit='99',
                   lat=32.05591,
                   lon=77.81169,
                   code=123)


# glacier object attempting to be created with invalid ID
id_tests = [(55555, TypeError),
         (100.55, TypeError),
         ('000', ValueError)]


@pytest.mark.parametrize("id, error", id_tests)
def test_invalid_glacier_id(id, error):
    with raises(error) as exception:
        Glacier(glacier_id=id,
                name='GLACIER',
                unit='AR',
                lat=-33.08750,
                lon=-70.05670,
                code=123)


# test that creating a glacier with an invalid name isn't possible
def test_invalid_glacier_name():
    with raises(TypeError) as exception:
        Glacier(glacier_id='04532',
                name=200,
                unit='AR',
                lat=-33.08750,
                lon=-70.05670,
                code=123)


# test inputting an invalid glacier political unit
unit_tests = [(55, TypeError),
              ('longunit', ValueError)]


@pytest.mark.parametrize("unit, error", unit_tests)
def test_invalid_political_unit(unit, error):
    with raises(error) as exception:
        Glacier(glacier_id='04532',
                name='AGUA NEGRA',
                unit=unit,
                lat=-30.16490,
                lon=-69.80940,
                code=638)


# testing invalid longitude and latitudes to glacier constructor
latlon_tests = [(TypeError, 'invalid_string_lat', -69.80940),
                (TypeError, -30.16490, 'invalid_string_lon'),
                (ValueError, 100.0, -69.80940),
                (ValueError, -100.0, -69.80940),
                (ValueError, -30.16490, 200.0),
                (ValueError, -30.16490, -200.0)]


@pytest.mark.parametrize("error, lat, lon", latlon_tests)
def test_invalid_lat_lon(error, lat, lon):
    with raises(error) as exception:
        Glacier(glacier_id='04532',
                name='AGUA NEGRA',
                unit='AR',
                lat=lat,
                lon=lon,
                code=638)


# testing invalid glacier type codes
code_tests = [('ABC', TypeError),
              ('123', TypeError),
              (0, ValueError),
              (1000.9, TypeError),
              (9999, ValueError)]


@pytest.mark.parametrize("code, error", code_tests)
def test_invalid_glacier_code(code, error):
    with raises(error) as exception:
        Glacier(glacier_id='04532',
                name='AGUA NEGRA',
                unit='AR',
                lat=-30.16490,
                lon=-69.80940,
                code=code)


# testing correct input on Glacier method for adding mass-balance measurement
correct_mb_tests = [(2021, -234.99, False),
                    (1999, 500, True),
                    (1999, 200.3, True),
                    (1999, 1000, False)]


@pytest.mark.parametrize("year, mass_balance, partial", correct_mb_tests)
def test_correct_mass_balance(year, mass_balance, partial):
    glacier = Glacier(glacier_id='04532',
                      name='AGUA NEGRA',
                      unit='AR',
                      lat=-30.16490,
                      lon=-69.80940,
                      code=638)

    assert glacier.add_mass_balance_measurement(year=year,
                                                mass_balance=mass_balance,
                                                partial=partial)


# test invalid input into mass-balance glacier method
invalid_mb_tests = [(ValueError, 2055, -234.99, False),
                    (ValueError, -10, 500, True),
                    (TypeError, "two thousand", -50.99, True),
                    (TypeError, 2016, "negative fifty", True),
                    (TypeError, 2000, 0.0, "not_a_bool")]


@pytest.mark.parametrize("error, year, mass_balance, partial", invalid_mb_tests)
def test_invalid_mass_balance_measurement(error, year, mass_balance, partial):
    glacier = Glacier(glacier_id='04532',
                      name='AGUA NEGRA',
                      unit='AR',
                      lat=-30.16490,
                      lon=-69.80940,
                      code=638)

    with raises(error) as exception:
        glacier.add_mass_balance_measurement(year=year,
                                             mass_balance=mass_balance,
                                             partial=partial)


# test correct input of glacier plotting method
def test_correct_glacier_plot():
    glacier = Glacier(glacier_id='04532',
                      name='AGUA NEGRA',
                      unit='AR',
                      lat=-30.16490,
                      lon=-69.80940,
                      code=638)

    glacier.add_mass_balance_measurement(year=2021, mass_balance=-200, partial=False)
    glacier.add_mass_balance_measurement(year=2020, mass_balance=-100, partial=False)
    glacier.add_mass_balance_measurement(year=2019, mass_balance=100, partial=False)

    file = Path('./figure.png')
    glacier.plot_mass_balance(file)

    assert file.is_file()


# test invalid input into glacier plot method and if no mass-balance data exists
def test_invalid_glacier_plot_inputs():
    glacier = Glacier(glacier_id='04532',
                      name='AGUA NEGRA',
                      unit='AR',
                      lat=-30.16490,
                      lon=-69.80940,
                      code=638)

    with raises(ValueError) as exception:
        file = Path('./figure.png')
        glacier.plot_mass_balance(file)

    glacier.add_mass_balance_measurement(year=2021, mass_balance=-200, partial=False)
    glacier.add_mass_balance_measurement(year=2020, mass_balance=-100, partial=False)

    with raises(TypeError) as exception:
        glacier.plot_mass_balance('just_a_string')


# test glacier construction on correct input
def test_correct_collection_init():
    file = Path('sheet-A.csv')
    assert GlacierCollection(file)


# invalid files input into the glacier collection constructor
invalid_file_tests = [('nonpathfile.csv', TypeError),
                      (Path('doesntexist.csv'), FileNotFoundError),
                      (Path('wrongextension.png'), ValueError),
                      (Path('emptyfile.csv'), EOFError),
                      (Path('invalid_latlon.csv'), ValueError),
                      (Path('invalid_code.csv'), ValueError),
                      (Path('duplicate_keys.csv'), KeyError)]


@pytest.mark.parametrize("file, error", invalid_file_tests)
def test_invalid_glacier_file(file, error):
    with raises(error) as exception:
        GlacierCollection(file)


# test reading in a correct mass-balance data file
def test_correct_mass_balance_file():
    file = Path('sheet-A.csv')
    collection = GlacierCollection(file)
    mb_file = Path('sheet-EE.csv')
    assert collection.read_mass_balance_data(mb_file)


# test invalid inputs into mass-balance reading method
mb_file_tests = [('nonpathfile.csv', TypeError),
                (Path('doesntexist.csv'), FileNotFoundError),
                (Path('wrongextension.png'), ValueError),
                (Path('emptyfile.csv'), EOFError),
                (Path('invalid_id.csv'), KeyError)]


@pytest.mark.parametrize("mb_file, error", mb_file_tests)
def test_no_mass_balance_file(mb_file, error):
    file = Path('sheet-A.csv')
    collection = GlacierCollection(file)

    with raises(error) as exception:
        collection.read_mass_balance_data(mb_file)


# test if find_nearest method works correctly on valid input
def test_correct_find_nearest():
    file = Path('sheet-A.csv')
    collection = GlacierCollection(file)
    mb_file = Path('sheet-EE.csv')
    collection.read_mass_balance_data(mb_file)

    nearest10 = collection.find_nearest(lat=-46.65000, lon=-73.18000, n=10)
    assert len(nearest10) == 10

    nearest1 = collection.find_nearest(lat=-11.88000, lon=-76.05000, n=1)
    assert (len(nearest1) == 1 and nearest1[0] == "SHULLCON")


# test invalid inputs into the find_nearest method
nearest_tests = [('1.1', 50.0, 5, TypeError),
                 (1.1, '50.0', 5, TypeError),
                 (1.1, 50.0, '5', TypeError),
                 (-71832, 50.0, 5, ValueError),
                 (1.1, 355.0, 5, ValueError),
                 (1.1, 355.0, 9999999, ValueError),
                 (1.1, 355.0, -10, ValueError)]


@pytest.mark.parametrize("lat, lon, n, error", nearest_tests)
def test_invalid_find_nearest(lat, lon, n, error):
    file = Path('sheet-A.csv')
    collection = GlacierCollection(file)
    mb_file = Path('sheet-EE.csv')
    collection.read_mass_balance_data(mb_file)

    with raises(error) as exception:
        collection.find_nearest(lat=lat, lon=lon, n=n)


# test filter method on correct valid input
def test_correct_filter():
    file = Path('sheet-A.csv')
    collection = GlacierCollection(file)
    mb_file = Path('sheet-EE.csv')
    collection.read_mass_balance_data(mb_file)

    res1 = collection.filter_by_code("638")
    assert len(res1) == 12

    res2 = collection.filter_by_code(638)
    assert len(res2) == 12

    res3 = collection.filter_by_code("52?")
    assert len(res3) == 16

    res4 = collection.filter_by_code("999")
    assert len(res4) == 0

    all_results = collection.filter_by_code("???")
    assert len(all_results) == 1696


# test invalid inputs into filter method
invalid_filter_tests = [(10.1, TypeError),
                        ("12345", ValueError),
                        ("ABC", ValueError),
                        ("1!2", ValueError)]


@pytest.mark.parametrize("filter, error", invalid_filter_tests)
def test_invalid_find_nearest(filter, error):
    file = Path('sheet-A.csv')
    collection = GlacierCollection(file)
    mb_file = Path('sheet-EE.csv')
    collection.read_mass_balance_data(mb_file)

    with raises(error) as exception:
        collection.filter_by_code(filter)


# test collection method sort_by_latest_mass_balance on valid inputs
def test_correct_sort():
    file = Path('sheet-A.csv')
    collection = GlacierCollection(file)
    mb_file = Path('sort_test_values.csv')
    collection.read_mass_balance_data(mb_file)

    res1 = collection.sort_by_latest_mass_balance(n=1, reverse=True)
    assert len(res1) == 1 and res1[0] == collection.glaciers['03987']

    res2 = collection.sort_by_latest_mass_balance(n=1, reverse=False)
    assert len(res2) == 1 and res2[0] == collection.glaciers['02660']

    res3 = collection.sort_by_latest_mass_balance(n=5, reverse=True)
    assert len(res3) == 5

    res4 = collection.sort_by_latest_mass_balance(n=5, reverse=False)
    assert len(res4) == 5


# test sort_by_latest_mass_balance for invalid inputs
invalid_sort_tests = [(TypeError, '66', False, 'sort_test_values.csv'),
                      (TypeError, 10, 'not true', 'sort_test_values.csv'),
                      (ValueError, -200, True, 'sort_test_values.csv'),
                      (ValueError, 10, False, 'sort_empty_values.csv')]


@pytest.mark.parametrize("error, n, reverse, data", invalid_sort_tests)
def test_invalid_sort(error, n, reverse, data):
    file = Path('sheet-A.csv')
    collection = GlacierCollection(file)
    mb_file = Path(data)
    collection.read_mass_balance_data(mb_file)

    with raises(error) as exception:
        collection.sort_by_latest_mass_balance(n=n, reverse=reverse)


# test summary method on correct valid data
def test_valid_summary():
    file = Path('sheet-A.csv')
    collection = GlacierCollection(file)
    mb_file = Path('sheet-EE.csv')
    collection.read_mass_balance_data(mb_file)

    assert collection.summary()


# test summary method on invalid data
def test_invalid_summary():
    file = Path('sheet-A.csv')
    collection = GlacierCollection(file)

    with raises(ZeroDivisionError) as exception:
        collection.summary()


# test collections method to plot extremes works for correct data/inputs
def test_extremes_plot():
    file = Path('sheet-A.csv')
    collection = GlacierCollection(file)
    mb_file = Path('sheet-EE.csv')
    collection.read_mass_balance_data(mb_file)

    fig = Path('./extremes_figure.png')
    collection.plot_extremes(fig)

    assert fig.is_file()


# test plot extremes method on invalid data
invalid_extremes_tests = [(TypeError, 'nonpathfile.png', 'sheet-EE.csv'),
                          (ValueError, Path('figure.png'), 'extremes1.csv'),
                          (ValueError, Path('figure.png'), 'extremes2.csv')]


@pytest.mark.parametrize("error, plot_file, data", invalid_extremes_tests)
def test_invalid_plot_extremes(error, plot_file, data):
    file = Path('sheet-A.csv')
    collection = GlacierCollection(file)
    mb_file = Path(data)
    collection.read_mass_balance_data(mb_file)

    with raises(error) as exception:
        collection.plot_extremes(plot_file)
