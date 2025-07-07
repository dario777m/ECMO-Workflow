import streamlit as st
import pandas as pd
import numpy as np
import math
import altair as alt

st.set_page_config(page_title="ECMO Complete Workflow", layout="wide")

st.title("🫀 ECMO Complete Workflow: Candidacy → Initiation")

# Initialize session state for workflow progression
if 'candidacy_completed' not in st.session_state:
    st.session_state.candidacy_completed = False
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {}

# --------------------- Step 1: Patient Information ---------------------
st.header("📝 Step 1: Patient Information")

col1, col2, col3 = st.columns(3)

with col1:
    name = st.text_input("Patient Name")
    age = st.number_input("Age", min_value=0, max_value=120, value=40)
    sex = st.selectbox("Sex", ["Male", "Female"])

with col2:
    weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, value=70.0)
    height = st.number_input("Height (cm)", min_value=0.0, max_value=250.0, value=170.0)
    bmi = weight / ((height/100) ** 2) if height > 0 else 0
    st.metric("BMI", f"{bmi:.1f}")
    
    # Calculate Ideal Body Weight (Devine Formula)
    if sex == "Male":
        ideal_weight = 50 + 2.3 * ((height - 152.4) / 2.54)
    else:
        ideal_weight = 45.5 + 2.3 * ((height - 152.4) / 2.54)
    
    # Calculate BSA using DuBois formula
    bsa = 0.007184 * (height ** 0.725) * (weight ** 0.425)
    
    st.metric("Ideal Weight", f"{ideal_weight:.1f} kg")
    st.metric("BSA", f"{bsa:.2f} m²")

with col3:
    ecmo_mode = st.selectbox("ECMO Mode", ["VV", "VA"])
    st.info(f"**Mode:** {ecmo_mode} ECMO")

# Store patient data
st.session_state.patient_data = {
    'name': name, 'age': age, 'sex': sex, 'weight': weight, 
    'height': height, 'bmi': bmi, 'ideal_weight': ideal_weight, 'bsa': bsa, 'ecmo_mode': ecmo_mode
}

# --------------------- Step 2: Scoring System (Mode-specific) ---------------------
if ecmo_mode == "VA":
    st.header("📊 Step 2: SAVE Score Assessment")
    st.markdown("**Survival After Veno-Arterial ECMO Score**")
    
    save_col1, save_col2, save_col3 = st.columns(3)

    with save_col1:
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
        
        # Weight points (using actual weight)
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

    with save_col2:
        # Pre-ECMO organ failure
        pre_ecmo_cardiac_arrest = st.checkbox("Pre-ECMO Cardiac Arrest")
        pre_ecmo_cardiac_arrest_points = 15 if pre_ecmo_cardiac_arrest else 0
        st.metric("Pre-ECMO Cardiac Arrest Points", pre_ecmo_cardiac_arrest_points)
        
        # Acute etiology
        acute_etiology = st.selectbox("Acute Etiology", 
                                     ["Post-cardiotomy", "Acute MI", "Myocarditis", "Other"])
        acute_etiology_points = {"Post-cardiotomy": 0, "Acute MI": 6, "Myocarditis": 8, "Other": 4}
        st.metric("Acute Etiology Points", acute_etiology_points[acute_etiology])

    with save_col3:
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
    
    # Store score for later use
    mode_score = save_score
    mode_score_name = "SAVE"

