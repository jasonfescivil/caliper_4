from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from loguru import logger


class ReviewCriteria:
    """Represents review criteria loaded from a file to guide the review process."""

    def __init__(self, criteria_data: Dict[str, Any]):
        self.criteria_data = criteria_data
        self.focus_areas = criteria_data.get("focus_areas", [])
        self.required_sections = criteria_data.get("required_sections", [])
        self.required_topics = criteria_data.get("required_topics", [])
        self.citation_requirements = criteria_data.get("citation_requirements", [])
        self.technical_requirements = criteria_data.get("technical_requirements", [])
        self.style_requirements = criteria_data.get("style_requirements", [])
        self.custom_patterns = criteria_data.get("custom_patterns", [])
        
    @classmethod
    def from_file(cls, path: Optional[Path]) -> 'ReviewCriteria':
        """Load review criteria from a file or return default criteria if path is None."""
        if path and path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                return cls(data)
            except Exception as e:
                logger.warning(f"Failed to load review criteria from {path}: {e}")
                return cls(cls._default_criteria())
        else:
            return cls(cls._default_criteria())
    
    @classmethod
    def from_markdown(cls, path: Optional[Path]) -> 'ReviewCriteria':
        """Parse review criteria from a markdown file with structured sections."""
        if not path or not path.exists():
            return cls(cls._default_criteria())
            
        try:
            content = path.read_text(encoding="utf-8")
            
            # Extract sections from markdown
            criteria = {
                "focus_areas": [],
                "required_sections": [],
                "required_topics": [],
                "citation_requirements": [],
                "technical_requirements": [],
                "style_requirements": [],
                "custom_patterns": []
            }
            
            # Parse focus areas
            focus_match = re.search(r'#+\s*Focus Areas\s*\n(.*?)(?=\n#+\s*|$)', content, re.DOTALL)
            if focus_match:
                focus_text = focus_match.group(1).strip()
                criteria["focus_areas"] = [item.strip()[2:].strip() for item in focus_text.split('\n') if item.strip().startswith('- ')]
            
            # Parse required sections
            sections_match = re.search(r'#+\s*Required Sections\s*\n(.*?)(?=\n#+\s*|$)', content, re.DOTALL)
            if sections_match:
                sections_text = sections_match.group(1).strip()
                criteria["required_sections"] = [item.strip()[2:].strip() for item in sections_text.split('\n') if item.strip().startswith('- ')]
            
            # Parse required topics
            topics_match = re.search(r'#+\s*Required Topics\s*\n(.*?)(?=\n#+\s*|$)', content, re.DOTALL)
            if topics_match:
                topics_text = topics_match.group(1).strip()
                criteria["required_topics"] = [item.strip()[2:].strip() for item in topics_text.split('\n') if item.strip().startswith('- ')]
            
            # Parse citation requirements
            citations_match = re.search(r'#+\s*Citation Requirements\s*\n(.*?)(?=\n#+\s*|$)', content, re.DOTALL)
            if citations_match:
                citations_text = citations_match.group(1).strip()
                criteria["citation_requirements"] = [item.strip()[2:].strip() for item in citations_text.split('\n') if item.strip().startswith('- ')]
            
            # Parse technical requirements
            tech_match = re.search(r'#+\s*Technical Requirements\s*\n(.*?)(?=\n#+\s*|$)', content, re.DOTALL)
            if tech_match:
                tech_text = tech_match.group(1).strip()
                criteria["technical_requirements"] = [item.strip()[2:].strip() for item in tech_text.split('\n') if item.strip().startswith('- ')]
            
            # Parse style requirements
            style_match = re.search(r'#+\s*Style Requirements\s*\n(.*?)(?=\n#+\s*|$)', content, re.DOTALL)
            if style_match:
                style_text = style_match.group(1).strip()
                criteria["style_requirements"] = [item.strip()[2:].strip() for item in style_text.split('\n') if item.strip().startswith('- ')]
            
            # Parse custom patterns
            patterns_match = re.search(r'#+\s*Custom Patterns\s*\n(.*?)(?=\n#+\s*|$)', content, re.DOTALL)
            if patterns_match:
                patterns_text = patterns_match.group(1).strip()
                pattern_items = []
                for item in patterns_text.split('\n'):
                    if item.strip().startswith('- '):
                        pattern_item = item.strip()[2:].strip()
                        pattern_parts = pattern_item.split(':', 1)
                        if len(pattern_parts) == 2:
                            pattern_items.append({
                                "name": pattern_parts[0].strip(),
                                "pattern": pattern_parts[1].strip()
                            })
                criteria["custom_patterns"] = pattern_items
            
            return cls(criteria)
        except Exception as e:
            logger.warning(f"Failed to parse review criteria from markdown {path}: {e}")
            return cls(cls._default_criteria())
    
    @staticmethod
    def _default_criteria() -> Dict[str, Any]:
        """Return default review criteria."""
        return {
            "focus_areas": [
                "Accuracy of technical information",
                "Completeness of required sections",
                "Proper citation of sources",
                "Consistency with regulatory requirements"
            ],
            "required_sections": [
                "Introduction/Background",
                "Methodology",
                "Results",
                "Discussion",
                "Conclusion"
            ],
            "required_topics": [
                "Current conditions",
                "Regulatory framework",
                "Technical analysis",
                "Recommendations"
            ],
            "citation_requirements": [
                "All factual claims must be supported by evidence",
                "Citations should include specific page numbers when available",
                "Primary sources should be preferred over secondary sources"
            ],
            "technical_requirements": [
                "All calculations must be shown or referenced",
                "Units must be consistent throughout the document",
                "Assumptions must be clearly stated"
            ],
            "style_requirements": [
                "Use consistent terminology throughout",
                "Define all acronyms on first use",
                "Use active voice where appropriate"
            ],
            "custom_patterns": [
                {"name": "design_period", "pattern": r"design period|planning horizon|20[- ]year"},
                {"name": "flows_link", "pattern": r"Q\s*avg|ADWF|Q\s*max|peaking factor|Q\s*min"}
            ]
        }
    
    def check_section_coverage(self, text: str) -> List[Dict[str, Any]]:
        """Check if all required sections are present in the text."""
        issues = []
        
        # Extract headings to check for section presence
        headings = re.findall(r'^#+\s+(.+)$', text, re.MULTILINE)
        heading_text = " ".join(headings).lower()
        
        for section in self.required_sections:
            # Try multiple approaches to detect section presence
            section_lower = section.lower()
            
            # Check for exact heading match
            if any(section_lower in h.lower() for h in headings):
                continue
                
            # Check for section name in text with word boundaries
            pattern = re.compile(rf"\b{re.escape(section)}\b", re.IGNORECASE)
            if pattern.search(text):
                continue
                
            # Check for section name with flexible matching (allow partial matches in headings)
            # This helps with variations like "Executive Summary" vs "Summary"
            words = section_lower.split()
            if len(words) > 1 and any(all(w in h.lower() for w in words) for h in headings):
                continue
                
            # If we get here, the section is likely missing
            issues.append({
                "id": f"SECTION-{section.replace(' ', '_')}",
                "severity": "high",
                "kind": "missing_section",
                "message": f"Required section '{section}' appears to be missing",
                "suggestion": f"Add a section covering '{section}' to comply with WAC 173-240-060 requirements",
                "where": None
            })
        return issues
    
    def check_topic_coverage(self, text: str) -> List[Dict[str, Any]]:
        """Check if all required topics are covered in the text."""
        issues = []
        
        for topic in self.required_topics:
            topic_lower = topic.lower()
            words = topic_lower.split()
            
            # For multi-word topics, check if all words appear within a reasonable proximity
            if len(words) > 1:
                # Check if all words appear within a 100-character window
                found = False
                for i in range(len(text) - 100):
                    window = text[i:i+100].lower()
                    if all(w in window for w in words):
                        found = True
                        break
                        
                if found:
                    continue
            
            # Fall back to simple pattern matching
            pattern = re.compile(rf"\b{re.escape(topic)}\b", re.IGNORECASE)
            if pattern.search(text):
                continue
                
            # Topic is missing
            issues.append({
                "id": f"TOPIC-{topic.replace(' ', '_')}",
                "severity": "medium",
                "kind": "missing_topic",
                "message": f"Required topic '{topic}' appears to be missing or inadequately covered",
                "suggestion": f"Ensure the document addresses '{topic}' as required by WAC 173-240-060",
                "where": None
            })
        return issues
    
    def check_custom_patterns(self, text: str) -> List[Dict[str, Any]]:
        """Check for custom patterns specified in the criteria."""
        issues = []
        for i, pattern_def in enumerate(self.custom_patterns):
            name = pattern_def.get("name", f"pattern_{i}")
            pattern_str = pattern_def.get("pattern", "")
            required = pattern_def.get("required", True)
            severity = pattern_def.get("severity", "medium")
            
            if not pattern_str:
                continue
                
            try:
                pattern = re.compile(pattern_str, re.IGNORECASE)
                if required and not pattern.search(text):
                    issues.append({
                        "id": f"PATTERN-{name}",
                        "severity": severity,
                        "kind": "missing_pattern",
                        "message": f"Required content matching '{name}' pattern is missing",
                        "suggestion": f"Add content that addresses the '{name}' requirement",
                        "where": None
                    })
            except re.error:
                logger.warning(f"Invalid regex pattern '{pattern_str}' for '{name}'")
        
        return issues
    
    def check_technical_requirements(self, text: str) -> List[Dict[str, Any]]:
        """Check technical requirements based on criteria."""
        issues = []
        
        # Check for unit consistency
        units = re.findall(r'\b(\d+(?:\.\d+)?)\s*([a-zA-Z]+)\b', text)
        unit_counts = {}
        for _, unit in units:
            unit_counts[unit.lower()] = unit_counts.get(unit.lower(), 0) + 1
        
        # Check for common unit inconsistencies
        unit_groups = [
            ['mgd', 'gpd', 'gpm'],  # Flow units
            ['mg/l', 'ppm', 'ug/l', 'ng/l'],  # Concentration units
            ['ft', 'm', 'in', 'cm']  # Length units
        ]
        
        for group in unit_groups:
            used_units = [u for u in group if unit_counts.get(u, 0) > 0]
            if len(used_units) > 1:
                issues.append({
                    "id": f"UNITS-{'-'.join(used_units)}",
                    "severity": "medium",
                    "kind": "unit_inconsistency",
                    "message": f"Multiple units from the same category used: {', '.join(used_units)}",
                    "suggestion": "Standardize units or provide clear conversions",
                    "where": None
                })
        
        return issues
    
    def generate_llm_prompt(self) -> str:
        """Generate a prompt for LLM-based review based on the criteria."""
        prompt_parts = [
            "Review the document based on the following criteria:",
            "\nFocus Areas:",
        ]
        
        for area in self.focus_areas:
            prompt_parts.append(f"- {area}")
        
        if self.required_sections:
            prompt_parts.append("\nRequired Sections:")
            for section in self.required_sections:
                prompt_parts.append(f"- {section}")
        
        if self.required_topics:
            prompt_parts.append("\nRequired Topics:")
            for topic in self.required_topics:
                prompt_parts.append(f"- {topic}")
        
        if self.citation_requirements:
            prompt_parts.append("\nCitation Requirements:")
            for req in self.citation_requirements:
                prompt_parts.append(f"- {req}")
        
        if self.technical_requirements:
            prompt_parts.append("\nTechnical Requirements:")
            for req in self.technical_requirements:
                prompt_parts.append(f"- {req}")
        
        if self.style_requirements:
            prompt_parts.append("\nStyle Requirements:")
            for req in self.style_requirements:
                prompt_parts.append(f"- {req}")
        
        prompt_parts.append("\nProvide a detailed review that addresses each of these criteria. For each issue found, indicate the severity (high, medium, low), describe the issue, and suggest how to fix it.")
        
        return "\n".join(prompt_parts)


