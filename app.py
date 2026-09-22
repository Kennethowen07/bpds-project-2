import streamlit as st
import pandas as pd
import joblib

MODEL_PATH = "model/dropout_model.joblib"
COLUMNS_PATH = "model/feature_columns.joblib"
THRESHOLD = 0.4

DEFAULTS = {
    "Application_mode": 17,
    "Application_order": 1,
    "Previous_qualification": 1,
    "Nacionality": 1,
    "Mothers_qualification": 19,
    "Fathers_qualification": 19,
    "Mothers_occupation": 5,
    "Fathers_occupation": 7,
    "Educational_special_needs": 0,
    "International": 0,
    "Curricular_units_1st_sem_credited": 0,
    "Curricular_units_1st_sem_without_evaluations": 0,
    "Unemployment_rate": 11.1,
    "Inflation_rate": 1.4,
    "GDP": 0.32,
}

COURSES = {
    33: "Biofuel Production Technologies",
    171: "Animation and Multimedia Design",
    8014: "Social Service (kelas malam)",
    9003: "Agronomy",
    9070: "Communication Design",
    9085: "Veterinary Nursing",
    9119: "Informatics Engineering",
    9130: "Equinculture",
    9147: "Management",
    9238: "Social Service",
    9254: "Tourism",
    9500: "Nursing",
    9556: "Oral Hygiene",
    9670: "Advertising and Marketing Management",
    9773: "Journalism and Communication",
    9853: "Basic Education",
    9991: "Management (kelas malam)",
}

MARITAL = {
    1: "Lajang",
    2: "Menikah",
    3: "Janda atau duda",
    4: "Bercerai",
    5: "Kumpul kebo",
    6: "Pisah secara hukum",
}


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH), joblib.load(COLUMNS_PATH)


model, feature_columns = load_model()

st.set_page_config(page_title="Prediksi Dropout Siswa", page_icon="🎓", layout="wide")

st.title("Prediksi Risiko Dropout Siswa")
st.caption("Jaya Jaya Institut. Model memakai data sampai akhir semester satu.")

with st.form("form"):
    st.subheader("Profil siswa")
    c1, c2, c3 = st.columns(3)

    with c1:
        course = st.selectbox("Program studi", list(COURSES.keys()), index=11,
                              format_func=lambda x: COURSES[x])
        age = st.number_input("Usia saat mendaftar", 17, 70, 20)
        gender = st.radio("Jenis kelamin", [0, 1],
                          format_func=lambda x: "Perempuan" if x == 0 else "Laki laki")

    with c2:
        marital = st.selectbox("Status pernikahan", list(MARITAL.keys()),
                               format_func=lambda x: MARITAL[x])
        attendance = st.radio("Waktu kuliah", [1, 0],
                              format_func=lambda x: "Siang" if x == 1 else "Malam")
        displaced = st.checkbox("Merantau dari luar daerah", value=True)

    with c3:
        admission_grade = st.number_input("Nilai masuk", 95.0, 190.0, 126.1)
        prev_grade = st.number_input("Nilai kualifikasi sebelumnya", 95.0, 190.0, 133.1)

    st.subheader("Kondisi finansial")
    f1, f2, f3 = st.columns(3)
    with f1:
        tuition = st.checkbox("Biaya kuliah lunas", value=True)
    with f2:
        debtor = st.checkbox("Punya tunggakan sebagai debitur", value=False)
    with f3:
        scholarship = st.checkbox("Penerima beasiswa", value=False)

    st.subheader("Akademik semester satu")
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        enrolled = st.number_input("Mata kuliah diambil", 0, 26, 6)
    with a2:
        evaluations = st.number_input("Jumlah evaluasi", 0, 45, 8)
    with a3:
        approved = st.number_input("Mata kuliah lulus", 0, 26, 5)
    with a4:
        grade = st.number_input("Nilai rata rata", 0.0, 20.0, 12.3)

    submitted = st.form_submit_button("Prediksi", type="primary")

if submitted:
    data = dict(DEFAULTS)
    data.update({
        "Marital_status": marital,
        "Course": course,
        "Daytime_evening_attendance": attendance,
        "Previous_qualification_grade": prev_grade,
        "Admission_grade": admission_grade,
        "Displaced": int(displaced),
        "Debtor": int(debtor),
        "Tuition_fees_up_to_date": int(tuition),
        "Gender": gender,
        "Scholarship_holder": int(scholarship),
        "Age_at_enrollment": age,
        "Curricular_units_1st_sem_enrolled": enrolled,
        "Curricular_units_1st_sem_evaluations": evaluations,
        "Curricular_units_1st_sem_approved": approved,
        "Curricular_units_1st_sem_grade": grade,
    })

    X = pd.DataFrame([data]).reindex(columns=feature_columns, fill_value=0)
    proba = float(model.predict_proba(X)[0, 1])

    st.divider()
    r1, r2 = st.columns([1, 2])

    with r1:
        st.metric("Probabilitas dropout", f"{proba:.1%}")

    with r2:
        if proba >= THRESHOLD:
            st.error("Siswa masuk kategori berisiko dropout. Perlu dijadwalkan bimbingan.")
        else:
            st.success("Siswa tidak masuk kategori berisiko.")
        st.progress(min(proba, 1.0))

    st.caption(
        f"Ambang batas {THRESHOLD}. Pada data uji, precision 0.82 dan recall 0.89, "
        "jadi sekitar satu dari lima siswa yang ditandai sebenarnya akan lulus normal. "
        "Hasil ini dipakai sebagai prioritas bimbingan, bukan vonis."
    )