else:  # VV ECMO
    st.header("📊 Step 2: RESP Score Assessment")
    st.markdown("**Respiratory ECMO Survival Prediction Score**")
    
    resp_col1, resp_col2, resp_col3 = st.columns(3)

    with resp_col1:
        # Age points
        age_points = 0
        if age < 18:
            age_points = 0
        elif age < 50:
            age_points = -2
        elif age < 65:
            age_points = -1
        else:
            age_points = 0
        
        st.metric("Age Points", age_points)
        
        # Immunocompromised
        immunocompromised = st.checkbox("Immunocompromised")
        immuno_points = -2 if immunocompromised else 0
        st.metric("Immunocompromised Points", immuno_points)
        
        # Duration of mechanical ventilation
        mech_vent_duration = st.number_input("Duration of Mechanical Ventilation (hours)", min_value=0, value=0)
        vent_points = 0
        if mech_vent_duration < 48:
            vent_points = 3
        elif mech_vent_duration < 168:  # 7 days
            vent_points = 0
        else:
            vent_points = -3
        st.metric("Ventilation Duration Points", vent_points)

    with resp_col2:
        # PaO2/FiO2 ratio
        pao2_fio2 = st.number_input("PaO₂/FiO₂ ratio", min_value=0, value=100)
        if pao2_fio2 >= 150:
            oxy_points = 0
        elif pao2_fio2 >= 100:
            oxy_points = -1
        else:
            oxy_points = -3
        st.metric("PaO₂/FiO₂ Points", oxy_points)
        
        # pH
        ph_value = st.number_input("pH", min_value=6.0, max_value=8.0, value=7.4, step=0.01)
        if ph_value >= 7.15:
            ph_points = 0
        else:
            ph_points = -2
        st.metric("pH Points", ph_points)
        
        # PEEP
        peep = st.number_input("PEEP (cmH₂O)", min_value=0, value=10)
        if peep >= 10:
            peep_points = -1
        else:
            peep_points = 0
        st.metric("PEEP Points", peep_points)

    with resp_col3:
        # Plateau pressure
        plateau_pressure = st.number_input("Plateau Pressure (cmH₂O)", min_value=0, value=30)
        if plateau_pressure >= 30:
            plateau_points = -1
        else:
            plateau_points = 0
        st.metric("Plateau Pressure Points", plateau_points)
        
        # Acute diagnosis
        acute_diagnosis = st.selectbox("Acute Diagnosis", 
                                      ["Viral pneumonia", "Bacterial pneumonia", "Asthma", "Trauma/surgery", "Other"])
        diagnosis_points = {"Viral pneumonia": 0, "Bacterial pneumonia": 0, "Asthma": 6, "Trauma/surgery": 3, "Other": 0}
        st.metric("Diagnosis Points", diagnosis_points[acute_diagnosis])
        
        # Central nervous system dysfunction
        cns_dysfunction = st.checkbox("Central Nervous System Dysfunction")
        cns_points = -7 if cns_dysfunction else 0
        st.metric("CNS Dysfunction Points", cns_points)

    # Calculate RESP score
    resp_score = age_points + immuno_points + vent_points + oxy_points + ph_points + peep_points + plateau_points + diagnosis_points[acute_diagnosis] + cns_points

    st.markdown(f"### 🎯 **RESP Score: {resp_score}**")

    # RESP Score interpretation
    if resp_score >= 6:
        resp_risk = "Very Low Risk"
        resp_survival = "~92%"
    elif resp_score >= 3:
        resp_risk = "Low Risk"
        resp_survival = "~76%"
    elif resp_score >= 0:
        resp_risk = "Medium Risk"
        resp_survival = "~57%"
    elif resp_score >= -3:
        resp_risk = "High Risk"
        resp_survival = "~33%"
    else:
        resp_risk = "Very High Risk"
        resp_survival = "~18%"

    st.info(f"**Risk Level:** {resp_risk} | **Predicted Survival:** {resp_survival}")
    
    # Store score for later use
    mode_score = resp_score
    mode_score_name = "RESP"

# --------------------- Step 3: SOFA Score ---------------------
st.header("🏥 Step 3: SOFA Score Assessment")
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

# --------------------- Step 4: ECMO Criteria (including ECPR) ---------------------
st.header("✅ Step 4: ECMO Candidacy Criteria")

# ECPR section
st.subheader("🚨 ECPR Criteria (if applicable)")
ecpr_applicable = st.checkbox("Is this an ECPR case?")

if ecpr_applicable:
    st.markdown("**ECPR Inclusion Criteria:**")
    ecpr_col1, ecpr_col2 = st.columns(2)
    
    with ecpr_col1:
        witnessed_arrest = st.checkbox("Witnessed cardiac arrest")
        bystander_cpr = st.checkbox("Bystander CPR initiated")
        no_rosc = st.checkbox("No ROSC within 60 minutes")
        
    with ecpr_col2:
        ph_value_ecpr = st.number_input("pH (ECPR)", min_value=6.0, max_value=8.0, value=7.0, step=0.01)
        lactate_ecpr = st.number_input("Lactate (mmol/L)", min_value=0.0, value=10.0)
        
        ph_appropriate = ph_value_ecpr >= 6.8
        lactate_appropriate = lactate_ecpr <= 15.0
        
        st.metric("pH Appropriate", "✅" if ph_appropriate else "❌")
        st.metric("Lactate Appropriate", "✅" if lactate_appropriate else "❌")
    
    ecpr_criteria_met = sum([witnessed_arrest, bystander_cpr, no_rosc, ph_appropriate, lactate_appropriate])
    st.metric("ECPR Criteria Met", f"{ecpr_criteria_met}/5")

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

