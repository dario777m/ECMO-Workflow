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

with col3:
    ecmo_mode = st.selectbox("ECMO Mode", ["VV", "VA"])
    st.info(f"**Mode:** {ecmo_mode} ECMO")

# Store patient data
st.session_state.patient_data = {
    'name': name, 'age': age, 'sex': sex, 'weight': weight, 
    'height': height, 'bmi': bmi, 'ecmo_mode': ecmo_mode
}

# --------------------- Step 2: SAVE Score ---------------------
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

# --------------------- Step 4: ECMO Criteria ---------------------
st.header("✅ Step 4: ECMO Candidacy Criteria")

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
        nurse = st.checkbox("ECMO Specialist Nurse")
        respiratory = st.checkbox("Respiratory Therapist")
        
        team_present = sum([surgeon, anesthesiologist, perfusionist, nurse, respiratory])
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
        cannulas_available = st.checkbox("Cannulas available (correct sizes)")
        pump_functional = st.checkbox("Pump functional test passed")
        oxygenator_ready = st.checkbox("Oxygenator ready")
        
        circuit_ready = sum([circuit_primed, cannulas_available, pump_functional, oxygenator_ready])
        st.metric("Circuit Ready", f"{circuit_ready}/4")
    
    with equip_col2:
        st.markdown("**Monitoring:**")
        a_line_ready = st.checkbox("Arterial line ready")
        cvp_ready = st.checkbox("CVP line ready")
        sat_monitor = st.checkbox("Oxygen saturation monitor")
        ecg_monitor = st.checkbox("ECG monitor")
        
        monitoring_ready = sum([a_line_ready, cvp_ready, sat_monitor, ecg_monitor])
        st.metric("Monitoring Ready", f"{monitoring_ready}/4")
    
    with equip_col3:
        st.markdown("**Emergency Equipment:**")
        crash_cart = st.checkbox("Crash cart available")
        defibrillator = st.checkbox("Defibrillator ready")
        emergency_drugs = st.checkbox("Emergency drugs available")
        backup_equipment = st.checkbox("Backup equipment available")
        
        emergency_ready = sum([crash_cart, defibrillator, emergency_drugs, backup_equipment])
        st.metric("Emergency Ready", f"{emergency_ready}/4")
    
    # Procedure planning
    st.markdown("### 📋 Procedure Planning")
    plan_col1, plan_col2 = st.columns(2)
    
    with plan_col1:
        st.markdown("**Site & Approach:**")
        site_marked = st.checkbox("Insertion site marked")
        approach_confirmed = st.checkbox("Surgical approach confirmed")
        landmarks_identified = st.checkbox("Anatomical landmarks identified")
        sterile_field = st.checkbox("Sterile field prepared")
        
        site_ready = sum([site_marked, approach_confirmed, landmarks_identified, sterile_field])
        st.metric("Site Ready", f"{site_ready}/4")
    
    with plan_col2:
        st.markdown("**Anticoagulation:**")
        heparin_available = st.checkbox("Heparin available")
        act_baseline = st.number_input("Baseline ACT (seconds)", min_value=0, value=120)
        anticoagulation_plan = st.selectbox("Anticoagulation plan", 
                                           ["Heparin bolus + infusion", "Bivalirudin", "Argatroban", "None"])
        
        st.metric("Baseline ACT", f"{act_baseline} sec")
    
    # Safety checks
    st.markdown("### ⚠️ Critical Safety Checks")
    safety_col1, safety_col2 = st.columns(2)
    
    with safety_col1:
        st.markdown("**Pre-Procedure:**")
        airway_secure = st.checkbox("Airway secure")
        iv_access = st.checkbox("IV access adequate")
        blood_available = st.checkbox("Blood products available")
        imaging_reviewed = st.checkbox("Recent imaging reviewed")
        
        safety_checks = sum([airway_secure, iv_access, blood_available, imaging_reviewed])
        st.metric("Safety Checks", f"{safety_checks}/4")
    
    with safety_col2:
        st.markdown("**Complications Plan:**")
        bleeding_plan = st.checkbox("Bleeding management plan")
        limb_ischemia_plan = st.checkbox("Limb ischemia monitoring plan")
        recirculation_plan = st.checkbox("Recirculation monitoring plan (VV)")
        weaning_plan = st.checkbox("Weaning strategy discussed")
        
        complication_plans = sum([bleeding_plan, limb_ischemia_plan, recirculation_plan, weaning_plan])
        st.metric("Complication Plans", f"{complication_plans}/4")
    
    # Calculate timeout completion
    total_checks = team_present + patient_verified + circuit_ready + monitoring_ready + emergency_ready + site_ready + safety_checks + complication_plans
    max_checks = 5 + 4 + 4 + 4 + 4 + 4 + 4 + 4  # Total possible checks
    timeout_percentage = (total_checks / max_checks) * 100
    
    # Timeout decision
    st.markdown("### 🎯 Timeout Decision")
    
    if timeout_percentage >= 90:
        timeout_status = "🟢 **PROCEED WITH CANNULATION**"
        can_proceed = True
        st.success(timeout_status)
    elif timeout_percentage >= 75:
        timeout_status = "🟡 **PROCEED WITH CAUTION**"
        can_proceed = True
        st.warning(timeout_status)
        st.warning("Address missing items before proceeding")
    else:
        timeout_status = "🔴 **DO NOT PROCEED**"
        can_proceed = False
        st.error(timeout_status)
        st.error("Critical items missing - resolve before proceeding")
    
    st.metric("Timeout Completion", f"{timeout_percentage:.1f}%")
    
    # Missing items summary
    if timeout_percentage < 100:
        st.markdown("### ❌ Missing Items to Address:")
        missing_items = []
        
        if team_present < 5:
            missing_items.append("Team members not present")
        if patient_verified < 4:
            missing_items.append("Patient verification incomplete")
        if circuit_ready < 4:
            missing_items.append("ECMO circuit not ready")
        if monitoring_ready < 4:
            missing_items.append("Monitoring equipment not ready")
        if emergency_ready < 4:
            missing_items.append("Emergency equipment not ready")
        if site_ready < 4:
            missing_items.append("Surgical site not ready")
        if safety_checks < 4:
            missing_items.append("Safety checks incomplete")
        if complication_plans < 4:
            missing_items.append("Complication plans incomplete")
        
        for item in missing_items:
            st.write(f"• {item}")
    
    # Store timeout status
    st.session_state.timeout_completed = can_proceed
    st.session_state.timeout_percentage = timeout_percentage

