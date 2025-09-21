"""
Suggestions System
Provides specific, actionable feedback for resume improvement.
"""

from typing import Dict, Any, List, Tuple
import random

class SuggestionsSystem:
    """
    Generates specific, actionable suggestions for resume improvement
    based on analysis results and scoring.
    """
    
    def __init__(self):
        # Pre-defined suggestion templates
        self.skill_suggestions = {
            'programming_languages': [
                "Add specific programming languages you've used in projects",
                "Mention version numbers for programming languages (e.g., Python 3.9)",
                "Include both frontend and backend technologies if applicable",
                "Add emerging technologies relevant to your field"
            ],
            'web_technologies': [
                "List specific frameworks and libraries you've worked with",
                "Mention responsive design and mobile-first development experience",
                "Include API development and integration experience",
                "Add version control systems (Git, GitHub, GitLab)"
            ],
            'databases': [
                "Specify database management systems you've used",
                "Mention both SQL and NoSQL databases if applicable",
                "Include database design and optimization experience",
                "Add data modeling and schema design skills"
            ],
            'cloud_platforms': [
                "List cloud platforms and services you've used",
                "Mention specific AWS/Azure/GCP services",
                "Include containerization technologies (Docker, Kubernetes)",
                "Add CI/CD pipeline experience"
            ],
            'soft_skills': [
                "Include leadership and team collaboration skills",
                "Mention communication and presentation abilities",
                "Add problem-solving and analytical thinking skills",
                "Include project management and organizational skills"
            ]
        }
        
        self.section_suggestions = {
            'summary': [
                "Add a professional summary highlighting your key achievements",
                "Include 2-3 lines summarizing your expertise and career goals",
                "Mention years of experience and key specializations",
                "Include your most impressive accomplishment or metric"
            ],
            'experience': [
                "Use action verbs to start each bullet point (Developed, Implemented, Led)",
                "Include quantifiable achievements and metrics",
                "Mention specific technologies and tools used",
                "Focus on impact and results rather than just responsibilities"
            ],
            'education': [
                "Include your degree, major, university, and graduation year",
                "Add relevant coursework if you're a recent graduate",
                "Mention academic achievements, honors, or high GPA",
                "Include relevant certifications and professional development"
            ],
            'skills': [
                "Organize skills into categories (Technical, Languages, Tools)",
                "List skills in order of proficiency",
                "Include both hard and soft skills",
                "Match skills to job requirements when possible"
            ],
            'projects': [
                "Include 2-4 relevant projects with brief descriptions",
                "Mention technologies used and your role",
                "Add links to GitHub repos or live demos",
                "Quantify impact or results where possible"
            ]
        }
        
        self.formatting_suggestions = [
            "Use consistent formatting throughout the document",
            "Keep margins between 0.5-1 inch on all sides",
            "Use a professional, readable font (Arial, Calibri, Times New Roman)",
            "Maintain consistent font sizes (10-12pt for body, 14-16pt for headers)",
            "Use bullet points for easy scanning",
            "Ensure adequate white space between sections",
            "Keep resume to 1-2 pages maximum",
            "Save as PDF to preserve formatting"
        ]
        
        self.content_improvement_tips = {
            'action_verbs': [
                "Achieved", "Developed", "Implemented", "Led", "Managed", "Created",
                "Improved", "Increased", "Reduced", "Optimized", "Designed", "Built"
            ],
            'metrics_examples': [
                "Increased system efficiency by 25%",
                "Reduced processing time by 4 hours daily",
                "Led a cross-functional team of 8 developers",
                "Improved user satisfaction scores from 3.2 to 4.6",
                "Generated $2M+ in additional revenue through optimization",
                "Completed 95% of projects ahead of schedule"
            ]
        }
    
    def generate_skill_suggestions(self, skills_analysis: Dict[str, List[str]], 
                                 detailed_scores: Dict[str, float]) -> List[str]:
        """
        Generate suggestions for improving skills section.
        """
        suggestions = []
        
        # Check skills diversity
        if detailed_scores.get('skills_diversity', 0) < 7.0:
            suggestions.append("💡 **Skills Diversity**: Add skills from different categories (technical, tools, soft skills)")
            
            # Suggest missing categories
            present_categories = set(skills_analysis.keys())
            all_categories = set(self.skill_suggestions.keys())
            missing_categories = all_categories - present_categories
            
            if missing_categories:
                for category in list(missing_categories)[:2]:  # Suggest up to 2 categories
                    suggestion = random.choice(self.skill_suggestions[category])
                    suggestions.append(f"✨ **{category.replace('_', ' ').title()}**: {suggestion}")
        
        # Check skills quantity
        if detailed_scores.get('skills_quantity', 0) < 7.0:
            suggestions.append("📈 **Skills Quantity**: Add more specific skills and technologies you've worked with")
            
            # Add specific suggestions for existing categories
            for category, skills_list in skills_analysis.items():
                if len(skills_list) < 3:
                    suggestion = random.choice(self.skill_suggestions.get(category, 
                        ["Add more specific skills in this category"]))
                    suggestions.append(f"🔧 **{category.replace('_', ' ').title()}**: {suggestion}")
        
        return suggestions
    
    def generate_section_suggestions(self, sections_analysis: Dict[str, bool],
                                   detailed_scores: Dict[str, float]) -> List[str]:
        """
        Generate suggestions for resume sections.
        """
        suggestions = []
        
        # Check for missing essential sections
        essential_sections = ['experience', 'education', 'skills']
        for section in essential_sections:
            if not sections_analysis.get(section, False):
                suggestions.append(f"⚠️ **Missing {section.title()} Section**: This is essential for any resume")
        
        # Check for missing important sections
        important_sections = ['summary', 'projects']
        for section in important_sections:
            if not sections_analysis.get(section, False):
                suggestion = random.choice(self.section_suggestions[section])
                suggestions.append(f"➕ **Add {section.title()} Section**: {suggestion}")
        
        # Suggest improvements for existing sections
        if detailed_scores.get('sections_completeness', 0) < 8.0:
            for section, present in sections_analysis.items():
                if present and section in self.section_suggestions:
                    suggestion = random.choice(self.section_suggestions[section])
                    suggestions.append(f"✏️ **Improve {section.title()} Section**: {suggestion}")
        
        return suggestions
    
    def generate_content_suggestions(self, analysis_result: Dict[str, Any],
                                   detailed_scores: Dict[str, float]) -> List[str]:
        """
        Generate suggestions for content improvement.
        """
        suggestions = []
        
        # Content length suggestions
        word_count = analysis_result.get('readability', {}).get('word_count', 0)
        if detailed_scores.get('content_length', 0) < 7.0:
            if word_count < 150:
                suggestions.append("📝 **Content Length**: Your resume is too brief. Add more details about your experience and achievements")
            elif word_count > 800:
                suggestions.append("✂️ **Content Length**: Your resume is too long. Focus on the most relevant and impactful information")
        
        # Readability suggestions
        readability = analysis_result.get('readability', {})
        if detailed_scores.get('readability', 0) < 7.0:
            avg_sentence_length = readability.get('avg_sentence_length', 20)
            if avg_sentence_length > 25:
                suggestions.append("🎯 **Readability**: Use shorter, more concise sentences for better readability")
            
            complexity_ratio = readability.get('complexity_ratio', 0.3)
            if complexity_ratio > 0.5:
                suggestions.append("💭 **Readability**: Simplify complex words where possible while maintaining professionalism")
        
        # Project quality suggestions
        projects = analysis_result.get('projects', [])
        if detailed_scores.get('project_quality', 0) < 7.0:
            if len(projects) == 0:
                suggestions.append("🚀 **Projects**: Add 2-3 relevant projects that showcase your skills")
            elif len(projects) < 3:
                suggestions.append("🚀 **Projects**: Add more projects to demonstrate your practical experience")
            
            # Check project description quality
            short_projects = [p for p in projects if len(p.split()) < 10]
            if short_projects:
                suggestions.append("📋 **Project Descriptions**: Expand your project descriptions with technologies used and impact achieved")
        
        # Contact information suggestions
        contact_info = analysis_result.get('contact_info', {})
        if detailed_scores.get('contact_completeness', 0) < 8.0:
            missing_contact = []
            if 'email' not in contact_info:
                missing_contact.append('professional email')
            if 'phone' not in contact_info:
                missing_contact.append('phone number')
            if 'linkedin' not in contact_info:
                missing_contact.append('LinkedIn profile')
            
            if missing_contact:
                suggestions.append(f"📞 **Contact Info**: Add {', '.join(missing_contact)}")
        
        return suggestions
    
    def generate_formatting_suggestions(self, detailed_scores: Dict[str, float]) -> List[str]:
        """
        Generate general formatting and presentation suggestions.
        """
        suggestions = []
        
        # Always include some formatting tips
        formatting_tips = random.sample(self.formatting_suggestions, 3)
        for tip in formatting_tips:
            suggestions.append(f"🎨 **Formatting**: {tip}")
        
        return suggestions
    
    def generate_content_enhancement_tips(self) -> List[str]:
        """
        Generate tips for enhancing content with action verbs and metrics.
        """
        suggestions = []
        
        # Action verbs suggestion
        action_verbs = random.sample(self.content_improvement_tips['action_verbs'], 4)
        suggestions.append(f"💪 **Action Verbs**: Start bullet points with strong verbs like: {', '.join(action_verbs)}")
        
        # Metrics suggestion
        metrics_examples = random.sample(self.content_improvement_tips['metrics_examples'], 3)
        examples_text = " | ".join(metrics_examples)
        suggestions.append(f"📊 **Quantify Achievements**: Include specific metrics and numbers (e.g., {examples_text})")
        
        return suggestions
    
    def generate_priority_suggestions(self, analysis_result: Dict[str, Any],
                                    rating_result: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Generate prioritized suggestions based on analysis and rating results.
        """
        detailed_scores = rating_result.get('detailed_scores', {})
        improvement_priority = rating_result.get('improvement_priority', [])
        
        all_suggestions = {
            'critical': [],  # Most important improvements
            'important': [], # Important but not critical
            'enhancement': [] # Nice-to-have improvements
        }
        
        # Critical suggestions (lowest scoring areas)
        for priority in improvement_priority:
            if 'skills' in priority.lower():
                all_suggestions['critical'].extend(
                    self.generate_skill_suggestions(
                        analysis_result.get('skills', {}), detailed_scores
                    )[:2]
                )
            elif 'section' in priority.lower():
                all_suggestions['critical'].extend(
                    self.generate_section_suggestions(
                        analysis_result.get('sections', {}), detailed_scores
                    )[:2]
                )
            elif 'content' in priority.lower() or 'readability' in priority.lower():
                all_suggestions['critical'].extend(
                    self.generate_content_suggestions(analysis_result, detailed_scores)[:2]
                )
        
        # Important suggestions
        all_suggestions['important'].extend(
            self.generate_content_suggestions(analysis_result, detailed_scores)[2:4]
        )
        all_suggestions['important'].extend(
            self.generate_section_suggestions(
                analysis_result.get('sections', {}), detailed_scores
            )[2:4]
        )
        
        # Enhancement suggestions
        all_suggestions['enhancement'].extend(
            self.generate_formatting_suggestions(detailed_scores)[:2]
        )
        all_suggestions['enhancement'].extend(
            self.generate_content_enhancement_tips()[:3]
        )
        
        # Remove duplicates and empty suggestions
        for category in all_suggestions:
            all_suggestions[category] = list(set(filter(None, all_suggestions[category])))
        
        return all_suggestions
    
    def generate_improvement_action_plan(self, suggestions: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """
        Generate a structured action plan for resume improvement.
        """
        action_plan = []
        
        # Critical actions (do first)
        if suggestions['critical']:
            action_plan.append({
                'priority': 'High Priority',
                'timeline': 'Complete within 1-2 days',
                'items': suggestions['critical'][:3],
                'impact': 'These changes will significantly improve your resume score'
            })
        
        # Important actions (do next)
        if suggestions['important']:
            action_plan.append({
                'priority': 'Medium Priority',
                'timeline': 'Complete within 1 week',
                'items': suggestions['important'][:3],
                'impact': 'These improvements will make your resume more competitive'
            })
        
        # Enhancement actions (nice to have)
        if suggestions['enhancement']:
            action_plan.append({
                'priority': 'Low Priority',
                'timeline': 'Complete when you have time',
                'items': suggestions['enhancement'][:3],
                'impact': 'These refinements will polish your resume presentation'
            })
        
        return action_plan

# Convenience function for easy import
def generate_suggestions(analysis_result: Dict[str, Any], 
                        rating_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple function to generate comprehensive suggestions for resume improvement.
    """
    suggestions_system = SuggestionsSystem()
    
    priority_suggestions = suggestions_system.generate_priority_suggestions(
        analysis_result, rating_result
    )
    
    action_plan = suggestions_system.generate_improvement_action_plan(priority_suggestions)
    
    return {
        'suggestions_by_priority': priority_suggestions,
        'action_plan': action_plan,
        'total_suggestions': sum(len(suggestions) for suggestions in priority_suggestions.values())
    }