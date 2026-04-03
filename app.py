import streamlit as st
import pymongo
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

@st.cache_resource
def get_db():
    client = pymongo.MongoClient(os.getenv('MONGODB_URI'))
    db = client['facility-reporting']
    return db

db = get_db()
issues = db['issues']

st.set_page_config(
    page_title="🔧 ระบบรายงานปัญหา",
    page_icon="🔧",
    layout="wide"
)

# Sidebar Navigation
page = st.sidebar.radio(
    "📍 เลือกหน้า",
    ["ส่งรายงาน", "ติดตามสถานะ", "🔐 Admin"]
)

# ========== ส่งรายงาน ==========
if page == "ส่งรายงาน":
    st.header("🔧 ส่งรายงานปัญหา")
    st.markdown("---")
    
    with st.form("report_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            reporter_name = st.text_input("👤 ชื่อผู้รายงาน", placeholder="กรอกชื่อของคุณ")
            reporter_phone = st.text_input("📱 เบอร์โทรศัพท์", placeholder="08-xxxx-xxxx")
        
        with col2:
            category_options = {
                "💧 น้ำรั่ว": "water",
                "🚽 ห้องน้ำพัง": "toilet",
                "🗑️ ถังขยะเต็ม": "trash",
                "💡 ไฟฟ้า": "light",
                "❄️ ปรับอากาศ": "hvac",
                "🪑 เฟอร์นิเจอร์": "furniture",
                "🅿️ ที่จอดรถ": "parking",
                "📝 อื่นๆ": "other"
            }
            category = st.selectbox("🏷️ ประเภทปัญหา", list(category_options.keys()))
            category_value = category_options[category]
        
        location = st.text_input("📍 สถานที่เกิดปัญหา", placeholder="เช่น ชั้น 3, ห้อง 301")
        description = st.text_area("📝 รายละเอียดปัญหา", placeholder="บรรยายปัญหาที่เกิดขึ้นอย่างละเอียด", height=150)
        
        submitted = st.form_submit_button("✅ ส่งรายงาน", use_container_width=True)
        
        if submitted:
            if not reporter_name or not reporter_phone or not location or not description:
                st.error("❌ กรุณากรอกข้อมูลทั้งหมด")
            else:
                report_id = f"RTP{int(datetime.now().timestamp())}"
                issue = {
                    "reportId": report_id,
                    "reporterName": reporter_name,
                    "reporterPhone": reporter_phone,
                    "category": category_value,
                    "location": location,
                    "description": description,
                    "status": "pending",
                    "files": [],
                    "dateSubmitted": datetime.now(),
                    "createdAt": datetime.now(),
                    "updatedAt": datetime.now()
                }
                
                try:
                    issues.insert_one(issue)
                    st.success(f"✅ ส่งรายงานสำเร็จ! หมายเลข: **{report_id}**")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")

# ========== ติดตามสถานะ ==========
elif page == "ติดตามสถานะ":
    st.header("📊 ติดตามสถานะรายงาน")
    st.markdown("---")
    
    search_term = st.text_input("🔍 ค้นหาหมายเลขรายงาน", placeholder="ค้นหา...")
    
    try:
        if search_term:
            issues_list = list(issues.find({
                "$or": [
                    {"reportId": {"$regex": search_term, "$options": "i"}},
                    {"location": {"$regex": search_term, "$options": "i"}},
                    {"reporterName": {"$regex": search_term, "$options": "i"}}
                ]
            }).sort("createdAt", -1))
        else:
            issues_list = list(issues.find().sort("createdAt", -1))
        
        if issues_list:
            for issue in issues_list:
                status_emoji = {
                    "pending": "🟡",
                    "inprogress": "🔵",
                    "resolved": "🟢"
                }
                status_text = {
                    "pending": "รอการตรวจสอบ",
                    "inprogress": "กำลังแก้ไข",
                    "resolved": "แก้ไขแล้ว"
                }
                
                col1, col2, col3 = st.columns([0.5, 3, 1])
                with col1:
                    st.write(status_emoji.get(issue["status"], "❓"))
                with col2:
                    st.markdown(f"""
                    **#{issue["reportId"]}** - {issue["location"]}
                    
                    {issue["description"][:100]}...
                    
                    👤 {issue["reporterName"]} | 📱 {issue["reporterPhone"]}
                    """)
                with col3:
                    st.write(f"**{status_text.get(issue['status'], issue['status'])}**")
                st.markdown("---")
        else:
            st.info("📭 ไม่พบรายงาน")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")

# ========== Admin ==========
elif page == "🔐 Admin":
    st.header("🔐 Admin Dashboard")
    st.markdown("---")
    
    password = st.text_input("🔐 รหัสผ่าน", type="password", placeholder="กรอกรหัสผ่าน")
    
    if password == os.getenv('ADMIN_PASSWORD', 'admin123456'):
        st.success("✅ เข้าสู่ระบบแล้ว")
        st.markdown("---")
        
        try:
            issues_list = list(issues.find().sort("createdAt", -1))
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 รายงานทั้งหมด", len(issues_list))
            with col2:
                pending = len([i for i in issues_list if i["status"] == "pending"])
                st.metric("🟡 รอการตรวจสอบ", pending)
            with col3:
                inprogress = len([i for i in issues_list if i["status"] == "inprogress"])
                st.metric("🔵 กำลังแก้ไข", inprogress)
            with col4:
                resolved = len([i for i in issues_list if i["status"] == "resolved"])
                st.metric("🟢 แก้ไขแล้ว", resolved)
            
            st.markdown("---")
            
            # Issues management
            for issue in issues_list:
                col1, col2, col3 = st.columns([2, 1, 0.5])
                
                with col1:
                    st.write(f"**#{issue['reportId']}** - {issue['location']}")
                    st.write(f"👤 {issue['reporterName']} | 📱 {issue['reporterPhone']}")
                
                with col2:
                    new_status = st.selectbox(
                        "สถานะ",
                        ["pending", "inprogress", "resolved"],
                        index=["pending", "inprogress", "resolved"].index(issue["status"]),
                        key=f"status_{issue['reportId']}"
                    )
                    if new_status != issue["status"]:
                        issues.update_one(
                            {"reportId": issue["reportId"]},
                            {"$set": {"status": new_status, "updatedAt": datetime.now()}}
                        )
                        st.rerun()
                
                with col3:
                    if st.button("🗑️ ลบ", key=f"del_{issue['reportId']}"):
                        issues.delete_one({"reportId": issue["reportId"]})
                        st.rerun()
                
                st.markdown("---")
        
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")
    
    elif password:
        st.error("❌ รหัสผ่านไม่ถูกต้อง")
