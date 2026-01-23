# AI Recruiter Agency 🤖

An intelligent recruitment system powered by local LLMs and autonomous AI agents. This application processes job seeker resumes, extracts key information, analyzes candidate profiles, matches them with job listings, and provides comprehensive recommendations.

## Features

- **Resume Processing**: Automatically extracts structured information from PDF resumes
- **Candidate Analysis**: Analyzes skills, experience, education, and key achievements
- **Job Matching**: Intelligently matches candidates with available job positions
- **Screening**: Evaluates candidate fit based on job requirements
- **Recommendations**: Generates personalized job recommendations with match scores
- **Local LLM**: Uses Ollama with llama3.2 model for all AI processing (no cloud dependencies)
- **SQLite Database**: Maintains a local job database with comprehensive job listings

## Architecture

### System Overview

```
User Interface (Streamlit)
        ↓
Resume Upload & Processing (app.py)
        ↓
Orchestrator Agent
        ↓
┌─────────────────────────────────────────────┐
│  Sequential Agent Pipeline                  │
├─────────────────────────────────────────────┤
│ 1. Extractor Agent    → PDF text extraction │
│ 2. Analyzer Agent     → Profile analysis    │
│ 3. Matcher Agent      → Job matching (DB)   │
│ 4. Screener Agent     → Fit evaluation      │
│ 5. Recommender Agent  → Final recommendations│
└─────────────────────────────────────────────┘
        ↓
Ollama LLM Server (http://localhost:11434)
        ↓
SQLite Database (jobs.sqlite)
```

### Agent-Based Communication Flow

Each agent is autonomous and specializes in a single task:

1. **ExtractorAgent** - Parses resume PDF and structures resume data
2. **AnalyzerAgent** - Analyzes candidate skills, experience level, and achievements
3. **MatcherAgent** - Searches the job database and calculates match scores
4. **ScreenerAgent** - Evaluates candidate-job fit with detailed analysis
5. **RecommenderAgent** - Generates final recommendations with reasoning

Agents communicate through **context dictionaries** containing intermediate results. The Orchestrator coordinates the entire workflow.

## Prerequisites

### Required Software

- **Python 3.13+** (tested with Python 3.14)
- **Ollama** - Local LLM server
  - Download from: https://ollama.ai
  - Must be running on port 11434
  - Uses `llama3.2` model

### Installation Steps

#### 1. Set Up Ollama

```bash
# Download and install Ollama from https://ollama.ai
# Start Ollama server (ensure it's running on http://localhost:11434)
ollama pull llama3.2
ollama serve
```

#### 2. Create Virtual Environment

```powershell
# Navigate to project directory
cd C:\Users\DELL\Desktop\ollama

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

#### 3. Install Dependencies

```powershell
# Using pip
pip install -r requirements.txt

# Or with uv package manager
uv pip install -r requirements.txt
```

#### 4. Seed the Database

```powershell
# Populate database with sample job listings
python db/seed_jobs.py
```

## Project Structure

```
ollama/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── agents/                         # AI Agent modules
│   ├── __init__.py
│   ├── base_agent.py              # Base class for all agents
│   ├── orchestrator.py            # Orchestrator agent (coordinator)
│   ├── extractor_agent.py         # Resume text extraction
│   ├── analyzer_agent.py          # Candidate profile analysis
│   ├── matcher_agent.py           # Job matching logic
│   ├── screener_agent.py          # Candidate screening
│   ├── profile_enhancer_agent.py  # Profile enhancement
│   └── recommender_agent.py       # Final recommendations
│
├── db/                            # Database layer
│   ├── __init__.py
│   ├── database.py                # JobDatabase class (SQLite)
│   ├── schema.sql                 # Database schema
│   ├── jobs.sqlite                # SQLite database file
│   └── seed_jobs.py               # Sample job data loader
│
├── data/                          # Data utilities
│   ├── __init__.py
│   └── job_database.py
│
├── utils/                         # Utility modules
│   ├── __init__.py
│   ├── logger.py                  # Logging setup
│   └── exceptions.py              # Custom exceptions
│
├── uploads/                       # Temporary uploaded resumes (auto-created)
└── results/                       # Analysis results output (auto-created)
```

## How to Run

### 1. Activate Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Ensure Ollama is Running

```bash
# In a separate terminal, start Ollama
ollama serve
# Should show: Listening on 127.0.0.1:11434
```

### 3. Start the Streamlit App

```powershell
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage Guide

### Uploading and Processing Resumes

1. **Upload Resume**: Click "Upload Resume" in the sidebar
2. **Select PDF File**: Choose a resume PDF from your computer
3. **Wait for Processing**: The app processes through the agent pipeline
4. **View Results**: See extracted information, analysis, matched jobs, and recommendations

### Understanding Results

**Extraction Tab**

- Structured resume data (contact info, experience, education, skills)

**Analysis Tab**

- Technical skills identified
- Experience level (Junior/Mid-level/Senior)
- Key achievements extracted

**Matching Tab**

- Top 3 job matches from database
- Match score percentages (based on skill overlap)
- Job details (title, company, location, salary range)

**Screening Tab**

- Detailed fit analysis
- Qualification alignment percentage
- Strengths and potential gaps

