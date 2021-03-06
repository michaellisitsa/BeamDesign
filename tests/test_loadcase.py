import numpy as np

import pytest

from beamdesign.loadcase import LoadCase
from beamdesign.const import LoadComponents
from beamdesign.utility.exceptions import LoadCaseError


def test_LoadCase_init():
    """
    Test we can instantiate an empty LoadCase
    """

    l = LoadCase()

    assert l


def test_LoadCase_init2():
    """
    Test we can instantiate a full load case object.
    :return:
    """

    loads = [
        [0.0, 0, 0, 0, 0, 0, 0],
        [0.25, 1, 2, 3, 4, 5, 6],
        [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5],
        [0.5, 10, 10, 10, 10, 10, 10],
        [0.75, 2, 3, 4, 5, 6, 7],
        [1.0, 3, 4, 5, 6, 7, 8],
    ]

    a = LoadCase(loads=loads)

    assert a


@pytest.mark.xfail(strict=True, raises=LoadCaseError)
def test_LoadCase_init_error():

    loads = [
        [0.0, 0, 0, 0, 0, 0],
        [0.25, 1, 2, 3, 4, 5, 6],
        [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5],
        [0.5, 10, 10, 10, 10, 10, 10],
        [0.75, 2, 3, 4, 5, 6, 7],
        [1.0, 3, 4, 5, 6, 7, 8],
    ]

    a = LoadCase(loads=loads)

    # should fail by this point
    assert a


def test_get_loads_1():
    a = LoadCase()

    assert a._get_input_loads(component="VX") is None
    assert a._get_input_loads(component="VY") is None
    assert a._get_input_loads(component="N") is None
    assert a._get_input_loads(component="MX") is None
    assert a._get_input_loads(component="MY") is None
    assert a._get_input_loads(component="T") is None


def test_get_loads_2():

    a = LoadCase(loads=[0.5, 1, 2, 3, 4, 5, 6])

    assert np.array_equal(a._get_input_loads(component="VX"), np.array([[0.5, 1]]))
    assert np.array_equal(a._get_input_loads(component="VY"), np.array([[0.5, 2]]))
    assert np.array_equal(a._get_input_loads(component="N"), np.array([[0.5, 3]]))
    assert np.array_equal(a._get_input_loads(component="MX"), np.array([[0.5, 4]]))
    assert np.array_equal(a._get_input_loads(component="MY"), np.array([[0.5, 5]]))
    assert np.array_equal(a._get_input_loads(component="T"), np.array([[0.5, 6]]))


def test_get_loads_3():
    loads = [[0.25, 1, 2, 3, 4, 5, 6], [0.75, 2, 3, 4, 5, 6, 7]]

    a = LoadCase(loads=loads)

    assert np.array_equal(
        a._get_input_loads(component="VX"), np.array([[0.25, 1], [0.75, 2]])
    )
    assert np.array_equal(
        a._get_input_loads(component="VY"), np.array([[0.25, 2], [0.75, 3]])
    )
    assert np.array_equal(
        a._get_input_loads(component="N"), np.array([[0.25, 3], [0.75, 4]])
    )
    assert np.array_equal(
        a._get_input_loads(component="MX"), np.array([[0.25, 4], [0.75, 5]])
    )
    assert np.array_equal(
        a._get_input_loads(component="MY"), np.array([[0.25, 5], [0.75, 6]])
    )
    assert np.array_equal(
        a._get_input_loads(component="T"), np.array([[0.25, 6], [0.75, 7]])
    )


