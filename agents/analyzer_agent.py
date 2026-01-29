from typing import Dict, Any
from .base_agent import BaseAgent
import datetime
import re
import json

class AnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Analyzer",
            instructions="""Analyze candidate profiles and extract:
            1. Technical skills (as a list)
            2. Years of experience (numeric)
            3. Education level
            4. Experience level (Junior/Mid-level/Senior)
            5. Key achievements
            6. Domain expertise
            
            Format the output as structured data.""",
        )
        # Common tech skills for fallback extraction
        self.common_skills = {
            "python", "javascript", "java", "c++", "c#", "typescript", "sql",
            "react", "angular", "vue", "nodejs", "express", "django", "flask",
            "aws", "azure", "gcp", "kubernetes", "docker", "git", "linux",
            "machine learning", "ml", "ai", "deep learning", "nlp", "computer vision",
            "data science", "analytics", "tableau", "power bi", "excel",
            "html", "css", "bootstrap", "tailwind", "sass",
            "mongodb", "postgresql", "mysql", "redis", "elasticsearch",
            "agile", "scrum", "kanban", "jira", "confluence",
            "rest api", "graphql", "microservices", "oop", "solid",
            "testing", "jest", "pytest", "selenium", "junit",
            "ci/cd", "jenkins", "gitlab", "github", "terraform",
            "communication", "leadership", "project management", "problem solving"
        }

    async def run(self, messages: list) -> Dict[str, Any]:
        """Analyze the extracted resume data"""
        print("🔍 Analyzer: Analyzing candidate profile")

        extracted_data = eval(messages[-1]["content"])

        # Improved LLM prompt with explicit formatting
        analysis_prompt = f"""
        Analyze this resume data and extract key information. 
        
        IMPORTANT: Return ONLY valid JSON, no explanations or markdown.
        
        Resume data:
        {extracted_data["structured_data"]}
        
        Return this exact JSON structure (use lowercase for skill names):
        {{
            "technical_skills": ["python", "javascript", "react"],
            "years_of_experience": 5,
            "education": {{
                "level": "Bachelors",
                "field": "Computer Science"
            }},
            "experience_level": "Mid-level",
            "key_achievements": ["achievement1", "achievement2"],
            "domain_expertise": ["domain1", "domain2"]
        }}
        """

        analysis_results = self._query_ollama(analysis_prompt)
        parsed_results = self._parse_json_safely(analysis_results)

        # FALLBACK: If LLM extraction failed or skills are empty, use regex
        if "error" in parsed_results or not parsed_results.get("technical_skills"):
            print("⚠️ LLM extraction incomplete, using regex fallback...")
            fallback_skills = self._extract_skills_regex(extracted_data["structured_data"])
            
            if parsed_results.get("error"):
                # Complete fallback if JSON parsing failed
                parsed_results = {
                    "technical_skills": fallback_skills,
                    "years_of_experience": 0,
                    "education": {"level": "Unknown", "field": "Unknown"},
                    "experience_level": "Mid-level",
                    "key_achievements": [],
                    "domain_expertise": [],
                }
            else:
                # Enhance existing result with regex extraction
                parsed_results["technical_skills"] = fallback_skills or parsed_results.get("technical_skills", [])

        # Ensure technical_skills is never empty if we can extract anything
        if not parsed_results.get("technical_skills"):
            parsed_results["technical_skills"] = self._extract_skills_regex(str(extracted_data))

        return {
            "skills_analysis": parsed_results,
            "analysis_timestamp": datetime.datetime.now().isoformat(),
            "confidence_score": 0.85 if "error" not in parsed_results else 0.5,
        }

    def _extract_skills_regex(self, text: str) -> list:
        """
        Fallback method to extract skills using regex and pattern matching.
        More reliable than LLM for structured skill lists.
        """
        text_lower = str(text).lower()
        found_skills = set()
        
        # Direct skill matching
        for skill in self.common_skills:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                # Normalize skill name
                normalized = skill.title() if " " not in skill else skill.replace(" ", " ").title()
                found_skills.add(normalized)
        
        # Try to extract skills from "Skills" section if exists
        skills_section = re.search(r'(?:skills?|competencies?|expertise|technical)[\s:]*([^\n]*(?:\n[^\n]*)*?)(?=\n\n|\Z)', 
                                   text_lower, re.IGNORECASE | re.MULTILINE)
        if skills_section:
            section_text = skills_section.group(1)
            # Split by common delimiters and check against known skills
            tokens = re.split(r'[,;/•\-\n]', section_text)
            for token in tokens:
                token_clean = token.strip().lower()
                if token_clean in self.common_skills:
                    found_skills.add(token_clean.title())
        
        # Return as sorted list
        return sorted(list(found_skills)) if found_skills else []

