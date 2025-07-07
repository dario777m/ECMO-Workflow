import streamlit as st
import math
import pandas as pd
import altair as alt

st.set_page_config(page_title="ECMO Cannula & CI Estimator", layout="centered")
st.title("🩸 ECMO Cannula & Cardiac Index Estimator")

# Sidebar Inputs
st.sidebar.header("Patient Info")
weight = st.sidebar.number_input("Weight (kg)", min_value=1.0, step=0.1)
height = st.sidebar.number_input("Height (cm)", min_value=30.0, step=0.1)
sex = st.sidebar.selectbox("Sex", ["Male", "Female"])
ecmo_mode = st.sidebar.selectbox("ECMO Mode", ["VV", "VA"])

# Cannula flow logic
def cannula_rec(required_flow):
    # Add 30% safety margin
    min_needed = required_flow * 1.3

    # Define cannulas and flow capacity
    cannulas = [
        ("19 Fr", 3.5),
        ("21 Fr", 4.5),
        ("23 Fr", 5.5),
        ("25 Fr", 6.5),
        ("27 Fr", 7.5),
        ("29+ Fr", 8.5)
    ]

    for size, max_flow in cannulas:
        if max_flow >= min_needed:
            return size, max_flow

    return "29+ Fr", 8.5  # fallback if no match

if weight > 0 and height > 0:
    # --- Du Bois BSA Calculation ---
    bsa = 0.007184 * (height ** 0.725) * (weight ** 0.425)
    st.markdown(f"### 🧮 BSA (Du Bois): `{bsa:.2f} m²`")

    target_ci = 3.0
    target_flow = target_ci * bsa
    st.markdown(f"### 🎯 Target CI: `{target_ci:.1f} L/min/m²` → `{target_flow:.1f} L/min`")

    # Get recommended cannula
    recommended_cannula, max_flow = cannula_rec(target_flow)
    st.markdown(f"### 🔧 Recommended Cannula: **{recommended_cannula}** (max {max_flow} L/min)")

    # Calculate ECMO CI contribution
    ecmo_ci = max_flow / bsa
    ci_met = min(ecmo_ci, target_ci)
    ci_excess = max(0, ecmo_ci - target_ci)
    achieved_ci = ecmo_ci

    # Cannula Flow Reference
    st.markdown("### 🔍 Cannula Flow Reference Guide")
    cannula_data = {
        "19 Fr": {"flow": "2.5–3.5 L/min", "notes": "Small adult or low-flow support"},
        "21 Fr": {"flow": "3.5–4.5 L/min", "notes": "Moderate adult flow"},
        "23 Fr": {"flow": "4.5–5.5 L/min", "notes": "Standard drainage for VV ECMO"},
        "25 Fr": {"flow": "5.5–6.5 L/min", "notes": "High flow needs"},
        "27 Fr": {"flow": "6.5–7.5 L/min", "notes": "Large adult or obese patient"},
        "29+ Fr": {"flow": "7.5+ L/min", "notes": "Very high flow, VA or VV-VA setups"}
    }

    selected = st.selectbox("Choose a cannula size to see flow info:", list(cannula_data.keys()))
    if selected:
        st.write(f"**Typical Flow:** {cannula_data[selected]['flow']}")
        st.write(f"**Notes:** {cannula_data[selected]['notes']}")

    # --- Side-by-side Chart Layout ---
    chart_df = pd.DataFrame({
        "Label": ["Target CI", "ECMO CI", "ECMO CI"],
        "Part": ["Target", "Met", "Excess"],
        "CI": [target_ci, ci_met, ci_excess]
    })

    color_scale = alt.Scale(
        domain=["Target", "Met", "Excess"],
        range=["#cccccc", "#4b9cd3", "#4caf50"]
    )

    chart = alt.Chart(chart_df).mark_bar().encode(
        x=alt.X("Label:N", title=None),
        y=alt.Y("CI:Q", title="Cardiac Index (L/min/m²)", stack="zero",
                scale=alt.Scale(domain=[0, max(achieved_ci, target_ci) + 0.5])),
        color=alt.Color("Part:N", scale=color_scale),
        tooltip=["Label", "Part", "CI"]
    ).properties(
        title="Cardiac Index: Target vs ECMO Capacity",
        width=300,
        height=300
    )

    st.altair_chart(chart, use_container_width=False)

    st.markdown("⚙️ **Initial RPM Estimate:** `2500 - 3200`")
    st.caption("Blue shows ECMO support meeting CI goal. Green shows ECMO CI exceeding goal. Gray is full CI target.")

else:
    st.info("👈 Enter weight and height to get started.")


