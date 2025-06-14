"""Fuzzy query classifier for detecting vague terms that need semantic resolution."""

import re
from typing import Any, Dict, List

import structlog
from app.ai.core.config import AIConfig
from app.ai.prompts import FuzzyClassifierPrompts
from app.core.config import settings
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

logger = structlog.get_logger()


class FuzzyClassifier:
    """Classifier to detect if a query contains fuzzy/vague terms."""

    def __init__(self, config: AIConfig):
        """Initialize the fuzzy classifier.

        Args:
            config: AI configuration settings
        """
        self.config = config

        # Initialize LLM with low temperature for consistent classification
        self.llm = ChatOpenAI(
            model=self.config.model_name,
            temperature=0.2,  # Low temperature for consistent classification
            verbose=settings.DEBUG,
            api_key=self.config.api_key,
        )

        # Get fuzzy classification prompt from prompts module
        self.fuzzy_classification_prompt = FuzzyClassifierPrompts.get_fuzzy_classification_prompt()

        # Initialize chain
        self.classification_chain = self.fuzzy_classification_prompt | self.llm

    async def classify(self, query: str) -> Dict[str, Any]:
        """Classify if a query is fuzzy and extract fuzzy terms.

        Args:
            query: User query to classify

        Returns:
            Dictionary with 'classification' and 'fuzzy_terms' keys
        """
        try:
            logger.info(
                "[FUZZY-CLASSIFIER] Classifying query",
                query=query,
                agent_type="fuzzy_classifier",
            )

            # Get classification from LLM
            result = await self.classification_chain.ainvoke({"query": query})
            response_text = str(result.content).strip()

            # Parse the structured response
            parsed_result = self._parse_llm_response(response_text)

            # If LLM says it's fuzzy, use fallback method to extract the actual fuzzy terms
            # since the LLM only returns classification, not the specific terms
            if parsed_result["classification"] == "fuzzy":
                fallback_result = self._fallback_classification(query)
                parsed_result["fuzzy_terms"] = fallback_result["fuzzy_terms"]

            # Validate classification
            if parsed_result["classification"] not in ["fuzzy", "precise"]:
                logger.warning(
                    "[FUZZY-CLASSIFIER] Invalid classification, falling back to rule-based check",
                    raw_response=response_text,
                    query=query,
                    agent_type="fuzzy_classifier",
                )
                # Fallback to rule-based approach
                fallback_result = self._fallback_classification(query)
                parsed_result = fallback_result

            logger.info(
                "[FUZZY-CLASSIFIER] Query classified",
                query=query,
                classification=parsed_result["classification"],
                fuzzy_terms=parsed_result["fuzzy_terms"],
                agent_type="fuzzy_classifier",
            )

            return parsed_result

        except Exception as e:
            logger.error(
                "[FUZZY-CLASSIFIER] Error classifying query",
                error=str(e),
                query=query,
                agent_type="fuzzy_classifier",
            )
            # Default to precise on error to avoid breaking the flow
            return {"classification": "precise", "fuzzy_terms": []}

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the structured LLM response.

        Args:
            response_text: Raw response from LLM

        Returns:
            Parsed result with classification and fuzzy terms
        """
        try:
            # Clean up the response
            response_text = response_text.strip().upper()

            # The prompt asks for a simple one-word response: "FUZZY" or "PRECISE"
            if response_text == "FUZZY":
                # For fuzzy classification, we'll use the fallback method to extract terms
                # since the LLM only returns the classification, not the specific terms
                fallback_result = self._fallback_classification("")  # We'll get terms from fallback
                return {"classification": "fuzzy", "fuzzy_terms": []}
            elif response_text == "PRECISE":
                return {"classification": "precise", "fuzzy_terms": []}
            else:
                # Try to parse structured format as fallback (in case prompt changes)
                lines = response_text.split("\n")
                classification = "precise"
                fuzzy_terms = []

                for line in lines:
                    line = line.strip()
                    if line.startswith("CLASSIFICATION:"):
                        classification = line.split(":", 1)[1].strip().lower()
                    elif line.startswith("FUZZY TERMS:"):
                        terms_text = line.split(":", 1)[1].strip()
                        if terms_text.lower() != "none":
                            # Split by comma and clean up
                            fuzzy_terms = [
                                term.strip() for term in terms_text.split(",") if term.strip()
                            ]

                return {"classification": classification, "fuzzy_terms": fuzzy_terms}

        except Exception as e:
            logger.error(
                "[FUZZY-CLASSIFIER] Error parsing LLM response",
                error=str(e),
                response_text=response_text,
                agent_type="fuzzy_classifier",
            )
            return {"classification": "precise", "fuzzy_terms": []}

    def _fallback_classification(self, query: str) -> Dict[str, Any]:
        """Fallback rule-based classification and term extraction.

        Args:
            query: User query to classify

        Returns:
            Classification result with extracted fuzzy terms
        """
        fuzzy_terms = []
        query_lower = query.lower()

        # Enhanced patterns for better edge case handling
        fuzzy_patterns = [
            # Skill categories
            r"\b(frontend|backend|mobile|cloud|data|web|design|analytics|devops|security|testing)\b",
            # Experience levels and expertise
            r"\b(senior|junior|experienced|lead|management|leadership|expert|specialist)\b",
            # Role abbreviations
            r"\b(SSE|TL|PM|QA|SE|SDE|BA|UX|ARCH|PE|TDO)\b",
            # Team references
            r"\b(design team|qa team|backend team|frontend team|mobile team|cloud team|data team)\b",
            # Skill experience queries (but not project status)
            r"\bdevelopers?\s+with\s+\w+\s+experience\b",
            r"\bwho knows\s+\w+",
            r"\bexperts?\s+in\s+\w+",
            # General developer references (broad role term)
            r"\bdevelopers?\b(?!\s+with\s+(React|Java|Python|JavaScript|specific))",
            # Vague descriptors (excluding project status)
            r"\b(good at|skilled in|familiar with|proficient in)\b",
        ]

        # Precise patterns that should NOT be fuzzy
        precise_patterns = [
            # Project status queries
            r"\bworking on\s+(active|customer|internal|completed)\s+projects?\b",
            r"\bassigned to\s+projects?\b",
            r"\ballocated to\s+projects?\b",
            # Allocation queries
            r"\b(overallocated|underutilized|available)\s+employees?\b",
            # Specific skill queries
            r"\bemployees?\s+with\s+(React|Java|Python|JavaScript|AWS|Docker|specific)\s+skills?\b",
        ]

        # Check for precise patterns first
        is_precise = False
        for pattern in precise_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                is_precise = True
                break

        if is_precise:
            return {"classification": "precise", "fuzzy_terms": []}

        # Extract fuzzy terms
        for pattern in fuzzy_patterns:
            matches = re.findall(pattern, query_lower, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    fuzzy_terms.extend(match)
                else:
                    fuzzy_terms.append(match)

        # Special handling for "developers" - only fuzzy if not with specific skills
        if "developers" in query_lower:
            # Check if it's with specific skills
            specific_skills = [
                "react",
                "java",
                "python",
                "javascript",
                "aws",
                "docker",
                "kubernetes",
            ]
            has_specific_skill = any(skill in query_lower for skill in specific_skills)
            if not has_specific_skill:
                fuzzy_terms.append("developers")

        # Remove duplicates while preserving order
        fuzzy_terms = list(dict.fromkeys(fuzzy_terms))

        classification = "fuzzy" if fuzzy_terms else "precise"

        return {"classification": classification, "fuzzy_terms": fuzzy_terms}

    async def is_fuzzy(self, query: str) -> bool:
        """Check if query is fuzzy (convenience method).

        Args:
            query: User query to check

        Returns:
            True if fuzzy, False if precise
        """
        result = await self.classify(query)
        return result["classification"] == "fuzzy"

    async def get_fuzzy_terms(self, query: str) -> List[str]:
        """Extract fuzzy terms from query (convenience method).

        Args:
            query: User query to analyze

        Returns:
            List of fuzzy terms that need resolution
        """
        result = await self.classify(query)
        return result["fuzzy_terms"]
