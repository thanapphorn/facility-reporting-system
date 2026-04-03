import streamlit as st
import pickle
import pandas as pd
import importlib

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="centered")
st.title("🎬 Movie Recommender System")
st.caption("แอปนี้ใช้ข้อมูลจาก recommendation_data.pkl และฟังก์ชัน get_movie_recommendations จาก myfunction_67130701922.py")

# โหลดโมดูลฟังก์ชัน
try:
    mod = importlib.import_module("myfunction_67130701922")
    get_movie_recommendations = getattr(mod, "get_movie_recommendations")
    st.success("✅ โหลดฟังก์ชันสำเร็จ!")
except Exception as e:
    st.error(f"ไม่สามารถโหลดฟังก์ชันได้: {e}")

# โหลดข้อมูล .pkl
uploaded = st.file_uploader("📂 Upload recommendation_data.pkl", type=["pkl"])
if uploaded is not None:
    try:
        user_similarity_df, user_movie_ratings = pickle.load(uploaded)
        st.success("✅ โหลดข้อมูลเรียบร้อยแล้ว!")
    except Exception as e:
        st.error(f"❌ โหลดข้อมูลล้มเหลว: {e}")
else:
    st.info("📁 โปรดอัปโหลดไฟล์ recommendation_data.pkl")

# เลือกพารามิเตอร์
st.subheader("🎯 Recommendation Settings")
user_id = st.number_input("User ID", min_value=0, value=1, step=1)
top_n = st.slider("จำนวนคำแนะนำ (Top N)", 1, 20, 10)

# ปุ่มสำหรับสร้างคำแนะนำ
if st.button("💡 สร้างคำแนะนำ"):
    try:
        recommendations = get_movie_recommendations(user_id, user_similarity_df, user_movie_ratings, top_n)
        if recommendations:
            st.success(f"Top {top_n} Movie Recommendations for User {user_id}")
            for i, movie in enumerate(recommendations, 1):
                st.write(f"{i}. {movie}")
        else:
            st.warning("ไม่พบคำแนะนำสำหรับผู้ใช้นี้")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