def test_get_load_None():
    """
    Test that if we input no loads, we get None out.
    """

    a = LoadCase()

    position = 1.0

    assert np.array_equal(
        a.get_load(position=position, component="VX"), np.array([[1.0, None]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="VY"), np.array([[1.0, None]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="N"), np.array([[1.0, None]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MX"), np.array([[1.0, None]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MY"), np.array([[1.0, None]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="T"), np.array([[1.0, None]])
    )


def test_get_load_single():
    """
    Test that if we input a single load position, we get out the same value at multiple
    positions.
    """

    a = LoadCase(loads=[0.5, 1, 2, 3, 4, 5, 6])

    position = 0.25

    for comp in ["VX", "VY", "N", "MX", "MY", "T"]:

        lc = LoadComponents[comp]

        expected = np.array([[position, lc.value]])
        actual = a.get_load(position=position, component=comp)

        assert np.array_equal(expected, actual)

    position = 0.5

    assert np.array_equal(
        a.get_load(position=position, component="VX"), np.array([[position, 1]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="VY"), np.array([[position, 2]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="N"), np.array([[position, 3]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MX"), np.array([[position, 4]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MY"), np.array([[position, 5]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="T"), np.array([[position, 6]])
    )

    position = 0.75

    assert np.array_equal(
        a.get_load(position=position, component="VX"), np.array([[position, 1]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="VY"), np.array([[position, 2]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="N"), np.array([[position, 3]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MX"), np.array([[position, 4]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MY"), np.array([[position, 5]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="T"), np.array([[position, 6]])
    )


def test_get_load_multiple():
    """
    Test that if we input a single load position, we get out the same value at multiple
    positions.
    """

    a = LoadCase(loads=[0.5, 1, 2, 3, 4, 5, 6])

    position = [0.25, 0.75]

    for comp in ["VX", "VY", "N", "MX", "MY", "T"]:

        lc = LoadComponents[comp]

        expected = np.array([[position[0], lc.value], [position[1], lc.value]])
        actual = a.get_load(position=position, component=comp)

        assert np.array_equal(expected, actual)

    position = 0.5

    assert np.array_equal(
        a.get_load(position=position, component="VX"), np.array([[position, 1]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="VY"), np.array([[position, 2]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="N"), np.array([[position, 3]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MX"), np.array([[position, 4]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MY"), np.array([[position, 5]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="T"), np.array([[position, 6]])
    )


def test_get_load_components():
    """
    Test the case where components are provided directly, rather than as a string
    :return:
    """
    a = LoadCase(loads=[0.5, 1, 2, 3, 4, 5, 6])

    position = 0.25

    actual = a.get_load(position=position, component=LoadComponents["VX"])

    assert np.array_equal(actual, np.array([[0.25, 1]]))
    assert np.array_equal(
        a.get_load(position=position, component=LoadComponents["VY"]),
        np.array([[0.25, 2]]),
    )
    assert np.array_equal(
        a.get_load(position=position, component=LoadComponents["N"]),
        np.array([[0.25, 3]]),
    )
    assert np.array_equal(
        a.get_load(position=position, component=LoadComponents["MX"]),
        np.array([[0.25, 4]]),
    )
    assert np.array_equal(
        a.get_load(position=position, component=LoadComponents["MY"]),
        np.array([[0.25, 5]]),
    )
    assert np.array_equal(
        a.get_load(position=position, component=LoadComponents["T"]),
        np.array([[0.25, 6]]),
    )


def test_get_load_multiple_positions():
    """Need to test the case where there are multiple positions of loads."""

    loads = [[0.25, 1, 2, 3, 4, 5, 6], [0.75, 2, 3, 4, 5, 6, 7]]

    a = LoadCase(loads=loads)

    position = 0.0

    assert np.array_equal(
        a.get_load(position=position, component="VX"), np.array([[0.0, 1]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="VY"), np.array([[0.0, 2]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="N"), np.array([[0.0, 3]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MX"), np.array([[0.0, 4]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MY"), np.array([[0.0, 5]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="T"), np.array([[0.0, 6]])
    )

    position = 0.25

    actual = a.get_load(position=position, component="VX")
    expected = np.array([[0.25, 1]])

    assert np.array_equal(actual, expected)
    assert np.array_equal(
        a.get_load(position=position, component="VY"), np.array([[0.25, 2]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="N"), np.array([[0.25, 3]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MX"), np.array([[0.25, 4]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MY"), np.array([[0.25, 5]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="T"), np.array([[0.25, 6]])
    )

    position = 0.5

    assert np.array_equal(
        a.get_load(position=position, component="VX"), np.array([[0.5, 1.5]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="VY"), np.array([[0.5, 2.5]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="N"), np.array([[0.5, 3.5]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MX"), np.array([[0.5, 4.5]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MY"), np.array([[0.5, 5.5]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="T"), np.array([[0.5, 6.5]])
    )

    position = 0.75

    assert np.array_equal(
        a.get_load(position=position, component="VX"), np.array([[0.75, 2]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="VY"), np.array([[0.75, 3]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="N"), np.array([[0.75, 4]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MX"), np.array([[0.75, 5]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MY"), np.array([[0.75, 6]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="T"), np.array([[0.75, 7]])
    )

    position = 1.0

    assert np.array_equal(
        a.get_load(position=position, component="VX"), np.array([[1.0, 2]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="VY"), np.array([[1.0, 3]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="N"), np.array([[1.0, 4]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MX"), np.array([[1.0, 5]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MY"), np.array([[1.0, 6]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="T"), np.array([[1.0, 7]])
    )


def test_get_load_multiple_positions2():
    """
    Now test the case where there are multiple loads at the same position.
    """

    loads = [
        [0.0, 0, 0, 0, 0, 0, 0],
        [0.25, 1, 2, 3, 4, 5, 6],
        [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5],
        [0.5, 10, 10, 10, 10, 10, 10],
        [0.75, 2, 3, 4, 5, 6, 7],
        [1.0, 3, 4, 5, 6, 7, 8],
    ]

    a = LoadCase(loads=loads)

    position = 0.0

    assert np.array_equal(
        a.get_load(position=position, component="VX"), np.array([[0.0, 0]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="VY"), np.array([[0.0, 0]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="N"), np.array([[0.0, 0]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MX"), np.array([[0.0, 0]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MY"), np.array([[0.0, 0]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="T"), np.array([[0.0, 0]])
    )

    position = 0.25

    assert np.array_equal(
        a.get_load(position=position, component="VX"), np.array([[0.25, 1]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="VY"), np.array([[0.25, 2]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="N"), np.array([[0.25, 3]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MX"), np.array([[0.25, 4]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MY"), np.array([[0.25, 5]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="T"), np.array([[0.25, 6]])
    )

    position = 0.4

    assert np.allclose(
        a.get_load(position=position, component="VX"), np.array([[0.4, 1.3]])
    )
    assert np.allclose(
        a.get_load(position=position, component="VY"), np.array([[0.4, 2.3]])
    )
    assert np.allclose(
        a.get_load(position=position, component="N"), np.array([[0.4, 3.3]])
    )
    assert np.allclose(
        a.get_load(position=position, component="MX"), np.array([[0.4, 4.3]])
    )
    assert np.allclose(
        a.get_load(position=position, component="MY"), np.array([[0.4, 5.3]])
    )
    assert np.allclose(
        a.get_load(position=position, component="T"), np.array([[0.4, 6.3]])
    )

    position = 0.5

    actual = a.get_load(position=position, component="VX")
    expected = np.array([[0.5, 1.5], [0.5, 10]])

    assert np.array_equal(actual, expected)
    assert np.array_equal(
        a.get_load(position=position, component="VY"), np.array([[0.5, 2.5], [0.5, 10]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="N"), np.array([[0.5, 3.5], [0.5, 10]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MX"), np.array([[0.5, 4.5], [0.5, 10]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MY"), np.array([[0.5, 5.5], [0.5, 10]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="T"), np.array([[0.5, 6.5], [0.5, 10]])
    )

    position = 0.6

    assert np.allclose(
        a.get_load(position=position, component="VX"), np.array([[0.6, 6.8]])
    )
    assert np.allclose(
        a.get_load(position=position, component="VY"), np.array([[0.6, 7.2]])
    )
    assert np.allclose(
        a.get_load(position=position, component="N"), np.array([[0.6, 7.6]])
    )
    assert np.allclose(
        a.get_load(position=position, component="MX"), np.array([[0.6, 8.0]])
    )
    assert np.allclose(
        a.get_load(position=position, component="MY"), np.array([[0.6, 8.4]])
    )
    assert np.allclose(
        a.get_load(position=position, component="T"), np.array([[0.6, 8.8]])
    )

    position = 0.75

    assert np.array_equal(
        a.get_load(position=position, component="VX"), np.array([[0.75, 2]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="VY"), np.array([[0.75, 3]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="N"), np.array([[0.75, 4]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MX"), np.array([[0.75, 5]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MY"), np.array([[0.75, 6]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="T"), np.array([[0.75, 7]])
    )

    position = 1.0

    assert np.array_equal(
        a.get_load(position=position, component="VX"), np.array([[1.0, 3]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="VY"), np.array([[1.0, 4]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="N"), np.array([[1.0, 5]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MX"), np.array([[1.0, 6]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="MY"), np.array([[1.0, 7]])
    )
    assert np.array_equal(
        a.get_load(position=position, component="T"), np.array([[1.0, 8]])
    )


def test_get_load_multiple_positions3():
    """
    Now test the case where no component is specified.

    :return:
    """

    loads = [
        [0.0, 0, 0, 0, 0, 0, 0],
        [0.25, 1, 2, 3, 4, 5, 6],
        [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5],
        [0.5, 10, 10, 10, 10, 10, 10],
        [0.75, 2, 3, 4, 5, 6, 7],
        [1.0, 3, 4, 5, 6, 7, 8],
    ]

    a = LoadCase(loads=loads)

    position = 0.0

    assert np.array_equal(
        a.get_load(position=position), np.array([[0.0, 0, 0, 0, 0, 0, 0]])
    )

    position = 0.25

    assert np.array_equal(
        a.get_load(position=position), np.array([[0.25, 1, 2, 3, 4, 5, 6]])
    )

    position = 0.4

    assert np.allclose(
        a.get_load(position=position), np.array([[0.4, 1.3, 2.3, 3.3, 4.3, 5.3, 6.3]])
    )

    position = 0.5

    assert np.array_equal(
        a.get_load(position=position),
        np.array([[0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5], [0.5, 10, 10, 10, 10, 10, 10]]),
    )

    position = 0.6

    assert np.allclose(
        a.get_load(position=position), np.array([[0.6, 6.8, 7.2, 7.6, 8.0, 8.4, 8.8]])
    )

    position = 0.75

    assert np.array_equal(
        a.get_load(position=position), np.array([[0.75, 2, 3, 4, 5, 6, 7]])
    )

    position = 1.0

    assert np.array_equal(
        a.get_load(position=position), np.array([[1.0, 3, 4, 5, 6, 7, 8]])
    )


def test_get_load_multiple_positions4():
    """
    Now test the get_load method with a list of positions.
    """

    loads = [
        [0.0, 0, 0, 0, 0, 0, 0],
        [0.25, 1, 2, 3, 4, 5, 6],
        [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5],
        [0.5, 10, 10, 10, 10, 10, 10],
        [0.75, 2, 3, 4, 5, 6, 7],
        [1.0, 3, 4, 5, 6, 7, 8],
    ]

    a = LoadCase(loads=loads)

    position = [0.0, 0.4, 0.25, 0.5, 0.6, 0.75, 1.0]

    assert np.allclose(
        a.get_load(position=position),
        np.array(
            [
                [0.0, 0, 0, 0, 0, 0, 0],
                [0.25, 1, 2, 3, 4, 5, 6],
                [0.4, 1.3, 2.3, 3.3, 4.3, 5.3, 6.3],
                [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5],
                [0.5, 10, 10, 10, 10, 10, 10],
                [0.6, 6.8, 7.2, 7.6, 8.0, 8.4, 8.8],
                [0.75, 2, 3, 4, 5, 6, 7],
                [1.0, 3, 4, 5, 6, 7, 8],
            ]
        ),
    )


def test_get_load_min_positions():
    """
    Now test the get_load method with minimum no. of positions.
    """

    loads = [
        [0.0, 0, 0, 0, 0, 0, 0],
        [0.25, 1, 2, 3, 4, 5, 6],
        [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5],
        [0.5, 10, 10, 10, 10, 10, 10],
        [0.75, 2, 3, 4, 5, 6, 7],
        [1.0, 3, 4, 5, 6, 7, 8],
    ]

    a = LoadCase(loads=loads)

    assert np.allclose(
        a.get_load(min_positions=5),
        np.array(
            [
                [0.0, 0, 0, 0, 0, 0, 0],
                [0.25, 1, 2, 3, 4, 5, 6],
                [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5],
                [0.5, 10, 10, 10, 10, 10, 10],
                [0.75, 2, 3, 4, 5, 6, 7],
                [1.0, 3, 4, 5, 6, 7, 8],
            ]
        ),
    )


@pytest.mark.xfail(strict=True)
def test_get_load_position_error():
    """
    Test the case where the user inputs a position and a minimum no. of positions -
    this should raise an assertion error.
    """

    loads = [
        [0.0, 0, 0, 0, 0, 0, 0],
        [0.25, 1, 2, 3, 4, 5, 6],
        [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5],
        [0.5, 10, 10, 10, 10, 10, 10],
        [0.75, 2, 3, 4, 5, 6, 7],
        [1.0, 3, 4, 5, 6, 7, 8],
    ]

    a = LoadCase(loads=loads)

    a.get_load(position=0.5, min_positions=2)

    assert True


@pytest.mark.xfail(strict=True)
def test_get_load_position_error1():
    """
    Test the case where the user doesn't provide a position or a no. of positions -
    this should raise an assertion error.
    """

    loads = [
        [0.0, 0, 0, 0, 0, 0, 0],
        [0.25, 1, 2, 3, 4, 5, 6],
        [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5],
        [0.5, 10, 10, 10, 10, 10, 10],
        [0.75, 2, 3, 4, 5, 6, 7],
        [1.0, 3, 4, 5, 6, 7, 8],
    ]

    a = LoadCase(loads=loads)

    a.get_load()

    assert True


def test_constant_load():
    """
    Test the class method that generates a constant load case.
    """

    a = LoadCase.constant_load()

    pos = 0.25

    expected = np.array([[pos, 0, 0, 0, 0, 0, 0]])
    actual = a.get_load(position=pos)

    assert np.allclose(expected, actual)

    pos = 0.75

    expected = np.array([[pos, 0, 0, 0, 0, 0, 0]])
    actual = a.get_load(position=pos)

    assert np.allclose(expected, actual)

    a = LoadCase.constant_load(VY=3.0, T=5.0)

    pos = 0.25

    expected = np.array([[pos, 0, 3.0, 0, 0, 0, 5.0]])
    actual = a.get_load(position=pos)

    assert np.allclose(expected, actual)

    pos = 0.75

    expected = np.array([[pos, 0, 3.0, 0, 0, 0, 5.0]])
    actual = a.get_load(position=pos)

    assert np.allclose(expected, actual)
