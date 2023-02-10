# Source: https://coast.noaa.gov/data/marinecadastre/ais/VesselTypeCodes2018.pdf
from dataclasses import dataclass, field
from typing import List, Optional


def make_vessel_codes() -> List["AisVesselCode"]:
    return [
        AisVesselCode(
            "Not Available",
            0,
            0,
            "Not available or no ship, default",
        ),
        AisVesselCode(
            "Other",
            1,
            19,
            "Reserved for future use",
        ),
        AisVesselCode(
            "Other",
            20,
            20,
            "Wing in ground (WIG), all ships of this type",
        ),
        AisVesselCode(
            "Tug Tow",
            21,
            21,
            "Wing in ground (WIG), hazardous category A",
        ),
        AisVesselCode(
            "Tug Tow",
            22,
            22,
            "Wing in ground (WIG), hazardous category B",
        ),
        AisVesselCode(
            "Other",
            23,
            23,
            "Wing in ground (WIG), hazardous category C",
        ),
        AisVesselCode(
            "Other",
            24,
            24,
            "Wing in ground (WIG), hazardous category D",
        ),
        AisVesselCode(
            "Other",
            25,
            25,
            "Wing in ground (WIG), reserved for future use",
        ),
        AisVesselCode(
            "Other",
            26,
            26,
            "Wing in ground (WIG), reserved for future use",
        ),
        AisVesselCode(
            "Other",
            27,
            27,
            "Wing in ground (WIG), reserved for future use",
        ),
        AisVesselCode(
            "Other",
            28,
            28,
            "Wing in ground (WIG), reserved for future use",
        ),
        AisVesselCode(
            "Other",
            29,
            29,
            "Wing in ground (WIG), reserved for future use",
        ),
        AisVesselCode("Fishing", 30, 30, "Fishing"),
        AisVesselCode("Tug Tow", 31, 31, "Towing"),
        AisVesselCode(
            "Tug Tow",
            32,
            32,
            "Towing: length exceeds 200m or breadth exceeds 25m",
        ),
        AisVesselCode(
            "Other",
            33,
            33,
            "Dredging or underwater operations",
        ),
        AisVesselCode("Other", 34, 34, "Diving operations"),
        AisVesselCode(
            "Military",
            35,
            35,
            "Military operations",
        ),
        AisVesselCode(
            "Pleasure Craft/Sailing",
            36,
            36,
            "Sailing",
        ),
        AisVesselCode(
            "Pleasure Craft/Sailing",
            37,
            37,
            "Pleasure Craft",
        ),
        AisVesselCode("Other", 38, 38, "Reserved"),
        AisVesselCode("Other", 39, 39, "Reserved"),
        AisVesselCode(
            "Other",
            40,
            40,
            "High speed craft (HSC), all ships of this type",
        ),
        AisVesselCode(
            "Other",
            41,
            41,
            "High speed craft (HSC), hazardous category A",
        ),
        AisVesselCode(
            "Other",
            42,
            42,
            "High speed craft (HSC), hazardous category B",
        ),
        AisVesselCode(
            "Other",
            43,
            43,
            "High speed craft (HSC), hazardous category C",
        ),
        AisVesselCode(
            "Other",
            44,
            44,
            "High speed craft (HSC), hazardous category D",
        ),
        AisVesselCode(
            "Other",
            45,
            45,
            "High speed craft (HSC), reserved for future use",
        ),
        AisVesselCode(
            "Other",
            46,
            46,
            "High speed craft (HSC), reserved for future use",
        ),
        AisVesselCode(
            "Other",
            47,
            47,
            "High speed craft (HSC), reserved for future use",
        ),
        AisVesselCode(
            "Other",
            48,
            48,
            "High speed craft (HSC), reserved for future use",
        ),
        AisVesselCode(
            "Other",
            49,
            49,
            "High speed craft (HSC), no additional information",
        ),
        AisVesselCode("Other", 50, 50, "Pilot Vessel"),
        AisVesselCode(
            "Other",
            51,
            51,
            "Search and Rescue vessel",
        ),
        AisVesselCode("Tug Tow", 52, 52, "Tug"),
        AisVesselCode("Other", 53, 53, "Port Tender"),
        AisVesselCode(
            "Other",
            54,
            54,
            "Anti-pollution equipment",
        ),
        AisVesselCode("Other", 55, 55, "Law Enforcement"),
        AisVesselCode(
            "Other",
            56,
            56,
            "Spare - for assignment to local vessel",
        ),
        AisVesselCode(
            "Other",
            57,
            57,
            "Spare - for assignment to local vessel",
        ),
        AisVesselCode("Other", 58, 58, "Medical Transport"),
        AisVesselCode(
            "Other",
            59,
            59,
            "Ship according to RR Resolution No. 18",
        ),
        AisVesselCode(
            "Passenger",
            60,
            60,
            "Passenger, all ships of this type",
        ),
        AisVesselCode(
            "Passenger",
            61,
            61,
            "Passenger, hazardous category A",
        ),
        AisVesselCode(
            "Passenger",
            62,
            62,
            "Passenger, hazardous category B",
        ),
        AisVesselCode(
            "Passenger",
            63,
            63,
            "Passenger, hazardous category C",
        ),
        AisVesselCode(
            "Passenger",
            64,
            64,
            "Passenger, hazardous category D",
        ),
        AisVesselCode(
            "Passenger",
            65,
            65,
            "Passenger, reserved for future use",
        ),
        AisVesselCode(
            "Passenger",
            66,
            66,
            "Passenger, reserved for future use",
        ),
        AisVesselCode(
            "Passenger",
            67,
            67,
            "Passenger, reserved for future use",
        ),
        AisVesselCode(
            "Passenger",
            68,
            68,
            "Passenger, reserved for future use",
        ),
        AisVesselCode(
            "Passenger",
            69,
            69,
            "Passenger, no additional information",
        ),
        AisVesselCode(
            "Cargo",
            70,
            70,
            "Cargo, all ships of this type",
        ),
        AisVesselCode(
            "Cargo",
            71,
            71,
            "Cargo, hazardous category A",
        ),
        AisVesselCode(
            "Cargo",
            72,
            72,
            "Cargo, hazardous category B",
        ),
        AisVesselCode(
            "Cargo",
            73,
            73,
            "Cargo, hazardous category C",
        ),
        AisVesselCode(
            "Cargo",
            74,
            74,
            "Cargo, hazardous category D",
        ),
        AisVesselCode(
            "Cargo",
            75,
            75,
            "Cargo, reserved for future use",
        ),
        AisVesselCode(
            "Cargo",
            76,
            76,
            "Cargo, reserved for future use",
        ),
        AisVesselCode(
            "Cargo",
            77,
            77,
            "Cargo, reserved for future use",
        ),
        AisVesselCode(
            "Cargo",
            78,
            78,
            "Cargo, reserved for future use",
        ),
        AisVesselCode(
            "Cargo",
            79,
            79,
            "Cargo, no additional information",
        ),
        AisVesselCode(
            "Tanker",
            80,
            80,
            "Tanker, all ships of this type",
        ),
        AisVesselCode(
            "Tanker",
            81,
            81,
            "Tanker, hazardous category A",
        ),
        AisVesselCode(
            "Tanker",
            82,
            82,
            "Tanker, hazardous category B",
        ),
        AisVesselCode(
            "Tanker",
            83,
            83,
            "Tanker, hazardous category C",
        ),
        AisVesselCode(
            "Tanker",
            84,
            84,
            "Tanker, hazardous category D",
        ),
        AisVesselCode(
            "Tanker",
            85,
            85,
            "Tanker, reserved for future use",
        ),
        AisVesselCode(
            "Tanker",
            86,
            86,
            "Tanker, reserved for future use",
        ),
        AisVesselCode(
            "Tanker",
            87,
            87,
            "Tanker, reserved for future use",
        ),
        AisVesselCode(
            "Tanker",
            88,
            88,
            "Tanker, reserved for future use",
        ),
        AisVesselCode(
            "Tanker",
            89,
            89,
            "Tanker, no additional information",
        ),
        AisVesselCode(
            "Other",
            90,
            90,
            "Other Type, all ships of this type",
        ),
        AisVesselCode(
            "Other",
            91,
            91,
            "Other Type, hazardous category A",
        ),
        AisVesselCode(
            "Other",
            92,
            92,
            "Other Type, hazardous category B",
        ),
        AisVesselCode(
            "Other",
            93,
            93,
            "Other Type, hazardous category C",
        ),
        AisVesselCode(
            "Other",
            94,
            94,
            "Other Type, hazardous category D",
        ),
        AisVesselCode(
            "Other",
            95,
            95,
            "Other Type, reserved for future use",
        ),
        AisVesselCode(
            "Other",
            96,
            96,
            "Other Type, reserved for future use",
        ),
        AisVesselCode(
            "Other",
            97,
            97,
            "Other Type, reserved for future use",
        ),
        AisVesselCode(
            "Other",
            98,
            98,
            "Other Type, reserved for future use",
        ),
        AisVesselCode(
            "Other",
            99,
            99,
            "Other Type, no additional information",
        ),
        AisVesselCode(
            "Other",
            100,
            199,
            "100 to 199 Reserved for regional use",
        ),
        AisVesselCode(
            "Other",
            200,
            255,
            "200 to 255 Reserved for future use",
        ),
        AisVesselCode(
            "Other",
            256,
            999,
            "256 to 999 No designation",
        ),
        AisVesselCode(
            "Fishing",
            1001,
            1001,
            "Commercial Fishing Vessel",
        ),
        AisVesselCode(
            "Fishing",
            1002,
            1002,
            "Fish Processing Vessel",
        ),
        AisVesselCode("Cargo", 1003, 1003, "Freight Barge"),
        AisVesselCode("Cargo", 1004, 1004, "Freight Ship"),
        AisVesselCode(
            "Other",
            1005,
            1005,
            "Industrial Vessel",
        ),
        AisVesselCode(
            "Other",
            1006,
            1006,
            "Miscellaneous Vessel",
        ),
        AisVesselCode(
            "Other",
            1007,
            1007,
            "Mobile Offshore Drilling Unit",
        ),
        AisVesselCode("Other", 1008, 1008, "Non-vessel"),
        AisVesselCode("Other", 1009, 1009, "NON-VESSEL"),
        AisVesselCode(
            "Other",
            1010,
            1010,
            "Offshore Supply Vessel",
        ),
        AisVesselCode("Other", 1011, 1011, "Oil Recovery"),
        AisVesselCode(
            "Passenger",
            1012,
            1012,
            "Passenger (Inspected)",
        ),
        AisVesselCode(
            "Passenger",
            1013,
            1013,
            "Passenger (Uninspected)",
        ),
        AisVesselCode(
            "Passenger",
            1014,
            1014,
            "Passenger Barge (Inspected)",
        ),
        AisVesselCode(
            "Passenger",
            1015,
            1015,
            "Passenger Barge (Uninspected)",
        ),
        AisVesselCode(
            "Cargo",
            1016,
            1016,
            "Public Freight",
        ),
        AisVesselCode(
            "Tanker",
            1017,
            1017,
            "Public Tankship/Barge",
        ),
        AisVesselCode(
            "Other",
            1018,
            1018,
            "Public Vessel, Unclassified",
        ),
        AisVesselCode(
            "Pleasure Craft Sailing",
            1019,
            1019,
            "Recreational",
        ),
        AisVesselCode(
            "Other",
            1020,
            1020,
            "Research Vessel",
        ),
        AisVesselCode(
            "Military",
            1021,
            1021,
            "SAR Aircraft",
        ),
        AisVesselCode("Other", 1022, 1022, "School Ship"),
        AisVesselCode("Tug Tow", 1023, 1023, "Tank Barge"),
        AisVesselCode("Tanker", 1024, 1024, "Tank Ship"),
        AisVesselCode(
            "Tug Tow",
            1025,
            1025,
            "Towing Vessel",
        ),
    ]


