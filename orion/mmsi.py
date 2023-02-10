import re
from dataclasses import dataclass, field
from typing import List, Optional

import geopandas


def make_jurisdictions() -> List["Jurisdiction"]:
    return [
        Jurisdiction("AL", "201", "Albania"),
        Jurisdiction("AD", "202", "Andorra"),
        Jurisdiction("AT", "203", "Austria"),
        Jurisdiction("PT-20", "204", "Azores"),
        Jurisdiction("BE", "205", "Belgium"),
        Jurisdiction("BY", "206", "Belarus"),
        Jurisdiction("BG", "207", "Bulgaria"),
        Jurisdiction("VA", "208", "Vatican City"),
        Jurisdiction("CY", "209", "Cyprus"),
        Jurisdiction("CY", "210", "Cyprus"),
        Jurisdiction("CY", "212", "Cyprus"),
        Jurisdiction("DE", "211", "Germany"),
        Jurisdiction("DE", "218", "Germany"),
        Jurisdiction("GE", "213", "Georgia"),
        Jurisdiction("MD", "214", "Moldova"),
        Jurisdiction("MT", "215", "Malta"),
        Jurisdiction("MT", "229", "Malta"),
        Jurisdiction("MT", "248", "Malta"),
        Jurisdiction("MT", "249", "Malta"),
        Jurisdiction("MT", "256", "Malta"),
        Jurisdiction("AM", "216", "Armenia"),
        Jurisdiction("DK", "219", "Denmark"),
        Jurisdiction("DK", "220", "Denmark"),
        Jurisdiction("ES", "224", "Spain"),
        Jurisdiction("ES", "225", "Spain"),
        Jurisdiction("FR", "226", "France"),
        Jurisdiction("FR", "227", "France"),
        Jurisdiction("FR", "228", "France"),
        Jurisdiction("FI", "230", "Finland"),
        Jurisdiction("FO", "231", "Faroe Islands"),
        Jurisdiction("GB", "232", "United Kingdom"),
        Jurisdiction("GB", "233", "United Kingdom"),
        Jurisdiction("GB", "234", "United Kingdom"),
        Jurisdiction("GB", "235", "United Kingdom"),
        Jurisdiction("GI", "236", "Gibraltar"),
        Jurisdiction("GR", "237", "Greece"),
        Jurisdiction("GR", "239", "Greece"),
        Jurisdiction("GR", "240", "Greece"),
        Jurisdiction("GR", "241", "Greece"),
        Jurisdiction("HR", "238", "Croatia"),
        Jurisdiction("MA", "242", "Morocco"),
        Jurisdiction("HU", "243", "Hungary"),
        Jurisdiction("NL", "244", "Netherlands"),
        Jurisdiction("NL", "245", "Netherlands"),
        Jurisdiction("NL", "246", "Netherlands"),
        Jurisdiction("IT", "247", "Italy"),
        Jurisdiction("IE", "250", "Ireland"),
        Jurisdiction("IS", "251", "Iceland"),
        Jurisdiction("LI", "252", "Liechtenstein"),
        Jurisdiction("LU", "253", "Luxembourg"),
        Jurisdiction("MC", "254", "Monaco"),
        Jurisdiction("PT-30", "255", "Madeira"),
        Jurisdiction("NO", "257", "Norway"),
        Jurisdiction("NO", "258", "Norway"),
        Jurisdiction("NO", "259", "Norway"),
        Jurisdiction("PL", "261", "Poland"),
        Jurisdiction("ME", "262", "Montenegro"),
        Jurisdiction("PT", "263", "Portugal"),
        Jurisdiction("RO", "264", "Romania"),
        Jurisdiction("SE", "265", "Sweden"),
        Jurisdiction("SE", "266", "Sweden"),
        Jurisdiction("SK", "267", "Slovakia"),
        Jurisdiction("SM", "268", "San Marino"),
        Jurisdiction("CH", "269", "Switzerland"),
        Jurisdiction("CZ", "270", "Czech Republic"),
        Jurisdiction("TR", "271", "Turkey"),
        Jurisdiction("UA", "272", "Ukraine"),
        Jurisdiction("RU", "273", "Russia"),
        Jurisdiction("MK", "274", "Macedonia"),
        Jurisdiction("LV", "275", "Latvia"),
        Jurisdiction("EE", "276", "Estonia"),
        Jurisdiction("LT", "277", "Lithuania"),
        Jurisdiction("SI", "278", "Slovenia"),
        Jurisdiction("RS", "279", "Serbia"),
        Jurisdiction("AI", "301", "Anguilla"),
        Jurisdiction("US-AK", "303", "Alaska"),
        Jurisdiction("AG", "304", "Antigua and Barbuda"),
        Jurisdiction("AG", "305", "Antigua and Barbuda"),
        Jurisdiction(
            "BQ, CW, SX", "306", "Caribbean Netherlands, Curaçao, Sint Maarten"
        ),
        Jurisdiction("AW", "307", "Aruba"),
        Jurisdiction("BS", "308", "Bahamas"),
        Jurisdiction("BS", "309", "Bahamas"),
        Jurisdiction("BS", "311", "Bahamas"),
        Jurisdiction("BM", "310", "Bermuda"),
        Jurisdiction("BZ", "312", "Belize"),
        Jurisdiction("BB", "314", "Barbados"),
        Jurisdiction("CA", "316", "Canada"),
        Jurisdiction("KY", "319", "Cayman Islands"),
        Jurisdiction("CR", "321", "Costa Rica"),
        Jurisdiction("CU", "323", "Cuba"),
        Jurisdiction("DM", "325", "Dominica"),
        Jurisdiction("DO", "327", "Dominican Republic"),
        Jurisdiction("GP", "329", "Guadeloupe"),
        Jurisdiction("GD", "330", "Grenada"),
        Jurisdiction("GL", "331", "Greenland"),
        Jurisdiction("GT", "332", "Guatemala"),
        Jurisdiction("HN", "334", "Honduras"),
        Jurisdiction("HT", "336", "Haiti"),
        Jurisdiction("US", "338", "United States of America"),
        Jurisdiction("US", "366", "United States of America"),
        Jurisdiction("US", "367", "United States of America"),
        Jurisdiction("US", "368", "United States of America"),
        Jurisdiction("US", "369", "United States of America"),
        Jurisdiction("JM", "339", "Jamaica"),
        Jurisdiction("KN", "341", "Saint Kitts and Nevis"),
        Jurisdiction("LC", "343", "Saint Lucia"),
        Jurisdiction("MX", "345", "Mexico"),
        Jurisdiction("MQ", "347", "Martinique"),
        Jurisdiction("MS", "348", "Montserrat"),
        Jurisdiction("NI", "350", "Nicaragua"),
        Jurisdiction("PA", "351", "Panama"),
        Jurisdiction("PA", "352", "Panama"),
        Jurisdiction("PA", "353", "Panama"),
        Jurisdiction("PA", "354", "Panama"),
        Jurisdiction("PA", "355", "Panama"),
        Jurisdiction("PA", "356", "Panama"),
        Jurisdiction("PA", "357", "Panama"),
        Jurisdiction("PA", "370", "Panama"),
        Jurisdiction("PA", "371", "Panama"),
        Jurisdiction("PA", "372", "Panama"),
        Jurisdiction("PA", "373", "Panama"),
        Jurisdiction("PA", "374", "Panama"),
        Jurisdiction("PR", "358", "Puerto Rico"),
        Jurisdiction("SV", "359", "El Salvador"),
        Jurisdiction("PM", "361", "Saint Pierre and Miquelon"),
        Jurisdiction("TT", "362", "Trinidad and Tobago"),
        Jurisdiction("TC", "364", "Turks and Caicos Islands"),
        Jurisdiction("VC", "375", "Saint Vincent and the Grenadines"),
        Jurisdiction("VC", "376", "Saint Vincent and the Grenadines"),
        Jurisdiction("VC", "377", "Saint Vincent and the Grenadines"),
        Jurisdiction("VG", "378", "British Virgin Islands"),
        Jurisdiction("VI", "379", "US Virgin Islands"),
        Jurisdiction("AF", "401", "Afghanistan"),
        Jurisdiction("SA", "403", "Saudi Arabia"),
        Jurisdiction("BD", "405", "Bangladesh"),
        Jurisdiction("BH", "408", "Bahrain"),
        Jurisdiction("BT", "410", "Bhutan"),
        Jurisdiction("CN", "412", "China"),
        Jurisdiction("CN", "413", "China"),
        Jurisdiction("CN", "414", "China"),
        Jurisdiction("TW", "416", "Taiwan"),
        Jurisdiction("LK", "417", "Sri Lanka"),
        Jurisdiction("IN", "419", "India"),
        Jurisdiction("IR", "422", "Iran"),
        Jurisdiction("AZ", "423", "Azerbaijan"),
        Jurisdiction("IQ", "425", "Iraq"),
        Jurisdiction("IL", "428", "Israel"),
        Jurisdiction("JP", "431", "Japan"),
        Jurisdiction("JP", "432", "Japan"),
        Jurisdiction("TM", "434", "Turkmenistan"),
        Jurisdiction("KZ", "436", "Kazakhstan"),
        Jurisdiction("UZ", "437", "Uzbekistan"),
        Jurisdiction("JO", "438", "Jordan"),
        Jurisdiction("KR", "440", "Korea"),
        Jurisdiction("KR", "441", "Korea"),
        Jurisdiction("PS", "443", "Palestinian Authority"),
        Jurisdiction("KP", "445", "North Korea"),
        Jurisdiction("KW", "447", "Kuwait"),
        Jurisdiction("LB", "450", "Lebanon"),
        Jurisdiction("KG", "451", "Kyrgyzstan"),
        Jurisdiction("MO", "453", "Macao"),
        Jurisdiction("MV", "455", "Maldives"),
        Jurisdiction("MN", "457", "Mongolia"),
        Jurisdiction("NP", "459", "Nepal"),
        Jurisdiction("OM", "461", "Oman"),
        Jurisdiction("PK", "463", "Pakistan"),
        Jurisdiction("QA", "466", "Qatar"),
        Jurisdiction("SY", "468", "Syria"),
        Jurisdiction("AE", "470", "United Arab Emirates"),
        Jurisdiction("AE", "471", "United Arab Emirates"),
        Jurisdiction("TJ", "472", "Tajikistan"),
        Jurisdiction("YE", "473", "Yemen"),
        Jurisdiction("YE", "475", "Yemen"),
        Jurisdiction("HK", "477", "Hong Kong"),
        Jurisdiction("BA", "478", "Bosnia and Herzegovina"),
        Jurisdiction("TF", "501", "Adelie Land"),
        Jurisdiction("AU", "503", "Australia"),
        Jurisdiction("MM", "506", "Myanmar"),
        Jurisdiction("BN", "508", "Brunei"),
        Jurisdiction("FM", "510", "Micronesia"),
        Jurisdiction("PW", "511", "Palau"),
        Jurisdiction("NZ", "512", "New Zealand"),
        Jurisdiction("KH", "514", "Cambodia"),
        Jurisdiction("KH", "515", "Cambodia"),
        Jurisdiction("CX", "516", "Christmas Island"),
        Jurisdiction("CK", "518", "Cook Islands"),
        Jurisdiction("FJ", "520", "Fiji"),
        Jurisdiction("CC", "523", "Cocos"),
        Jurisdiction("ID", "525", "Indonesia"),
        Jurisdiction("KI", "529", "Kiribati"),
        Jurisdiction("LA", "531", "Laos"),
        Jurisdiction("MY", "533", "Malaysia"),
        Jurisdiction("MP", "536", "Northern Mariana Islands"),
        Jurisdiction("MH", "538", "Montenegro"),
        Jurisdiction("NC", "540", "New Caledonia"),
        Jurisdiction("NU", "542", "Niue"),
        Jurisdiction("NR", "544", "Nauru"),
        Jurisdiction("PF", "546", "French Polynesia"),
        Jurisdiction("PH", "548", "Philippines"),
        Jurisdiction("PG", "553", "Papua New Guinea"),
        Jurisdiction("PN", "555", "Pitcairn Island"),
        Jurisdiction("SB", "557", "Solomon Islands"),
        Jurisdiction("AS", "559", "American Samoa"),
        Jurisdiction("WS", "561", "Samoa"),
        Jurisdiction("SG", "563", "Singapore"),
        Jurisdiction("SG", "564", "Singapore"),
        Jurisdiction("SG", "565", "Singapore"),
        Jurisdiction("SG", "566", "Singapore"),
        Jurisdiction("TH", "567", "Thailand"),
        Jurisdiction("TO", "570", "Tonga"),
        Jurisdiction("TV", "572", "Tuvalu"),
        Jurisdiction("VN", "574", "Vietnam"),
        Jurisdiction("VU", "576", "Vanuatu"),
        Jurisdiction("VU", "577", "Vanuatu"),
        Jurisdiction("WF", "578", "Wallis and Futuna Islands"),
        Jurisdiction("ZA", "601", "South Africa"),
        Jurisdiction("AO", "603", "Angola"),
        Jurisdiction("DZ", "605", "Algeria"),
        Jurisdiction("TF-SP", "607", "Saint Paul and Amsterdam Islands"),
        Jurisdiction("SH-AC", "608", "Ascension Island"),
        Jurisdiction("BI", "609", "Burundi"),
        Jurisdiction("BJ", "610", "Benin"),
        Jurisdiction("BW", "611", "Botswana"),
        Jurisdiction("CF", "612", "Central African Republic"),
        Jurisdiction("CM", "613", "Cameroon"),
        Jurisdiction("CG", "615", "Congo"),
        Jurisdiction("KM", "616", "Comoros"),
        Jurisdiction("KM", "620", "Comoros"),
        Jurisdiction("CV", "617", "Cape Verde"),
        Jurisdiction("TF-CA", "618", "Crozet Archipelago"),
        Jurisdiction("CI", "619", "Côte d'Ivoire"),
        Jurisdiction("DJ", "621", "Djibouti"),
        Jurisdiction("EG", "622", "Egypt"),
        Jurisdiction("ET", "624", "Ethiopia"),
        Jurisdiction("ER", "625", "Eritrea"),
        Jurisdiction("GA", "626", "Gabonese Republic"),
        Jurisdiction("GH", "627", "Ghana"),
        Jurisdiction("GM", "629", "Gambia"),
        Jurisdiction("GW", "630", "Guinea-Bissau"),
        Jurisdiction("GQ", "631", "Equatorial Guinea"),
        Jurisdiction("GN", "632", "Guinea"),
        Jurisdiction("BF", "633", "Burkina Faso"),
        Jurisdiction("KE", "634", "Kenya"),
        Jurisdiction("TF-KI", "635", "Kerguelen Islands"),
        Jurisdiction("LR", "636", "Liberia"),
        Jurisdiction("LR", "637", "Liberia"),
        Jurisdiction("SS", "638", "South Sudan"),
        Jurisdiction("LY", "642", "Libya"),
        Jurisdiction("LS", "644", "Lesotho"),
        Jurisdiction("MU", "645", "Mauritius"),
        Jurisdiction("MG", "647", "Madagascar"),
        Jurisdiction("ML", "649", "Mali"),
        Jurisdiction("MZ", "650", "Mozambique"),
        Jurisdiction("MR", "654", "Mauritania"),
        Jurisdiction("MW", "655", "Malawi"),
        Jurisdiction("NE", "656", "Niger"),
        Jurisdiction("NG", "657", "Nigeria"),
        Jurisdiction("NA", "659", "Namibia"),
        Jurisdiction("RE", "660", "Réunion"),
        Jurisdiction("RW", "661", "Rwanda"),
        Jurisdiction("SD", "662", "Sudan"),
        Jurisdiction("SN", "663", "Senegal"),
        Jurisdiction("SC", "664", "Seychelles"),
        Jurisdiction("SH-HL", "665", "Saint Helena"),
        Jurisdiction("SO", "666", "Somalia"),
        Jurisdiction("SL", "667", "Sierra Leone"),
        Jurisdiction("ST", "668", "São Tomé and Príncipe"),
        Jurisdiction("SZ", "669", "Swaziland"),
        Jurisdiction("TD", "670", "Chad"),
        Jurisdiction("TG", "671", "Togo"),
        Jurisdiction("TN", "672", "Tunisia"),
        Jurisdiction("TZ", "674", "Tanzania"),
        Jurisdiction("TZ", "677", "Tanzania"),
        Jurisdiction("UG", "675", "Uganda"),
        Jurisdiction("CD", "676", "Democratic Republic of the Congo"),
        Jurisdiction("ZM", "678", "Zambia"),
        Jurisdiction("ZW", "679", "Zimbabwe"),
        Jurisdiction("AR", "701", "Argentina"),
        Jurisdiction("BR", "710", "Brazil"),
        Jurisdiction("BO", "720", "Bolivia"),
        Jurisdiction("CL", "725", "Chile"),
        Jurisdiction("CO", "730", "Colombia"),
        Jurisdiction("EC", "735", "Ecuador"),
        Jurisdiction("FK", "740", "Falkland Islands"),
        Jurisdiction("GF", "745", "Guiana"),
        Jurisdiction("GY", "750", "Guyana"),
        Jurisdiction("PY", "755", "Paraguay"),
        Jurisdiction("PE", "760", "Peru"),
        Jurisdiction("SR", "765", "Suriname"),
        Jurisdiction("UY", "770", "Uruguay"),
        Jurisdiction("VE", "775", "Venezuela"),
    ]


