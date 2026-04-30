# Streamlit Web Application
import streamlit as st
import asyncio
import os
from datetime import datetime
from pathlib import Path
from streamlit_option_menu import option_menu
from agents.orchestrator import OrchestratorAgent
from utils.logger import setup_logger
from utils.exceptions import ResumeProcessingError

# Configure Streamlit page
st.set_page_config(
    page_title="AI Recruiter Agency",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize logger
logger = setup_logger()

# Custom CSS — loaded from styles/main.css
_css_path = Path(__file__).parent / "styles" / "main.css"
st.markdown(
    f"<style>{_css_path.read_text(encoding='utf-8')}</style>",
    unsafe_allow_html=True,
)


async def process_resume(file_path: str) -> dict:
    """Process resume through the AI recruitment pipeline"""
    try:
        orchestrator = OrchestratorAgent()
        resume_data = {
            "file_path": file_path,
            "submission_timestamp": datetime.now().isoformat(),
        }
        return await orchestrator.process_application(resume_data)
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        raise


def save_uploaded_file(uploaded_file) -> str:
    """Save uploaded file and return the file path"""
    try:
        # Create uploads directory if it doesn't exist
        save_dir = Path("uploads")
        save_dir.mkdir(exist_ok=True)

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = save_dir / f"resume_{timestamp}_{uploaded_file.name}"

        # Save the file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return str(file_path)
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        raise


def main():
    # Sidebar navigation
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center; padding: 1.2rem 0 0.5rem 0;">
                <div style="font-size:2.8rem; letter-spacing:-1px; font-weight:800; background:linear-gradient(90deg,#a78bfa,#60a5fa); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">AI</div>
                <div style="font-size:1.25rem; font-weight:700;
                     background:linear-gradient(90deg,#a78bfa,#60a5fa);
                     -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                    AI Recruiter
                </div>
                <div style="font-size:0.75rem; color:#64748b; letter-spacing:0.15em; text-transform:uppercase; margin-top:2px;">Agency</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()
        selected = option_menu(
            menu_title="Navigation",
            options=["Upload Resume", "About"],
            icons=["cloud-upload", "info-circle"],
            menu_icon="cast",
            default_index=0,
        )

    if selected == "Upload Resume":
        st.markdown(
            """
            <div style="margin-bottom:1.5rem;">
                <h1 style="margin-bottom:0.25rem;">Resume Analysis</h1>
                <p style="color:#94a3b8; font-size:1rem; margin:0;">Upload a resume to get AI-powered insights and job matches.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        uploaded_file = st.file_uploader(
            "Choose a PDF resume file",
            type=["pdf"],
            help="Upload a PDF resume to analyze",
        )

        if uploaded_file:
            try:
                with st.spinner("Saving uploaded file..."):
                    file_path = save_uploaded_file(uploaded_file)

                st.info("Resume uploaded successfully! Processing...")

                # Create placeholder for progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Process resume
                try:
                    status_text.text("Analyzing resume...")
                    progress_bar.progress(25)

                    # Run analysis asynchronously
                    result = asyncio.run(process_resume(file_path))

                    if result["status"] == "completed":
                        progress_bar.progress(100)
                        status_text.text("Analysis complete!")

                        # Display results in tabs
                        tab1, tab2, tab3, tab4 = st.tabs(
                            [
                                "Analysis",
                                "Job Matches",
                                "Screening",
                                "Recommendation",
                            ]
                        )

                        with tab1:
                            st.subheader("Skills Analysis")
                            st.write(result["analysis_results"]["skills_analysis"])
                            st.metric(
                                "Confidence Score",
                                f"{result['analysis_results']['confidence_score']:.0%}",
                            )

                        with tab2:
                            st.subheader("Matched Positions")
                            
                            # DEBUG INFO - Remove later
                            with st.expander("Debug Info"):
                                st.write(f"**Skills Extracted:** {result['analysis_results'].get('skills_analysis', {}).get('technical_skills', [])}")
                                st.write(f"**Experience Level:** {result['analysis_results'].get('skills_analysis', {}).get('experience_level', 'N/A')}")
                                st.write(f"**Total Matches Found:** {result['job_matches'].get('number_of_matches', 0)}")
                            
                            if not result["job_matches"]["matched_jobs"]:
                                st.warning("No suitable positions found. This could mean:")
                                st.info("""
                                1. **Skills not extracted properly** - Check the CV parsing
                                2. **Limited job database** - Ensure jobs are seeded in the database
                                3. **No skill overlap** - Upload a CV with Python, JavaScript, React, etc.
                                4. **Empty technical_skills field** - Review the analyzer output
                                """)
                            else:
                                seen_titles = set()  # ← ADD THIS LINE
                                for job in result["job_matches"]["matched_jobs"]:
                                    if job["title"] not in seen_titles:
                                        seen_titles.add(job["title"])
                                        st.markdown(
                                            f"""
                                            <div class="job-card">
                                                <div class="job-title">{job['title']}</div>
                                                <div class="job-meta">{job.get('location', 'N/A')}</div>
                                                <div style="margin-top:0.6rem;">
                                                    <span class="match-badge">Match: {job.get('match_score', 'N/A')}</span>
                                                </div>
                                            </div>
                                            """,
                                            unsafe_allow_html=True,
                                        )
                        with tab3:
                            st.subheader("Screening Results")
                            st.metric(
                                "Screening Score",
                                f"{result['screening_results']['screening_score']}%",
                            )
                            st.write(result["screening_results"]["screening_report"])

                        with tab4:
                            st.subheader("Final Recommendation")
                            st.info(
                                result["final_recommendation"]["final_recommendation"],
                            )

                        # Save results
                        output_dir = Path("results")
                        output_dir.mkdir(exist_ok=True)
                        output_file = (
                            output_dir
                            / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        )

                        with open(output_file, "w") as f:
                            f.write(str(result))

                        st.success(f"Results saved to: {output_file}")

                    else:
                        st.error(
                            f"Process failed at stage: {result['current_stage']}\n"
                            f"Error: {result.get('error', 'Unknown error')}"
                        )

                except Exception as e:
                    st.error(f"Error processing resume: {str(e)}")
                    logger.error(f"Processing error: {str(e)}", exc_info=True)

                finally:
                    # Cleanup uploaded file
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        logger.error(f"Error removing temporary file: {str(e)}")

            except Exception as e:
                st.error(f"Error handling file upload: {str(e)}")
                logger.error(f"Upload error: {str(e)}", exc_info=True)

    elif selected == "About":
        st.markdown(
            """
            <div style="margin-bottom:1.5rem;">
                <h1 style="margin-bottom:0.25rem;">About</h1>
                <p style="color:#94a3b8; font-size:1rem; margin:0;">Cutting-edge recruitment analysis powered by AI agents.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(
                """
                <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.09);
                            border-radius:16px;padding:1.4rem 1.6rem;height:100%;">
                    <div style="font-size:1.1rem;font-weight:600;color:#e2e8f0;margin-bottom:0.8rem;">Powered By</div>
                    <ul style="color:#cbd5e1;line-height:2;list-style:none;padding:0;margin:0;">
                        <li><strong style="color:#a78bfa">Ollama (llama3.2)</strong> — Local LLM inference</li>
                        <li><strong style="color:#60a5fa">Swarm Framework</strong> — Multi-agent orchestration</li>
                        <li><strong style="color:#34d399">Streamlit</strong> — Interactive web interface</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_b:
            st.markdown(
                """
                <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.09);
                            border-radius:16px;padding:1.4rem 1.6rem;height:100%;">
                    <div style="font-size:1.1rem;font-weight:600;color:#e2e8f0;margin-bottom:0.8rem;">Agent Pipeline</div>
                    <ol style="color:#cbd5e1;line-height:2;padding-left:1.2rem;margin:0;">
                        <li>Extract information from resumes</li>
                        <li>Analyse candidate profiles</li>
                        <li>Match with suitable positions</li>
                        <li>Screen candidates</li>
                        <li>Provide detailed recommendations</li>
                    </ol>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("Upload a resume on the **Upload Resume** page to experience AI-powered recruitment analysis!")


if __name__ == "__main__":
    main()
