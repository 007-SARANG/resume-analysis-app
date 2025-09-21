"""
Resume Analysis App - Main Streamlit Application
A comprehensive resume analysis tool that provides ratings, suggestions, and professional summaries.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64
from typing import Dict, Any
import json
import os
import sys

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.pdf_parser import parse_pdf
    from src.text_analyzer import analyze_resume_text
    from src.rating_system import rate_resume
    from src.suggestions import generate_suggestions
    from src.summary_generator import generate_professional_summary
except ImportError:
    # Fallback for development
    st.error("Please ensure all required modules are installed and the src directory is properly structured.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Resume Analysis App",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
    }
    
    .score-number {
        font-size: 4rem;
        font-weight: bold;
        margin: 0;
    }
    
    .score-category {
        font-size: 1.5rem;
        margin: 0.5rem 0;
    }
    
    .suggestion-card {
        background: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    
    .skill-tag {
        background: #e3f2fd;
        color: #1976d2;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.9rem;
    }
    
    .metric-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def create_skills_visualization(skills_data: Dict[str, list]) -> go.Figure:
    """Create a radar chart for skills visualization."""
    if not skills_data:
        return None
    
    categories = list(skills_data.keys())
    values = [len(skills_list) for skills_list in skills_data.values()]
    
    # Normalize values for better visualization
    max_val = max(values) if values else 1
    normalized_values = [(v/max_val) * 10 for v in values]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=normalized_values,
        theta=[cat.replace('_', ' ').title() for cat in categories],
        fill='toself',
        name='Skills Distribution',
        line=dict(color='rgb(31, 119, 180)'),
        fillcolor='rgba(31, 119, 180, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=False,
        title="Skills Distribution by Category",
        height=400
    )
    
    return fig

def create_score_breakdown_chart(score_breakdown: list) -> go.Figure:
    """Create a horizontal bar chart for score breakdown."""
    if not score_breakdown:
        return None
    
    df = pd.DataFrame(score_breakdown)
    
    fig = go.Figure(go.Bar(
        x=df['score'],
        y=df['criterion'],
        orientation='h',
        marker_color=['#ff6b6b' if score < 5 else '#feca57' if score < 7 else '#48ca57' 
                     for score in df['score']],
        text=[f"{score:.1f}" for score in df['score']],
        textposition='auto',
    ))
    
    fig.update_layout(
        title="Score Breakdown by Criteria",
        xaxis_title="Score (0-10)",
        yaxis_title="Criteria",
        height=400,
        showlegend=False
    )
    
    return fig

def create_wordcloud(keywords: list) -> plt.Figure:
    """Create a word cloud from keywords."""
    if not keywords:
        return None
    
    # Create word frequency
    word_freq = {word: len(word) for word in keywords}  # Simple frequency based on word length
    
    # Generate word cloud
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        colormap='viridis',
        max_words=50
    ).generate_from_frequencies(word_freq)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    plt.title('Key Resume Keywords', fontsize=16, pad=20)
    
    return fig

def display_skills_section(skills_data: Dict[str, list]):
    """Display skills in an organized format."""
    if not skills_data:
        st.warning("No skills detected in your resume.")
        return
    
    st.subheader("🔧 Detected Skills")
    
    # Create columns for skills display
    for category, skills_list in skills_data.items():
        if skills_list:
            st.markdown(f"**{category.replace('_', ' ').title()}**")
            skills_html = ""
            for skill in skills_list:
                skills_html += f'<span class="skill-tag">{skill}</span>'
            st.markdown(skills_html, unsafe_allow_html=True)
            st.markdown("---")

def display_suggestions_section(suggestions_data: Dict[str, Any]):
    """Display improvement suggestions in a structured format."""
    if not suggestions_data:
        st.warning("No suggestions available.")
        return
    
    st.subheader("💡 Improvement Suggestions")
    
    suggestions_by_priority = suggestions_data.get('suggestions_by_priority', {})
    action_plan = suggestions_data.get('action_plan', [])
    
    # Display by priority
    for plan_item in action_plan:
        priority = plan_item['priority']
        items = plan_item['items']
        impact = plan_item['impact']
        
        if priority == "High Priority":
            st.error(f"🚨 **{priority}**")
        elif priority == "Medium Priority":
            st.warning(f"⚠️ **{priority}**")
        else:
            st.info(f"💡 **{priority}**")
        
        for item in items:
            st.markdown(f"• {item}")
        
        st.markdown(f"*{impact}*")
        st.markdown("---")

def generate_report_download(analysis_data: Dict[str, Any]) -> str:
    """Generate a downloadable report."""
    report = {
        'resume_analysis_report': {
            'overall_score': analysis_data.get('rating', {}).get('overall_score', 0),
            'rating_category': analysis_data.get('rating', {}).get('rating_category', 'Unknown'),
            'skills_found': analysis_data.get('analysis', {}).get('skills', {}),
            'suggestions': analysis_data.get('suggestions', {}),
            'professional_summary': analysis_data.get('summary', {}).get('summary', ''),
            'detailed_scores': analysis_data.get('rating', {}).get('detailed_scores', {}),
            'metadata': analysis_data.get('metadata', {})
        }
    }
    
    return json.dumps(report, indent=2)

def main():
    """Main application function."""
    
    # Header
    st.markdown('<h1 class="main-header">📄 Resume Analysis App</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.2rem; color: #666;">
            Upload your resume and get instant analysis with ratings, suggestions, and professional summaries!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🎯 Analysis Options")
    
    # File upload
    uploaded_file = st.sidebar.file_uploader(
        "Upload Resume (PDF)",
        type=['pdf'],
        help="Upload your resume in PDF format for analysis"
    )
    
    # Job comparison option
    enable_job_comparison = st.sidebar.checkbox("Compare with Job Title", value=False)
    job_title = None
    
    if enable_job_comparison:
        job_options = [
            "Software Engineer", "Data Scientist", "Product Manager", 
            "Marketing Manager", "Business Analyst", "DevOps Engineer",
            "UI/UX Designer", "Cybersecurity Analyst"
        ]
        job_title = st.sidebar.selectbox("Select Target Job Title", job_options)
    
    # Analysis settings
    st.sidebar.markdown("### Analysis Settings")
    show_detailed_breakdown = st.sidebar.checkbox("Show Detailed Score Breakdown", value=True)
    show_visualizations = st.sidebar.checkbox("Show Visualizations", value=True)
    
    # Main content
    if uploaded_file is not None:
        with st.spinner("🔄 Analyzing your resume..."):
            # Parse PDF
            parsing_result = parse_pdf(uploaded_file)
            
            if not parsing_result['success']:
                st.error(f"❌ Error processing PDF: {parsing_result['error']}")
                return
            
            # Analyze text
            analysis_result = analyze_resume_text(parsing_result['text'])
            
            if 'error' in analysis_result:
                st.error(f"❌ Error analyzing resume: {analysis_result['error']}")
                return
            
            # Rate resume
            rating_result = rate_resume(analysis_result)
            
            # Generate suggestions
            suggestions_result = generate_suggestions(analysis_result, rating_result)
            
            # Generate professional summary
            summary_result = generate_professional_summary(analysis_result)
            
            # Store results in session state for download
            st.session_state.analysis_data = {
                'analysis': analysis_result,
                'rating': rating_result,
                'suggestions': suggestions_result,
                'summary': summary_result,
                'metadata': parsing_result['metadata']
            }
        
        # Display results
        st.success("✅ Resume analysis completed!")
        
        # Overall Score Display
        overall_score = rating_result.get('overall_score', 0)
        rating_category = rating_result.get('rating_category', 'Unknown')
        rating_description = rating_result.get('rating_description', '')
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div class="score-card">
                <div class="score-number">{overall_score}/10</div>
                <div class="score-category">{rating_category}</div>
                <div>{rating_description}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Tabs for different sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview", "🔧 Skills", "💡 Suggestions", 
            "📝 Summary", "📋 Detailed Report"
        ])
        
        with tab1:
            st.subheader("📊 Resume Overview")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            summary_stats = analysis_result.get('summary_stats', {})
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{summary_stats.get('total_skills_found', 0)}</h3>
                    <p>Skills Found</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{summary_stats.get('projects_found', 0)}</h3>
                    <p>Projects Detected</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{summary_stats.get('sections_present', 0)}</h3>
                    <p>Sections Present</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                readability_score = analysis_result.get('readability', {}).get('readability_score', 0)
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{readability_score:.1f}/10</h3>
                    <p>Readability Score</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Visualizations
            if show_visualizations:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Skills radar chart
                    skills_fig = create_skills_visualization(analysis_result.get('skills', {}))
                    if skills_fig:
                        st.plotly_chart(skills_fig, use_container_width=True)
                
                with col2:
                    # Score breakdown
                    if show_detailed_breakdown:
                        score_fig = create_score_breakdown_chart(
                            rating_result.get('score_breakdown', [])
                        )
                        if score_fig:
                            st.plotly_chart(score_fig, use_container_width=True)
            
            # Keywords word cloud
            if show_visualizations and analysis_result.get('keywords'):
                st.subheader("🔍 Key Keywords")
                wordcloud_fig = create_wordcloud(analysis_result.get('keywords', []))
                if wordcloud_fig:
                    st.pyplot(wordcloud_fig)
        
        with tab2:
            display_skills_section(analysis_result.get('skills', {}))
            
            # Projects section
            projects = analysis_result.get('projects', [])
            if projects:
                st.subheader("🚀 Detected Projects")
                for i, project in enumerate(projects, 1):
                    st.markdown(f"**Project {i}:** {project}")
            
            # Contact information
            contact_info = analysis_result.get('contact_info', {})
            if contact_info:
                st.subheader("📞 Contact Information")
                for key, value in contact_info.items():
                    st.markdown(f"**{key.title()}:** {value}")
        
        with tab3:
            display_suggestions_section(suggestions_result)
        
        with tab4:
            st.subheader("📝 Professional Summary")
            
            summary_text = summary_result.get('summary', '')
            if summary_text:
                st.markdown(f"""
                <div style="background: #f0f8ff; padding: 1.5rem; border-radius: 10px; 
                           border-left: 4px solid #1f77b4; margin: 1rem 0;">
                    <h4 style="color: #1f77b4; margin-top: 0;">Generated Professional Summary</h4>
                    <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 0;">
                        {summary_text}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Alternative summaries
                alternatives = summary_result.get('alternatives', [])
                if alternatives:
                    st.subheader("🔄 Alternative Versions")
                    for i, alt in enumerate(alternatives, 1):
                        st.markdown(f"**Option {i}:** {alt}")
            else:
                st.warning("Could not generate professional summary.")
        
        with tab5:
            st.subheader("📋 Detailed Analysis Report")
            
            # Detailed scores
            if show_detailed_breakdown and rating_result.get('detailed_scores'):
                st.subheader("🎯 Detailed Scoring")
                
                detailed_scores = rating_result.get('detailed_scores', {})
                score_df = pd.DataFrame([
                    {'Criteria': k.replace('_', ' ').title(), 'Score': f"{v:.1f}/10"}
                    for k, v in detailed_scores.items()
                ])
                st.dataframe(score_df, use_container_width=True)
            
            # Job comparison results
            if enable_job_comparison and job_title:
                st.subheader(f"🎯 Comparison with {job_title}")
                
                comparison_result = analysis_result.get('job_comparison', {})
                if comparison_result and 'error' not in comparison_result:
                    match_score = comparison_result.get('match_score', 0)
                    st.metric("Job Match Score", f"{match_score:.1f}%")
                    
                    missing_keywords = comparison_result.get('missing_keywords', [])
                    if missing_keywords:
                        st.subheader("❌ Missing Keywords")
                        for keyword in missing_keywords[:10]:  # Show top 10
                            st.markdown(f"• {keyword}")
            
            # Download report
            if st.session_state.get('analysis_data'):
                report_json = generate_report_download(st.session_state.analysis_data)
                
                st.download_button(
                    label="📥 Download Detailed Report",
                    data=report_json,
                    file_name="resume_analysis_report.json",
                    mime="application/json"
                )
    
    else:
        # Instructions when no file is uploaded
        st.markdown("""
        ## 🚀 How to Use This App
        
        1. **Upload Your Resume**: Click on the file uploader in the sidebar and select your PDF resume
        2. **Get Instant Analysis**: The app will analyze your resume and provide comprehensive feedback
        3. **Review Your Score**: See your overall resume score and rating category
        4. **Check Suggestions**: Get actionable improvement recommendations
        5. **Use Professional Summary**: Copy the generated summary for your resume
        6. **Download Report**: Get a detailed JSON report of your analysis
        
        ## 🎯 What You'll Get
        
        - **Resume Rating**: Score out of 10 based on multiple criteria
        - **Skills Analysis**: Detected technical and soft skills
        - **Improvement Suggestions**: Prioritized recommendations
        - **Professional Summary**: AI-generated 2-line summary
        - **Keyword Analysis**: Important keywords from your resume
        - **Visual Insights**: Charts and graphs of your resume data
        
        ## 📋 Tips for Best Results
        
        - Ensure your PDF is text-based (not scanned image)
        - Include complete sections (experience, education, skills)
        - Use standard resume formatting
        - Keep file size under 10MB
        """)

if __name__ == "__main__":
    main()