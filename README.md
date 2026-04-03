# 🔧 ระบบรายงานปัญหาสิ่งอำนวยความสะดวก
## Facility Issue Reporting System with MongoDB

---

## 📋 ความต้องการของระบบ

- **Node.js** v14 ขึ้นไป
- **MongoDB** (ติดตั้งในเครื่องหรือใช้ MongoDB Atlas Cloud)
- **npm** หรือ **yarn**
- **Browser** ที่มี JavaScript support

---

## 🚀 วิธีการติดตั้ง

### ขั้นที่ 1: ตรวจสอบ Node.js และ npm

```bash
node --version
npm --version
```

### ขั้นที่ 2: สร้างโฟลเดอร์โปรเจค

```bash
mkdir facility-reporting-system
cd facility-reporting-system
```

### ขั้นที่ 3: สร้างโครงสร้างไฟล์

```
facility-reporting-system/
├── server.js              # Backend server
├── package.json           # npm dependencies
├── public/
│   ├── index.html         # หน้าหลัก (User)
│   ├── admin.html         # หน้า Admin
│   └── style.css          # CSS ร่วม
├── models/
│   └── Issue.js           # MongoDB schema
├── routes/
│   ├── issues.js          # API routes
│   └── admin.js           # Admin routes
└── .env                   # Environment variables
```

### ขั้นที่ 4: ติดตั้ง Dependencies

```bash
npm init -y
npm install express mongoose dotenv cors multer
```

### ขั้นที่ 5: ตั้งค่า MongoDB

**ตัวเลือกที่ 1: MongoDB Atlas (Cloud)**
1. ไปที่ https://www.mongodb.com/cloud/atlas
2. สมัครสมาชิก (ฟรี)
3. สร้าง Cluster
4. ได้ Connection String เช่น: `mongodb+srv://username:password@cluster.mongodb.net/dbname`

**ตัวเลือกที่ 2: MongoDB ในเครื่อง (Local)**
```bash
# macOS (ถ้าติดตั้ง Homebrew)
brew install mongodb-community
brew services start mongodb-community

# Linux/Windows: ดาวน์โหลดจาก https://www.mongodb.com/try/download/community
```

### ขั้นที่ 6: ตั้งค่า Environment Variables

สร้างไฟล์ `.env`:
```
PORT=3000
MONGODB_URI=mongodb://localhost:27017/facility-reporting
ADMIN_PASSWORD=admin123456
NODE_ENV=development
```

**หมายเหตุ**: ถ้าใช้ MongoDB Atlas ให้เปลี่ยนเป็น:
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/facility-reporting
```

### ขั้นที่ 7: รัน Server

```bash
node server.js
```

ถ้าสำเร็จจะเห็น:
```
✓ Server running on http://localhost:3000
✓ Connected to MongoDB
```

---

## 🌐 วิธีการใช้งาน

### ผู้ใช้ทั่วไป
1. เปิด http://localhost:3000
2. ส่งรายงานปัญหา
3. ติดตามสถานะรายงาน

### ผู้ดูแลระบบ (Admin)
1. เปิด http://localhost:3000/admin
2. ใส่รหัสผ่าน (default: `admin123456`)
3. ดูรายงานทั้งหมด
4. แก้ไขสถานะ
5. ลบรายงาน

---

## 📡 API Endpoints

### User API
```
POST   /api/issues              - ส่งรายงานใหม่
GET    /api/issues              - ดูรายงานทั้งหมด
GET    /api/issues/:id          - ดูรายงานตาม ID
GET    /api/issues/search/:term - ค้นหารายงาน
```

### Admin API
```
PUT    /api/admin/issues/:id    - แก้ไขสถานะ
DELETE /api/admin/issues/:id    - ลบรายงาน
GET    /api/admin/stats         - สถิติรายงาน
```

---

## 🔐 ความปลอดภัย

- เปลี่ยนรหัสผ่าน Admin ใน `.env`
- ในการ Deploy ให้ใช้ HTTPS
- ป้องกัน CORS สำหรับ origin ที่อนุญาตเท่านั้น

---

## 📦 Deployment

### Option 1: Heroku
```bash
heroku login
heroku create facility-reporting
git push heroku main
```

### Option 2: Railway
1. ไปที่ https://railway.app
2. สมัครสมาชิก
3. Connect GitHub repo
4. Set environment variables
5. Deploy

### Option 3: DigitalOcean / AWS
1. ติดตั้ง Node.js บนเซิร์ฟเวอร์
2. Clone repository
3. ติดตั้ง dependencies
4. ใช้ PM2 เพื่อให้ server ทำงานแบบ daemon

---

## 🐛 Troubleshooting

**Error: Cannot connect to MongoDB**
- ตรวจสอบ MongoDB กำลังรัน
- ตรวจสอบ MONGODB_URI ถูกต้อง

**Error: Port 3000 already in use**
```bash
# macOS/Linux
lsof -ti:3000 | xargs kill -9

# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**Admin password not working**
- ตรวจสอบค่า ADMIN_PASSWORD ใน `.env`
- Restart server หลังแก้ไข

---

## 📞 ต้องการความช่วยเหลือเพิ่มเติม?

สอบถามทีม IT หรือติดต่อผู้พัฒนา