**Recommendation Tab**

- Final recommendations with reasoning
- Prioritized job suggestions

## Configuration

### Change LLM Model

Edit [agents/base_agent.py](agents/base_agent.py) to change the model:

```python
response = self.ollama_client.chat.completions.create(
    model="llama3.2",  # Change this to another model
    messages=[...]
)
```

Available models: `llama3.2`, `llama3`, `llama2`, `mistral`, etc.

### Adjust Match Threshold

Edit [agents/matcher_agent.py](agents/matcher_agent.py) to change job match score threshold:

```python
if match_score >= 30:  # Lower this for more matches, raise for stricter filtering
    scored_jobs.append({...})
```

## Database Management

### View Database Contents

Using SQLite extension in VS Code:

1. Install "SQLite" extension
2. Right-click `db/jobs.sqlite`
3. Click "Open Database"

Or via Python:

```python
from db.database import JobDatabase
db = JobDatabase()
jobs = db.get_all_jobs()
for job in jobs:
    print(f"{job['title']} at {job['company']}")
```

### Add Custom Jobs

```python
from db.database import JobDatabase

db = JobDatabase()
db.add_job({
    "title": "Machine Learning Engineer",
    "company": "TechCorp",
    "location": "San Francisco, CA",
    "type": "Full-time",
    "experience_level": "Senior",
    "salary_range": "$150,000 - $200,000",
    "description": "Build ML models for production systems",
    "requirements": ["Python", "TensorFlow", "AWS", "5+ years experience"],
    "benefits": ["Health insurance", "Stock options", "Remote work"]
})
```

### Reset Database

```powershell
# Delete old database
Remove-Item db/jobs.sqlite

# Reseed with sample data
python db/seed_jobs.py
```

## Dependencies

| Package               | Version  | Purpose                         |
| --------------------- | -------- | ------------------------------- |
| openai                | >=1.40.0 | LLM API client for Ollama       |
| pdfminer.six          | 20221105 | PDF text extraction             |
| python-dotenv         | 1.0.0    | Environment variable management |
| rich                  | 13.7.0   | Terminal formatting             |
| streamlit             | Latest   | Web UI framework                |
| streamlit-option-menu | Latest   | Navigation menu UI              |
| numpy                 | Latest   | Numerical computing             |

## Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit_option_menu'"

```powershell
pip install streamlit-option-menu
```

### "Cannot connect to Ollama"

- Ensure Ollama is running: `ollama serve`
- Check if it's accessible at `http://localhost:11434`
- Verify firewall isn't blocking port 11434

### "No jobs found" / Empty database

```powershell
# Reseed the database
python db/seed_jobs.py
```

### "Client.**init**() got unexpected keyword argument 'proxies'"

Update packages:

```powershell
pip install --upgrade "openai>=1.40.0" "httpx>=0.24.0,<0.28"
```

### PDF text extraction issues

- Ensure PDF is text-based (not scanned images)
- Try a different resume format or OCR the PDF first

## Performance Tips

1. **Faster Processing**: Use smaller Ollama models (`mistral` is faster than `llama3.2`)
2. **Batch Processing**: Process multiple resumes in sequence (not parallel)
3. **Database Queries**: Job matching is fastest with well-indexed requirements
4. **Memory**: Ollama requires ~4GB RAM minimum for llama3.2

## Development

### Adding New Agents

1. Create new file in `agents/` directory
2. Inherit from `BaseAgent` class
3. Implement `async def run(self, messages)` method
4. Add to `OrchestratorAgent._setup_agents()`

Example:

```python
from .base_agent import BaseAgent
from typing import Dict, Any

class NewAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="NewAgent",
            instructions="Your agent instructions here"
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        prompt = messages[-1]["content"]
        response = self._query_ollama(prompt)
        return self._parse_json_safely(response)
```

### Debugging

Enable logging:

```python
from utils.logger import setup_logger
logger = setup_logger()
logger.debug("Debug message")
logger.error("Error message")
```

## API Endpoints

This is a **local-only system** with no REST APIs. All communication happens:

- **Frontend ↔ Backend**: Streamlit session state
- **Backend ↔ LLM**: Local Ollama HTTP client
- **Backend ↔ Database**: SQLite direct connection

## Future Enhancements

- [ ] Parallel agent processing for faster results
- [ ] Multiple LLM model support selection in UI
- [ ] Resume enrichment with LinkedIn data
- [ ] Candidate ranking system
- [ ] Email notifications for job matches
- [ ] Admin panel for job management
- [ ] Interview question generation
- [ ] Salary negotiation advice

## License

This project is for educational purposes.

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review agent logs in console output
3. Verify Ollama is running and accessible
4. Check database integrity: `python db/seed_jobs.py`

## Key Insights

- **Zero Cloud Dependencies**: Everything runs locally
- **Extensible Agent System**: Easy to add new processing stages
- **Database-Driven**: Easily customize job listings
- **LLM-Agnostic**: Switch Ollama models as needed
- **Privacy-First**: Resumes never leave your machine

---

**Last Updated**: January 23, 2026  
**Python Version**: 3.13+  
**Ollama Model**: llama3.2
