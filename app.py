import streamlit as st
import pymongo
from datetime import datetime
import os

st.set_page_config(page_title="🔧 ระบบรายงานปัญหา", page_icon="🔧", layout="wide")

try:
    client = pymongo.MongoClient(os.getenv('MONGODB_URI'))
    db = client['facility-reporting']
    issues = db['issues']
except Exception as e:
    st.error(f"❌ ไม่สามารถเชื่อมต่อ MongoDB: {str(e)}")
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

# ===== ส่งรายงาน =====
if st.session_state.page == "report":
    st.subheader("📝 ส่งรายงานปัญหา")
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("👤 ชื่อ", placeholder="กรอกชื่อของคุณ")
        phone = st.text_input("📱 เบอร์โทร", placeholder="08-xxxx-xxxx")
    
    with col2:
        category = st.selectbox("🏷️ ประเภท", ["💧 น้ำรั่ว", "🚽 ห้องน้ำ", "🗑️ ถังขยะ", "💡 ไฟฟ้า", "❄️ ปรับอากาศ", "🪑 เฟอร์นิเจอร์", "🅿️ ที่จอด", "📝 อื่นๆ"])
    
    location = st.text_input("📍 สถานที่", placeholder="เช่น ชั้น 3, ห้อง 301")
    description = st.text_area("📝 รายละเอียด", placeholder="บรรยายปัญหา", height=150)
    
    if st.button("✅ ส่ง", use_container_width=True):
        if not name or not phone or not location or not description:
            st.error("❌ กรุณากรอกทั้งหมด")
        elif not issues:
            st.error("❌ ไม่สามารถเชื่อมต่อ MongoDB")
        else:
            try:
                report_id = f"RTP{int(datetime.now().timestamp())}"
                cat_map = {"💧 น้ำรั่ว": "water", "🚽 ห้องน้ำ": "toilet", "🗑️ ถังขยะ": "trash", "💡 ไฟฟ้า": "light", "❄️ ปรับอากาศ": "hvac", "🪑 เฟอร์นิเจอร์": "furniture", "🅿️ ที่จอด": "parking", "📝 อื่นๆ": "other"}
                
                issues.insert_one({
                    "reportId": report_id,
                    "reporterName": name,
                    "reporterPhone": phone,
                    "category": cat_map[category],
                    "location": location,
                    "description": description,
                    "status": "pending",
                    "files": [],
                    "dateSubmitted": datetime.now(),
                    "createdAt": datetime.now(),
                    "updatedAt": datetime.now()
                })
                st.success(f"✅ ส่งสำเร็จ! #{report_id}")
                st.balloons()
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")

# ===== ติดตามสถานะ =====
elif st.session_state.page == "status":
    st.subheader("📊 ติดตามสถานะ")
    search = st.text_input("🔍 ค้นหา", placeholder="ค้นหาหมายเลขรายงาน")
    
    if not issues:
        st.error("❌ ไม่สามารถเชื่อมต่อ MongoDB")
    else:
        try:
            if search:
                docs = list(issues.find({
                    "$or": [
                        {"reportId": {"$regex": search, "$options": "i"}},
                        {"location": {"$regex": search, "$options": "i"}}
                    ]
                }).sort("createdAt", -1))
            else:
                docs = list(issues.find().sort("createdAt", -1))
            
            if docs:
                for doc in docs:
                    status_icons = {"pending": "🟡", "inprogress": "🔵", "resolved": "🟢"}
                    status_text = {"pending": "รอตรวจสอบ", "inprogress": "กำลังแก้ไข", "resolved": "แก้ไขแล้ว"}
                    
                    st.write(f"{status_icons.get(doc['status'])} **#{doc['reportId']}** - {doc['location']}")
                    st.write(f"📝 {doc['description'][:100]}...")
                    st.write(f"👤 {doc['reporterName']} | 📱 {doc['reporterPhone']} | {status_text.get(doc['status'])}")
                    st.divider()
            else:
                st.info("📭 ไม่พบรายงาน")
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")

# ===== Admin =====
elif st.session_state.page == "admin":
    st.subheader("🔐 Admin Dashboard")
    pwd = st.text_input("🔐 รหัสผ่าน", type="password", placeholder="กรอกรหัสผ่าน")
    
    if pwd == os.getenv('ADMIN_PASSWORD', 'admin123456'):
        st.success("✅ เข้าสู่ระบบแล้ว")
        
        if not issues:
            st.error("❌ ไม่สามารถเชื่อมต่อ MongoDB")
        else:
            try:
                docs = list(issues.find().sort("createdAt", -1))
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📊 ทั้งหมด", len(docs))
                with col2:
                    pending = len([d for d in docs if d["status"] == "pending"])
                    st.metric("🟡 รอตรวจสอบ", pending)
                with col3:
                    inprogress = len([d for d in docs if d["status"] == "inprogress"])
                    st.metric("🔵 กำลังแก้ไข", inprogress)
                with col4:
                    resolved = len([d for d in docs if d["status"] == "resolved"])
                    st.metric("🟢 แก้ไขแล้ว", resolved)
                
                st.divider()
                
                for doc in docs:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**#{doc['reportId']}** - {doc['location']}")
                        st.write(f"👤 {doc['reporterName']} | 📱 {doc['reporterPhone']}")
                    
                    with col2:
                        new_status = st.selectbox(
                            "สถานะ",
                            ["pending", "inprogress", "resolved"],
                            index=["pending", "inprogress", "resolved"].index(doc["status"]),
                            key=f"status_{doc['reportId']}"
                        )
                        if new_status != doc["status"]:
                            issues.update_one(
                                {"reportId": doc["reportId"]},
                                {"$set": {"status": new_status, "updatedAt": datetime.now()}}
                            )
                            st.rerun()
                    
                    with col3:
                        if st.button("🗑️ ลบ", key=f"del_{doc['reportId']}"):
                            issues.delete_one({"reportId": doc["reportId"]})
                            st.rerun()
                    
                    st.divider()
            
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")
    
    elif pwd:
        st.error("❌ รหัสผ่านไม่ถูกต้อง")
