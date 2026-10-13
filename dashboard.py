
import streamlit as st
import pandas as pd
import json
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Healthcare Operations AI",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Healthcare Operations AI Dashboard")
st.caption("AI-powered healthcare analytics | Synthetic data only")


def get_data(endpoint):
    with urlopen(API_URL + endpoint, timeout=10) as response:
        return json.load(response)


try:
    summary = get_data("/appointments/summary")
    quality = get_data("/data-quality")
    dna_data = get_data("/practices/dna-rates")

except (URLError, HTTPError, TimeoutError) as error:
    st.error("Unable to connect to the Healthcare Operations API.")
    st.info("Make sure your FastAPI server is running.")
    st.stop()


total = summary["total_appointments"]
statuses = summary["status_breakdown"]

attended = statuses["Attended"]
dna = statuses["Did Not Attend"]
eligible = attended + dna

overall_dna_rate = (
    round(dna / eligible * 100, 2)
    if eligible > 0 else 0
)

col1, col2, col3 = st.columns(3)

col1.metric("Total Appointments", f"{total:,}")
col2.metric("Overall DNA Rate", f"{overall_dna_rate:.2f}%")
col3.metric("Data Quality", quality["status"])

st.divider()

st.subheader("Appointment Outcomes")

outcomes_df = pd.DataFrame(
    {
        "Status": list(statuses.keys()),
        "Appointments": list(statuses.values())
    }
).set_index("Status")

st.bar_chart(outcomes_df)

st.divider()

st.subheader("DNA Rate by Practice")

practices_df = pd.DataFrame(dna_data["practices"])

st.bar_chart(
    practices_df.set_index("practice")["dna_rate_percent"]
)

st.caption(
    "DNA rate = Did Not Attend / (Attended + Did Not Attend) × 100. "
    "Cancelled and unknown appointments are excluded."
)

st.subheader("Practice Performance Details")

st.dataframe(practices_df, use_container_width=True)


st.divider()

st.subheader("🤖 AI Practice Analyst")

st.write(
    "Select a GP practice to explore its verified appointment "
    "statistics and generate AI-assisted investigation ideas."
)

practice_names = practices_df["practice"].tolist()

selected_practice = st.selectbox(
    "Choose a practice",
    practice_names
)

if st.button("Generate AI Analysis", type="primary"):

    from urllib.parse import quote

    with st.spinner("Analysing practice performance using local AI..."):
        try:
            endpoint = (
                "/ai/practice-analysis?practice_name="
                + quote(selected_practice)
            )

            with urlopen(API_URL + endpoint, timeout=180) as response:
                analysis = json.load(response)

            st.success("Analysis completed!")

            st.markdown("#### Verified Statistics")
            st.write(analysis["verified_summary"])

            st.markdown("#### AI Investigation Ideas")
            st.write(analysis["ai_investigation_ideas"])

            st.caption(
                "AI suggestions are hypotheses, not established causes. "
                "All appointment data are synthetic."
            )

        except Exception as error:
            st.error("AI analysis could not be completed.")
            st.code(str(error))
