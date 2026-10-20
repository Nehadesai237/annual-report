# 📚 Annual Report Portal - Complete Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Database Design](#database-design)
5. [Backend Implementation](#backend-implementation)
6. [Frontend Implementation](#frontend-implementation)
7. [Authentication & Security](#authentication--security)
8. [Activity Management System](#activity-management-system)
9. [Admin Panel & Review System](#admin-panel--review-system)
10. [Report Generation](#report-generation)
11. [File Upload & Management](#file-upload--management)
12. [Deployment](#deployment)

---

## Project Overview

The **Annual Report Portal (EduReport)** is a comprehensive web application designed for educational institutions to:
- Collect and manage student/faculty activities
- Validate uploaded images using Machine Learning
- Verify certificates using OCR and semantic similarity
- Enable admin review of rejected activities
- Generate downloadable annual reports with analytics

### Key Features
✅ Role-based authentication (Student, Faculty, Admin)  
✅ Activity submission with multiple images  
✅ Certificate validation using OCR and keyword matching  
✅ ML-powered image verification  
✅ Admin panel for reviewing rejected activities  
✅ PDF/HTML report generation with charts  
✅ Responsive design with modern UI  

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     React Frontend                       │
│  (React Router, TailwindCSS, Axios, React Icons)        │
└────────────────────┬────────────────────────────────────┘
                     │ REST API (JSON)
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                         │
│  ┌──────────────┬──────────────┬───────────────────┐   │
│  │ Auth Service │ Activity Svc │ Report Service    │   │
│  │              │ ML Service   │ Certificate Svc   │   │
│  └──────────────┴──────────────┴───────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  MongoDB Database                        │
│  Collections: users, activities, reports, notifications │
└─────────────────────────────────────────────────────────┘
```

### Request Flow

1. **User Authentication**
   - User submits credentials → FastAPI validates → JWT token generated → Client stores token

2. **Activity Submission**
   - User uploads activity + images + certificate → Backend saves files → ML validates images → Certificate OCR validation → Status determined → Database updated

3. **Admin Review**
   - Admin fetches rejected activities → Reviews details → Approves/Discards → Status updated → User notified

---

## Technology Stack

### Backend Technologies
| Technology | Version | Purpose |
|-----------|---------|---------|
| **FastAPI** | 0.104+ | High-performance web framework |
| **Python** | 3.9+ | Programming language |
| **MongoDB** | 4.6+ | NoSQL database |
| **Motor** | 3.3+ | Async MongoDB driver |
| **Pydantic** | 2.8+ | Data validation & serialization |
| **JWT (python-jose)** | 3.3+ | Authentication tokens |
| **Bcrypt** | 3.2+ | Password hashing |
| **TensorFlow** | 2.10+ | ML model inference |
| **Pytesseract** | 0.3.10+ | OCR for certificate validation |
| **OpenCV** | 4.8+ | Image preprocessing |
| **Pillow** | 10.0+ | Image manipulation |
| **Jinja2** | 3.1+ | HTML template rendering |

**File:** `backend/requirements.txt`

### Frontend Technologies
| Technology | Version | Purpose |
|-----------|---------|---------|
| **React** | 18.2 | UI library |
| **React Router** | 6.3 | Routing |
| **TailwindCSS** | 3.1 | Styling framework |
| **Axios** | 0.27 | HTTP client |
| **React Hot Toast** | 2.4 | Notifications |
| **React Icons** | 4.4 | Icon library |
| **Recharts** | 2.5 | Data visualization |
| **React Dropzone** | 14.2 | File upload |
| **jsPDF** | 2.5 | PDF generation |

**File:** `frontend/package.json`

---

## Database Design

### MongoDB Collections

#### 1. Users Collection (`users`)
```javascript
{
  _id: ObjectId,
  name: String,              // Full name
  email: String,             // Unique email (login)
  password_hash: String,     // Bcrypt hashed password
  department: String,        // Department/Program
  role: String,              // "student", "faculty", "admin"
  student_id: String,        // For students only
  phone: String,             // Optional
  year_of_study: Integer,    // For students (1-5)
  is_active: Boolean,        // Account status
  email_verified: Boolean,   // Email verification
  last_login: DateTime,
  created_at: DateTime,
  updated_at: DateTime
}
```

**File:** `backend/app/models/user.py`

#### 2. Activities Collection (`activities`)
```javascript
{
  _id: ObjectId,
  user_id: String,           // Reference to user
  department: String,        // User's department
  title: String,             // Activity title
  description: String,       // Detailed description
  type: String,              // "social", "sports", "academic", "cultural", "technical"
  year: Integer,             // Year (2020-2030)
  achievement_type: String,  // "individual" or "group"
  group_members: [String],   // Array of user IDs for group
  
  // Image verification
  images: [{
    filename: String,
    path: String,
    verdict: String,         // "normal" or "abnormal"
    score: Float,            // ML confidence score
    ml_checked_at: DateTime
  }],
  
  // Certificate validation
  certificate_path: String,
  has_certificate: Boolean,
  certificate_validated: Boolean,
  certificate_validation_result: {
    valid: Boolean,
    confidence: Float,
    found_keywords: [String],
    missing_keywords: [String],
    match_percentage: Float,
    reason: String,
    extracted_text: String
  },
  
  // Status tracking
  status: String,            // "pending", "accepted", "rejected"
  ml_checked_at: DateTime,
  admin_reviewed_at: DateTime,
  admin_reviewed_by: String,
  admin_comments: String,
  
  created_at: DateTime,
  updated_at: DateTime
}
```

**File:** `backend/app/models/activity.py`

#### 3. Reports Collection (`reports`)
```javascript
{
  _id: ObjectId,
  type: String,              // "individual", "group", "department", "yearly"
  title: String,
  description: String,
  generated_by: String,      // User ID
  params: Object,            // Report parameters
  status: String,            // "generating", "completed", "failed"
  file_path: String,         // Path to generated file
  file_size: Integer,
  generated_at: DateTime,
  completed_at: DateTime
}
```

**File:** `backend/app/models/report.py`

#### 4. Notifications Collection (`notifications`)
```javascript
{
  _id: ObjectId,
  user_id: String,
  title: String,
  message: String,
  type: String,              // "info", "success", "warning", "error"
  read: Boolean,
  link: String,              // Optional link
  created_at: DateTime
}
```

**File:** `backend/app/models/notification.py`

---

## Backend Implementation

### Project Structure

```
backend/
├── app/
│   ├── main.py                      # FastAPI app entry point
│   ├── core/                        # Core configurations
│   │   ├── config.py                # Settings (MongoDB, JWT, etc.)
│   │   ├── database.py              # Database connection
│   │   ├── security.py              # Auth helpers (JWT, bcrypt)
│   │   └── exceptions.py            # Custom exceptions
│   ├── models/                      # Pydantic schemas
│   │   ├── user.py
│   │   ├── activity.py
│   │   ├── report.py
│   │   └── notification.py
│   ├── services/                    # Business logic
│   │   ├── user_service.py
│   │   ├── activity_service.py
│   │   ├── ml_service.py            # ML image verification
│   │   ├── certificate_validator.py # Certificate OCR validation
│   │   ├── report_service.py
│   │   └── notification_service.py
│   └── api/
│       └── v1/
│           ├── api.py               # Router aggregator
│           └── endpoints/
│               ├── auth.py          # /auth/login, /auth/register
│               ├── activities.py    # Activity CRUD
│               ├── admin.py         # Admin review
│               ├── reports.py       # Report generation
│               └── users.py         # User management
├── uploads/                         # Uploaded files
│   └── certificates/
├── reports/                         # Generated reports
├── ml/                              # ML models
├── scripts/
│   └── seed_db.py                   # Database seeding
├── tests/                           # Unit tests
├── requirements.txt
└── force_reseed.py                  # Reset database
```

### 1. Application Entry Point

**File:** `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.api.v1.api import api_router

# Create FastAPI app
app = FastAPI(
    title="Annual Report Portal API",
    description="API for managing academic activities and reports",
    version="1.0.0",
    docs_url="/docs"
)

# Lifespan events - MongoDB connection
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    app.state.db = AsyncIOMotorClient(settings.MONGODB_URL)
    await app.state.db.admin.command('ping')
    app.state.database = app.state.db[settings.DATABASE_NAME]
    print("✅ Connected to MongoDB")
    
    yield
    
    # Shutdown: Close MongoDB connection
    app.state.db.close()
    print("✅ Disconnected from MongoDB")

# CORS middleware - Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Annual Report Portal API", "version": "1.0.0"}
```

**Key Points:**
- FastAPI creates automatic OpenAPI documentation at `/docs`
- MongoDB connection managed in lifespan events
- CORS configured for React frontend
- All routes prefixed with `/api/v1`

### 2. Configuration Management

**File:** `backend/app/core/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Annual Report Portal"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "annual_report"
    
    # Security
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # ML Configuration
    ML_MODEL_PATH: str = "./ml/models/model.h5"
    ML_THRESHOLD: float = 0.6
    
    class Config:
        env_file = ".env"  # Load from .env file

settings = Settings()
```

**Environment Variables (.env):**
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=annual_report
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
ML_THRESHOLD=0.6
```

### 3. Authentication System

**File:** `backend/app/core/security.py`

```python
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def decode_access_token(token: str):
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.JWTError:
        return None
```

**Authentication Flow:**

1. **Registration** (`POST /api/v1/auth/register`)
   ```python
   # File: backend/app/api/v1/endpoints/auth.py
   
   @router.post("/register")
   async def register(user_data: UserCreate, db: AsyncIOMotorDatabase):
       # Validate user data
       # Check if email already exists
       existing = await db.users.find_one({"email": user_data.email})
       if existing:
           raise HTTPException(status_code=400, detail="Email already registered")
       
       # Hash password
       password_hash = get_password_hash(user_data.password)
       
       # Create user document
       user_doc = {
           "name": user_data.name,
           "email": user_data.email,
           "password_hash": password_hash,
           "department": user_data.department,
           "role": user_data.role,
           "is_active": True,
           "created_at": datetime.utcnow()
       }
       
       # Insert into database
       result = await db.users.insert_one(user_doc)
       
       return {"message": "Registration successful"}
   ```

2. **Login** (`POST /api/v1/auth/login`)
   ```python
   @router.post("/login")
   async def login(credentials: UserLogin, db: AsyncIOMotorDatabase):
       # Find user by email
       user = await db.users.find_one({"email": credentials.email})
       if not user:
           raise HTTPException(status_code=401, detail="Invalid credentials")
       
       # Verify password
       if not verify_password(credentials.password, user["password_hash"]):
           raise HTTPException(status_code=401, detail="Invalid credentials")
       
       # Create JWT token
       access_token = create_access_token(
           data={
               "sub": str(user["_id"]),
               "email": user["email"],
               "role": user["role"]
           },
           expires_delta=timedelta(minutes=30)
       )
       
       # Update last login
       await db.users.update_one(
           {"_id": user["_id"]},
           {"$set": {"last_login": datetime.utcnow()}}
       )
       
       return {
           "access_token": access_token,
           "token_type": "bearer",
           "user": user
       }
   ```

3. **Protected Routes** (JWT Authentication)
   ```python
   from fastapi import Depends, HTTPException
   from fastapi.security import HTTPBearer
   
   security = HTTPBearer()
   
   async def get_current_user(
       credentials: HTTPAuthorizationCredentials = Depends(security),
       db: AsyncIOMotorDatabase = Depends(get_database)
   ):
       token = credentials.credentials
       payload = decode_access_token(token)
       
       if not payload:
           raise HTTPException(status_code=401, detail="Invalid token")
       
       user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
       if not user:
           raise HTTPException(status_code=401, detail="User not found")
       
       return user
   ```

---

## Frontend Implementation

### Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── App.js                       # Main app with routing
│   ├── index.js                     # React entry point
│   ├── components/
│   │   ├── Navbar.js                # Navigation bar
│   │   ├── GuestNavbar.js           # Navbar for guests
│   │   ├── ProtectedRoute.js        # Route guard
│   │   └── landing/                 # Landing page components
│   ├── pages/
│   │   ├── LandingPage.js           # Home page
│   │   ├── Login.js                 # Login page
│   │   ├── Register.js              # Registration page
│   │   ├── Dashboard.js             # User dashboard
│   │   ├── Activities.js            # Activity list
│   │   ├── CreateActivity.js        # Submit activity
│   │   ├── EditActivity.js          # Edit activity
│   │   ├── ActivityDetail.js        # Activity details
│   │   ├── AdminPanel.js            # Admin review panel
│   │   ├── Reports.js               # Reports page
│   │   └── Profile.js               # User profile
│   ├── contexts/
│   │   ├── AuthContext.js           # Authentication state
│   │   └── NotificationContext.js   # Notifications
│   ├── services/
│   │   ├── authService.js           # Auth API calls
│   │   └── landingData.js           # Static data
│   ├── App.css
│   └── index.css                    # TailwindCSS
├── package.json
└── tailwind.config.js
```

### 1. Application Entry & Routing

**File:** `frontend/src/App.js`

```javascript
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar';

// Pages
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import Register from './pages/Register';
import Activities from './pages/Activities';
import CreateActivity from './pages/CreateActivity';
import AdminPanel from './pages/AdminPanel';
import Reports from './pages/Reports';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected routes */}
          <Route path="/activities" element={
            <ProtectedRoute>
              <Navbar />
              <Activities />
            </ProtectedRoute>
          } />
          
          <Route path="/activities/create" element={
            <ProtectedRoute>
              <Navbar />
              <CreateActivity />
            </ProtectedRoute>
          } />
          
          {/* Admin only route */}
          <Route path="/admin" element={
            <ProtectedRoute requireRole="admin">
              <Navbar />
              <AdminPanel />
            </ProtectedRoute>
          } />
          
          <Route path="/reports" element={
            <ProtectedRoute>
              <Navbar />
              <Reports />
            </ProtectedRoute>
          } />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
```

### 2. Authentication Context

**File:** `frontend/src/contexts/AuthContext.js`

```javascript
import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load user from localStorage on mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    
    if (token && savedUser) {
      setUser(JSON.parse(savedUser));
      // Set default axios header
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const response = await axios.post('http://localhost:8000/api/v1/auth/login', {
      email,
      password
    });
    
    const { access_token, user: userData } = response.data;
    
    // Save to localStorage
    localStorage.setItem('token', access_token);
    localStorage.setItem('user', JSON.stringify(userData));
    
    // Set axios default header
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    
    setUser(userData);
    return userData;
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };

  const register = async (userData) => {
    await axios.post('http://localhost:8000/api/v1/auth/register', userData);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, register, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
```

### 3. Protected Routes

**File:** `frontend/src/components/ProtectedRoute.js`

```javascript
import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';

const ProtectedRoute = ({ children, requireRole }) => {
  const { user, loading } = useContext(AuthContext);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    // Not logged in, redirect to login
    return <Navigate to="/login" replace />;
  }

  if (requireRole && user.role !== requireRole) {
    // User doesn't have required role
    return <Navigate to="/" replace />;
  }

  return children;
};

export default ProtectedRoute;
```

---

## Activity Management System

### Activity Submission Flow

**File:** `frontend/src/pages/CreateActivity.js` (Simplified)

```javascript
const CreateActivity = () => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    type: 'academic',
    year: new Date().getFullYear(),
    hasCertificate: false
  });
  const [images, setImages] = useState([]);
  const [certificate, setCertificate] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Create FormData for file upload
    const data = new FormData();
    data.append('title', formData.title);
    data.append('description', formData.description);
    data.append('type', formData.type);
    data.append('year', formData.year);
    data.append('has_certificate', formData.hasCertificate);
    
    // Add images
    images.forEach(image => {
      data.append('files', image);
    });
    
    // Add certificate if provided
    if (formData.hasCertificate && certificate) {
      data.append('certificate', certificate);
    }
    
    try {
      const response = await axios.post(
        'http://localhost:8000/api/v1/activities/',
        data,
        {
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      );
      
      toast.success('Activity submitted successfully!');
      navigate('/activities');
    } catch (error) {
      if (error.response?.data?.error?.code === 'CERTIFICATE_VALIDATION_FAILED') {
        toast.error('Certificate validation failed: ' + error.response.data.error.message);
      } else {
        toast.error('Failed to submit activity');
      }
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input 
        type="text" 
        value={formData.title}
        onChange={(e) => setFormData({...formData, title: e.target.value})}
        placeholder="Activity Title"
        required
      />
      
      <textarea
        value={formData.description}
        onChange={(e) => setFormData({...formData, description: e.target.value})}
        placeholder="Description"
        required
      />
      
      <input
        type="file"
        multiple
        accept="image/*"
        onChange={(e) => setImages(Array.from(e.target.files))}
        required
      />
      
      <label>
        <input
          type="checkbox"
          checked={formData.hasCertificate}
          onChange={(e) => setFormData({...formData, hasCertificate: e.target.checked})}
        />
        I have a certificate
      </label>
      
      {formData.hasCertificate && (
        <input
          type="file"
          accept="image/*,.pdf"
          onChange={(e) => setCertificate(e.target.files[0])}
          required
        />
      )}
      
      <button type="submit">Submit Activity</button>
    </form>
  );
};
```

### Backend Activity Creation

**File:** `backend/app/api/v1/endpoints/activities.py`

```python
@router.post("/", response_model=Activity)
async def create_activity(
    title: str = Form(...),
    description: str = Form(...),
    type: str = Form(...),
    year: int = Form(...),
    has_certificate: bool = Form(False),
    files: List[UploadFile] = File(...),
    certificate: Optional[UploadFile] = File(None),
    current_user: TokenData = Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create new activity with ML validation"""
    
    # 1. Validate and save uploaded images
    image_paths = []
    for file in files:
        # Validate file type
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(400, "Invalid file type")
        
        # Save file
        file_path = f"uploads/{uuid.uuid4()}.{file.filename.split('.')[-1]}"
        with open(file_path, "wb") as f:
            f.write(await file.read())
        image_paths.append(file_path)
    
    # 2. ML Image Verification
    ml_service = MLService()
    image_results = await ml_service.verify_images(image_paths)
    
    # 3. Certificate Validation (if provided)
    certificate_path = None
    certificate_validated = False
    certificate_result = None
    
    if has_certificate and certificate:
        # Save certificate
        cert_path = f"uploads/certificates/cert_{uuid.uuid4()}.{certificate.filename.split('.')[-1]}"
        with open(cert_path, "wb") as f:
            f.write(await certificate.read())
        certificate_path = cert_path
        
        # Validate certificate using OCR
        validation = certificate_validator.validate_certificate(
            certificate_path=cert_path,
            activity_title=title,
            activity_description=description
        )
        
        certificate_validated = validation["valid"]
        certificate_result = validation
        
        # Reject if certificate doesn't match
        if not certificate_validated:
            os.remove(cert_path)  # Delete invalid certificate
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "CERTIFICATE_VALIDATION_FAILED",
                    "message": validation["reason"],
                    "details": validation
                }
            )
    
    # 4. Determine activity status
    # If all images are "normal", status = "accepted"
    # If any image is "abnormal", status = "rejected" (needs admin review)
    all_normal = all(img["verdict"] == "normal" for img in image_results)
    status = "accepted" if all_normal else "rejected"
    
    # 5. Create activity document
    activity_doc = {
        "user_id": current_user.user_id,
        "title": title,
        "description": description,
        "type": type,
        "year": year,
        "images": image_results,
        "certificate_path": certificate_path,
        "has_certificate": has_certificate,
        "certificate_validated": certificate_validated,
        "certificate_validation_result": certificate_result,
        "status": status,
        "ml_checked_at": datetime.utcnow(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # 6. Save to database
    result = await db.activities.insert_one(activity_doc)
    activity_doc["_id"] = str(result.inserted_id)
    
    return activity_doc
```

**Key Points:**
- Files uploaded as `multipart/form-data`
- Images validated by ML service
- Certificate validated using OCR
- Status determined automatically
- Rejected activities go to admin review

---

## Admin Panel & Review System

### Admin Dashboard

**File:** `frontend/src/pages/AdminPanel.js` (Simplified)

```javascript
const AdminPanel = () => {
  const [rejectedActivities, setRejectedActivities] = useState([]);
  
  useEffect(() => {
    fetchRejectedActivities();
  }, []);
  
  const fetchRejectedActivities = async () => {
    const response = await axios.get('http://localhost:8000/api/v1/admin/rejected');
    setRejectedActivities(response.data);
  };
  
  const handleApprove = async (activityId) => {
    await axios.post(`http://localhost:8000/api/v1/admin/approve/${activityId}`, {
      comments: "Approved after manual review"
    });
    toast.success('Activity approved!');
    fetchRejectedActivities();
  };
  
  const handleDiscard = async (activityId) => {
    await axios.post(`http://localhost:8000/api/v1/admin/discard/${activityId}`, {
      comments: "Does not meet criteria"
    });
    toast.success('Activity discarded');
    fetchRejectedActivities();
  };
  
  return (
    <div>
      <h1>Rejected Activities - Admin Review</h1>
      {rejectedActivities.map(activity => (
        <div key={activity.id}>
          <h3>{activity.title}</h3>
          <p>{activity.description}</p>
          
          {/* Show images */}
          <div>
            {activity.images.map((img, i) => (
              <div key={i}>
                <img src={`http://localhost:8000/${img.path}`} />
                <span>ML Verdict: {img.verdict} ({img.score})</span>
              </div>
            ))}
          </div>
          
          <button onClick={() => handleApprove(activity.id)}>
            ✓ Approve
          </button>
          <button onClick={() => handleDiscard(activity.id)}>
            ✗ Discard
          </button>
        </div>
      ))}
    </div>
  );
};
```

### Backend Admin Endpoints

**File:** `backend/app/api/v1/endpoints/admin.py`

```python
@router.get("/rejected")
async def get_rejected_activities(
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all rejected activities for admin review"""
    activities = []
    cursor = db.activities.find({"status": "rejected"}).sort("created_at", -1)
    
    async for activity in cursor:
        activity["_id"] = str(activity["_id"])
        activities.append(activity)
    
    return activities

@router.post("/approve/{activity_id}")
async def approve_activity(
    activity_id: str,
    comments: Optional[str] = None,
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Approve a rejected activity"""
    result = await db.activities.update_one(
        {"_id": ObjectId(activity_id)},
        {
            "$set": {
                "status": "accepted",
                "admin_reviewed_at": datetime.utcnow(),
                "admin_reviewed_by": current_user.user_id,
                "admin_comments": comments,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(404, "Activity not found")
    
    return {"message": "Activity approved"}

@router.post("/discard/{activity_id}")
async def discard_activity(
    activity_id: str,
    comments: Optional[str] = None,
    current_user: TokenData = Depends(require_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Permanently discard an activity"""
    result = await db.activities.delete_one({"_id": ObjectId(activity_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(404, "Activity not found")
    
    return {"message": "Activity discarded"}
```

---

## Report Generation

### Report Service

**File:** `backend/app/services/report_service.py`

```python
class ReportService:
    """Generate HTML/PDF reports with statistics"""
    
    async def generate_individual_report(self, user_id: str) -> str:
        """Generate report for individual user"""
        # Get user activities
        activities = await self.db.activities.find({
            "user_id": user_id,
            "status": "accepted"
        }).to_list(length=None)
        
        # Get user info
        user = await self.db.users.find_one({"_id": ObjectId(user_id)})
        
        # Calculate statistics
        stats = {
            "total": len(activities),
            "by_type": self._count_by_type(activities),
            "by_year": self._count_by_year(activities)
        }
        
        # Render HTML template
        template = self.jinja_env.get_template('individual_report.html')
        html = template.render(
            user=user,
            activities=activities,
            stats=stats,
            generated_at=datetime.utcnow()
        )
        
        return html
    
    async def generate_department_report(self, department: str, year: int):
        """Generate report for entire department"""
        # Get all activities for department
        activities = await self.db.activities.find({
            "department": department,
            "year": year,
            "status": "accepted"
        }).to_list(length=None)
        
        # Calculate statistics
        stats = {
            "total_activities": len(activities),
            "total_students": len(set(a["user_id"] for a in activities)),
            "by_type": self._count_by_type(activities),
            "top_performers": await self._get_top_performers(department, year)
        }
        
        # Render template
        template = self.jinja_env.get_template('department_report.html')
        html = template.render(
            department=department,
            year=year,
            stats=stats,
            activities=activities
        )
        
        return html
```

---

## File Upload & Management

### File Storage Structure

```
uploads/
├── {uuid}.jpg              # Activity images
├── {uuid}.png
└── certificates/
    ├── cert_{uuid}.jpg     # Certificates
    └── cert_{uuid}.pdf
```

### File Upload Handling

```python
# Validate file type
ALLOWED_IMAGES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
ALLOWED_CERT = ALLOWED_IMAGES + ["application/pdf"]

# Validate file size
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_CERT_SIZE = 15 * 1024 * 1024   # 15MB

# Generate unique filename
filename = f"{uuid.uuid4()}.{original_filename.split('.')[-1]}"

# Save file
file_path = os.path.join("uploads", filename)
with open(file_path, "wb") as f:
    f.write(await file.read())
```

---

## Deployment

### Using Docker Compose

**File:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:6
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongodb:27017
      - DATABASE_NAME=annual_report
    depends_on:
      - mongodb
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/reports:/app/reports
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  mongodb_data:
```

**Commands:**
```bash
# Start all services
docker-compose up --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

---

## Summary

This project implements a complete workflow for:

1. ✅ **User Management** - Registration, login, JWT authentication
2. ✅ **Activity Submission** - Upload activities with images and certificates
3. ✅ **ML Validation** - Automatic image verification using CNN
4. ✅ **Certificate OCR** - Extract and validate certificate text
5. ✅ **Admin Review** - Manual review of rejected activities
6. ✅ **Report Generation** - PDF/HTML reports with charts
7. ✅ **Responsive UI** - Modern React + TailwindCSS interface

**Key Technologies:**
- **Backend:** FastAPI + MongoDB + TensorFlow + PyTesseract
- **Frontend:** React + TailwindCSS + Axios
- **Deployment:** Docker + Docker Compose

**Security Features:**
- JWT authentication
- Bcrypt password hashing
- Role-based access control
- File type and size validation
- CORS configuration

---

**For detailed ML and certificate validation logic, see:** `ML_CERTIFICATE_VALIDATION_GUIDE.md`