@dataclass
class Jurisdiction:
    name: str
    midcode: str
    full_name: str


@dataclass
class Mmsi:
    jurisdictions: List[Jurisdiction] = field(default_factory=make_jurisdictions)

    def is_valid_ship_mmsi(self, mmsi: int) -> bool:
        """check if mmsi is a ship.

        Args:
            mmsi (int): mmsi number

        Returns:
            bool: True if mmsi is a ship, False otherwise
        """

        mmsi_str = str(mmsi)

        ship_pattern = re.compile(r"([2-7]\d{2})\d{6}")

        return bool(ship_pattern.match(mmsi_str))

    def get_mid(self, mmsi: int) -> str:
        """If MMSI is a ship, return the MID code.

        Args:
            mmsi (int): mmsi number

        Raises:
            ValueError: If the mmsi is not a ship, raise ValueError

        Returns:
            str: MID code
        """
        mmsi_str = str(mmsi)

        ship_pattern = re.compile(r"([2-7]\d{2})\d{6}")

        if match := ship_pattern.match(mmsi_str):
            return match[1]
        else:
            raise ValueError("MMSI is not a ship")

    def get_jurisdiction(self, mmsi: int) -> Optional[Jurisdiction]:
        """Get the jurisdiction of a ship.

        Args:
            mmsi (int): mmsi number

        Returns:
            str: Jurisdiction code
        """

        mid = self.get_mid(mmsi)

        return next(
            (
                jurisdiction
                for jurisdiction in self.jurisdictions
                if jurisdiction.midcode == mid
            ),
            None,
        )

    def get_jurisdiction_name(self, mmsi: int) -> str:
        """Get the jurisdiction name of a ship.

        Args:
            mmsi (int): mmsi number

        Returns:
            str: Jurisdiction name
        """
        jurisdiction = self.get_jurisdiction(mmsi)

        return jurisdiction.name if jurisdiction else "Not Found"

    def is_norwegian(self, mmsi: int) -> bool:
        """Check if a ship is Norwegian.

        Args:
            mmsi (int): mmsi number

        Returns:
            bool: True if Norwegian, False otherwise
        """
        return self.get_jurisdiction_name(mmsi) == "NO"

    def remove_norwegian_gdf(  # type: ignore[no-any-unimported]
        self, gdf: geopandas.GeoDataFrame
    ) -> geopandas.GeoDataFrame:
        """Removes all Norwegian ships from a dataframe.

        Args:
            df (panda.DataFrane): _description_

        Returns:
            _type_: _description_
        """
        return gdf[~gdf.mmsi.apply(self.is_norwegian)]

    def remove_norwegian_list(  # type: ignore[no-any-unimported]
        self, ships: List[int]
    ) -> List[int]:
        """Removes all Norwegian ships from a list.

        Args:
            ships (List): A list of ships

        Returns:
            List: A list of ships without Norwegian ships
        """

        return [s for s in ships if not self.is_norwegian(s)]


class MmsiMixin:
    mmsi: Mmsi = Mmsi()
