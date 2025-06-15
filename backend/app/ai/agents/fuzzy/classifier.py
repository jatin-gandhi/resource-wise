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

            # Get fuzzy terms from both methods for comparison
            regex_fuzzy_terms = self._extract_fuzzy_terms_from_patterns(query)
            llm_fuzzy_terms = parsed_result.get("fuzzy_terms", [])

            # Use regex as primary, LLM as fallback
            if regex_fuzzy_terms:
                # Regex found terms - use them
                final_fuzzy_terms = regex_fuzzy_terms
                extraction_method = "regex"
            elif llm_fuzzy_terms:
                # Regex found nothing, use LLM terms
                final_fuzzy_terms = llm_fuzzy_terms
                extraction_method = "llm_fallback"
            else:
                # Neither method found terms
                final_fuzzy_terms = []
                extraction_method = "none"

            # Compare and log accuracy/matching
            self._log_extraction_comparison(
                query, regex_fuzzy_terms, llm_fuzzy_terms, extraction_method
            )

            # Update result with final fuzzy terms
            parsed_result["fuzzy_terms"] = final_fuzzy_terms
            parsed_result["extraction_method"] = extraction_method

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
                extraction_method=parsed_result["extraction_method"],
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
            return {"classification": "precise", "fuzzy_terms": [], "extraction_method": "none"}

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the structured LLM response in JSON format.

        Args:
            response_text: Raw response from LLM (should be JSON)

        Returns:
            Parsed result with classification and fuzzy terms
        """
        try:
            # Clean up the response (remove any markdown formatting)
            response_text = response_text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith("```"):
                response_text = response_text[3:]  # Remove ```
            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove ```

            response_text = response_text.strip()

            # Parse JSON
            import json

            parsed_json = json.loads(response_text)

            # Extract and validate fields
            classification = parsed_json.get("classification", "").upper()
            fuzzy_terms = parsed_json.get("fuzzy_terms", [])

            # Normalize classification
            classification = "fuzzy" if classification == "FUZZY" else "precise"

            # Ensure fuzzy_terms is a list
            if not isinstance(fuzzy_terms, list):
                fuzzy_terms = []

            # Clean up fuzzy terms (remove empty strings, strip whitespace)
            fuzzy_terms = [term.strip() for term in fuzzy_terms if term and term.strip()]

            logger.info(
                "[FUZZY-CLASSIFIER] LLM JSON response parsed",
                classification=classification,
                llm_fuzzy_terms=fuzzy_terms,
                agent_type="fuzzy_classifier",
            )

            return {"classification": classification, "fuzzy_terms": fuzzy_terms}

        except json.JSONDecodeError as e:
            logger.warning(
                "[FUZZY-CLASSIFIER] JSON parsing failed, trying fallback parsing",
                error=str(e),
                response_text=response_text[:200],
                agent_type="fuzzy_classifier",
            )
            # Fallback to old text parsing method
            return self._parse_llm_response_fallback(response_text)

        except Exception as e:
            logger.error(
                "[FUZZY-CLASSIFIER] Error parsing LLM response",
                error=str(e),
                response_text=response_text[:200],
                agent_type="fuzzy_classifier",
            )
            return {"classification": "precise", "fuzzy_terms": []}

    def _parse_llm_response_fallback(self, response_text: str) -> Dict[str, Any]:
        """Fallback parser for non-JSON responses.

        Args:
            response_text: Raw response from LLM

        Returns:
            Parsed result with classification and fuzzy terms
        """
        try:
            # Parse structured text format as fallback
            lines = response_text.split("\n")
            classification = "precise"
            fuzzy_terms = []

            for line in lines:
                line = line.strip()
                if line.startswith("Classification:"):
                    classification = line.split(":", 1)[1].strip().upper()
                    classification = "fuzzy" if classification == "FUZZY" else "precise"
                elif line.startswith("Fuzzy Terms:"):
                    terms_text = line.split(":", 1)[1].strip()
                    if terms_text.lower() != "none":
                        fuzzy_terms = [
                            term.strip() for term in terms_text.split(",") if term.strip()
                        ]

            logger.info(
                "[FUZZY-CLASSIFIER] Fallback parsing successful",
                classification=classification,
                llm_fuzzy_terms=fuzzy_terms,
                agent_type="fuzzy_classifier",
            )

            return {"classification": classification, "fuzzy_terms": fuzzy_terms}

        except Exception as e:
            logger.error(
                "[FUZZY-CLASSIFIER] Fallback parsing failed",
                error=str(e),
                response_text=response_text[:200],
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
        query_lower = query.lower()

        # Precise patterns that should NOT be fuzzy
        precise_patterns = [
            # Project status queries
            r"\bworking on\s+(active|customer|internal|completed)\s+projects?\b",
            r"\bassigned to\s+projects?\b",
            r"\ballocated to\s+projects?\b",
            # Allocation queries (but not skill-based availability queries)
            r"\b(overallocated|underutilized)\s+employees?\b",
            r"\bavailable\s+employees?\s*$",  # Only pure availability queries without additional criteria
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

        # Extract fuzzy terms using shared method
        fuzzy_terms = self._extract_fuzzy_terms_from_patterns(query)
        classification = "fuzzy" if fuzzy_terms else "precise"

        return {"classification": classification, "fuzzy_terms": fuzzy_terms}

    def _extract_fuzzy_terms_from_patterns(self, query: str) -> List[str]:
        """Extract fuzzy terms from query using regex patterns.

        Args:
            query: User query to extract terms from

        Returns:
            List of fuzzy terms found in the query
        """
        fuzzy_terms = []
        query_lower = query.lower()

        # Fuzzy patterns for term extraction
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

        return fuzzy_terms

    def _extract_fuzzy_terms(self, query: str) -> List[str]:
        """Extract fuzzy terms from query without classification.

        Used when LLM has already classified the query as fuzzy.

        Args:
            query: User query to extract terms from

        Returns:
            List of fuzzy terms found in the query
        """
        return self._extract_fuzzy_terms_from_patterns(query)

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

    def _log_extraction_comparison(
        self,
        query: str,
        regex_fuzzy_terms: List[str],
        llm_fuzzy_terms: List[str],
        extraction_method: str,
    ):
        """Log the comparison between regex and LLM fuzzy terms.

        Args:
            query: User query to analyze
            regex_fuzzy_terms: List of fuzzy terms extracted by regex
            llm_fuzzy_terms: List of fuzzy terms extracted by LLM
            extraction_method: Method used for extraction
        """
        # Convert to sets for comparison (case-insensitive)
        regex_set = set(term.lower() for term in regex_fuzzy_terms)
        llm_set = set(term.lower() for term in llm_fuzzy_terms)

        # Calculate overlap and differences
        common_terms = regex_set.intersection(llm_set)
        regex_only = regex_set - llm_set
        llm_only = llm_set - regex_set

        # Calculate metrics
        total_unique_terms = len(regex_set.union(llm_set))
        overlap_percentage = (
            len(common_terms) / total_unique_terms if total_unique_terms > 0 else 0.0
        )

        # Determine scenario
        scenario = self._classify_extraction_scenario(regex_fuzzy_terms, llm_fuzzy_terms)

        logger.info(
            "[FUZZY-CLASSIFIER] Extraction comparison",
            query=query,
            regex_fuzzy_terms=regex_fuzzy_terms,
            llm_fuzzy_terms=llm_fuzzy_terms,
            extraction_method=extraction_method,
            scenario=scenario,
            common_terms=list(common_terms),
            regex_only=list(regex_only),
            llm_only=list(llm_only),
            overlap_percentage=round(overlap_percentage, 2),
            total_unique_terms=total_unique_terms,
            agent_type="fuzzy_classifier",
        )

    def _classify_extraction_scenario(self, regex_terms: List[str], llm_terms: List[str]) -> str:
        """Classify the extraction scenario for monitoring.

        Args:
            regex_terms: Terms found by regex
            llm_terms: Terms found by LLM

        Returns:
            Scenario classification string
        """
        regex_count = len(regex_terms)
        llm_count = len(llm_terms)

        if regex_count == 0 and llm_count == 0:
            return "both_empty"
        elif regex_count > 0 and llm_count == 0:
            return "regex_only"
        elif regex_count == 0 and llm_count > 0:
            return "llm_only"
        elif set(term.lower() for term in regex_terms) == set(term.lower() for term in llm_terms):
            return "perfect_match"
        elif set(term.lower() for term in regex_terms).issubset(
            set(term.lower() for term in llm_terms)
        ):
            return "regex_subset_of_llm"
        elif set(term.lower() for term in llm_terms).issubset(
            set(term.lower() for term in regex_terms)
        ):
            return "llm_subset_of_regex"
        else:
            return "partial_overlap"
