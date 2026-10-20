# Setup Guide - Annual Report Portal

This guide will help you set up and run the Annual Report Portal application on your local machine.

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your system:

1. **Python 3.9 or higher**
   - Download from: https://www.python.org/downloads/
   - Verify installation: `python --version`

2. **Node.js 18 or higher and npm**
   - Download from: https://nodejs.org/
   - Verify installation: `node --version` and `npm --version`

3. **MongoDB**
   - Download from: https://www.mongodb.com/try/download/community
   - Or use MongoDB Atlas (cloud): https://www.mongodb.com/atlas
   - Verify installation: `mongod --version`

4. **Git** (optional, for cloning)
   - Download from: https://git-scm.com/downloads

## 🔧 Installation Steps

### Step 1: Extract the Project

If you received a ZIP file:
1. Extract the ZIP file to a location of your choice
2. Navigate to the extracted folder using terminal/command prompt

### Step 2: Set Up Backend

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a Python virtual environment (recommended):**
   
   **For Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
   
   **For macOS/Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note:** If you encounter issues with `tensorflow`, try:
   ```bash
   pip install tensorflow --upgrade
   ```
   
   **Note:** For `pytesseract` (OCR), you may need to install Tesseract separately:
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - macOS: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`

4. **Configure environment variables:**
   - Copy `env.example` file from the root directory to `backend/.env`
   - Or create a `.env` file in the `backend` directory with the following content:
   ```env
   # Database Configuration
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=annual_report

   # JWT Configuration
   SECRET_KEY=your-secret-key-change-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # CORS Configuration
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

   # File Upload Configuration
   MAX_FILE_SIZE=10485760
   ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/gif,image/webp
   UPLOAD_DIR=uploads

   # ML Configuration
   ML_MODEL_PATH=./ml/models/model.h5
   ML_THRESHOLD=0.6
   ML_ENABLED=true

   # Application Configuration
   APP_NAME=Annual Report Portal
   VERSION=1.0.0
   DEBUG=false

   # Frontend Configuration
   REACT_APP_API_URL=http://localhost:8000
   REACT_APP_ENVIRONMENT=development
   ```

5. **Start MongoDB:**
   
   **If MongoDB is installed locally:**
   - Windows: MongoDB should start automatically as a service, or run:
     ```bash
     mongod
     ```
   - macOS/Linux: 
     ```bash
     sudo systemctl start mongod
     # or
     mongod
     ```
   
   **If using MongoDB Atlas:**
   - Update `MONGODB_URL` in `.env` with your Atlas connection string

6. **Create necessary directories:**
   ```bash
   # In the backend directory
   mkdir uploads
   ```

### Step 3: Set Up Frontend

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```
   (Or from root: `cd ../frontend`)

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```
   
   This may take a few minutes. If you encounter issues:
   - Try deleting `node_modules` and `package-lock.json`, then run `npm install` again
   - On Windows, you might need to run PowerShell as Administrator

3. **Create environment file (optional):**
   - The frontend reads from `process.env.REACT_APP_API_URL`
   - Default is `http://localhost:8000` which should work if backend is running on port 8000
   - To customize, create a `.env` file in the `frontend` directory:
   ```env
   REACT_APP_API_URL=http://localhost:8000
   REACT_APP_ENVIRONMENT=development
   ```

## 🚀 Running the Application

### Start MongoDB

Make sure MongoDB is running before starting the application.

**Check if MongoDB is running:**
```bash
# Windows
mongod --version

# macOS/Linux
sudo systemctl status mongod
```

### Start Backend Server

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Activate virtual environment (if not already activated):**
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. **Run the backend server:**
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```

   You should see output like:
   ```
   INFO:     Uvicorn running on http://127.0.0.1:8000
   INFO:     Application startup complete.
   ✅ Connected to MongoDB
   ```

4. **Verify backend is running:**
   - Open browser: http://localhost:8000
   - API documentation: http://localhost:8000/docs

### Start Frontend Server

1. **Open a new terminal/command prompt**

2. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

3. **Start the React development server:**
   ```bash
   npm start
   ```

   This will:
   - Start the development server
   - Automatically open http://localhost:3000 in your browser
   - If it doesn't open automatically, navigate to http://localhost:3000

4. **You should see the application running!**

## 📝 Quick Start Commands Summary

### One-time Setup:
```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
mkdir uploads
# Create .env file (copy from env.example)

