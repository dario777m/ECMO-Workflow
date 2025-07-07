import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="ECMO Candidacy Checker", layout="wide")

st.title("🫀 ECMO Candidacy Checker with SAVE + SOFA + Criteria")

note = "SOAP Note\n===========\n"

# --------------------- Patient Info ---------------------
st.header("📝 Patient Info")
name = st.text_input("Patient Name")
age = st.number_input("Age", min_value=0, max_value=120, value=40)
weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, value=70.0)
height = st.number_input("Height (cm)", min_value=0.0, max_value=250.0, value=170.0)
sex = st.selectbox("Sex", ["Male", "Female"])
bmi = weight / ((height/100) ** 2) if height > 0 else 0

# --------------------- SAVE Score ---------------------
st.header("📊 SAVE Score")
st.markdown("**Survival After Veno-Arterial ECMO Score**")

col1, col2, col3 = st.columns(3)

with col1:
    # Age points
    age_points = 0
    if age < 18:
        age_points = 0
    elif age < 45:
        age_points = 7
    elif age < 55:
        age_points = 12
    elif age < 65:
        age_points = 18
    else:
        age_points = 22
    
    st.metric("Age Points", age_points)
    
    # Weight points
    weight_points = 0
    if weight < 65:
        weight_points = 0
    elif weight < 85:
        weight_points = 1
    elif weight < 95:
        weight_points = 2
    else:
        weight_points = 3
    
    st.metric("Weight Points", weight_points)

with col2:
    # Pre-ECMO organ failure
    pre_ecmo_cardiac_arrest = st.checkbox("Pre-ECMO Cardiac Arrest")
    pre_ecmo_cardiac_arrest_points = 15 if pre_ecmo_cardiac_arrest else 0
    st.metric("Pre-ECMO Cardiac Arrest Points", pre_ecmo_cardiac_arrest_points)
    
    # Acute etiology
    acute_etiology = st.selectbox("Acute Etiology", 
                                 ["Post-cardiotomy", "Acute MI", "Myocarditis", "Other"])
    acute_etiology_points = {"Post-cardiotomy": 0, "Acute MI": 6, "Myocarditis": 8, "Other": 4}
    st.metric("Acute Etiology Points", acute_etiology_points[acute_etiology])

with col3:
    # Duration of intubation
    intubation_duration = st.number_input("Duration of Intubation (hours)", min_value=0, value=0)
    intubation_points = 0
    if intubation_duration < 10:
        intubation_points = 0
    elif intubation_duration < 29:
        intubation_points = 3
    else:
        intubation_points = 7
    st.metric("Intubation Duration Points", intubation_points)
    
    # Diastolic blood pressure
    dbp = st.number_input("Diastolic BP (mmHg)", min_value=0, value=80)
    dbp_points = 0
    if dbp < 20:
        dbp_points = 11
    elif dbp < 40:
        dbp_points = 8
    elif dbp < 60:
        dbp_points = 5
    else:
        dbp_points = 0
    st.metric("Diastolic BP Points", dbp_points)

# Calculate SAVE score
save_score = age_points + weight_points + pre_ecmo_cardiac_arrest_points + acute_etiology_points[acute_etiology] + intubation_points + dbp_points

st.markdown(f"### 🎯 **SAVE Score: {save_score}**")

# SAVE Score interpretation
if save_score <= -5:
    save_risk = "Very High Risk"
    save_survival = "~18%"
elif save_score <= -1:
    save_risk = "High Risk"
    save_survival = "~33%"
elif save_score <= 5:
    save_risk = "Medium Risk"
    save_survival = "~50%"
else:
    save_risk = "Low Risk"
    save_survival = "~75%"

st.info(f"**Risk Level:** {save_risk} | **Predicted Survival:** {save_survival}")

# --------------------- SOFA Score ---------------------
st.header("🏥 SOFA Score")
st.markdown("**Sequential Organ Failure Assessment**")

sofa_col1, sofa_col2, sofa_col3 = st.columns(3)

with sofa_col1:
    # Respiratory
    pao2_fio2 = st.number_input("PaO₂/FiO₂ ratio", min_value=0, value=300)
    if pao2_fio2 >= 400:
        resp_points = 0
    elif pao2_fio2 >= 300:
        resp_points = 1
    elif pao2_fio2 >= 200:
        resp_points = 2
    elif pao2_fio2 >= 100:
        resp_points = 3
    else:
        resp_points = 4
    st.metric("Respiratory Points", resp_points)
    
    # Coagulation
    platelets = st.number_input("Platelets (×10³/μL)", min_value=0, value=150)
    if platelets >= 150:
        coag_points = 0
    elif platelets >= 100:
        coag_points = 1
    elif platelets >= 50:
        coag_points = 2
    elif platelets >= 20:
        coag_points = 3
    else:
        coag_points = 4
    st.metric("Coagulation Points", coag_points)