# --------------------- Step 5: Final Assessment ---------------------
st.header("🎯 Step 5: Final ECMO Candidacy Assessment")

# Calculate overall candidacy
candidacy_score = 0
candidacy_reasons = []

# Mode-specific score assessment
if mode_score_name == "SAVE":
    if mode_score >= 5:
        candidacy_score += 2
        candidacy_reasons.append("✅ Good SAVE score (low risk)")
    elif mode_score >= -1:
        candidacy_score += 1
        candidacy_reasons.append("⚠️ Moderate SAVE score")
    else:
        candidacy_score -= 1
        candidacy_reasons.append("❌ Poor SAVE score (high risk)")
else:  # RESP score
    if mode_score >= 3:
        candidacy_score += 2
        candidacy_reasons.append("✅ Good RESP score (low risk)")
    elif mode_score >= 0:
        candidacy_score += 1
        candidacy_reasons.append("⚠️ Moderate RESP score")
    else:
        candidacy_score -= 1
        candidacy_reasons.append("❌ Poor RESP score (high risk)")

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

# ECPR assessment
if ecpr_applicable:
    if ecpr_criteria_met >= 4:
        candidacy_score += 1
        candidacy_reasons.append("✅ ECPR criteria met")
    else:
        candidacy_score -= 1
        candidacy_reasons.append("❌ ECPR criteria not met")

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
    is_candidate = True
elif candidacy_score >= 1:
    recommendation = "🟡 **CONSIDER ECMO** (case-by-case)"
    recommendation_color = "warning"
    is_candidate = True
else:
    recommendation = "🔴 **NOT RECOMMENDED for ECMO**"
    recommendation_color = "error"
    is_candidate = False

st.markdown(f"### {recommendation}")
st.markdown(f"**Candidacy Score:** {candidacy_score}/8")

# Display reasons
st.subheader("📋 Assessment Details")
for reason in candidacy_reasons:
    st.write(reason)

# Store candidacy result
st.session_state.is_candidate = is_candidate
st.session_state.candidacy_score = candidacy_score

