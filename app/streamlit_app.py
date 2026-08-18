"""Interactive portfolio demo for ticket priority prediction."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from it_ticket_priority.inference import TicketPriorityPredictor
from it_ticket_priority.schemas import TicketRequest

st.set_page_config(
    page_title="AI Service Desk Priority Predictor",
    page_icon="🎫",
    layout="wide",
)


@st.cache_resource
def load_predictor() -> TicketPriorityPredictor:
    return TicketPriorityPredictor()


st.title("AI-Powered IT Service Desk Priority Predictor")
st.caption(
    "Portfolio demo: hybrid NLP + operational metadata classification with explainable predictions."
)

with st.sidebar:
    st.header("Model behavior")
    st.markdown(
        "- P1 predictions always require analyst confirmation.\n"
        "- Predictions below 65% confidence are routed to human review.\n"
        "- The included model is trained only on reproducible synthetic data."
    )

left, right = st.columns([2, 1])
with left:
    description = st.text_area(
        "Ticket description",
        value=(
            "The logistics application cannot process orders at warehouse north. "
            "All warehouse processing is blocked and there is no workaround."
        ),
        height=150,
    )
    category = st.selectbox(
        "Category",
        [
            "business_application",
            "network",
            "security",
            "identity_access",
            "endpoint",
            "collaboration",
            "hardware",
            "service_request",
        ],
    )
    channel = st.selectbox("Channel", ["portal", "email", "phone", "monitoring"])
    service_criticality = st.selectbox(
        "Service criticality",
        ["mission_critical", "high", "medium", "low"],
    )
    site = st.selectbox(
        "Site",
        ["warehouse_north", "warehouse_south", "headquarters", "regional_office", "remote_user"],
    )

with right:
    affected_users = st.number_input("Affected users", min_value=0, max_value=100_000, value=180)
    related_incidents = st.number_input(
        "Related incidents in 30 days", min_value=0, max_value=10_000, value=6
    )
    vip_user = int(st.checkbox("VIP user involved"))
    outage_indicator = int(st.checkbox("Outage indicator", value=True))
    security_indicator = int(st.checkbox("Security indicator"))
    business_hours = int(st.checkbox("Business hours", value=True))

if st.button("Predict priority", type="primary", use_container_width=True):
    request = TicketRequest(
        description=description,
        category=category,
        channel=channel,
        service_criticality=service_criticality,
        site=site,
        affected_users=int(affected_users),
        vip_user=vip_user,
        outage_indicator=outage_indicator,
        security_indicator=security_indicator,
        business_hours=business_hours,
        related_incidents_30d=int(related_incidents),
    )

    try:
        result = load_predictor().predict(request)
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()

    priority = result["predicted_priority"]
    confidence = result["confidence"]
    metric_col, review_col = st.columns(2)
    metric_col.metric("Predicted priority", priority)
    metric_col.metric("Confidence", f"{confidence:.1%}")
    if result["requires_human_review"]:
        review_col.warning("Human analyst review required")
    else:
        review_col.success("Prediction may enter the normal triage workflow")

    probability_frame = pd.DataFrame(
        {
            "Priority": list(result["probabilities"].keys()),
            "Probability": list(result["probabilities"].values()),
        }
    ).set_index("Priority")
    st.subheader("Class probabilities")
    st.bar_chart(probability_frame)

    st.subheader("Top positive contributors")
    contributors = pd.DataFrame(result["top_contributors"])
    if contributors.empty:
        st.info("No local feature explanation is available for this estimator.")
    else:
        st.dataframe(contributors, use_container_width=True, hide_index=True)