with sofa_col2:
    # Liver
    bilirubin = st.number_input("Bilirubin (mg/dL)", min_value=0.0, value=1.0)
    if bilirubin < 1.2:
        liver_points = 0
    elif bilirubin < 2.0:
        liver_points = 1
    elif bilirubin < 6.0:
        liver_points = 2
    elif bilirubin < 12.0:
        liver_points = 3
    else:
        liver_points = 4
    st.metric("Liver Points", liver_points)
    
    # Cardiovascular
    map = st.number_input("Mean Arterial Pressure (mmHg)", min_value=0, value=70)
    vasopressors = st.selectbox("Vasopressors", ["None", "Dopamine ≤5 or Dobutamine", "Dopamine >5 or NE ≤0.1", "NE >0.1 or Epi ≤0.1", "NE >0.1 or Epi >0.1"])
    vasopressor_points = {"None": 0, "Dopamine ≤5 or Dobutamine": 1, "Dopamine >5 or NE ≤0.1": 2, "NE >0.1 or Epi ≤0.1": 3, "NE >0.1 or Epi >0.1": 4}
    st.metric("Cardiovascular Points", vasopressor_points[vasopressors])

with sofa_col3:
    # CNS
    glasgow = st.number_input("Glasgow Coma Scale", min_value=3, max_value=15, value=15)
    if glasgow >= 15:
        cns_points = 0
    elif glasgow >= 13:
        cns_points = 1
    elif glasgow >= 10:
        cns_points = 2
    elif glasgow >= 6:
        cns_points = 3
    else:
        cns_points = 4
    st.metric("CNS Points", cns_points)
    
    # Renal
    creatinine = st.number_input("Creatinine (mg/dL)", min_value=0.0, value=1.0)
    urine_output = st.number_input("Urine Output (mL/day)", min_value=0, value=500)
    if creatinine < 1.2 and urine_output >= 500:
        renal_points = 0
    elif creatinine < 2.0 or urine_output < 500:
        renal_points = 1
    elif creatinine < 3.5 or urine_output < 200:
        renal_points = 2
    elif creatinine < 5.0 or urine_output < 200:
        renal_points = 3
    else:
        renal_points = 4
    st.metric("Renal Points", renal_points)

# Calculate SOFA score
sofa_score = resp_points + coag_points + liver_points + vasopressor_points[vasopressors] + cns_points + renal_points

st.markdown(f"### 🎯 **SOFA Score: {sofa_score}**")

# SOFA interpretation
if sofa_score <= 6:
    sofa_mortality = "~10%"
elif sofa_score <= 9:
    sofa_mortality = "~15%"
elif sofa_score <= 12:
    sofa_mortality = "~40%"
elif sofa_score <= 15:
    sofa_mortality = "~60%"
else:
    sofa_mortality = "~80%"

st.info(f"**Predicted Mortality:** {sofa_mortality}")

# --------------------- ECMO Criteria ---------------------
st.header("✅ ECMO Candidacy Criteria")

criteria_col1, criteria_col2 = st.columns(2)

with criteria_col1:
    st.subheader("🟢 Inclusion Criteria")
    
    # Reversible condition
    reversible_condition = st.checkbox("Reversible underlying condition")
    
    # Age criteria
    age_appropriate = age >= 18 and age <= 75
    
    # BMI criteria
    bmi_appropriate = 18 <= bmi <= 50
    
    # No absolute contraindications
    no_contraindications = st.checkbox("No absolute contraindications")
    
    # Informed consent
    informed_consent = st.checkbox("Informed consent obtained")
    
    # Failure of conventional therapy
    conventional_failure = st.checkbox("Failure of conventional therapy")
    
    inclusion_score = sum([reversible_condition, age_appropriate, bmi_appropriate, 
                          no_contraindications, informed_consent, conventional_failure])
    
    st.metric("Inclusion Criteria Met", f"{inclusion_score}/6")

