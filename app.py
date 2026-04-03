import streamlit as st
import pymongo
from datetime import datetime
import os

st.set_page_config(page_title="🔧 ระบบรายงานปัญหา", page_icon="🔧", layout="wide")

st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        padding: 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

try:
    client = pymongo.MongoClient(os.getenv('MONGODB_URI'))
    db = client['facility-reporting']
    issues = db['issues']
except:
    st.error("❌ ไม่สามารถเชื่อมต่อ MongoDB")
    issues = None

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

if st.session_state.page == "report":
    st.subheader("📝 ส่งรายงานปัญหา")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("👤 ชื่อ")
        phone = st.text_input("📱 เบอร์โทร")
    with col2:
        category = st.selectbox("🏷️ ประเภท", ["💧 น้ำรั่ว", "🚽 ห้องน้ำ", "🗑️ ถังขยะ", "💡 ไฟฟ้า", "❄️ ปรับอากาศ", "🪑 เฟอร์นิเจอร์", "🅿️ ที่จอด", "📝 อื่นๆ"])
    location = st.text_input("📍 สถานที่")
    description = st.text_area("📝 รายละเอียด", height=150)
    
    if st.button("✅ ส่ง", use_container_width=True):
        if not name or not phone or not location or not description:
            st.error("❌ กรุณากรอกทั้งหมด")
        elif issues:
            report_id = f"RTP{int(datetime.now().timestamp())}"
            cat_map = {"💧 น้ำรั่ว": "water", "🚽 ห้องน้ำ": "toilet", "🗑️ ถังขยะ": "trash", "💡 ไฟฟ้า": "light", "❄️ ปรับอากาศ": "hvac", "🪑 เฟอร์นิเจอร์": "furniture", "🅿️ ที่จอด": "parking", "📝 อื่นๆ": "other"}
            try:
                issues.insert_one({"reportId": report_id, "reporterName": name, "reporterPhone": phone, "category": cat_map[category], "location": location, "description": description, "status": "pending", "files": [], "dateSubmitted": datetime.now(), "createdAt": datetime.now(), "updatedAt": datetime.now()})
                st.success(f"✅ ส่งสำเร็จ! #{report_id}")
                st.balloons()
            except Exception as e:
                st.error(f"❌ {e}")

elif st.session_state.page == "status":
    st.subheader("📊 ติดตามสถานะ")
    search = st.text_input("🔍 ค้นหา")
    if issues:
        try:
            if search:
                docs = list(issues.find({"$or": [{"reportId": {"$regex": search, "$options": "i"}}, {"location": {"$regex": search, "$options": "i"}}]}).sort("createdAt", -1))
            else:
                docs = list(issues.find().sort("createdAt", -1))
            if docs:
                for doc in docs:
                    st.write(f"**#{doc['reportId']}** - {doc['location']}")
                    st.write(doc['description'][:100])
                    st.write(f"👤 {doc['reporterName']}")
                    st.divider()
            else:
                st.info("📭 ไม่มี")
        except Exception as e:
            st.error(f"❌ {e}")

elif st.session_state.page == "admin":
    st.subheader("🔐 Admin")
    pwd = st.text_input("🔐 รหัส", type="password")
    if pwd == os.getenv('ADMIN_PASSWORD', 'admin123456') and issues:
        st.success("✅ OK")
        docs = list(issues.find().sort("createdAt", -1))
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 ทั้งหมด", len(docs))
        with col2:
            st.metric("🟡 รอ", len(
