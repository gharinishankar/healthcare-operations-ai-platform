# Healthcare Operations AI Platform

A full-stack healthcare analytics application built with Python, FastAPI, SQLite, Streamlit and a locally hosted Qwen language model.

The platform analyses synthetic GP appointment records, compares operational performance across six practices, identifies data-quality issues and generates AI-assisted investigation suggestions.

> **Project status:** Local working prototype. Uses synthetic data only. Not intended for clinical decision-making.

## Features

- **Appointment analytics:** Summarises appointment outcomes and attendance.
- **Practice comparisons:** Calculates Did Not Attend (DNA) rates across six practices.
- **Interactive dashboard:** Displays operational KPIs, charts and practice-level performance.
- **Data-quality monitoring:** Flags records with unknown appointment statuses.
- **AI Practice Analyst:** Uses a locally hosted language model to suggest possible areas for operational investigation.
- **API validation:** Includes basic checks for valid and invalid API requests.

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Data processing | pandas |
| Database | SQLite |
| Backend API | FastAPI |
| Frontend | Streamlit |
| AI model | Qwen 2.5 3B via Ollama |
| Data visualisation | Streamlit charts |
| Development environment | Jupyter Notebook |

## Architecture

```text
Streamlit Dashboard
        |
        v
    FastAPI
     /   \
    v     v
 SQLite  Ollama
Database  |
          v
     Qwen 2.5 3B
```

The dashboard communicates with FastAPI rather than querying the database directly.

## DNA Rate Calculation

DNA means **Did Not Attend**.

The platform calculates DNA rates using:

```text
DNA Rate (%) = DNA appointments / (Attended + DNA appointments) × 100
```

Cancelled appointments and records with unknown statuses are excluded from the denominator.

Python calculates and verifies the statistics independently of the language model.

## Example Results

The initial synthetic dataset contains 1,000 appointments across six GP practices.

| Metric | Value |
|---|---:|
| Total appointments | 1,000 |
| Attended | 327 |
| Did Not Attend | 162 |
| Cancelled | 313 |
| Unknown status | 198 |
| Overall DNA rate | 33.13% |
| Unknown status rate | 19.8% |

These results describe generated demonstration data and are not real NHS performance figures.

## Responsible AI Design

The AI component does not calculate official metrics or establish the causes of missed appointments.

Instead:

1. Python retrieves and verifies the appointment statistics.
2. The verified summary is passed to the local AI model.
3. The model suggests possible areas for further investigation.
4. Suggestions are clearly distinguished from verified findings.

No real patient information is used.

## Local Development

The application currently requires:

- Python
- FastAPI and Uvicorn
- Streamlit
- pandas
- Ollama with the `qwen2.5:3b` model
- A locally generated SQLite database containing synthetic appointment records

To download the local AI model:

```bash
ollama pull qwen2.5:3b
```

To start the backend:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

To start the dashboard in another terminal:

```bash
streamlit run dashboard.py
```

The dashboard is available at:

```text
http://127.0.0.1:8501
```

**Note:** The synthetic-data generation and database setup process is not yet packaged for fresh installations. These steps will be added in a future update.

## Future Improvements

- Reproducible synthetic-data generation and database setup
- Automated unit and integration tests
- Improved dashboard filtering and visual design
- API error handling and reliability improvements
- Containerisation and deployment documentation
- Expanded operational analytics

## Disclaimer

This is an independent portfolio project for software engineering, data analytics and AI development. It is not affiliated with or endorsed by the NHS.

All appointment data are synthetic. The application is not designed for clinical use.