# Initialize variables for SOAP note
bsa = 0
target_ci = 0
target_flow = 0
recommended_cannula = "N/A"

# --------------------- Step 7: ECMO Initiation (if candidate and timeout passed) ---------------------
if is_candidate and st.session_state.get('timeout_completed', False):
    st.header("🩸 Step 7: ECMO Initiation Recommendations")
    
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
        
        # Target CI based on ECMO mode
        if ecmo_mode == "VV":
            target_ci = 3.0  # VV ECMO target
        else:  # VA ECMO
            target_ci = 2.5  # VA ECMO target (lower due to native heart)
        
        target_flow = target_ci * bsa
        
        # Get recommended cannula
        recommended_cannula, max_flow = cannula_rec(target_flow)
        
        # Calculate ECMO CI contribution
        ecmo_ci = max_flow / bsa
        ci_met = min(ecmo_ci, target_ci)
        ci_excess = max(0, ecmo_ci - target_ci)
        achieved_ci = ecmo_ci

        # Display recommendations
        init_col1, init_col2 = st.columns(2)
        
        with init_col1:
            st.markdown("### 📊 Patient Calculations")
            st.metric("BSA (Du Bois)", f"{bsa:.2f} m²")
            st.metric("Target CI", f"{target_ci:.1f} L/min/m²")
            st.metric("Target Flow", f"{target_flow:.1f} L/min")
            
            st.markdown("### 🔧 Cannula Recommendations")
            st.metric("Recommended Cannula", recommended_cannula)
            st.metric("Max Flow Capacity", f"{max_flow} L/min")
            
            # Initial settings
            st.markdown("### ⚙️ Initial Settings")
            st.metric("Initial RPM", "2500 - 3200")
            st.metric("Target Flow", f"{target_flow:.1f} L/min")
            
            # Mode-specific recommendations
            if ecmo_mode == "VV":
                st.markdown("### 🔄 VV ECMO Setup")
                st.write("• **Drainage:** Femoral vein (23-25 Fr)")
                st.write("• **Return:** Internal jugular vein (19-21 Fr)")
                st.write("• **Target:** 60-80% of cardiac output")
            else:  # VA ECMO
                st.markdown("### 🔄 VA ECMO Setup")
                st.write("• **Drainage:** Femoral vein (23-25 Fr)")
                st.write("• **Return:** Femoral artery (17-19 Fr)")
                st.write("• **Target:** Full cardiac support")

        with init_col2:
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

            # Chart
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

            st.altair_chart(chart, use_container_width=True)

        # Safety considerations
        st.markdown("### ⚠️ Safety Considerations")
        safety_col1, safety_col2 = st.columns(2)
        
        with safety_col1:
            st.markdown("**Pre-cannulation:**")
            st.write("• Confirm anticoagulation (ACT > 180s)")
            st.write("• Verify cannula sizes available")
            st.write("• Prepare for potential complications")
            
        with safety_col2:
            st.markdown("**Post-cannulation:**")
            st.write("• Monitor for limb ischemia (VA)")
            st.write("• Check for recirculation (VV)")
            st.write("• Optimize flow and RPM settings")

