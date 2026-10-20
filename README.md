# Annual Report Portal (EduReport)

A comprehensive web application for collecting department/student activities, validating images with ML, admin review, and generating downloadable annual reports.

## 🚀 Features

- **User Authentication**: JWT-based auth with roles (student, faculty, admin)
- **Activity Management**: Submit activities with images and metadata
- **ML Image Verification**: CNN-based automatic image validation
- **Admin Review**: Manual review for ML-rejected activities
- **Report Generation**: PDF/HTML reports with charts and analytics
- **Multi-language Support**: English and Marathi
- **Responsive Design**: Modern UI with TailwindCSS

## 🏗️ Architecture

- **Frontend**: React + Vite + TailwindCSS + React Router
- **Backend**: FastAPI + Python + MongoDB
- **ML**: TensorFlow/Keras CNN for image classification
- **Database**: MongoDB with Motor async driver
- **Deployment**: Docker + Docker Compose

## 📁 Project Structure

```
annual-report/
├── backend/           # FastAPI backend
├── frontend/          # React frontend
├── ml/               # ML models and inference
├── infra/            # Docker and deployment configs
├── docs/             # Documentation
├── sample_data/      # Sample data and images
└── .github/workflows/ # CI/CD pipeline
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.9+ (for local development)

### Using Docker (Recommended)

```bash
# Clone and navigate to project
git clone <repository-url>
cd annual-report

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development

**📖 For detailed setup instructions, see [SETUP.md](./SETUP.md)**

Quick start:
```bash
# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000

# Frontend (in a new terminal)
cd frontend
npm install
npm start
```

**Note:** Make sure MongoDB is running before starting the backend server.

## 🔧 Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=annual_report

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ML
ML_MODEL_PATH=./ml/models/model.h5
ML_THRESHOLD=0.6
```

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Activities
- `POST /api/activities` - Submit activity
- `GET /api/activities` - List activities
- `GET /api/activities/{id}` - Get activity details
- `PUT /api/activities/{id}` - Update activity

### Admin
- `GET /api/admin/rejected` - Get rejected activities
- `POST /api/admin/approve/{id}` - Approve activity
- `POST /api/admin/discard/{id}` - Discard activity

### Reports
- `GET /api/reports/individual/{id}` - Individual report
- `GET /api/reports/group` - Group report
- `GET /api/reports/individual/{id}/pdf` - Download PDF

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# All tests
docker-compose -f docker-compose.test.yml up --build
```

## 📈 ML Model Training

```bash
cd ml
jupyter notebook train.ipynb
```

## 🚀 Deployment

### Production Docker

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables

See `.env.example` for all required environment variables.

## 📝 Sample Data

The application includes sample data:
- Admin user: admin@example.com / password123
- Sample students and activities
- Test images for ML verification

## 🔒 Security Features

- JWT authentication
- Password hashing with bcrypt
- CORS configuration
- Input validation and sanitization
- Rate limiting
- File upload restrictions

## 📱 UI/UX Features

- Responsive design
- Dark/light mode
- Multi-language support
- Real-time notifications
- Interactive charts and analytics
- Professional report templates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For issues and questions:
- Check the documentation in `/docs`
- Review API documentation at `/docs` endpoint
- Create an issue in the repository

## 🎯 Milestones

- [x] MVP: Auth + Activity Submission + ML + Admin Review + PDF
- [x] Analytics & Charts + Report Templates
- [x] Tests, Docker, CI
- [x] ML Training Notebook
- [x] Documentation and Sample Data