with criteria_col2:
    st.subheader("🔴 Exclusion Criteria")
    
    # Absolute contraindications
    irreversible_brain_damage = st.checkbox("Irreversible brain damage")
    terminal_illness = st.checkbox("Terminal illness")
    severe_bleeding = st.checkbox("Severe bleeding/coagulopathy")
    severe_immunosuppression = st.checkbox("Severe immunosuppression")
    advanced_age = age > 75
    extreme_bmi = bmi < 18 or bmi > 50
    
    exclusion_count = sum([irreversible_brain_damage, terminal_illness, severe_bleeding, 
                          severe_immunosuppression, advanced_age, extreme_bmi])
    
    st.metric("Exclusion Criteria", f"{exclusion_count} present")

# --------------------- Final Assessment ---------------------
st.header("🎯 Final ECMO Candidacy Assessment")

# Calculate overall candidacy
candidacy_score = 0
candidacy_reasons = []

# SAVE score assessment
if save_score >= 5:
    candidacy_score += 2
    candidacy_reasons.append("✅ Good SAVE score (low risk)")
elif save_score >= -1:
    candidacy_score += 1
    candidacy_reasons.append("⚠️ Moderate SAVE score")
else:
    candidacy_score -= 1
    candidacy_reasons.append("❌ Poor SAVE score (high risk)")

# SOFA score assessment
if sofa_score <= 9:
    candidacy_score += 2
    candidacy_reasons.append("✅ Acceptable SOFA score")
elif sofa_score <= 12:
    candidacy_score += 1
    candidacy_reasons.append("⚠️ Elevated SOFA score")
else:
    candidacy_score -= 1
    candidacy_reasons.append("❌ High SOFA score")

# Inclusion criteria
if inclusion_score >= 5:
    candidacy_score += 2
    candidacy_reasons.append("✅ Most inclusion criteria met")
elif inclusion_score >= 3:
    candidacy_score += 1
    candidacy_reasons.append("⚠️ Some inclusion criteria met")
else:
    candidacy_score -= 2
    candidacy_reasons.append("❌ Few inclusion criteria met")

# Exclusion criteria
if exclusion_count == 0:
    candidacy_score += 2
    candidacy_reasons.append("✅ No exclusion criteria")
elif exclusion_count <= 1:
    candidacy_score += 0
    candidacy_reasons.append("⚠️ Minor exclusion criteria")
else:
    candidacy_score -= 2
    candidacy_reasons.append("❌ Multiple exclusion criteria")

# Final recommendation
if candidacy_score >= 4:
    recommendation = "🟢 **RECOMMENDED for ECMO**"
    recommendation_color = "success"
elif candidacy_score >= 1:
    recommendation = "🟡 **CONSIDER ECMO** (case-by-case)"
    recommendation_color = "warning"
else:
    recommendation = "🔴 **NOT RECOMMENDED for ECMO**"
    recommendation_color = "error"

st.markdown(f"### {recommendation}")
st.markdown(f"**Candidacy Score:** {candidacy_score}/8")

# Display reasons
st.subheader("📋 Assessment Details")
for reason in candidacy_reasons:
    st.write(reason)

# --------------------- Summary ---------------------
st.header("📊 Summary")
summary_data = {
    "Metric": ["SAVE Score", "SOFA Score", "Inclusion Criteria", "Exclusion Criteria", "Overall Candidacy"],
    "Value": [save_score, sofa_score, f"{inclusion_score}/6", f"{exclusion_count} present", f"{candidacy_score}/8"],
    "Risk": [save_risk, f"{sofa_mortality} mortality", "Appropriate" if inclusion_score >= 4 else "Limited", 
             "Acceptable" if exclusion_count <= 1 else "Concerning", recommendation.split("**")[1]]
}

summary_df = pd.DataFrame(summary_data)
st.dataframe(summary_df, use_container_width=True)

# --------------------- Notes Section ---------------------
st.header("📝 Clinical Notes")
clinical_notes = st.text_area("Additional clinical considerations:", height=150)

if st.button("Generate SOAP Note"):
    soap_note = f"""
**Subjective:**
Patient: {name if name else 'Unknown'}
Age: {age} years, Sex: {sex}
Weight: {weight} kg, Height: {height} cm, BMI: {bmi:.1f}

**Objective:**
SAVE Score: {save_score} ({save_risk} risk, {save_survival} predicted survival)
SOFA Score: {sofa_score} ({sofa_mortality} predicted mortality)
ECMO Candidacy Score: {candidacy_score}/8

**Assessment:**
{recommendation}

**Plan:**
{clinical_notes if clinical_notes else 'No additional notes provided.'}
"""
    st.text_area("Generated SOAP Note:", soap_note, height=200)



