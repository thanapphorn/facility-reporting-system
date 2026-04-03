require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const path = require('path');
const multer = require('multer');
const fs = require('fs');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Multer for file uploads
const uploadDir = 'uploads';
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir);
}

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + '-' + file.originalname);
  }
});

const upload = multer({ storage });

// MongoDB Connection
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/facility-reporting')
  .then(() => console.log('✓ Connected to MongoDB'))
  .catch(err => console.log('✗ MongoDB Error:', err));

// Issue Schema
const issueSchema = new mongoose.Schema({
  reportId: {
    type: String,
    unique: true,
    default: () => 'RTP' + Date.now()
  },
  reporterName: String,
  reporterPhone: String,
  category: String,
  location: String,
  description: String,
  files: [String],
  status: {
    type: String,
    enum: ['pending', 'inprogress', 'resolved'],
    default: 'pending'
  },
  dateSubmitted: Date,
  assignedTo: String,
  notes: String,
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

const Issue = mongoose.model('Issue', issueSchema);

// ========== USER API ==========

// ส่งรายงานใหม่
app.post('/api/issues', upload.array('files', 5), async (req, res) => {
  try {
    const { reporterName, reporterPhone, category, location, description } = req.body;

    if (!reporterName || !reporterPhone || !category || !location || !description) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    const files = req.files.map(f => f.filename);

    const issue = new Issue({
      reporterName,
      reporterPhone,
      category,
      location,
      description,
      files,
      dateSubmitted: new Date()
    });

    await issue.save();

    res.status(201).json({
      success: true,
      message: 'ส่งรายงานสำเร็จ',
      reportId: issue.reportId,
      issue
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to create issue' });
  }
});

// ดูรายงานทั้งหมด
app.get('/api/issues', async (req, res) => {
  try {
    const issues = await Issue.find().sort({ createdAt: -1 });
    res.json(issues);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch issues' });
  }
});

// ดูรายงานตาม ID
app.get('/api/issues/:id', async (req, res) => {
  try {
    const issue = await Issue.findOne({ reportId: req.params.id });
    if (!issue) {
      return res.status(404).json({ error: 'Issue not found' });
    }
    res.json(issue);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch issue' });
  }
});

// ค้นหารายงาน
app.get('/api/issues/search/:term', async (req, res) => {
  try {
    const term = req.params.term;
    const issues = await Issue.find({
      $or: [
        { reportId: new RegExp(term, 'i') },
        { location: new RegExp(term, 'i') },
        { reporterName: new RegExp(term, 'i') }
      ]
    }).sort({ createdAt: -1 });
    res.json(issues);
  } catch (err) {
    res.status(500).json({ error: 'Search failed' });
  }
});

// ========== ADMIN API ==========

// Verify Admin Password
const verifyAdmin = (req, res, next) => {
  const password = req.headers['x-admin-password'];
  if (password !== process.env.ADMIN_PASSWORD) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  next();
};

// อัปเดตสถานะรายงาน
app.put('/api/admin/issues/:id', verifyAdmin, async (req, res) => {
  try {
    const { status, assignedTo, notes } = req.body;

    const issue = await Issue.findOneAndUpdate(
      { reportId: req.params.id },
      {
        status,
        assignedTo,
        notes,
        updatedAt: new Date()
      },
      { new: true }
    );

    if (!issue) {
      return res.status(404).json({ error: 'Issue not found' });
    }

    res.json({
      success: true,
      message: 'อัปเดตรายงานสำเร็จ',
      issue
    });
  } catch (err) {
    res.status(500).json({ error: 'Failed to update issue' });
  }
});

// ลบรายงาน
app.delete('/api/admin/issues/:id', verifyAdmin, async (req, res) => {
  try {
    const issue = await Issue.findOneAndDelete({ reportId: req.params.id });

    if (!issue) {
      return res.status(404).json({ error: 'Issue not found' });
    }

    // ลบไฟล์ที่อัปโหลด
    issue.files.forEach(file => {
      const filePath = path.join(uploadDir, file);
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
      }
    });

    res.json({
      success: true,
      message: 'ลบรายงานสำเร็จ'
    });
  } catch (err) {
    res.status(500).json({ error: 'Failed to delete issue' });
  }
});

// สถิติรายงาน
app.get('/api/admin/stats', verifyAdmin, async (req, res) => {
  try {
    const total = await Issue.countDocuments();
    const pending = await Issue.countDocuments({ status: 'pending' });
    const inprogress = await Issue.countDocuments({ status: 'inprogress' });
    const resolved = await Issue.countDocuments({ status: 'resolved' });

    const byCategory = await Issue.aggregate([
      { $group: { _id: '$category', count: { $sum: 1 } } }
    ]);

    res.json({
      total,
      pending,
      inprogress,
      resolved,
      byCategory
    });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch stats' });
  }
});

// ดูรายงานทั้งหมด (Admin)
app.get('/api/admin/issues', verifyAdmin, async (req, res) => {
  try {
    const issues = await Issue.find().sort({ createdAt: -1 });
    res.json(issues);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch issues' });
  }
});

// Static files
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/admin', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'admin.html'));
});

// 404 Handler
app.use((req, res) => {
  res.status(404).json({ error: 'Not found' });
});

// Error Handler
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: 'Internal server error' });
});

// Start Server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`✓ Server running on http://localhost:${PORT}`);
  console.log(`✓ User App: http://localhost:${PORT}`);
  console.log(`✓ Admin Panel: http://localhost:${PORT}/admin`);
});