# --------------------- Step 6: Pre-Cannulation Timeout (if candidate) ---------------------
if is_candidate:
    st.header("⏰ Step 6: Pre-Cannulation Timeout")
    st.markdown("**Critical Safety Check - All team members must be present**")
    
    # Timeout verification
    st.markdown("### 👥 Team Verification")
    timeout_col1, timeout_col2 = st.columns(2)
    
    with timeout_col1:
        st.markdown("**Team Members Present:**")
        surgeon = st.checkbox("Surgeon/Proceduralist")
        anesthesiologist = st.checkbox("Anesthesiologist")
        perfusionist = st.checkbox("Perfusionist")
        ecmo_specialist = st.checkbox("ECMO Specialist")
        respiratory = st.checkbox("Respiratory Therapist")
        
        team_present = sum([surgeon, anesthesiologist, perfusionist, ecmo_specialist, respiratory])
        st.metric("Team Members", f"{team_present}/5")
    
    with timeout_col2:
        st.markdown("**Patient Verification:**")
        patient_identified = st.checkbox("Patient identity confirmed")
        consent_verified = st.checkbox("Consent verified and documented")
        allergies_confirmed = st.checkbox("Allergies confirmed")
        pregnancy_test = st.checkbox("Pregnancy test negative (if applicable)")
        
        patient_verified = sum([patient_identified, consent_verified, allergies_confirmed, pregnancy_test])
        st.metric("Patient Checks", f"{patient_verified}/4")
    
    # Equipment and supplies
    st.markdown("### 🔧 Equipment & Supplies")
    equip_col1, equip_col2, equip_col3 = st.columns(3)
    
    with equip_col1:
        st.markdown("**ECMO Circuit:**")
        circuit_primed = st.checkbox("Circuit primed and tested")
        backup_circuit = st.checkbox("Backup circuit available")
        cannulas_ready = st.checkbox("Appropriate cannulas available")
        
        circuit_ready = sum([circuit_primed, backup_circuit, cannulas_ready])
        st.metric("Circuit Ready", f"{circuit_ready}/3")
    
    with equip_col2:
        st.markdown("**Monitoring:**")
        arterial_line = st.checkbox("Arterial line (right arm)")
        central_line = st.checkbox("Central venous access")
        monitoring_equipment = st.checkbox("All monitoring equipment ready")
        
        monitoring_ready = sum([arterial_line, central_line, monitoring_equipment])
        st.metric("Monitoring Ready", f"{monitoring_ready}/3")
    
    with equip_col3:
        st.markdown("**Emergency Equipment:**")
        crash_cart = st.checkbox("Crash cart available")
        defibrillator = st.checkbox("Defibrillator ready")
        emergency_drugs = st.checkbox("Emergency drugs available")
        
        emergency_ready = sum([crash_cart, defibrillator, emergency_drugs])
        st.metric("Emergency Ready", f"{emergency_ready}/3")
    
    # Procedure planning
    st.markdown("### 📋 Procedure Planning")
    plan_col1, plan_col2 = st.columns(2)
    
    with plan_col1:
        st.markdown("**Cannulation Plan:**")
        cannulation_site = st.selectbox("Cannulation Site", ["Femoral-Femoral", "Femoral-Jugular", "Femoral-Axillary", "Other"])
        ultrasound_available = st.checkbox("Ultrasound available")
        fluoroscopy_available = st.checkbox("Fluoroscopy available (if needed)")
        
        plan_ready = sum([cannulation_site != "", ultrasound_available, fluoroscopy_available])
        st.metric("Plan Ready", f"{plan_ready}/3")
    
    with plan_col2:
        st.markdown("**Safety Checks:**")
        correct_side = st.checkbox("Correct side marked")
        positioning_appropriate = st.checkbox("Patient positioning appropriate")
        sterile_field = st.checkbox("Sterile field prepared")
        
        safety_ready = sum([correct_side, positioning_appropriate, sterile_field])
        st.metric("Safety Ready", f"{safety_ready}/3")
    
    # Final timeout decision
    total_checks = team_present + patient_verified + circuit_ready + monitoring_ready + emergency_ready + plan_ready + safety_ready
    max_checks = 5 + 4 + 3 + 3 + 3 + 3 + 3  # Total possible checks
    
    timeout_passed = total_checks >= (max_checks * 0.8)  # 80% threshold
    
    st.markdown("### 🎯 Timeout Decision")
    if timeout_passed:
        st.success(f"✅ **TIMEOUT PASSED** - Ready to proceed with cannulation")
        st.metric("Overall Readiness", f"{total_checks}/{max_checks} ({total_checks/max_checks*100:.0f}%)")
    else:
        st.error(f"❌ **TIMEOUT FAILED** - Address missing items before proceeding")
        st.metric("Overall Readiness", f"{total_checks}/{max_checks} ({total_checks/max_checks*100:.0f}%)")
    
    # Store timeout result
    st.session_state.timeout_passed = timeout_passed
    st.session_state.timeout_score = total_checks

# --------------------- Step 7: Initiation Recommendations (if timeout passed) ---------------------
if is_candidate and st.session_state.get('timeout_passed', False):
    st.header("🚀 Step 7: ECMO Initiation Recommendations")
    
    # Calculate required flow based on BSA
    required_flow = st.session_state.patient_data['bsa'] * 2.4  # L/min/m²
    
    st.markdown(f"### 📊 **Initial Settings**")
    init_col1, init_col2, init_col3 = st.columns(3)
    
    with init_col1:
        st.metric("Target Flow", f"{required_flow:.1f} L/min")
        st.metric("BSA", f"{st.session_state.patient_data['bsa']:.2f} m²")
    
    with init_col2:
        st.metric("Sweep Gas", "2-3 LPM")
        st.metric("Initial FiO₂", "1.0")
    
    with init_col3:
        st.metric("Anticoagulation", "Heparin")
        st.metric("Target ACT", "180-220 sec")
    
    # Cannula recommendations
    st.markdown("### 🔌 **Cannula Recommendations**")
    
    def cannula_rec(required_flow):
        # Add 30% safety margin
        safety_flow = required_flow * 1.3
        
        if safety_flow <= 4.0:
            return "19-21 Fr"
        elif safety_flow <= 5.5:
            return "21-23 Fr"
        elif safety_flow <= 7.0:
            return "23-25 Fr"
        else:
            return "25+ Fr"
    
    if ecmo_mode == "VV":
        st.markdown(f"**Drainage Cannula:** {cannula_rec(required_flow)}")
        st.markdown(f"**Return Cannula:** {cannula_rec(required_flow)}")
        st.markdown("**Preferred Sites:** Femoral vein (drainage) + Internal jugular vein (return)")
    else:  # VA
        st.markdown(f"**Venous Cannula:** {cannula_rec(required_flow)}")
        st.markdown(f"**Arterial Cannula:** {cannula_rec(required_flow)}")
        st.markdown("**Preferred Sites:** Femoral vein + Femoral artery")
    
    # Monitoring recommendations
    st.markdown("### 📈 **Monitoring Recommendations**")
    monitor_col1, monitor_col2 = st.columns(2)
    
    with monitor_col1:
        st.markdown("**Continuous Monitoring:**")
        st.write("• MAP > 65 mmHg")
        st.write("• SpO₂ > 95%")
        st.write("• SvO₂ > 70%")
        st.write("• Lactate trending down")
    
    with monitor_col2:
        st.markdown("**ECMO Parameters:**")
        st.write("• Flow: Target ± 0.5 L/min")
        st.write("• RPM: < 3500")
        st.write("• ΔP: < 400 mmHg")
        st.write("• ACT: 180-220 sec")
    
    # Initial management
    st.markdown("### 💊 **Initial Management**")
    mgmt_col1, mgmt_col2 = st.columns(2)
    
    with mgmt_col1:
        st.markdown("**Immediate Actions:**")
        st.write("• Start heparin infusion")
        st.write("• Titrate vasopressors")
        st.write("• Optimize volume status")
        st.write("• Monitor for complications")
    
    with mgmt_col2:
        st.markdown("**First 24 Hours:**")
        st.write("• Daily CXR")
        st.write("• Serial ABGs")
        st.write("• Monitor for bleeding")
        st.write("• Assess for weaning")

