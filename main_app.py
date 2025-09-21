"""
Resume Analysis App - Main Streamlit Application
A comprehensive tool for analyzing resumes and providing actionable feedback.
"""

import streamlit as st
import sys
import os
import json
from io import BytesIO

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import our modules
from src.pdf_parser import parse_pdf
from src.text_analyzer import analyze_resume_text
from src.rating_system import rate_resume
from src.suggestions import generate_suggestions
from src.summary_generator import generate_professional_summary

# Page configuration
st.set_page_config(
    page_title="Resume Analysis App",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .suggestion-high {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .suggestion-medium {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .suggestion-low {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .summary-box {
        background-color: #e3f2fd;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #2196f3;
        margin: 1rem 0;
        color: #1565c0;
    }
    .summary-box p {
        color: #1565c0 !important;
        font-weight: 500;
    }
    .score-excellent {
        background: linear-gradient(135deg, #4caf50, #66bb6a);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .score-good {
        background: linear-gradient(135deg, #ff9800, #ffb74d);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .score-average {
        background: linear-gradient(135deg, #ffc107, #ffca28);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .score-poor {
        background: linear-gradient(135deg, #f44336, #ef5350);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .skill-tag {
        background-color: #e1f5fe;
        color: #0277bd;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        margin: 0.2rem;
        display: inline-block;
        border: 1px solid #0277bd;
    }
    .project-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

def create_score_display(score, title):
    """Create an enhanced score display with better styling."""
    # Determine style class and emoji based on score
    if score >= 8:
        emoji = "🎉"
        style_class = "score-excellent"
        performance = "Excellent"
    elif score >= 6:
        emoji = "�"
        style_class = "score-good"
        performance = "Good"
    elif score >= 4:
        emoji = "⚠️"
        style_class = "score-average"
        performance = "Average"
    else:
        emoji = "�"
        style_class = "score-poor"
        performance = "Needs Improvement"
    
    st.markdown(f"""
    <div class="{style_class}">
        <h1 style="margin: 0; font-size: 3rem;">{emoji}</h1>
        <h2 style="margin: 10px 0; font-size: 2.5rem;">{score:.1f}/10</h2>
        <h3 style="margin: 5px 0; font-size: 1.2rem;">{performance}</h3>
        <p style="margin: 5px 0; font-size: 1rem; opacity: 0.9;">{title}</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application function."""
    
    # Header
    st.markdown('<h1 class="main-header">📄 Resume Analysis App</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.2rem; color: #666;">
            Upload your resume and get instant analysis with actionable feedback to improve your job application success rate.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎯 How it works")
        st.markdown("""
        1. **Upload** your resume (PDF format)
        2. **Get Analysis** of skills, keywords, and structure
        3. **Receive Rating** out of 10 for overall quality
        4. **Review Suggestions** for improvement
        5. **Generate Summary** for your resume
        """)
        
        st.markdown("### 📊 What you'll get")
        st.markdown("""
        - ⭐ Resume score (1-10)
        - 🔍 Skills analysis
        - 📝 Improvement suggestions
        - ✨ Professional summary
        - 📈 Detailed breakdown
        - 🎯 Action plan
        """)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose your resume (PDF format)",
        type=['pdf'],
        help="Upload a PDF file of your resume for analysis"
    )
    
    if uploaded_file is not None:
        # Show file info
        st.success(f"✅ File uploaded: {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        # Add processing indicator
        with st.spinner("🔄 Analyzing your resume..."):
            
            # Step 1: Parse PDF
            pdf_result = parse_pdf(uploaded_file)
            
            if not pdf_result['success']:
                st.error(f"❌ Error parsing PDF: {pdf_result['error']}")
                st.info("💡 **Tip**: Make sure your PDF contains selectable text (not just images)")
                return
            
            resume_text = pdf_result['text']
            metadata = pdf_result['metadata']
            pdf_success = True
        
        if pdf_success:
            # Add processing indicator for analysis
            with st.spinner("🔄 Analyzing resume content..."):
                # Step 2: Analyze text
                analysis_result = analyze_resume_text(resume_text)
                
                if 'error' in analysis_result:
                    st.error(f"❌ Error analyzing resume: {analysis_result['error']}")
                    return
                
                # Step 3: Rate resume
                rating_result = rate_resume(analysis_result)
                
                # Step 4: Generate suggestions
                suggestions_result = generate_suggestions(analysis_result, rating_result)
                
                # Step 5: Generate professional summary
                summary_result = generate_professional_summary(analysis_result)
        
        # Display results
        st.success("✅ Analysis complete!")
        
        # Show overall score
        st.markdown("### 🎯 Resume Score")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            overall_score = rating_result['overall_score']
            create_score_display(overall_score, "Overall Resume Score")
        
        # Quick stats
        st.markdown("### 📊 Quick Overview")
        summary_stats = analysis_result.get('summary_stats', {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Skills Found", summary_stats.get('total_skills_found', 0))
        with col2:
            st.metric("Skill Categories", summary_stats.get('skills_categories', 0))
        with col3:
            st.metric("Projects", summary_stats.get('projects_found', 0))
        with col4:
            st.metric("Resume Sections", f"{summary_stats.get('sections_present', 0)}/8")
        
        # Rating and suggestions
        st.markdown("### 🎯 Rating & Key Insights")
        rating_category = rating_result.get('rating_category', 'Unknown')
        rating_description = rating_result.get('rating_description', '')
        
        st.info(f"**{rating_category}**: {rating_description}")
        
        # Top suggestions
        suggestions_by_priority = suggestions_result.get('suggestions_by_priority', {})
        if suggestions_by_priority.get('critical'):
            st.markdown("### 🚨 Top Priority Improvements")
            for suggestion in suggestions_by_priority['critical'][:3]:
                st.warning(suggestion)
        
        # Professional summary
        if 'error' not in summary_result:
            st.markdown("### ✨ Generated Professional Summary")
            summary = summary_result.get('summary', '')
            st.markdown(f"""
            <div class="summary-box">
                <p style="font-size: 1.1rem; line-height: 1.6;">{summary}</p>
            </div>
            """, unsafe_allow_html=True)
        
            # Show more details option
            if st.button("📋 View Detailed Analysis"):
                st.session_state.show_details = True
        
        # Detailed analysis (if requested)
        if st.session_state.get('show_details', False):
            st.markdown("---")
            st.markdown("## 📖 Detailed Analysis")
            
            # Skills breakdown
            st.markdown("### 🔧 Skills Analysis")
            skills = analysis_result.get('skills', {})
            if skills:
                for category, skills_list in skills.items():
                    st.markdown(f"**{category.replace('_', ' ').title()} ({len(skills_list)} skills):**")
                    
                    # Create skill tags
                    skills_html = ""
                    for skill in skills_list:
                        skills_html += f'<span class="skill-tag">{skill}</span>'
                    
                    st.markdown(f'<div style="margin-bottom: 1rem;">{skills_html}</div>', unsafe_allow_html=True)
            
            # All suggestions
            st.markdown("### 💡 All Improvement Suggestions")
            for priority, suggestions in suggestions_by_priority.items():
                if suggestions:
                    st.markdown(f"**{priority.title()} Priority:**")
                    for suggestion in suggestions:
                        st.markdown(f"• {suggestion}")
            
            # Score breakdown
            st.markdown("### 📊 Detailed Score Breakdown")
            score_breakdown = rating_result.get('score_breakdown', [])
            if score_breakdown:
                for item in score_breakdown:
                    st.markdown(f"**{item['criterion']}**: {item['score']:.1f}/10 (Weight: {item['weight']:.1f}%)")
        
        # Download option
        st.markdown("---")
        download_data = {
            'analysis': analysis_result,
            'rating': rating_result,
            'suggestions': suggestions_result,
            'summary': summary_result
        }
        
        st.download_button(
            label="📄 Download Analysis Report",
            data=json.dumps(download_data, indent=2, default=str),
            file_name=f"resume_analysis_{uploaded_file.name.replace('.pdf', '')}.json",
            mime="application/json"
        )
    
    else:
        # Show instructions when no file is uploaded
        st.info("👆 Upload your resume PDF to get started!")
        
        st.markdown("""
        ### 🎯 What This App Does:
        
        - **Analyzes** your resume content for skills, keywords, and structure
        - **Rates** your resume on a scale of 1-10
        - **Provides** specific suggestions for improvement
        - **Generates** a professional summary
        - **Helps** you optimize for Applicant Tracking Systems (ATS)
        
        ### 📋 Requirements:
        - PDF format only
        - Maximum file size: 10MB
        - Text-based resume (not image-only)
        """)

if __name__ == "__main__":
    main()