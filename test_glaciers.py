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
                    (1999, 500, True)]


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
tests = [(ValueError, 2055, -234.99, False),
         (ValueError, -10, 500, True),
         (TypeError, "two thousand", -50.99, True),
         (TypeError, 2016, "negative fifty", True),
         (TypeError, 2000, 0.0, "not_a_bool")]


@pytest.mark.parametrize("error,year,mass_balance,partial", tests)
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


# a file which does not exist is input into the collection constructor
def test_no_glacier_file():
    with raises(FileNotFoundError) as exception:
        file = Path('invalid_file.png')
        GlacierCollection(file)


# existing glacier data file of correct format should pass
def test_correct_glacier_file():
    file = Path('sheet-A.csv')
    assert GlacierCollection(file)


# a non-existent file passed into mass-balance reading method
def test_no_mass_balance_file():
    with raises(FileNotFoundError) as exception:
        file = Path('sheet-A.csv')
        collection = GlacierCollection(file)
        mass_balance_file = Path("invalid_file.txt")
        collection.read_mass_balance_data(mass_balance_file)