@dataclass
class AisVesselCode:
    name: str
    fromCode: int
    toCode: int
    description: str


@dataclass
class AisVesselCodes:
    codes: List[AisVesselCode] = field(default_factory=make_vessel_codes)

    def get_vessel_type(self, code: int) -> Optional[AisVesselCode]:
        """Find a vessel type by code

        Args:
            code (int): the vessel code to search for

        Returns:
            Optional[AisVesselCode]: the vessel type if found, otherwise None
        """

        return next((c for c in self.codes if c.fromCode <= code <= c.toCode), None)

    def get_vessel_type_name(self, code: int) -> str:
        """Find a vessel type by code

        Args:
            code (int): the vessel code to search for

        Returns:
            Optional[AisVesselCode]: the vessel type if found, otherwise None
        """

        vessel_type = self.get_vessel_type(code)

        return vessel_type.name if vessel_type else "Not Found"

    def get_vessel_type_description(self, code: int) -> str:
        """Find a vessel type by code

        Args:
            code (int): the vessel code to search for

        Returns:
            Optional[AisVesselCode]: the vessel type if found, otherwise None
        """

        vessel_type = self.get_vessel_type(code)

        return vessel_type.description if vessel_type else "Not Found"

    def get_vessel_codes(self, vessel_type: str) -> List[int]:
        """Find codes for a vessel type

        Args:
            vessel_type (str): The name of the vessel type we are searching for

        Returns:
            List[AisVesselCode]: a list of codes for the vessel type
        """
        vessel_type = vessel_type.lower().strip()
        return [c.fromCode for c in self.codes if c.name.lower().strip() == vessel_type]

    def get_vessel_codes_from_description(self, vessel_description: str) -> List[int]:
        """Find codes for a vessel type

        Args:
            vessel_description (str): The description of the vessel type
                we are searching for

        Returns:
            List[AisVesselCode]: a list of codes for the vessel type
        """
        vessel_description = vessel_description.lower().strip()
        return [
            c.fromCode
            for c in self.codes
            if c.description.lower().strip() == vessel_description
        ]


class VesselCodeMixin:
    ais_vessel_codes: AisVesselCodes = AisVesselCodes()