# Frontend
cd frontend
npm install
```

### Daily Usage:
```bash
# Terminal 1 - Backend
cd backend
venv\Scripts\activate  # Windows (skip if already activated)
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm start
```

## 🗄️ Database Setup (Optional)

If you want to seed the database with sample data:

```bash
cd backend
python scripts/seed_db.py
```

This will create:
- Admin user: `admin@example.com` / `password123`
- Sample students and activities
- Test data for development

## 🔍 Verifying Installation

1. **Backend Health Check:**
   - Visit: http://localhost:8000/health
   - Should return: `{"status": "healthy", "service": "annual-report-api"}`

2. **API Documentation:**
   - Visit: http://localhost:8000/docs
   - Should show Swagger UI with all API endpoints

3. **Frontend:**
   - Visit: http://localhost:3000
   - Should show the landing page

## ⚠️ Common Issues and Solutions

### Issue: MongoDB Connection Error

**Solution:**
- Ensure MongoDB is installed and running
- Check `MONGODB_URL` in `.env` file
- Verify MongoDB is accessible: `mongosh` or `mongo` command
- For MongoDB Atlas, ensure IP is whitelisted

### Issue: Port Already in Use

**Solution:**
- Backend (8000): Change port in command: `--port 8001`
- Frontend (3000): React will prompt to use a different port, or set `PORT=3001` in `.env`

### Issue: Python Module Not Found

**Solution:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.9+)

### Issue: npm install fails

**Solution:**
- Clear cache: `npm cache clean --force`
- Delete `node_modules` and `package-lock.json`, then `npm install`
- Try: `npm install --legacy-peer-deps`

### Issue: TensorFlow Installation Issues

**Solution:**
- Install separately: `pip install tensorflow`
- On Windows, may need Visual C++ Redistributables
- Consider using CPU-only version if GPU drivers are missing

### Issue: pytesseract Not Working

**Solution:**
- Install Tesseract OCR separately (see Step 2.3)
- On Windows, add Tesseract to PATH or set `pytesseract.pytesseract.tesseract_cmd` in code

### Issue: Frontend Can't Connect to Backend

**Solution:**
- Verify backend is running on port 8000
- Check `REACT_APP_API_URL` in frontend `.env`
- Check browser console for CORS errors
- Ensure backend CORS settings include `http://localhost:3000`

### Issue: "Module not found: Error: Can't resolve './pages/EditActivity'"

**Solution:**
- This error occurs if the `EditActivity.js` file is missing from `frontend/src/pages/`
- Make sure you extracted all files from the ZIP
- Verify `frontend/src/pages/EditActivity.js` exists
- If missing, contact the project developer or check the latest version of the codebase
- **Note:** Some npm warnings about deprecated packages are normal and can be ignored. They don't prevent the application from running.

### Issue: Bcrypt/Passlib Compatibility Error

**Error Message:**
```
AttributeError: module 'bcrypt' has no attribute '__about__'
ValueError: password cannot be longer than 72 bytes
```

**Solution:**
1. Stop the backend server (Ctrl+C in the terminal)
2. Uninstall and reinstall bcrypt:
   ```bash
   pip uninstall bcrypt -y
   pip install "bcrypt>=3.2.0,<4.0.0"
   ```
3. Restart the backend server
4. Try registering/login again

**Why this happens:** Newer versions of bcrypt (4.0.0+) are incompatible with passlib 1.7.4. The fix ensures a compatible version is installed.

See `backend/FIX_BCRYPT.md` for detailed instructions.

## 🌐 Access Points

Once everything is running:

- **Frontend Application:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Alternative API Docs:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## 📦 Project Structure

```
annual-report/
├── backend/              # FastAPI backend
│   ├── app/             # Application code
│   ├── uploads/         # Uploaded files (create if missing)
│   ├── requirements.txt # Python dependencies
│   └── .env            # Environment variables (create this)
├── frontend/            # React frontend
│   ├── src/            # Source code
│   ├── public/         # Static files
│   └── package.json    # Node dependencies
├── ml/                  # ML models (optional)
└── SETUP.md            # This file
```

## 🆘 Need Help?

If you encounter issues:

1. Check the error messages carefully
2. Verify all prerequisites are installed
3. Ensure MongoDB is running
4. Check environment variables in `.env` files
5. Review the common issues section above

## ✅ Success Checklist

- [ ] Python 3.9+ installed
- [ ] Node.js 18+ and npm installed
- [ ] MongoDB installed and running
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] `.env` file created in backend directory
- [ ] `uploads` directory created in backend
- [ ] Backend server running on http://localhost:8000
- [ ] Frontend server running on http://localhost:3000
- [ ] Can access API docs at http://localhost:8000/docs

## 📦 Creating ZIP File for Client Delivery

### Fast ZIP Creation (Recommended)

To create a lightweight, fast ZIP file for your client (excluding node_modules, venv, etc.):

**For Windows (PowerShell):**
```powershell
.\create-client-zip.ps1
```

**For macOS/Linux (Bash):**
```bash
chmod +x create-client-zip.sh
./create-client-zip.sh
```

**Cross-platform (Python):**
```bash
python create-client-zip.py
```

These scripts will:
- ✅ Exclude `node_modules/` (can be 100+ MB)
- ✅ Exclude `venv/` or `env/` (virtual environment)
- ✅ Exclude `__pycache__/` (Python cache files)
- ✅ Exclude `.git/` (version control)
- ✅ Exclude `uploads/` and `reports/` (generated files)
- ✅ Exclude build artifacts and cache files
- ✅ Use **no compression** for maximum speed
- ✅ Create a much smaller ZIP file

**Expected Results:**
- Original project: 500+ MB (with node_modules, venv, etc.)
- Client ZIP: Usually 5-20 MB (source code only)
- Creation time: 10-30 seconds instead of several minutes

The client can then run `npm install` and `pip install -r requirements.txt` to restore dependencies.

---

**Happy Coding! 🎉**

