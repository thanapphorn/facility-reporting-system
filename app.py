import streamlit as st
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os

st.set_page_config(page_title="🔧 ระบบรายงานปัญหา", page_icon="🔧", layout="wide")

@st.cache_resource
def get_db():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    db = client["facility-reporting"]
    return db["issues"]

async def get_issues():
    db = get_db()
    return await db.find().to_list(length=1000)

async def insert_issue(issue_data):
    db = get_db()
    result = await db.insert_one(issue_data)
    return result.inserted_id

async def find_issues(query):
    db = get_db()
    return await db.find(query).to_list(length=1000)

async def update_issue(report_id, status):
    db = get_db()
    await db.update_one(
        {"reportId": report_id},
        {"$set": {"status": status, "updatedAt": datetime.now()}}
    )

async def delete_issue(report_id):
    db = get_db()
    await db.delete_one({"reportId": report_id})


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

# ========================
# ส่งรายงาน
# ========================
if st.session_state.page == "report":

    st.subheader("📝 ส่งรายงานปัญหา")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("👤 ชื่อ")
        phone = st.text_input("📱 เบอร์โทร")

    with col2:
        category = st.selectbox(
            "🏷️ ประเภท",
            [
                "💧 น้ำรั่ว",
                "🚽 ห้องน้ำ",
                "🗑️ ถังขยะ",
                "💡 ไฟฟ้า",
                "❄️ ปรับอากาศ",
                "🪑 เฟอร์นิเจอร์",
                "🅿️ ที่จอด",
                "📝 อื่นๆ"
            ]
        )

    location = st.text_input("📍 สถานที่")
    description = st.text_area("📝 รายละเอียด", height=150)

    if st.button("✅ ส่ง", use_container_width=True):

        if not name or not phone or not location or not description:
            st.error("❌ กรุณากรอกข้อมูลให้ครบ")

        else:

            report_id = f"RTP{int(datetime.now().timestamp())}"

            cat_map = {
                "💧 น้ำรั่ว": "water",
                "🚽 ห้องน้ำ": "toilet",
                "🗑️ ถังขยะ": "trash",
                "💡 ไฟฟ้า": "light",
                "❄️ ปรับอากาศ": "hvac",
                "🪑 เฟอร์นิเจอร์": "furniture",
                "🅿️ ที่จอด": "parking",
                "📝 อื่นๆ": "other"
            }

            issue_data = {
                "reportId": report_id,
                "reporterName": name,
                "reporterPhone": phone,
                "category": cat_map[category],
                "location": location,
                "description": description,
                "status": "pending",
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            }

            asyncio.run(insert_issue(issue_data))

            st.success(f"✅ ส่งสำเร็จ หมายเลข {report_id}")
            st.balloons()


# ========================
# ติดตามสถานะ
# ========================
elif st.session_state.page == "status":

    st.subheader("📊 ติดตามสถานะ")

    search = st.text_input("🔍 ค้นหาเลขรายงาน")

    if search:

        docs = asyncio.run(find_issues({
            "reportId": {"$regex": search, "$options": "i"}
        }))

    else:

        docs = asyncio.run(get_issues())

    if docs:

        docs = sorted(docs, key=lambda x: x["createdAt"], reverse=True)

        for doc in docs:

            status_icon = {
                "pending": "🟡",
                "inprogress": "🔵",
                "resolved": "🟢"
            }

            status_text = {
                "pending": "รอตรวจสอบ",
                "inprogress": "กำลังแก้ไข",
                "resolved": "แก้ไขแล้ว"
            }

            st.write(
                f"{status_icon[doc['status']]} **#{doc['reportId']}** - {doc['location']}"
            )

            st.write(doc["description"])

            st.write(
                f"👤 {doc['reporterName']} | 📱 {doc['reporterPhone']} | {status_text[doc['status']]}"
            )

            st.divider()

    else:

        st.info("📭 ไม่พบข้อมูล")


# ========================
# ADMIN
# ========================
elif st.session_state.page == "admin":

    st.subheader("🔐 Admin")

    pwd = st.text_input("รหัสผ่าน", type="password")

    if pwd == os.getenv("ADMIN_PASSWORD", "admin123456"):

        st.success("เข้าสู่ระบบแล้ว")

        docs = asyncio.run(get_issues())

        docs = sorted(docs, key=lambda x: x["createdAt"], reverse=True)

        for doc in docs:

            col1, col2, col3 = st.columns([2,1,1])

            with col1:
                st.write(f"#{doc['reportId']} - {doc['location']}")
                st.write(doc["description"])

            with col2:

                new_status = st.selectbox(
                    "สถานะ",
                    ["pending","inprogress","resolved"],
                    index=["pending","inprogress","resolved"].index(doc["status"]),
                    key=doc["reportId"]
                )

                if new_status != doc["status"]:

                    asyncio.run(update_issue(doc["reportId"], new_status))
                    st.rerun()

            with col3:

                if st.button("ลบ", key=f"del{doc['reportId']}"):

                    asyncio.run(delete_issue(doc["reportId"]))
                    st.rerun()

            st.divider()

    elif pwd:
        st.error("รหัสผ่านไม่ถูกต้อง")
