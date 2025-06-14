"""Predefined designation mappings for common abbreviations."""

from typing import Dict, List, Set


class DesignationConfig:
    """Manages predefined mappings for designation abbreviations."""

    # Predefined mappings for known designation abbreviations
    DESIGNATION_MAPPINGS: Dict[str, List[str]] = {
        # Senior Software Engineer variations
        "SSE": ["Senior Software Engineer"],
        "Sr SE": ["Senior Software Engineer"],
        "Sr. SE": ["Senior Software Engineer"],
        "Senior SE": ["Senior Software Engineer"],
        # Software Engineer variations
        "SE": ["Software Engineer", "Senior Software Engineer"],
        "SWE": ["Software Engineer"],
        # Software Development Engineer variations
        "SDE": ["Software Development Engineer"],
        "SDET": ["Software Development Engineer"],
        "SDE I": ["Software Development Engineer"],
        "SDE II": ["Senior Software Engineer"],  # Typically maps to senior level
        # Technical Lead variations
        "TL": ["Technical Lead"],
        "Tech Lead": ["Technical Lead"],
        "Team Lead": ["Technical Lead"],
        "Lead": ["Technical Lead"],
        # Project Manager variations
        "PM": ["Project Manager"],
        "Proj Manager": ["Project Manager"],
        "Project Mgr": ["Project Manager"],
        # Quality Assurance variations
        "QA": [
            "Quality Assurance Engineer",
            "Senior Quality Assurance Engineer",
            "Quality Assurance Intern",
        ],
        "QAE": ["Quality Assurance Engineer"],
        "QA Engineer": ["Quality Assurance Engineer"],
        "Tester": ["Quality Assurance Engineer"],
        "Test Engineer": ["Quality Assurance Engineer"],
        # Senior Quality Assurance variations
        "Sr QA": ["Senior Quality Assurance Engineer"],
        "Sr. QA": ["Senior Quality Assurance Engineer"],
        "Senior QA": ["Senior Quality Assurance Engineer"],
        "SQAE": ["Senior Quality Assurance Engineer"],
        # Business Analyst variations
        "BA": ["Business Analyst"],
        "Bus Analyst": ["Business Analyst"],
        "Business Ana": ["Business Analyst"],
        # Software Architect variations
        "SA": ["Software Architect"],
        "Architect": ["Software Architect"],
        "Tech Architect": ["Software Architect"],
        # Principal Software Engineer variations
        "PSE": ["Principal Software Engineer"],
        "Principal SE": ["Principal Software Engineer"],
        "Prin SE": ["Principal Software Engineer"],
        # UX Designer variations
        "UX": ["UX Designer"],
        "UI/UX": ["UX Designer"],
        "Designer": ["UX Designer"],
        # Technical Delivery Officer variations
        "TDO": ["Technical Delivery Officer"],
        "Tech Delivery": ["Technical Delivery Officer"],
        "Delivery Officer": ["Technical Delivery Officer"],
        # Intern variations
        "Intern": ["Software Development Engineer Intern", "Quality Assurance Intern"],
        "SDE Intern": ["Software Development Engineer Intern"],
        "QA Intern": ["Quality Assurance Intern"],
    }

    @classmethod
    def get_mapped_designations(cls, abbreviation: str) -> List[str]:
        """Get mapped designations for an abbreviation.

        Args:
            abbreviation: The abbreviation to look up (case-insensitive)

        Returns:
            List of full designation names, empty if not found
        """
        # Normalize the input (case-insensitive, strip whitespace)
        normalized_abbr = abbreviation.strip()

        # Try exact match first
        if normalized_abbr in cls.DESIGNATION_MAPPINGS:
            return cls.DESIGNATION_MAPPINGS[normalized_abbr].copy()

        # Try case-insensitive match
        for key, values in cls.DESIGNATION_MAPPINGS.items():
            if key.lower() == normalized_abbr.lower():
                return values.copy()

        return []

    @classmethod
    def is_known_designation_abbreviation(cls, term: str) -> bool:
        """Check if a term is a known designation abbreviation.

        Args:
            term: The term to check

        Returns:
            True if it's a known abbreviation, False otherwise
        """
        return len(cls.get_mapped_designations(term)) > 0

    @classmethod
    def get_all_abbreviations(cls) -> Set[str]:
        """Get all known abbreviations.

        Returns:
            Set of all known abbreviations
        """
        return set(cls.DESIGNATION_MAPPINGS.keys())

    @classmethod
    def get_all_full_designations(cls) -> Set[str]:
        """Get all full designation names from mappings.

        Returns:
            Set of all full designation names
        """
        all_designations = set()
        for designations in cls.DESIGNATION_MAPPINGS.values():
            all_designations.update(designations)
        return all_designations

    @classmethod
    def add_custom_mapping(cls, abbreviation: str, full_names: List[str]) -> None:
        """Add a custom mapping (for runtime additions).

        Args:
            abbreviation: The abbreviation
            full_names: List of full designation names
        """
        cls.DESIGNATION_MAPPINGS[abbreviation] = full_names.copy()

    @classmethod
    def get_mapping_info(cls) -> Dict[str, int]:
        """Get information about the mappings.

        Returns:
            Dictionary with mapping statistics
        """
        return {
            "total_abbreviations": len(cls.DESIGNATION_MAPPINGS),
            "total_unique_designations": len(cls.get_all_full_designations()),
            "average_mappings_per_abbreviation": sum(
                len(v) for v in cls.DESIGNATION_MAPPINGS.values()
            )
            / len(cls.DESIGNATION_MAPPINGS),
        }
