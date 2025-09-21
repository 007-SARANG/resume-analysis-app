"""
Professional Summary Generator
Creates compelling 2-line professional summaries based on resume analysis.
"""

from typing import Dict, Any, List, Optional
import re
import random

class SummaryGenerator:
    """
    Generates professional summaries by analyzing resume content
    and creating compelling, personalized summaries.
    """
    
    def __init__(self):
        # Professional summary templates
        self.templates = {
            'experienced': [
                "{experience} {role} with {years} of experience in {skills}. {achievement} and expertise in {specializations}.",
                "{expertise} {role} specializing in {skills} with {years} of proven experience. {achievement} and strong background in {specializations}.",
                "Results-driven {role} with {years} of experience in {skills}. {achievement} and demonstrated expertise in {specializations}."
            ],
            'entry_level': [
                "Recent {education} graduate with strong foundation in {skills}. {projects} and eager to contribute to {field} initiatives.",
                "Motivated {education} professional with expertise in {skills}. {projects} and passionate about {field} innovation.",
                "Dedicated {education} graduate specializing in {skills}. {projects} and committed to delivering high-quality {field} solutions."
            ],
            'career_change': [
                "Versatile professional transitioning to {new_field} with transferable skills in {skills}. {experience} and strong foundation in {specializations}.",
                "Dynamic professional pivoting to {new_field} with proven experience in {skills}. {achievement} and adaptable approach to {specializations}.",
                "Results-oriented professional expanding into {new_field} with expertise in {skills}. {experience} and commitment to {specializations}."
            ]
        }
        
        # Role determination keywords
        self.role_keywords = {
            'Software Engineer': ['programming', 'coding', 'software', 'development', 'engineer'],
            'Data Scientist': ['data', 'analytics', 'machine learning', 'statistics', 'science'],
            'Product Manager': ['product', 'management', 'strategy', 'roadmap', 'stakeholder'],
            'Marketing Manager': ['marketing', 'digital', 'campaign', 'brand', 'advertising'],
            'Business Analyst': ['business', 'analysis', 'requirements', 'process', 'analyst'],
            'DevOps Engineer': ['devops', 'infrastructure', 'cloud', 'automation', 'deployment'],
            'UI/UX Designer': ['design', 'user experience', 'interface', 'wireframe', 'prototype'],
            'Project Manager': ['project', 'management', 'agile', 'scrum', 'coordination'],
            'Full Stack Developer': ['fullstack', 'frontend', 'backend', 'web development'],
            'Mobile Developer': ['mobile', 'android', 'ios', 'app development'],
            'Cybersecurity Analyst': ['security', 'cybersecurity', 'vulnerability', 'threat'],
            'Quality Assurance': ['testing', 'qa', 'quality', 'automation testing']
        }
        
        # Experience level indicators
        self.experience_indicators = {
            'senior': ['senior', 'lead', 'principal', 'architect', 'manager', 'director'],
            'mid': ['developer', 'engineer', 'analyst', 'specialist', 'consultant'],
            'junior': ['junior', 'associate', 'intern', 'trainee', 'entry']
        }
        
        # Achievement templates
        self.achievement_templates = [
            "Proven track record of delivering high-quality solutions",
            "Successfully completed multiple complex projects",
            "Demonstrated ability to work in fast-paced environments",
            "Strong problem-solving and analytical skills",
            "Excellent collaboration and communication abilities",
            "Committed to continuous learning and professional growth",
            "Experience working with cross-functional teams",
            "Passionate about creating innovative solutions"
        ]
        
        # Specialization mappings
        self.specialization_mapping = {
            'programming_languages': 'software development',
            'web_technologies': 'web development',
            'databases': 'database management',
            'cloud_platforms': 'cloud computing',
            'data_science': 'data analysis and machine learning',
            'mobile_development': 'mobile application development',
            'devops_tools': 'DevOps and automation',
            'design_tools': 'UI/UX design',
            'project_management': 'project management',
            'soft_skills': 'team leadership and collaboration'
        }
    
    def _determine_role(self, analysis_result: Dict[str, Any]) -> str:
        """
        Determine the most likely professional role based on skills and content.
        """
        text = analysis_result.get('text', '').lower()
        skills = analysis_result.get('skills', {})
        
        # Score each role based on keyword presence
        role_scores = {}
        
        for role, keywords in self.role_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
                # Bonus points for skills categories
                for skill_category, skill_list in skills.items():
                    if keyword in ' '.join(skill_list).lower():
                        score += 2
            
            role_scores[role] = score
        
        # Return the highest scoring role, or generic if no clear match
        if role_scores:
            best_role = max(role_scores.items(), key=lambda x: x[1])
            return best_role[0] if best_role[1] > 0 else "Professional"
        
        return "Professional"
    
    def _estimate_experience_level(self, analysis_result: Dict[str, Any]) -> tuple[str, str]:
        """
        Estimate experience level and years based on content analysis.
        Returns (level, years_description)
        """
        text = analysis_result.get('text', '').lower()
        
        # Look for explicit year mentions
        year_patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:experience|exp)',
            r'(\d+)\+?\s*yrs?\s+(?:of\s+)?(?:experience|exp)',
            r'over\s+(\d+)\s+years?',
            r'more\s+than\s+(\d+)\s+years?'
        ]
        
        years_found = []
        for pattern in year_patterns:
            matches = re.findall(pattern, text)
            years_found.extend([int(match) for match in matches])
        
        if years_found:
            max_years = max(years_found)
            if max_years >= 7:
                return "senior", f"{max_years}+ years"
            elif max_years >= 3:
                return "mid", f"{max_years} years"
            else:
                return "entry", f"{max_years} years"
        
        # Fallback: analyze job titles and content complexity
        for level, indicators in self.experience_indicators.items():
            if any(indicator in text for indicator in indicators):
                if level == "senior":
                    return "senior", "7+ years"
                elif level == "mid":
                    return "mid", "3-6 years"
                else:
                    return "entry", "1-2 years"
        
        # Default based on content complexity
        word_count = analysis_result.get('readability', {}).get('word_count', 0)
        skills_count = sum(len(skill_list) for skill_list in analysis_result.get('skills', {}).values())
        projects_count = len(analysis_result.get('projects', []))
        
        complexity_score = word_count + (skills_count * 10) + (projects_count * 20)
        
        if complexity_score > 500:
            return "mid", "3+ years"
        elif complexity_score > 200:
            return "entry", "1-2 years"
        else:
            return "entry", "recent graduate"
    
    def _get_top_skills(self, skills: Dict[str, List[str]], top_n: int = 3) -> List[str]:
        """
        Get the top N most relevant skills for the summary.
        """
        # Prioritize technical skills over soft skills
        priority_categories = [
            'programming_languages', 'web_technologies', 'databases', 
            'cloud_platforms', 'data_science', 'mobile_development'
        ]
        
        top_skills = []
        
        # First, get skills from priority categories
        for category in priority_categories:
            if category in skills and len(top_skills) < top_n:
                category_skills = skills[category][:2]  # Max 2 per category
                top_skills.extend(category_skills)
        
        # Fill remaining slots with other skills
        if len(top_skills) < top_n:
            for category, skill_list in skills.items():
                if category not in priority_categories and len(top_skills) < top_n:
                    remaining_slots = top_n - len(top_skills)
                    top_skills.extend(skill_list[:remaining_slots])
        
        return top_skills[:top_n]
    
    def _get_specializations(self, skills: Dict[str, List[str]]) -> List[str]:
        """
        Get specialization areas based on skill categories.
        """
        specializations = []
        
        for category, skill_list in skills.items():
            if len(skill_list) >= 2:  # Only include categories with multiple skills
                if category in self.specialization_mapping:
                    specializations.append(self.specialization_mapping[category])
        
        return specializations[:2]  # Limit to 2 specializations
    
    def _detect_education_level(self, text: str) -> Optional[str]:
        """
        Detect education level from resume text.
        """
        text_lower = text.lower()
        
        education_levels = {
            'PhD': ['phd', 'ph.d', 'doctorate', 'doctoral'],
            'Master\'s': ['masters', 'master\'s', 'mba', 'ms', 'm.s', 'ma', 'm.a'],
            'Bachelor\'s': ['bachelors', 'bachelor\'s', 'bs', 'b.s', 'ba', 'b.a', 'btech', 'b.tech'],
            'Associate': ['associate', 'associates', 'aa', 'as']
        }
        
        for level, keywords in education_levels.items():
            if any(keyword in text_lower for keyword in keywords):
                return level
        
        return None
    
    def _extract_projects_summary(self, projects: List[str]) -> str:
        """
        Create a brief summary of projects for the professional summary.
        """
        if not projects:
            return "Strong technical foundation"
        
        project_count = len(projects)
        if project_count == 1:
            return "Demonstrated expertise through practical project implementation"
        elif project_count <= 3:
            return f"Successfully delivered {project_count} major projects"
        else:
            return "Extensive portfolio of successful project implementations"
    
    def generate_summary(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a professional 2-line summary based on resume analysis.
        """
        if 'error' in analysis_result:
            return {
                'summary': "Unable to generate summary due to analysis error.",
                'error': analysis_result['error'],
                'template_used': None,
                'components': {}
            }
        
        # Extract key information
        role = self._determine_role(analysis_result)
        experience_level, years = self._estimate_experience_level(analysis_result)
        skills = analysis_result.get('skills', {})
        projects = analysis_result.get('projects', [])
        
        # Get education info
        education = self._detect_education_level(analysis_result.get('text', ''))
        
        # Build summary components
        top_skills = self._get_top_skills(skills, 3)
        specializations = self._get_specializations(skills)
        achievement = random.choice(self.achievement_templates)
        projects_summary = self._extract_projects_summary(projects)
        
        # Determine template category
        if education and experience_level == "entry" and years in ["recent graduate", "1-2 years"]:
            template_category = "entry_level"
        elif experience_level == "senior":
            template_category = "experienced"
        else:
            template_category = "experienced"  # Default to experienced template
        
        # Select and fill template
        template = random.choice(self.templates[template_category])
        
        # Prepare template variables
        template_vars = {
            'role': role,
            'experience': "Experienced" if experience_level != "entry" else "Dedicated",
            'expertise': "Expert" if experience_level == "senior" else "Skilled",
            'years': years,
            'skills': ', '.join(top_skills) if top_skills else "multiple technologies",
            'specializations': ', '.join(specializations) if specializations else "innovative solutions",
            'achievement': achievement,
            'education': education or "technology",
            'projects': projects_summary,
            'field': role.split()[-1].lower() if ' ' in role else role.lower(),
            'new_field': role.lower()
        }
        
        # Generate summary
        try:
            summary = template.format(**template_vars)
        except KeyError as e:
            # Fallback to simple template if formatting fails
            summary = f"{template_vars['expertise']} {template_vars['role']} with {template_vars['years']} of experience in {template_vars['skills']}. {template_vars['achievement']} and expertise in {template_vars['specializations']}."
        
        # Ensure it's exactly 2 sentences
        sentences = summary.split('. ')
        if len(sentences) > 2:
            summary = '. '.join(sentences[:2]) + '.'
        elif len(sentences) == 1:
            # Split long single sentence if needed
            if len(summary) > 150:
                mid_point = summary.find('. ')
                if mid_point == -1:
                    mid_point = summary.find(' and ', len(summary)//2)
                    if mid_point != -1:
                        summary = summary[:mid_point] + '. ' + summary[mid_point+5:].capitalize()
        
        return {
            'summary': summary,
            'template_used': template_category,
            'components': {
                'role': role,
                'experience_level': experience_level,
                'years': years,
                'top_skills': top_skills,
                'specializations': specializations,
                'education': education
            },
            'alternatives': self._generate_alternatives(template_vars, template_category)
        }
    
    def _generate_alternatives(self, template_vars: Dict[str, str], 
                             template_category: str) -> List[str]:
        """
        Generate alternative summary versions for user choice.
        """
        alternatives = []
        available_templates = self.templates[template_category]
        
        # Generate 2 alternatives using different templates
        for template in available_templates[:2]:
            try:
                alternative = template.format(**template_vars)
                sentences = alternative.split('. ')
                if len(sentences) > 2:
                    alternative = '. '.join(sentences[:2]) + '.'
                alternatives.append(alternative)
            except KeyError:
                continue
        
        return alternatives

# Convenience function for easy import
def generate_professional_summary(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple function to generate a professional summary from resume analysis.
    """
    generator = SummaryGenerator()
    return generator.generate_summary(analysis_result)