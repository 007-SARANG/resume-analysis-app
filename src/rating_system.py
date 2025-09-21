"""
Resume Rating System
Provides comprehensive scoring of resumes based on multiple criteria.
"""

from typing import Dict, Any, List
import math

class ResumeRatingSystem:
    """
    Comprehensive resume rating system that evaluates resumes on multiple dimensions
    and provides a score out of 10.
    """
    
    def __init__(self):
        # Scoring weights for different aspects
        self.weights = {
            'skills_diversity': 0.20,    # 20% - Variety of skills
            'skills_quantity': 0.15,     # 15% - Number of skills
            'contact_completeness': 0.10, # 10% - Contact information
            'sections_completeness': 0.15, # 15% - Resume sections
            'readability': 0.15,         # 15% - Text readability
            'project_quality': 0.15,     # 15% - Project descriptions
            'content_length': 0.10       # 10% - Appropriate length
        }
        
        # Ideal ranges and thresholds
        self.thresholds = {
            'min_skills': 5,
            'ideal_skills': 15,
            'min_word_count': 150,
            'ideal_word_count': 400,
            'max_word_count': 800,
            'min_projects': 1,
            'ideal_projects': 3,
            'ideal_sentence_length': 15,
            'max_sentence_length': 25
        }
    
    def score_skills_diversity(self, skills: Dict[str, List[str]]) -> float:
        """
        Score based on diversity of skill categories.
        More categories = better score.
        """
        if not skills:
            return 0.0
        
        # Number of different skill categories
        categories = len(skills.keys())
        
        # Ideal is 4-6 categories (programming, web, database, tools, soft skills, etc.)
        if categories >= 5:
            return 10.0
        elif categories >= 3:
            return 7.0 + (categories - 3) * 1.5
        elif categories >= 1:
            return 4.0 + (categories - 1) * 1.5
        else:
            return 0.0
    
    def score_skills_quantity(self, skills: Dict[str, List[str]]) -> float:
        """
        Score based on total number of skills mentioned.
        """
        if not skills:
            return 0.0
        
        total_skills = sum(len(skill_list) for skill_list in skills.values())
        
        if total_skills >= self.thresholds['ideal_skills']:
            return 10.0
        elif total_skills >= self.thresholds['min_skills']:
            # Linear interpolation between min and ideal
            progress = (total_skills - self.thresholds['min_skills']) / \
                      (self.thresholds['ideal_skills'] - self.thresholds['min_skills'])
            return 5.0 + (progress * 5.0)
        else:
            # Below minimum
            return (total_skills / self.thresholds['min_skills']) * 5.0
    
    def score_contact_completeness(self, contact_info: Dict[str, str]) -> float:
        """
        Score based on completeness of contact information.
        """
        if not contact_info:
            return 0.0
        
        # Essential contact fields
        essential_fields = ['email', 'phone']
        bonus_fields = ['linkedin', 'github']
        
        score = 0.0
        
        # Essential fields (7 points total)
        for field in essential_fields:
            if field in contact_info:
                score += 3.5
        
        # Bonus fields (3 points total)
        for field in bonus_fields:
            if field in contact_info:
                score += 1.5
        
        return min(score, 10.0)
    
    def score_sections_completeness(self, sections: Dict[str, bool]) -> float:
        """
        Score based on presence of important resume sections.
        """
        if not sections:
            return 0.0
        
        # Essential sections
        essential = ['experience', 'education', 'skills']
        # Important sections  
        important = ['summary', 'projects']
        # Nice to have
        bonus = ['certifications', 'achievements']
        
        score = 0.0
        
        # Essential sections (6 points)
        for section in essential:
            if sections.get(section, False):
                score += 2.0
        
        # Important sections (3 points)
        for section in important:
            if sections.get(section, False):
                score += 1.5
        
        # Bonus sections (1 point)
        for section in bonus:
            if sections.get(section, False):
                score += 0.5
        
        return min(score, 10.0)
    
    def score_readability(self, readability_metrics: Dict[str, float]) -> float:
        """
        Score based on text readability metrics.
        """
        if not readability_metrics:
            return 5.0  # Neutral score if no metrics
        
        sentence_length = readability_metrics.get('avg_sentence_length', 20)
        complexity_ratio = readability_metrics.get('complexity_ratio', 0.3)
        
        # Score sentence length (0-5 points)
        if sentence_length <= self.thresholds['ideal_sentence_length']:
            length_score = 5.0
        elif sentence_length <= self.thresholds['max_sentence_length']:
            # Penalty for longer sentences
            excess = sentence_length - self.thresholds['ideal_sentence_length']
            max_excess = self.thresholds['max_sentence_length'] - self.thresholds['ideal_sentence_length']
            length_score = 5.0 - (excess / max_excess) * 2.0
        else:
            length_score = 3.0  # Heavily penalize very long sentences
        
        # Score complexity (0-5 points)
        # Ideal complexity ratio is 0.2-0.4 (20-40% complex words)
        if 0.2 <= complexity_ratio <= 0.4:
            complexity_score = 5.0
        elif complexity_ratio < 0.2:
            # Too simple
            complexity_score = 3.0 + (complexity_ratio / 0.2) * 2.0
        else:
            # Too complex
            complexity_score = 5.0 - ((complexity_ratio - 0.4) / 0.3) * 2.0
        
        return max(0, min(length_score + complexity_score, 10.0))
    
    def score_project_quality(self, projects: List[str]) -> float:
        """
        Score based on project descriptions quality and quantity.
        """
        if not projects:
            return 0.0
        
        num_projects = len(projects)
        
        # Base score for having projects
        if num_projects >= self.thresholds['ideal_projects']:
            quantity_score = 5.0
        elif num_projects >= self.thresholds['min_projects']:
            quantity_score = 3.0 + ((num_projects - 1) / 2) * 2.0
        else:
            quantity_score = 0.0
        
        # Quality score based on project description length and content
        quality_score = 0.0
        for project in projects[:3]:  # Evaluate top 3 projects
            words = len(project.split())
            if words >= 15:  # Substantial description
                quality_score += 1.67
            elif words >= 8:  # Decent description
                quality_score += 1.0
            else:  # Too brief
                quality_score += 0.5
        
        return min(quantity_score + quality_score, 10.0)
    
    def score_content_length(self, word_count: int) -> float:
        """
        Score based on appropriate resume length.
        """
        if word_count < self.thresholds['min_word_count']:
            # Too short
            return (word_count / self.thresholds['min_word_count']) * 4.0
        elif word_count <= self.thresholds['ideal_word_count']:
            # Ideal range
            return 7.0 + ((word_count - self.thresholds['min_word_count']) / 
                         (self.thresholds['ideal_word_count'] - self.thresholds['min_word_count'])) * 3.0
        elif word_count <= self.thresholds['max_word_count']:
            # Acceptable but getting long
            excess = word_count - self.thresholds['ideal_word_count']
            max_excess = self.thresholds['max_word_count'] - self.thresholds['ideal_word_count']
            return 10.0 - (excess / max_excess) * 3.0
        else:
            # Too long
            return 5.0
    
    def calculate_overall_score(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate overall resume score based on all criteria.
        """
        if 'error' in analysis_result:
            return {
                'overall_score': 0.0,
                'detailed_scores': {},
                'error': analysis_result['error']
            }
        
        # Extract data from analysis
        skills = analysis_result.get('skills', {})
        contact_info = analysis_result.get('contact_info', {})
        sections = analysis_result.get('sections', {})
        readability = analysis_result.get('readability', {})
        projects = analysis_result.get('projects', [])
        word_count = readability.get('word_count', 0)
        
        # Calculate individual scores
        detailed_scores = {
            'skills_diversity': self.score_skills_diversity(skills),
            'skills_quantity': self.score_skills_quantity(skills),
            'contact_completeness': self.score_contact_completeness(contact_info),
            'sections_completeness': self.score_sections_completeness(sections),
            'readability': self.score_readability(readability),
            'project_quality': self.score_project_quality(projects),
            'content_length': self.score_content_length(word_count)
        }
        
        # Calculate weighted overall score
        overall_score = sum(
            score * self.weights[criterion] 
            for criterion, score in detailed_scores.items()
        )
        
        # Round to 1 decimal place
        overall_score = round(overall_score, 1)
        
        # Generate rating category
        if overall_score >= 8.5:
            rating_category = "Excellent"
            rating_description = "Outstanding resume with strong impact potential"
        elif overall_score >= 7.0:
            rating_category = "Good"
            rating_description = "Solid resume with room for minor improvements"
        elif overall_score >= 5.5:
            rating_category = "Average"
            rating_description = "Decent resume but needs significant improvements"
        elif overall_score >= 3.0:
            rating_category = "Below Average"
            rating_description = "Resume needs major improvements to be competitive"
        else:
            rating_category = "Poor"
            rating_description = "Resume requires complete overhaul"
        
        return {
            'overall_score': overall_score,
            'rating_category': rating_category,
            'rating_description': rating_description,
            'detailed_scores': {k: round(v, 1) for k, v in detailed_scores.items()},
            'score_breakdown': self._generate_score_breakdown(detailed_scores),
            'improvement_priority': self._identify_improvement_priorities(detailed_scores)
        }
    
    def _generate_score_breakdown(self, detailed_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Generate a breakdown of scores with explanations.
        """
        breakdown = []
        
        explanations = {
            'skills_diversity': "Variety of skill categories (technical, soft skills, tools)",
            'skills_quantity': "Total number of skills mentioned throughout resume",
            'contact_completeness': "Presence of email, phone, LinkedIn, GitHub",
            'sections_completeness': "Essential sections: experience, education, skills, projects",
            'readability': "Text clarity, sentence length, and complexity",
            'project_quality': "Number and quality of project descriptions",
            'content_length': "Appropriate resume length (not too short or long)"
        }
        
        for criterion, score in detailed_scores.items():
            breakdown.append({
                'criterion': criterion.replace('_', ' ').title(),
                'score': score,
                'weight': self.weights[criterion] * 100,  # Convert to percentage
                'explanation': explanations[criterion],
                'contribution': round(score * self.weights[criterion], 1)
            })
        
        # Sort by contribution to overall score
        breakdown.sort(key=lambda x: x['contribution'], reverse=True)
        
        return breakdown
    
    def _identify_improvement_priorities(self, detailed_scores: Dict[str, float]) -> List[str]:
        """
        Identify the top areas for improvement based on lowest scores.
        """
        # Sort criteria by score (lowest first)
        sorted_scores = sorted(detailed_scores.items(), key=lambda x: x[1])
        
        priorities = []
        for criterion, score in sorted_scores[:3]:  # Top 3 lowest scores
            if score < 7.0:  # Only include scores that need improvement
                priorities.append(criterion.replace('_', ' ').title())
        
        return priorities

# Convenience function for easy import
def rate_resume(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple function to rate a resume analysis and return comprehensive scoring.
    """
    rating_system = ResumeRatingSystem()
    return rating_system.calculate_overall_score(analysis_result)