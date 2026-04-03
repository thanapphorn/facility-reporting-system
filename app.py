import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import os

st.set_page_config(page_title="🔧 ระบบรายงานปัญหา", page_icon="🔧", layout="wide")

@st.cache_resource
def get_db():
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client["facility-reporting"]
    return db["issues"]

def get_issues():
    db = get_db()
    return list(db.find().limit(1000))

def insert_issue(issue_data):
    db = get_db()
    db.insert_one(issue_data)

def update_issue(report_id, status):
    db = get_db()
    db.update_one(
        {"reportId": report_id},
        {"$set": {"status": status, "updatedAt": datetime.now()}}
    )

def delete_issue(report_id):
    db = get_db()
    db.delete_one({"reportId": report_id})

st.title("🔧 ระบบรายงานปัญหา")

if "page" not in st.session_state:
    st.session_state.page = "report"

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝 ส่งรายงาน", use_container_width=True):
        st.session_state.page = "report"

with col2:
    if st.button("📊 ติดตามสถานะ", use_container_width=True):
        st.session_state.page = "status"

with col3:
    if st.button("🔐 Admin", use_container_width=True):
        st.session_state.page = "admin"

st.divider()

# ====================
# ส่งรายงาน
# ====================

if st.session_state.page == "report":

    st.subheader("📝 ส่งรายงานปัญหา")

    name = st.text_input("👤 ชื่อ")
    phone = st.text_input("📱 เบอร์โทร")
    location = st.text_input("📍 สถานที่")
    description = st.text_area("📝 รายละเอียด")

    if st.button("ส่ง"):

        report_id = f"RTP{int(datetime.now().timestamp())}"

        issue_data = {
            "reportId": report_id,
            "reporterName": name,
            "reporterPhone": phone,
            "location": location,
            "description": description,
            "status": "pending",
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }

        insert_issue(issue_data)

        st.success(f"ส่งสำเร็จ #{report_id}")

# ====================
# ติดตามสถานะ
# ====================

elif st.session_state.page == "status":

    st.subheader("📊 ติดตามสถานะ")

    docs = get_issues()

    for doc in docs:

        st.write(f"#{doc['reportId']} - {doc['location']}")
        st.write(doc["description"])
        st.write(doc["status"])
        st.divider()

# ====================
# ADMIN
# ====================

elif st.session_state.page == "admin":

    st.subheader("🔐 Admin")

    pwd = st.text_input("รหัสผ่าน", type="password")

    if pwd == os.getenv("ADMIN_PASSWORD", "admin123"):

        st.success("เข้าสู่ระบบแล้ว")

        docs = get_issues()

        for doc in docs:

            col1, col2 = st.columns(2)

            with col1:
                st.write(f"#{doc['reportId']} - {doc['location']}")

            with col2:

                if st.button("ลบ", key=doc["reportId"]):
                    delete_issue(doc["reportId"])
                    st.rerun()

            st.divider()

    elif pwd:
        st.error("รหัสผ่านไม่ถูกต้อง")