# --------------------- Summary and Documentation ---------------------
if is_candidate:
    st.header("📋 Summary & Documentation")
    
    # Create summary table
    summary_data = {
        'Metric': ['Patient', 'ECMO Mode', f'{mode_score_name} Score', 'SOFA Score', 'Candidacy Score', 'BSA', 'Ideal Weight'],
        'Value': [
            name,
            ecmo_mode,
            f"{mode_score}",
            f"{sofa_score}",
            f"{candidacy_score}/8",
            f"{bsa:.2f} m²",
            f"{ideal_weight:.1f} kg"
        ],
        'Risk': [
            '',
            '',
            f"{save_risk if mode_score_name == 'SAVE' else resp_risk}",
            f"{sofa_mortality} mortality",
            recommendation.split('**')[1].split('**')[0],
            '',
            ''
        ]
    }
    
    # Add timeout info if applicable
    if st.session_state.get('timeout_passed') is not None:
        summary_data['Metric'].append('Timeout Status')
        summary_data['Value'].append('PASSED' if st.session_state.timeout_passed else 'FAILED')
        summary_data['Risk'].append(f"{st.session_state.get('timeout_score', 0)} checks passed")
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)
    
    # Generate SOAP note
    st.subheader("📝 SOAP Note")
    
    # Get variables for SOAP note
    timeout_status = "PASSED" if st.session_state.get('timeout_passed', False) else "FAILED" if st.session_state.get('timeout_passed') is not None else "N/A"
    timeout_score = st.session_state.get('timeout_score', 0)
    
    soap_note = f"""
**Subjective:**
{age}-year-old {sex.lower()} patient with {ecmo_mode} ECMO candidacy assessment.

**Objective:**
- {mode_score_name} Score: {mode_score} ({save_risk if mode_score_name == 'SAVE' else resp_risk})
- SOFA Score: {sofa_score} (predicted mortality: {sofa_mortality})
- BSA: {bsa:.2f} m², Ideal Weight: {ideal_weight:.1f} kg
- Candidacy Score: {candidacy_score}/8
- Timeout Status: {timeout_status} ({timeout_score} checks passed)

**Assessment:**
{recommendation}

**Plan:**
"""
    
    if st.session_state.get('timeout_passed', False):
        soap_note += f"""
- Proceed with {ecmo_mode} ECMO cannulation
- Target flow: {required_flow:.1f} L/min
- Monitor for complications
- Daily reassessment for weaning
"""
    else:
        soap_note += """
- Address timeout deficiencies before proceeding
- Re-evaluate candidacy if significant issues identified
"""
    
    st.text_area("SOAP Note", soap_note, height=300)
    
    # Download functionality
    csv = summary_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Summary CSV",
        data=csv,
        file_name=f"ECMO_Assessment_{name}_{ecmo_mode}.csv",
        mime="text/csv"
    )

else:
    st.warning("❌ Patient is not a candidate for ECMO. Please review exclusion criteria and consider alternative therapies.") 