def analyze_with_criteria(text: str, criteria: ReviewCriteria) -> List[Dict[str, Any]]:
    """Analyze text using the provided review criteria."""
    issues = []
    
    # Check for required sections
    issues.extend(criteria.check_section_coverage(text))
    
    # Check for required topics
    issues.extend(criteria.check_topic_coverage(text))
    
    # Check for custom patterns
    issues.extend(criteria.check_custom_patterns(text))
    
    # Check technical requirements
    issues.extend(criteria.check_technical_requirements(text))
    
    return issues


def llm_review_with_criteria(text: str, criteria: ReviewCriteria, outline_text: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Use LLM to review text based on criteria and optional outline.
    
    Args:
        text: The document text to review
        criteria: The review criteria to apply
        outline_text: Optional outline text to use as additional guidance
        
    Returns:
        Dictionary with review results or None if LLM is not available
    """
    try:
        from llama_index.core import Settings as _Settings  # type: ignore
    except Exception:
        return None
    
    llm = getattr(_Settings, "llm", None)
    if llm is None:
        return None
    
    # Process document in chunks to handle longer documents
    # First, extract document structure to help the LLM understand the overall organization
    import re
    
    # Extract headings to understand document structure
    headings = re.findall(r'^#+\s+(.+)$', text, re.MULTILINE)
    doc_structure = "\n".join([f"- {h}" for h in headings[:30]])  # Limit to first 30 headings
    
    # Extract document metadata if available
    title_match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    doc_title = title_match.group(1) if title_match else "Untitled Document"
    
    # Process outline if provided
    outline_section = ""
    if outline_text:
        # Extract the most relevant parts of the outline
        # Look for section descriptions and requirements
        outline_section = f"""
DOCUMENT OUTLINE GUIDANCE:
The following outline provides additional guidance for what should be included in this document:

{outline_text[:2000]}...
"""
    
    # Create a more structured prompt for better LLM review
    prompt = f"""You are an expert document reviewer specializing in wastewater facility plans and engineering documents.
Your task is to thoroughly review the provided document based on specific criteria and provide detailed, actionable feedback.

DOCUMENT TITLE: {doc_title}

DOCUMENT STRUCTURE OVERVIEW:
{doc_structure}

REVIEW CRITERIA:
{criteria.generate_llm_prompt()}
{outline_section}

REVIEW INSTRUCTIONS:
1. Focus on substantive content issues rather than minor formatting or style issues
2. Prioritize regulatory compliance and technical accuracy in your assessment
3. Identify missing required sections or topics as high-priority issues
4. Evaluate whether the document meets the specific requirements in WAC 173-240-060
5. Consider both the presence of required content and the quality/adequacy of that content
6. Check if the document follows the structure and requirements outlined in the guidance (if provided)

Please structure your response in the following JSON format:
{{
  "review": "A comprehensive review of the document addressing each criterion area",
  "issues": [
    {{
      "id": "ISSUE-1",
      "severity": "high|medium|low",
      "kind": "missing_section|missing_topic|technical_issue|regulatory_compliance|clarity|organization",
      "message": "Clear description of the issue",
      "suggestion": "Specific recommendation to address the issue",
      "location": "Section or page reference if applicable"
    }}
  ],
  "summary": {{
    "overall_assessment": "Brief overall assessment of the document quality",
    "strengths": ["Strength 1", "Strength 2", "Strength 3"],
    "key_weaknesses": ["Weakness 1", "Weakness 2", "Weakness 3"],
    "compliance_status": "Assessment of regulatory compliance with WAC 173-240-060"
  }}
}}

Document to review (first 12000 characters):

{text[:12000]}...

If the document is longer than what's shown, please focus on evaluating what you can see while noting that a complete review would require examining the full document.
"""
    
    try:
        # Try to get a structured JSON response
        if hasattr(llm, "complete_json"):
            resp = llm.complete_json(prompt)  # type: ignore
            raw = getattr(resp, "text", getattr(resp, "json", "{}"))
        else:
            # For LLMs without direct JSON support
            json_prompt = prompt + "\n\nRespond ONLY with valid JSON."
            resp = llm.complete(json_prompt)
            raw = getattr(resp, "text", str(resp))
        
        # Try to parse as JSON, but handle free-text response too
        try:
            # Clean the response to handle potential formatting issues
            cleaned_raw = raw.strip()
            # Remove markdown code block markers if present
            if cleaned_raw.startswith("```json"):
                cleaned_raw = cleaned_raw[7:]
            if cleaned_raw.startswith("```"):
                cleaned_raw = cleaned_raw[3:]
            if cleaned_raw.endswith("```"):
                cleaned_raw = cleaned_raw[:-3]
            
            data = json.loads(cleaned_raw.strip())
            if isinstance(data, dict):
                # Ensure the response has the expected structure
                if "review" not in data:
                    data["review"] = "Review analysis not provided in structured format."
                if "issues" not in data or not isinstance(data["issues"], list):
                    data["issues"] = []
                if "summary" not in data or not isinstance(data["summary"], dict):
                    data["summary"] = {"overall_assessment": "Assessment not provided in structured format."}
                return data
        except json.JSONDecodeError:
            # If not JSON, structure the text response
            logger.warning("LLM did not return valid JSON, using raw text")
            # Extract an overall assessment if possible
            assessment_match = re.search(r"overall\s+assessment:?\s*([^\n.]+)[.\n]", raw, re.IGNORECASE)
            overall = assessment_match.group(1).strip() if assessment_match else "See review text"
            
            return {
                "review": raw,
                "issues": [],
                "summary": {
                    "overall_assessment": overall,
                    "strengths": [],
                    "key_weaknesses": []
                }
            }
    except Exception as e:
        logger.warning(f"LLM review failed: {e}")
        return None