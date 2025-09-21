"""
Text Analyzer Module
Performs NLP analysis on resume text to extract skills, keywords, and insights.
"""

import json
import re
import os
from typing import List, Dict, Set, Any, Tuple
from collections import Counter
import nltk
from textblob import TextBlob
import pandas as pd

# Download required NLTK data if not present
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt', quiet=True)
    except:
        pass

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    try:
        nltk.download('punkt_tab', quiet=True)
    except:
        pass

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    try:
        nltk.download('stopwords', quiet=True)
    except:
        pass

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    try:
        nltk.download('averaged_perceptron_tagger', quiet=True)
    except:
        pass

try:
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')
except LookupError:
    try:
        nltk.download('averaged_perceptron_tagger_eng', quiet=True)
    except:
        pass

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag

class TextAnalyzer:
    """
    Comprehensive text analysis for resume content.
    Extracts skills, keywords, projects, and provides insights.
    """
    
    def __init__(self, skills_db_path: str = None, keywords_db_path: str = None):
        # Set default paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(os.path.dirname(current_dir), 'data')
        
        self.skills_db_path = skills_db_path or os.path.join(data_dir, 'skills_database.json')
        self.keywords_db_path = keywords_db_path or os.path.join(data_dir, 'job_keywords.json')
        
        # Load databases
        self.skills_database = self._load_skills_database()
        self.job_keywords = self._load_job_keywords()
        
        # Initialize stopwords
        self.stop_words = set(stopwords.words('english'))
        
        # Common resume sections (for section detection)
        self.resume_sections = {
            'contact': ['contact', 'email', 'phone', 'address', 'linkedin'],
            'summary': ['summary', 'profile', 'objective', 'about'],
            'experience': ['experience', 'work', 'employment', 'career', 'professional'],
            'education': ['education', 'degree', 'university', 'college', 'school'],
            'skills': ['skills', 'technical', 'technologies', 'competencies'],
            'projects': ['projects', 'portfolio', 'work samples'],
            'certifications': ['certifications', 'certificates', 'licensed'],
            'achievements': ['achievements', 'awards', 'honors', 'accomplishments']
        }
    
    def _load_skills_database(self) -> Dict:
        """Load the skills database from JSON file."""
        try:
            with open(self.skills_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Skills database not found at {self.skills_db_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Invalid JSON in skills database: {self.skills_db_path}")
            return {}
    
    def _load_job_keywords(self) -> Dict:
        """Load job-specific keywords from JSON file."""
        try:
            with open(self.keywords_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Keywords database not found at {self.keywords_db_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Invalid JSON in keywords database: {self.keywords_db_path}")
            return {}
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """
        Extract technical and soft skills from resume text.
        """
        text_lower = text.lower()
        found_skills = {}
        
        for category, skills_list in self.skills_database.items():
            found_skills[category] = []
            
            for skill in skills_list:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills[category].append(skill)
        
        # Remove empty categories
        found_skills = {k: v for k, v in found_skills.items() if v}
        
        return found_skills
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract important keywords using NLP techniques.
        """
        # Tokenize and remove stopwords
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords and non-alphabetic tokens
        filtered_tokens = [
            token for token in tokens 
            if token.isalpha() and token not in self.stop_words and len(token) > 2
        ]
        
        # Get POS tags and extract nouns and adjectives
        try:
            pos_tags = pos_tag(filtered_tokens)
            keywords = [
                word for word, pos in pos_tags 
                if pos.startswith('NN') or pos.startswith('JJ')  # Nouns and adjectives
            ]
        except LookupError:
            # Fallback: just use the filtered tokens without POS tagging
            keywords = filtered_tokens
        
        # Count frequency and return top keywords
        keyword_freq = Counter(keywords)
        top_keywords = [word for word, count in keyword_freq.most_common(20)]
        
        return top_keywords
    
    def detect_projects(self, text: str) -> List[str]:
        """
        Detect project descriptions in resume text.
        """
        projects = []
        
        # Split into sentences
        sentences = sent_tokenize(text)
        
        # Look for project indicators
        project_indicators = [
            'developed', 'built', 'created', 'designed', 'implemented',
            'project', 'application', 'system', 'website', 'app'
        ]
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check if sentence contains project indicators
            if any(indicator in sentence_lower for indicator in project_indicators):
                # Check if it's substantial (not just a skill mention)
                if len(sentence.split()) > 8:  # At least 8 words
                    projects.append(sentence.strip())
        
        return projects[:5]  # Return top 5 project descriptions
    
    def analyze_contact_info(self, text: str) -> Dict[str, str]:
        """
        Extract contact information from resume.
        """
        contact_info = {}
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Phone pattern (various formats)
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phone'] = ''.join(phones[0]) if isinstance(phones[0], tuple) else phones[0]
        
        # LinkedIn pattern
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin = re.findall(linkedin_pattern, text.lower())
        if linkedin:
            contact_info['linkedin'] = linkedin[0]
        
        # GitHub pattern
        github_pattern = r'github\.com/[\w-]+'
        github = re.findall(github_pattern, text.lower())
        if github:
            contact_info['github'] = github[0]
        
        return contact_info
    
    def detect_sections(self, text: str) -> Dict[str, bool]:
        """
        Detect which resume sections are present.
        """
        text_lower = text.lower()
        sections_found = {}
        
        for section_name, keywords in self.resume_sections.items():
            sections_found[section_name] = any(
                keyword in text_lower for keyword in keywords
            )
        
        return sections_found
    
    def calculate_readability(self, text: str) -> Dict[str, float]:
        """
        Calculate readability metrics for the resume.
        """
        blob = TextBlob(text)
        
        # Basic metrics
        sentences = len(blob.sentences)
        words = len(blob.words)
        
        if sentences == 0 or words == 0:
            return {'readability_score': 0, 'avg_sentence_length': 0, 'word_count': words}
        
        # Average sentence length
        avg_sentence_length = words / sentences
        
        # Simple readability score (lower is better for resumes)
        # Based on average sentence length and word complexity
        complex_words = len([word for word in blob.words if len(word) > 6])
        complexity_ratio = complex_words / words if words > 0 else 0
        
        # Readability score (1-10, higher is better)
        readability_score = max(1, 10 - (avg_sentence_length / 3) - (complexity_ratio * 5))
        
        return {
            'readability_score': round(readability_score, 2),
            'avg_sentence_length': round(avg_sentence_length, 2),
            'word_count': words,
            'sentence_count': sentences,
            'complexity_ratio': round(complexity_ratio, 2)
        }
    
    def analyze_resume(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive resume analysis combining all methods.
        """
        if not text or not text.strip():
            return {
                'error': 'No text provided for analysis',
                'skills': {},
                'keywords': [],
                'projects': [],
                'contact_info': {},
                'sections': {},
                'readability': {}
            }
        
        # Perform all analyses
        skills = self.extract_skills(text)
        keywords = self.extract_keywords(text)
        projects = self.detect_projects(text)
        contact_info = self.analyze_contact_info(text)
        sections = self.detect_sections(text)
        readability = self.calculate_readability(text)
        
        # Calculate summary statistics
        total_skills = sum(len(skill_list) for skill_list in skills.values())
        skills_diversity = len(skills.keys())
        
        return {
            'skills': skills,
            'keywords': keywords,
            'projects': projects,
            'contact_info': contact_info,
            'sections': sections,
            'readability': readability,
            'summary_stats': {
                'total_skills_found': total_skills,
                'skills_categories': skills_diversity,
                'projects_found': len(projects),
                'sections_present': sum(sections.values()),
                'has_contact_info': len(contact_info) > 0
            }
        }
    
    def compare_with_job(self, resume_analysis: Dict, job_title: str) -> Dict[str, Any]:
        """
        Compare resume analysis with job-specific requirements.
        """
        if job_title.lower() not in self.job_keywords:
            return {
                'error': f'Job title "{job_title}" not found in database',
                'missing_keywords': [],
                'match_score': 0
            }
        
        required_keywords = self.job_keywords[job_title.lower()]
        resume_text = ' '.join(resume_analysis.get('keywords', []))
        
        # Find missing keywords
        missing_keywords = []
        matched_keywords = []
        
        for keyword in required_keywords:
            if keyword.lower() in resume_text.lower():
                matched_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        # Calculate match score
        match_score = len(matched_keywords) / len(required_keywords) * 100 if required_keywords else 0
        
        return {
            'required_keywords': required_keywords,
            'matched_keywords': matched_keywords,
            'missing_keywords': missing_keywords,
            'match_score': round(match_score, 2),
            'recommendations': [
                f"Add '{keyword}' to relevant sections" for keyword in missing_keywords[:5]
            ]
        }

# Convenience function for easy import
def analyze_resume_text(text: str) -> Dict[str, Any]:
    """
    Simple function to analyze resume text and return comprehensive analysis.
    """
    analyzer = TextAnalyzer()
    return analyzer.analyze_resume(text)