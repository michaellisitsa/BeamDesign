"""
This file is intended to contain a class for AS4100 checks, and also the actual checks
themselves. Specific equations from the code have been split off into other files to
minimise the size of this file.
"""

import itertools
from typing import List, Union

from BeamDesign.Beam import Beam
from BeamDesign.CodeCheck.CodeCheck import CodeCheck
from BeamDesign.Sections.Section import Section


class AS4100(CodeCheck):
    def __init__(
        self, *, φ: float, αu: float, kt: float, beam: Beam = None, section=None
    ):
        """

        :param beam:
        :param section:
        :param kwargs:
        """

        super().__init__(beam=beam, section=section)

        self.φ = φ
        self.αu = αu
        self.kt = kt

    def tension_capacity(self):

        raise NotImplementedError()

    def get_all_sections(self) -> List[Section]:

        return super().get_all_sections()

    def get_section(
        self, position: Union[List[float], float] = None
    ) -> List[List[Section]]:

        return super().get_section(position=position)

    def Nt(self, *, position: Union[List[float], float] = None):
        """

        :return:
        """

        return min(self.Nty(position=position), self.Ntu(position=position))

    def φNt(self, *, position: Union[List[float], float] = None):
        """

        :return:
        """

        return self.φ * self.Nt(position=position)

    def Nty(self, *, position: Union[List[float], float] = None) -> float:
        """
        Calculates the tension yield capacity of the AS4100 object.

        :param position: The position to calculate the capacity at. Can be a float, can
            be a list of floats or can be None.

            Note that if None is provided, a single tension capacity is returned which
            is the minimum tension capacity of the entire AS4100 object.
        :return: The calculated tension yield capacity.
        """

        if isinstance(position, float):
            # if a float is provided, wrap it in a list for consistent logic below.
            position = [position]

        sections = self.get_section(position=position)

        # now flatten list to make it easier to check the values:
        sections = list(itertools.chain.from_iterable(sections))

        # now we have a list of all sections to check, do the check
        N = [self.s7_2_Nty(Ag=s.area, fy=s.min_strength_yield) for s in sections]

        return min(N)

    def φNty(self, *, position: Union[List[float], float] = None):
        """
        Calculates the tension yield capacity of the AS4100 object.

        :param position: The position to calculate the capacity at. Can be a float, can
            be a list of floats or can be None.

            Note that if None is provided, a single tension capacity is returned which
            is the minimum tension capacity of the entire AS4100 object.
        :return: The calculated tension yield capacity.
        """

        return self.φ * self.Nty(position=position)

    def Ntu(self, *, position: Union[List[float], float] = None):
        """
        Calculates the tension yield capacity of the AS4100 object.

        :param position: The position to calculate the capacity at. Can be a float, can
            be a list of floats or can be None.

            Note that if None is provided, a single tension capacity is returned which
            is the minimum tension capacity of the entire AS4100 object.
        :return: The calculated tension yield capacity.
        """

        if isinstance(position, float):
            # if a float is provided, wrap it in a list for consistent logic below.
            position = [position]

        sections = self.get_section(position=position)

        # now flatten list to make it easier to check the values:
        sections = list(itertools.chain.from_iterable(sections))

        # now we have a list of all sections to check, do the check
        N = [
            self.s7_2_Ntu(
                An=s.area_net, fu=s.min_strength_ultimate, kt=self.kt, αu=self.αu
            )
            for s in sections
        ]

        return min(N)

    def φNtu(self, *, position: Union[List[float], float] = None):
        """
        Calculates the tension yield capacity of the AS4100 object.

        :param position: The position to calculate the capacity at. Can be a float, can
            be a list of floats or can be None.

            Note that if None is provided, a single tension capacity is returned which
            is the minimum tension capacity of the entire AS4100 object.
        :return: The calculated tension yield capacity.
        """

        return self.φ * self.Nty(position=position)

    @staticmethod
    def s7_1_Nt(
        *, Ag: float, An: float, fy: float, fu: float, kt: float, αu: float
    ) -> float:
        """
        Calculates the tension capacity of a section according to AS4100 S7.1.

        :param Ag: Gross area of a section in m².
        :param An: Net area of the section in m², allowing for holes as required
            by AS4100.
        :param fy: The yield strength of the section in Pa. If different components
            have different yield strengths the minimum strength of the section
            should be used. Where a section has a significantly different strength
            the result may be too conservative and this function may not be
            appropriate (i.e. a 250 grade web and a 450 grade flange) - more
            detailed analysis (FEA modelling etc.) may be required.
        :param fu: The ultimate strength of the section in Pa.
        :param kt: The connection efficiency factor / eccentric connection factor
            as per AS4100.
        :param αu: A factor for the uncertainty in ultimate strength as per AS4100 S7.2.
            Note that AS4100 does not provide a variable name for this value so αu is
            used, consistent with other uses of α in AS4100. AS4100 provides a value of
            0.85 for this factor.
        :return:
        """

        return min(
            AS4100.s7_2_Nty(Ag=Ag, fy=fy), AS4100.s7_2_Ntu(An=An, fu=fu, kt=kt, αu=αu)
        )

    @staticmethod
    def s7_2_Nty(*, Ag: float, fy: float) -> float:
        """
        Calculates the yield capacity of a member but does not include the capacity
        reduction factor.

        :param Ag: Gross area of a section in m².
        :param fy: Yield strength of a section in Pa.
        :return: Returns the yielding capacity of the member in N.
        """

        return Ag * fy

    @staticmethod
    def s7_2_Ntu(*, An: float, fu: float, kt: float, αu: float) -> float:
        """
        Calculates the ultimate fracture capacity of a section and includes the
        additional uncertainty factor from AS4100.

        :param An: Net area of the section in m², allowing for holes as required
            by AS4100.
        :param fu: The ultimate strength of the section in Pa.
        :param kt: The connection efficiency factor / eccentric connection factor
            as per AS4100.
        :param αu: A factor for the uncertainty in ultimate strength as per AS4100 S7.2.
            Note that AS4100 does not provide a variable name for this value so αu is
            used, consistent with other uses of α in AS4100. AS4100 provides a value of
            0.85 for this factor.
        :return: Returns the ultimate fracture capacity in N.
        """

        return An * fu * kt * αu
