# ⚡ Quick Start Guide - ระบบรายงานปัญหา

## 🚀 เริ่มต้นใน 5 นาที

### 1️⃣ ติดตั้ง Node.js
- ดาวน์โหลดจาก https://nodejs.org (LTS version)
- ติดตั้งแบบปกติ

### 2️⃣ ตั้งค่า MongoDB
**ตัวเลือกที่ 1 - MongoDB Atlas (ง่ายที่สุด)**
```bash
# 1. ไปที่ https://www.mongodb.com/cloud/atlas
# 2. สมัครสมาชิกฟรี
# 3. สร้าง Cluster
# 4. ได้ Connection String
# 5. นำไปใส่ในไฟล์ .env
```

**ตัวเลือกที่ 2 - MongoDB ในเครื่อง (macOS)**
```bash
brew install mongodb-community
brew services start mongodb-community
```

**ตัวเลือกที่ 3 - MongoDB ในเครื่อง (Windows)**
- ดาวน์โหลด Community Server จาก MongoDB
- ติดตั้งแบบปกติ
- MongoDB จะรันเป็น Service โดยอัตโนมัติ

### 3️⃣ โหลด files
```bash
# สร้างโฟลเดอร์
mkdir facility-reporting-system
cd facility-reporting-system

# Copy ไฟล์ทั้งหมดที่ได้รับมา:
# - server.js
# - package.json
# - public/index.html
# - public/admin.html
# - public/style.css
# - .env.example
# - .gitignore
```

### 4️⃣ ติดตั้ง Dependencies
```bash
npm install
```

### 5️⃣ ตั้งค่า .env
```bash
# สร้างไฟล์ .env โดยคัดลอกจาก .env.example
cp .env.example .env

# แก้ไข .env ตามความต้องการของคุณ
# PORT=3000
# MONGODB_URI=mongodb://localhost:27017/facility-reporting
# ADMIN_PASSWORD=admin123456
```

### 6️⃣ รัน Server
```bash
npm start
```

### 7️⃣ เปิดแอป
```
ผู้ใช้ทั่วไป:  http://localhost:3000
Admin Panel:  http://localhost:3000/admin
รหัส Admin:   admin123456
```

---

## 📱 URL ที่สำคัญ

| URL | ประเภท | การใช้งาน |
|-----|---------|---------|
| http://localhost:3000 | Public | ส่งรายงานและติดตามสถานะ |
| http://localhost:3000/admin | Admin | จัดการรายงานและแก้สถานะ |

---

## 🔑 Admin Functions

### เข้าสู่ Admin
1. ไปที่ http://localhost:3000/admin
2. ใส่รหัสผ่าน (default: `admin123456`)
3. คลิก "เข้าสู่ระบบ"

### ฟีเจอร์ใน Admin
- 📊 ดูสถิติรายงาน
- 🔍 ค้นหารายงาน
- 🏷️ ตัดกลั่นตามสถานะ
- ✏️ แก้ไขสถานะ/หมายเหตุ/ผู้รับผิดชอบ
- 🗑️ ลบรายงาน

---

## 🐛 แก้ปัญหาทั่วไป

**❌ Error: Cannot connect to MongoDB**
```bash
# ตรวจสอบว่า MongoDB กำลังรัน
# macOS:
brew services list | grep mongodb

# ตรวจสอบ MONGODB_URI ใน .env ถูกต้อง
```

**❌ Error: Port 3000 already in use**
```bash
# macOS/Linux:
lsof -ti:3000 | xargs kill -9

# Windows PowerShell:
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess | Stop-Process
```

**❌ Admin password not working**
```bash
# 1. ตรวจสอบ ADMIN_PASSWORD ใน .env
# 2. Restart server (Ctrl+C แล้ว npm start)
```

**❌ Files not uploading**
```bash
# ตรวจสอบว่า uploads/ folder มีอยู่
mkdir uploads
```

---

## 📦 API Endpoints (สำหรับ Developer)

### User API
```
POST   /api/issues
GET    /api/issues
GET    /api/issues/:id
GET    /api/issues/search/:term
```

### Admin API (ต้อง Header: X-Admin-Password)
```
PUT    /api/admin/issues/:id
DELETE /api/admin/issues/:id
GET    /api/admin/stats
GET    /api/admin/issues
```

---

## 🚀 Deploy ขึ้น Production

### Option 1: Heroku (ฟรี)
```bash
heroku login
heroku create your-app-name
git push heroku main
```

### Option 2: Railway (ฟรี + บางส่วนเสียเงิน)
1. ไปที่ https://railway.app
2. Connect GitHub
3. Set Environment Variables
4. Deploy

### Option 3: DigitalOcean
1. สร้าง Droplet ($5/month)
2. SSH เข้า
3. Clone repo
4. ติดตั้ง Node.js + MongoDB
5. ใช้ PM2 เพื่อให้ app ทำงานตลอด

---

## 💡 ขั้นตอนถัดไป

1. **เปลี่ยนรหัส Admin** ใน .env
2. **ตั้งค่า MongoDB Atlas** สำหรับ Production
3. **Enable HTTPS** เมื่อ Deploy
4. **ตั้งค่า Email notification** (optional)
5. **เพิ่มประเภทปัญหา** ตามความต้องการ

---

## 📞 ต้องการความช่วยเหลือ?
สอบถาม IT Team หรือดู README.md สำหรับรายละเอียดเพิ่มเติม
