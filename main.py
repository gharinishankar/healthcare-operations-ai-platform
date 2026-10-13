
from fastapi import FastAPI, HTTPException
from pathlib import Path
import sqlite3

app = FastAPI(
    title="Healthcare Operations AI Platform",
    description="Healthcare analytics and AI-powered insights API",
    version="1.0.0"
)

DB_PATH = Path(__file__).parent / "healthcare_operations.db"


@app.get("/")
def home():
    return {
        "message": "Healthcare Operations AI Platform is running!",
        "status": "healthy"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Healthcare Operations API"
    }


@app.get("/appointments/summary")
def appointment_summary():

    if not DB_PATH.is_file():
        raise HTTPException(
            status_code=503,
            detail="Healthcare database is unavailable"
        )

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row

            rows = conn.execute("""
                SELECT
                    status,
                    COUNT(*) AS total
                FROM appointments
                GROUP BY status
            """).fetchall()

    except sqlite3.Error:
        raise HTTPException(
            status_code=503,
            detail="Unable to read appointment data"
        )

    status_counts = {
        "Attended": 0,
        "Did Not Attend": 0,
        "Cancelled": 0,
        "Unknown": 0
    }

    for row in rows:
        status_counts[row["status"]] = row["total"]

    return {
        "total_appointments": sum(status_counts.values()),
        "status_breakdown": status_counts
    }


@app.get("/practices/dna-rates")
def get_dna_rates():

    if not DB_PATH.is_file():
        raise HTTPException(
            status_code=503,
            detail="Healthcare database is unavailable"
        )

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row

            rows = conn.execute("""
                SELECT
                    practice,
                    COUNT(*) AS total_appointments,

                    SUM(
                        CASE WHEN status = 'Attended'
                        THEN 1 ELSE 0 END
                    ) AS attended,

                    SUM(
                        CASE WHEN status = 'Did Not Attend'
                        THEN 1 ELSE 0 END
                    ) AS did_not_attend,

                    ROUND(
                        100.0 * SUM(
                            CASE WHEN status = 'Did Not Attend'
                            THEN 1 ELSE 0 END
                        )
                        / NULLIF(
                            SUM(
                                CASE WHEN status IN
                                    ('Attended', 'Did Not Attend')
                                THEN 1 ELSE 0 END
                            ), 0
                        ),
                        2
                    ) AS dna_rate_percent

                FROM appointments
                GROUP BY practice
                ORDER BY dna_rate_percent DESC
            """).fetchall()

    except sqlite3.Error:
        raise HTTPException(
            status_code=503,
            detail="Unable to calculate DNA rates"
        )

    return {
        "metric_definition": (
            "DNA / (Attended + DNA) * 100. "
            "Cancelled and unknown statuses excluded."
        ),
        "practices": [dict(row) for row in rows]
    }


@app.get("/data-quality")
def get_data_quality(threshold: float = 5.0):

    if not 0 <= threshold <= 100:
        raise HTTPException(
            status_code=400,
            detail="Threshold must be between 0 and 100"
        )

    if not DB_PATH.is_file():
        raise HTTPException(
            status_code=503,
            detail="Healthcare database is unavailable"
        )

    try:
        with sqlite3.connect(DB_PATH) as conn:
            total = conn.execute("""
                SELECT COUNT(*) FROM appointments
            """).fetchone()[0]

            unknown = conn.execute("""
                SELECT COUNT(*)
                FROM appointments
                WHERE status = 'Unknown'
                   OR status IS NULL
            """).fetchone()[0]

            duplicates = conn.execute("""
                SELECT COUNT(*) - COUNT(DISTINCT appointment_id)
                FROM appointments
            """).fetchone()[0]

    except sqlite3.Error:
        raise HTTPException(
            status_code=503,
            detail="Unable to calculate data quality"
        )

    if total == 0:
        return {
            "total_records": 0,
            "status": "NO DATA"
        }

    unknown_percentage = round(
        unknown / total * 100, 2
    )

    status = (
        "WARNING"
        if unknown_percentage > threshold or duplicates > 0
        else "PASS"
    )

    return {
        "total_records": total,
        "unknown_count": unknown,
        "unknown_percentage": unknown_percentage,
        "duplicate_ids": duplicates,
        "threshold": threshold,
        "status": status
    }


@app.get("/ai/practice-analysis")
def ai_practice_analysis(practice_name: str):
    from analytics import calculate_dna_rate
    from ai_assistant import generate_investigation_ideas
    from urllib.error import URLError, HTTPError

    if not DB_PATH.is_file():
        raise HTTPException(
            status_code=503,
            detail="Healthcare database is unavailable"
        )

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row

            row = conn.execute("""
                SELECT
                    practice,
                    COUNT(*) AS total_appointments,
                    SUM(CASE WHEN status = 'Attended'
                        THEN 1 ELSE 0 END) AS attended,
                    SUM(CASE WHEN status = 'Did Not Attend'
                        THEN 1 ELSE 0 END) AS did_not_attend
                FROM appointments
                WHERE LOWER(practice) = LOWER(?)
                GROUP BY practice
            """, (practice_name.strip(),)).fetchone()

    except sqlite3.Error:
        raise HTTPException(
            status_code=503,
            detail="Unable to read appointment data"
        )

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Practice not found"
        )

    practice = dict(row)

    attended = practice["attended"]
    dna = practice["did_not_attend"]
    eligible = attended + dna

    rate = calculate_dna_rate(dna, attended)

    if rate is None:
        raise HTTPException(
            status_code=422,
            detail="No eligible appointments for DNA calculation"
        )

    verified_summary = (
        f"{practice['practice']} recorded {dna} missed "
        f"appointments and {attended} attended appointments. "
        f"The DNA rate was {rate:.2f}% "
        f"({dna} / {eligible} eligible appointments). "
        "Cancelled and unknown appointments were excluded. "
        "These figures come from synthetic data."
    )

    try:
        suggestions = generate_investigation_ideas(
            verified_summary
        )
    except (URLError, HTTPError, TimeoutError):
        raise HTTPException(
            status_code=503,
            detail="Local AI model is unavailable"
        )

    return {
        "practice": practice["practice"],
        "verified_statistics": {
            "total_appointments": practice["total_appointments"],
            "attended": attended,
            "did_not_attend": dna,
            "eligible_appointments": eligible,
            "dna_rate_percent": rate
        },
        "verified_summary": verified_summary,
        "ai_investigation_ideas": suggestions,
        "data_source": "Synthetic appointment data"
    }
