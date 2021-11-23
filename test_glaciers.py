from glaciers import Glacier, GlacierCollection
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
def test_invalid_glacier_id():
    tests = {
        55555: TypeError,
        100.55: TypeError,
        '000': ValueError,

    }

    for id, error in tests.items():
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
def test_invalid_political_unit():
    tests = {
        55: TypeError,
        'longunit': ValueError
    }

    for unit, error in tests.items():
        with raises(error) as exception:
            Glacier(glacier_id='04532',
                    name='AGUA NEGRA',
                    unit=unit,
                    lat=-30.16490,
                    lon=-69.80940,
                    code=638)


# testing invalid longitude and latitudes to glacier constructor
def test_invalid_lat_lon():
    tests = [[TypeError, 'invalid_string_lat', -69.80940],
             [TypeError, -30.16490, 'invalid_string_lon'],
             [ValueError, 100.0, -69.80940],
             [ValueError, -100.0, -69.80940],
             [ValueError, -30.16490, 200.0],
             [ValueError, -30.16490, -200.0]]

    for test in tests:
        error = test[0]
        lat = test[1]
        lon = test[2]

        with raises(error) as exception:
            Glacier(glacier_id='04532',
                    name='AGUA NEGRA',
                    unit='AR',
                    lat=lat,
                    lon=lon,
                    code=638)


# testing invalid glacier type codes
def test_invalid_glacier_code():
    tests = {
        'ABC': TypeError,
        '123': TypeError,
        0: ValueError,
        1000.9: TypeError,
        9999: ValueError
    }

    for code, error in tests.items():
        with raises(error) as exception:
            Glacier(glacier_id='04532',
                    name='AGUA NEGRA',
                    unit='AR',
                    lat=-30.16490,
                    lon=-69.80940,
                    code=code)
