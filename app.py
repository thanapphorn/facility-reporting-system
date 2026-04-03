import streamlit as st
import pymongo
from datetime import datetime
import os

# Page config
st.set_page_config(
    page_title="🔧 ระบบรายงานปัญหา",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem 1rem;
    }
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
    .stButton>button:hover {
        opacity: 0.9;
    }
    .header-title {
        text-align: center;
        color: #333;
        font-size: 48px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .header-subtitle {
        text-align: center;
        color: #666;
        font-size: 18px;
        margin-bottom: 30px;
    }
    .card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
    }
    </style>
""", unsafe_allow_html=True)

# MongoDB Connection
try:
    client = pymongo.MongoClient(os.getenv('MONGODB_URI'))
    db = client['facility-reporting']
    issues = db['issues']
except:
    st.error("❌ ไม่สามารถเชื่อมต่อ MongoDB")
    issues = None

# Header
st.markdown('<div class="header-title">🔧 ระบบรายงานปัญหา</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">แจ้งปัญหาสิ่งอำนวยความสะดวกเพื่อการแก้ไขอย่างรวดเร็ว</div>', unsafe_allow_html=True)

# Navigation
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

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "report"

# ========== ส่งรายงาน ==========
if st.session_state.page == "report":
    st.subheader("📝 ส่งรายงานปัญหา")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            reporter_name = st.text_input("👤 ชื่อผู้รายงาน", placeholder="กรอกชื่อของคุณ")
        
        with col2:
            reporter_phone = st.text_input("📱 เบอร์โทรศัพท์", placeholder="08-xxxx-xxxx")
        
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
        
        if st.button("✅ ส่งรายงาน", use_container_width=True):
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
                    if issues:
                        issues.insert_one(issue)
                        st.success(f"✅ ส่งรายงานสำเร็จ! หมายเลข: **{report_id}**")
                        st.balloons()
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")

# ========== ติดตามสถานะ ==========
elif st.session_state.page == "status":
    st.subheader("📊 ติดตามสถานะรายงาน")
    
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
            issues_list = list(issues.find().sort("createdAt", -1)) if issues else []
        
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
                
                with st.container():
                    col1, col2 = st.columns([0.1, 0.9])
                    with col1:
                        st.write(status_emoji.get(issue["status"], "❓"))
                    with col2:
                        st.markdown(f"""
                        **#{issue["reportId"]}** - {issue["location"]}
                        
                        {issue["description"][:120]}...
                        
                        👤 {issue["reporterName"]} | 📱 {issue["reporterPhone"]} | {status_text.get(issue['status'])}
                        """)
                    st.divider()
        else:
            st.info("📭 ไม่พบรายงาน")
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")

# ========== Admin ==========
elif st.session_state.page == "admin":
    st.subheader("🔐 Admin Dashboard")
    
    password = st.text_input("🔐 รหัสผ่าน", type="password", placeholder="กรอกรหัสผ่าน")
    
    if password == os.getenv('ADMIN_PASSWORD', 'admin123456'):
        st.success("✅ เข้าสู่ระบบแล้ว")
        st.divider()
        
        try:
            if issues:
                issues_list = list(issues.find().sort("createdAt", -1))
                
                # Statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📊 ทั้งหมด", len(issues_list))
                with col2:
                    pending = len([i for i in issues_list if i["status"] == "pending"])
                    st.metric("🟡 รอตรวจสอบ", pending)
                with col3:
                    inprogress = len([i for i in issues_list if i["status"] == "inprogress"])
                    st.metric("🔵 กำลังแก้ไข", inprogress)
                with col4:
                    resolved = len([i for i in issues_list if i["status"] == "resolved"])
                    st.metric("🟢 แก้ไขแล้ว", resolved)
                
                st.divider()
                
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
                        if st.button("🗑️", key=f"del_{issue['reportId']}"):
                            issues.delete_one({"reportId": issue["reportId"]})
                            st.rerun()
                    
                    st.divider()
        
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")
    
    elif password:
        st.error("❌ รหัสผ่านไม่ถูกต้อง")
