"""
This file is intended to define a class that will describe beam objects. These
are intended to represent real world structural elements and as such their
properties will be limited to those that are explicitly real world properties,
such as:

* Length
* Cross section
* Material.py Properties
* Internal loads (i.e. bending moments etc.).

At this point in time it is NOT intended to include descriptions of applied loads (i.e.
point load of x at position y) and / or to calculate load diagrams directly (i.e.
through basic statics such as BM=PL/4 or a more advanced FEA method), although a
sub-class may / could be created to allow this.

Information that is design code specific will NOT be stored. This includes
(but is not limited to):

* Capacity reduction factors, safety factors
* Location and types of restraints in compression / bending etc.
* Capacity ratios / strength calculations etc.

The intent here is to make the ``Beam`` class as generic as possible for use
with multiple design codes.
"""

import itertools
from typing import List, Union, Tuple

import numpy as np

from beamdesign.element import Element
from beamdesign.const import LoadComponents
from beamdesign.utility.exceptions import (
    ElementError,
    ElementCaseError,
    ElementLengthError,
    PositionNotInElementError,
    PositionNotInBeamError,
    InvalidPositionError,
)
from beamdesign.sections.section import Section


class Beam:
    """
    This is a ``Beam`` object, intended to form the basis of all design checks. It is a
    wrapper object around at least 1x ``Element`` object which corresponds to
    (for example) an FEA beam element. This allows a ``Beam`` object to correspond to
    multiple FEA elements (as will often be the case in a real design scenario).
    """

    def __init__(self, *, elements: Union[Element, List[Element]]):
        """
        Constructor for the ``Beam`` object.

        :param elements: A list of ``Element`` objects that underly the ``Beam`` object.
           They should be ordered consistently, as should the ``LoadCase`` objects in
           them, such that:

           Element_0 length=1.0 == Element_1 length=0.0
           Element_1 length=1.0 == Element_2 length=0.0

           and so-on.
        """

        # first do some consistency checking of the elements.

        if isinstance(elements, Element):
            # make into a list for consistent handling below.
            elements = [elements]

        self._check_elements(elements=elements)

        self._elements = elements

    def _check_elements(self, *, elements: List[Element]):
        """
        A helper method for checking the elements provided to the __init__ method for
        consistency.

        Has no side-effects other than calling appropriate errors as required.

        :param elements: The elements to check for consistency.
        """

        # first check that there is at least an element.

        if elements == None or elements == [] or elements == [None]:
            raise ElementError(
                f"Expected at least one element to create the Beam. "
                f"Was given the following elements: {elements}"
            )

        # next check for any Nones

        if not all(isinstance(e, Element) for e in elements):
            raise ElementError(
                f"At least one provided element in the elements list is not an "
                f"Element object."
            )

        # next check that each element has a matching no of load cases.

        no_cases = [i.no_load_cases for i in elements]
        first_no_cases = no_cases[0]

        if not all(c == first_no_cases for c in no_cases):
            raise ElementCaseError(
                f"No. of load cases should match across all Elements in a Beam. "
                f"No. of cases for each element is: {no_cases}"
            )

        # next check that the elements match.

        cases = [i.load_cases for i in elements]
        first_cases = cases[0]

        if not all(c == first_cases for c in cases):
            raise ElementCaseError(
                f"The index used for load cases should match across "
                f"all Elements in a Beam. At least one Element has non-matching cases."
            )

    @property
    def elements(self) -> List[Element]:
        """
        Return the elements that make up the ``Beam``.

        :return: Returns the elements that make up the ``Beam``.
        """

        return self._elements

    @property
    def length(self) -> float:
        """
        Get the total length of the ``Beam`` object.

        :return: Returns the length of the ``Beam`` object.
        """

        return sum([e.length for e in self.elements])

    @property
    def no_elements(self) -> int:
        """
        Get the no. of elements that make up the ``Beam``.

        :return: The no. of elements.
        """

        return len(self._elements)

    @property
    def no_load_cases(self) -> int:
        """
        Get the no. of load cases available on the ``Element`` objects that make the
        ``Beam``.

        :return: The no. of load cases.
        """

        # Relies on the fact that the elements are checked for consistency when the
        # ``Beam`` to ensure that a correct no. of load cases is returned.

        return self.elements[0].no_load_cases

    @property
    def load_cases(self) -> List[int]:
        """
        Gets a list of the load cases that are available on the ``Element`` objects that
        make up the ``Beam``.

        :return: A list of the load cases.
        """

        # Relies on the fact that the elements are checked for consistency when the
        # ``Beam`` to ensure that a correct no. of load cases is returned.

        return self.elements[0].load_cases

    @property
    def element_ends(self) -> List[List[float]]:
        """
        Returns the ``Element`` starting & ending points as positions from the
        start of the ``Beam``. ``Beam.elements[0]`` always starts at 0.0.
        ``Beam.elements[n]`` (where n is the last element) always ends at
        ``Beam.length``.

        Return is a list of the form:

        [[start_0, end_0]
         [start_1, end_1]
         ...
         [start_n, end_n]
         ]

        :return: The element starting & ending points.
        """

        starts_ends = []

        for i, e in enumerate(self.elements):

            if i == 0:
                starts_ends += [[0.0, e.length]]

            else:

                prev_end = starts_ends[i - 1][1]

                starts_ends += [[prev_end, prev_end + e.length]]

        return starts_ends

    @property
    def sections(self) -> List[Section]:
        """
        Returns all the sections from the elements that make up the ``Beam`` object.

        :return: A list of all the sections.
        """

        return [e.section for e in self.elements]

    def get_element_start_end(self, *, element: int) -> List[float]:
        """
        Gets the start & end positions of a given ``Element`` in the ``Beam``.

        :param element: The id of the ``Element`` to get the start & end positions of.
        :return: Returns a List of the start & end postions [start, end]
        """

        return self.element_ends[element]

    def in_elements(self, *, position: float) -> List[int]:
        """
        Returns a list of all elements that a given position along the beam fits into.

        If the position is part-way along the length of an ``Element`` only a single
        value will be returned. If exactly at the boundary between 2x or more elements
        multiple element ids will be returned. The list takes the following format:

        [element_id_n, element_id_n+1, ..., element_id_n+o]

        NOTE: if position is > ``Beam.Length`` or < 0.0, returns an empty list []

        :param position: The position to test.
        :return: A list of elements that the position overlaps.
        """

        ret_list = []

        for i in range(0, len(self.elements)):

            start_end = self.get_element_start_end(element=i)

            if position >= start_end[0] and position <= start_end[1]:
                ret_list += [i]

        return ret_list

    def beam_to_local_position(self, *, position: float, element: int) -> float:
        """
        Gets the local position of a *real* position normalised onto an ``Element``.

        :param position: The position to test.
        :param element: The element to get the local position on.
        :return: The local position of the *real* position as a value between 0.0 and
            1.0
        """

        start = self.get_element_start_end(element=element)[0]
        length = self.elements[element].length

        overlap = position - start

        if overlap < 0 or overlap > length:
            raise PositionNotInElementError(
                "Expected position to be within element {element}."
            )

        if length == 0.0:
            raise ElementLengthError(
                "Local position on an element with zero length is" + " ambiguous"
            )
        else:
            return (position - start) / length

    def local_to_beam_position(self, *, position: float, element: int) -> float:
        """
        Gets the *real* position of an ``Element`` local position on the ``Beam``
        object.

        :param position: The local position between 0.0 and 1.0 to convert to a *real*
            position on the ``Beam``.
        :param element: The element on which the position applies.
        :return: Returns the real position of the local element position.
        """

        if position < 0 or position > 1.0:
            raise PositionNotInElementError(
                f"Expected position to be between 0.0 and 1.0. "
                + f"Position given was {position}"
            )

        start = self.get_element_start_end(element=element)[0]
        length = self.elements[element].length

        return start + position * length

    def get_loads(
        self,
        *,
        load_case: int,
        position: Union[List[float], float] = None,
        min_positions: int = None,
        component: Union[int, str, LoadComponents] = None,
    ) -> np.ndarray:
        """
        Gets the load in a ``Beam`` in a given load case and at a given position.
        If there are multiple loads at a position it returns all of them. Returns in the
        form of a numpy array of the format:

        [[pos, load_1]
         [pos, load_2]
         ...
         [pos, load_n]
        ]

        If ``component`` is not provided, then an array of all loads at the given
        position is returned:

        [[pos, vx_1, vy_1, N_1, mx_1, my_1, T_1]
         [pos, vx_2, vy_2, N_2, mx_2, my_2, T_2]
         ...
         [pos, vx_n, vy_n, N_n, mx_n, my_n, T_n]
        ]

        The values of position are 'real' positions along the beam.

        :param load_case: The load case to get the loads in.
        :param position: The position at which to return the load. Position values
            should be entered as floats between 0.0 and ``Beam.length``

            Positions can be a single position or a list of positions. If a list is
            provided, any duplicate values will be ignored, and the order will be
            ignored - return values will be at positions sorted ascending from 0.0 to
            ``Beam.length``. If the specified position is at an element or load
            discontinuity multiple values may be returned.

            If ``position`` is provided, ``min_positions`` must be ``None`` to
            avoid ambiguity.
        :param min_positions: The minimum number of positions to return. Positions will
            be returned such that loads are returned at equally spaced positions between
            0.0 and ``Beam.length`` (inclusive). All stored load positions and element
            start / end positions will also be included to ensure that discontinuities
            are included.

            If ``min_positions`` is provided,
            ``position`` must be ``None`` to avoid ambiguity.
        :param component: The component of load to return.
        :return: A numpy array containing the loads at the specified position.
        """

        # first check for ambiguities in position / min_positions

        position, elements, local_positions = self.list_positions(
            load_case=load_case, min_positions=min_positions, position=position
        )

        # we now have a list of all the positions at which we intend to get the loads.

        ret_val = None

        for p, e, l in zip(position, elements, local_positions):

            val = self.elements[e].get_loads(
                load_case=load_case, position=l, component=component
            )

            # now we need to get the beam_position of the element and replace with the
            # real position.

            val[..., 0] = p

            if ret_val is None:
                ret_val = val
            else:
                ret_val = np.vstack((ret_val, val))

        return ret_val

    def list_positions(
        self,
        *,
        position: Union[List[float], float] = None,
        min_positions: int = None,
        load_case: int = None,
    ) -> Tuple[List[float], List[int], List[float]]:
        """
        Build a list of positions along a Beam element, and the elements and local
        positions they correspond to.

        In the simple case of a provided position/s it returns value at the provided
        positions only. If min_positions is provided, it returns at least
        min_positions number of positions, but will also include any element starts /
        ends and any load discontinuities in the given load case.

        :param position: A provided position or positions to check.
        :param min_positions: The minimum no. of positions to return.
        :param load_case: The load case to consider if using min_positions. Can be
            ``None``, in which case only the start & ends of elements are returned.
        :return: Returns a tuple in the format
            (
                [
                    beam_position_0,
                    ...,
                    beam_position_n,
                ],
                [
                    element_0,
                    ...,
                    element_n,
                ],
                [
                    local_position_0,
                    ...,
                    local_position_n,
                ],
            )
        """

        # first do some checking that either a position or a no. of positions required
        # is provided.
        if position is None and min_positions is None:
            raise InvalidPositionError(
                f"Expected either position or num_positions to be provided."
                + f"Both were None."
            )

        if position is not None and min_positions is not None:
            raise InvalidPositionError(
                f"Expected only position or num_positions. Both were provided."
            )

        # next build a list of positions.

        if position is not None:
            # if position is the provided value then use it.

            if isinstance(position, float):
                # if position is just a float, wrap it in a list for consistency with
                # following code.
                position = [position]

            # do some error checking.
            for p in position:
                if p < 0 or p > self.length:
                    raise PositionNotInBeamError(
                        f"Expected position to be > 0 or < the length of the beam. "
                        + f"Provided positions were{position}, beam length is"
                        + f" {self.length}."
                    )

            # convert to unique values and guarantee a sorted list.
            position = list(sorted(set(position)))

        else:
            # else if min_positions is provided we need to build a list of positions to
            # get the loads at.

            lin_pos = list(np.linspace(0.0, self.length, min_positions))

            # next concatenate with all the starts & ends and the load positions on the
            # elements to do this we need to get all the load positions on the elements
            # and convert them to real positions.

            position = list(itertools.chain.from_iterable(self.element_ends))

            for i, e in enumerate(self.elements):
                # get the local positions of all the loads

                if load_case is None:
                    # if no load case provided, just use the element starts & ends.
                    element_pos = [0.0, 1.0]
                else:
                    # else, use the load positions
                    element_pos = e.load_positions(load_case=load_case)

                # now convert to *real* positions
                real_pos = [
                    self.local_to_beam_position(position=p, element=i)
                    for p in element_pos
                ]

                # now add to the collecting list.
                position += real_pos

            # now make sure we only have unique values
            position = set(position)
            position.update(lin_pos)

            position = list(sorted(position))  # now sort

        # now we have the positions also get the elements & the local positions

        position_list = []
        element_list = []
        local_position_list = []

        for p in position:

            elements = self.in_elements(position=p)

            for e in elements:

                if self.elements[e].length == 0:
                    # handle the case of a 0 length element - the local position method
                    # will not work when converting a real to local position on a zero
                    # length element.

                    if load_case is None:
                        # if no load case is provided, then simply use the start and
                        # end values of the element.
                        load_pos = [0.0, 1.0]
                    else:
                        # else use all the load values.
                        load_pos = self.elements[e].load_positions(load_case=load_case)

                        # and make sure the element start & ends are included
                        if load_pos[0] != 0:
                            load_pos = [0.0] + load_pos
                        if load_pos[-1] != 1.0:
                            load_pos = load_pos + [1.0]

                    for l in load_pos:
                        position_list += [p]
                        element_list += [e]
                        local_position_list += [l]

                else:
                    position_list += [p]
                    element_list += [e]
                    local_position_list += [
                        self.beam_to_local_position(position=p, element=e)
                    ]

        return position_list, element_list, local_position_list

    def get_section(
        self,
        position: Union[List[float], float],
        min_positions: int = None,
        load_case: int = None,
    ) -> Tuple[List[float], List[Section]]:
        """
        Returns the sections from the elements that make up the ``Beam`` object.

        :param position: A provided position or positions to check.
        :param min_positions: The minimum no. of positions to return.
        :param load_case: The load case to consider if using min_positions. Can be
            ``None``, in which case only the start & ends of elements are returned.
        :return: Returns a tuple of positions and sections:

            (
                [pos_1, ..., pos_n]
                [section_1, ..., section_n]
            )
        """

        # get a list of positions & elements
        locations = self.list_positions(
            position=position, min_positions=min_positions, load_case=load_case
        )

        position = locations[0]
        element_ids = locations[1]

        elements = [self.elements[e].section for e in element_ids]

        return (position, elements)

    @classmethod
    def empty_beam(cls, length: float = 0, section: Section = None) -> "Beam":
        """
        Helper constructor to build an empty Beam object with an empty element object,
        which has no loads. Primarily intended for testing purposes.

        :param length: An optional length for the empty ``Beam``.
        :param section: An optional Section to provide for the ``Element``.
        :return: Returns a ``Beam`` object.
        """

        element = Element.empty_element(length=length, section=section)

        return cls(elements=element)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            + f"length={self.length}, "
            + f"no. elements={self.no_elements}, "
            + f"no. load cases={self.no_load_cases}"
            + f")"
        )