else:
    st.header("❌ ECMO Not Recommended")
    st.error("Based on the assessment, ECMO is not recommended for this patient.")
    st.markdown("### Alternative Considerations:")
    st.write("• Continue conventional therapy")
    st.write("• Consider palliative care consultation")
    st.write("• Reassess if clinical condition changes")

# --------------------- Summary Report ---------------------
st.header("📊 Complete Assessment Summary")

# Create summary data with consistent array lengths
base_metrics = ["SAVE Score", "SOFA Score", "Inclusion Criteria", "Exclusion Criteria", "Overall Candidacy"]
base_values = [save_score, sofa_score, f"{inclusion_score}/6", f"{exclusion_count} present", f"{candidacy_score}/8"]
base_risks = [save_risk, f"{sofa_mortality} mortality", "Appropriate" if inclusion_score >= 4 else "Limited", 
              "Acceptable" if exclusion_count <= 1 else "Concerning", recommendation.split("**")[1]]

# Add timeout info if applicable
if is_candidate and st.session_state.get('timeout_completed') is not None:
    base_metrics.append("Pre-Cannulation Timeout")
    base_values.append(f"{st.session_state.get('timeout_percentage', 0):.1f}%")
    base_risks.append("Passed" if st.session_state.get('timeout_completed', False) else "Failed")

summary_data = {
    "Metric": base_metrics,
    "Value": base_values,
    "Risk": base_risks
}

summary_df = pd.DataFrame(summary_data)
st.dataframe(summary_df, use_container_width=True)

# --------------------- Clinical Notes ---------------------
st.header("📝 Clinical Notes")
clinical_notes = st.text_area("Additional clinical considerations:", height=150)

if st.button("Generate Complete SOAP Note"):
    soap_note = f"""
**Subjective:**
Patient: {name if name else 'Unknown'}
Age: {age} years, Sex: {sex}
Weight: {weight} kg, Height: {height} cm, BMI: {bmi:.1f}
ECMO Mode: {ecmo_mode}

**Objective:**
SAVE Score: {save_score} ({save_risk} risk, {save_survival} predicted survival)
SOFA Score: {sofa_score} ({sofa_mortality} predicted mortality)
ECMO Candidacy Score: {candidacy_score}/8

**Assessment:**
{recommendation}

**Plan:**
{'ECMO Initiation Recommended:' if is_candidate else 'ECMO Not Recommended:'}
{'• Pre-Cannulation Timeout: ' + f"{st.session_state.get('timeout_percentage', 0):.1f}% completion" if is_candidate and st.session_state.get('timeout_completed') is not None else ''}
{'• BSA: ' + f"{bsa:.2f} m²" if is_candidate and bsa > 0 else ''}
{'• Target CI: ' + f"{target_ci:.1f} L/min/m²" if is_candidate and target_ci > 0 else ''}
{'• Recommended Cannula: ' + recommended_cannula if is_candidate and recommended_cannula != "N/A" else ''}
{'• Initial RPM: 2500-3200' if is_candidate else ''}
{'• Target Flow: ' + f"{target_flow:.1f} L/min" if is_candidate and target_flow > 0 else ''}

{clinical_notes if clinical_notes else 'No additional notes provided.'}
"""
    st.text_area("Generated SOAP Note:", soap_note, height=300)

# --------------------- Navigation ---------------------
st.markdown("---")
st.markdown("### 🔄 Workflow Navigation")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Restart Assessment"):
        st.session_state.candidacy_completed = False
        st.rerun()

with col2:
    if st.button("📋 Export Report"):
        st.info("Report export functionality can be added here")

with col3:
    if st.button("💾 Save Assessment"):
        st.success("Assessment saved to session state") 