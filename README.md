# 🤖 AI File Management System - Advanced

An intelligent file management system powered by AI that automatically detects duplicates, analyzes content similarity, and helps optimize storage space. Built with modern web technologies and advanced machine learning algorithms.

## ✨ Features

### 🔍 **Smart Duplicate Detection**
- **Hash-based scanning**: Lightning-fast exact duplicate detection using SHA-256 hashing
- **Content-based analysis**: AI-powered similarity detection using advanced embeddings
- **Metadata comparison**: Compare file properties, creation dates, and EXIF data
- **Configurable similarity thresholds**: Adjust sensitivity from 50% to 100%

### 🎯 **Advanced File Analysis**
- **Multi-format support**: Images (PNG, JPG, GIF, WebP), PDFs, text files
- **Visual similarity**: Detect visually similar images even with different formats
- **Text content analysis**: Compare document contents using NLP techniques
- **Perceptual hashing**: Find near-duplicate images with slight modifications

### 🚀 **Modern Tech Stack**
- **Frontend**: Next.js 14 with TypeScript, Tailwind CSS, and Radix UI
- **Backend**: FastAPI with Python, async processing
- **ML/AI**: Sentence Transformers, CLIP models, PyTorch
- **Database**: PostgreSQL with Prisma ORM
- **Authentication**: NextAuth.js with secure session management

### 📊 **Smart Analytics**
- **Duplicate grouping**: Automatically organize similar files
- **Storage optimization**: Calculate potential space savings
- **Batch operations**: Select and download multiple files
- **Progress tracking**: Real-time upload and scanning progress

## 🛠️ Tech Stack

### Frontend (Next.js App)
```
📁 apps/web/
├── 🎨 Next.js 14 + TypeScript
├── 💅 Tailwind CSS + Radix UI
├── 🔐 NextAuth.js Authentication
├── 📦 Zustand State Management
└── 🔄 React Query for API calls
```

### Backend Services
```
📁 services/
├── 🔥 api/ (FastAPI)
│   ├── 🔐 JWT Authentication
│   ├── 📄 File Upload & Processing
│   ├── 🎯 Duplicate Detection Logic
│   └── 📊 Results Management
└── 🤖 ml-service/ (AI/ML)
    ├── 🧠 Sentence Transformers
    ├── 👁️ CLIP Vision Models  
    ├── 🔍 Similarity Algorithms
    └── ⚡ Async Processing
```

### Shared Packages
```
📁 packages/
├── 🎨 ui/ (React Components)
├── 🔧 core/ (Business Logic)
├── 💾 db/ (Database Schema)
└── 📝 types/ (TypeScript Definitions)
```

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and **pnpm** 8+
- **Python** 3.9+ with **pip**
- **PostgreSQL** database (local or cloud)

### 1️⃣ Clone Repository
```bash
git clone https://github.com/vibhorjoshi/AI-File-Management-System-Advanced.git
cd AI-File-Management-System-Advanced
```

### 2️⃣ Install Dependencies
```bash
# Install Node.js dependencies
pnpm install

# Install Python dependencies (API Service)
cd services/api
python -m venv api_env
source api_env/bin/activate  # Windows: api_env\\Scripts\\activate
pip install -r requirements.txt

# Install Python dependencies (ML Service)
cd ../ml-service
python -m venv ml_env
source ml_env/bin/activate  # Windows: ml_env\\Scripts\\activate
pip install -r requirements.txt
```

### 3️⃣ Environment Setup

Create environment files:

**Frontend** (`.env.local` in `apps/web/`):
```env
# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-super-secret-nextauth-key-32-chars-min

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_APP_ENV=development

# Database (Prisma Accelerate)
DATABASE_URL=prisma+postgres://accelerate.prisma-data.net/?api_key=your-api-key
```

**API Service** (`.env` in `services/api/`):
```env
# Database Configuration
DATABASE_URL=postgresql://user:pass@host:5432/dbname?sslmode=require

# Security
SESSION_SECRET=your-super-secret-session-key-32-chars-min
JWT_SECRET=your-jwt-secret-key-32-characters-min

# ML Service
ML_SERVICE_URL=http://localhost:3002
```

**ML Service** (`.env` in `services/ml-service/`):
```env
# Server Configuration
HOST=0.0.0.0
PORT=3002

# Model Configuration
TEXT_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
IMAGE_MODEL_NAME=openai/clip-vit-base-patch32
MODEL_CACHE_DIR=./models_cache

# Processing
MAX_BATCH_SIZE=32
DEVICE=cpu
```

### 4️⃣ Database Setup
```bash
# Generate Prisma client
pnpm run db:generate

# Push schema to database
pnpm run db:push

# (Optional) Seed with sample data
pnpm run db:seed
```

### 5️⃣ Start Development Servers

**Option A: Start All Services**
```bash
pnpm run dev
```

**Option B: Start Individual Services**
```bash
# Terminal 1: Frontend
pnpm run dev:web

# Terminal 2: API Service  
pnpm run dev:api

# Terminal 3: ML Service
pnpm run dev:ml
```

### 6️⃣ Access Application
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:3001/docs
- **ML Service**: http://localhost:3002/docs

## 📖 Usage Guide

### 1. **Upload Files**
- Navigate to `/upload` 
- Drag & drop or select files (Images, PDFs, Text)
- Configure scan options (hash, content, metadata)
- Set similarity threshold (50-100%)

### 2. **Configure Scanning**
- **Hash Scanning**: Fast exact duplicate detection
- **Content Scanning**: AI-powered similarity analysis  
- **Metadata Scanning**: Compare file properties
- **Similarity Threshold**: Adjust detection sensitivity

### 3. **Review Results**
- View grouped duplicates with similarity scores
- See potential storage savings
- Select files to keep or remove
- Download results as ZIP

### 4. **Manage Files**
- Batch select duplicates
- Preview file details
- Download selected files
- Start new scans

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js Web   │    │   FastAPI API   │    │   ML Service    │
│   Frontend      │◄──►│   Backend       │◄──►│   (AI/ML)       │
│                 │    │                 │    │                 │
│ • File Upload   │    │ • Authentication│    │ • Embeddings    │
│ • Progress UI   │    │ • File Process  │    │ • Similarity    │
│ • Results View  │    │ • Dedupe Logic  │    │ • ML Models     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   Database      │
                    │                 │
                    │ • User Data     │
                    │ • File Metadata │
                    │ • Scan Results  │
                    └─────────────────┘
```

## 🔧 Configuration

### Similarity Detection
- **Exact Match**: SHA-256 hash comparison
- **High Similarity**: 90-100% content match
- **Medium Similarity**: 75-89% content match
- **Custom Threshold**: User-configurable 50-100%

### File Limits
- **Max File Size**: 10MB per file
- **Max Total Upload**: 100MB
- **Max Files**: 100 files per upload
- **Supported Formats**: PNG, JPG, GIF, WebP, PDF, TXT

## 🚀 Deployment

### Frontend (Vercel)
```bash
# Build and deploy
pnpm run build:web
vercel --prod
```

### Backend (Railway/Render)
```bash
# API Service
cd services/api
pip install -r requirements.txt
python run.py

# ML Service
cd services/ml-service  
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Database (Neon/Supabase)
- Use PostgreSQL-compatible service
- Set `DATABASE_URL` environment variable
- Run migrations: `pnpm run db:push`

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`  
5. **Open Pull Request**

### Development Guidelines
- Follow TypeScript best practices
- Write tests for new features
- Update documentation
- Follow conventional commits

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Sentence Transformers** for text embeddings
- **OpenAI CLIP** for vision models
- **Next.js** team for the amazing framework
- **FastAPI** for the high-performance API framework
- **Prisma** for the excellent ORM

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/vibhorjoshi/AI-File-Management-System-Advanced/issues)
- **Discussions**: [GitHub Discussions](https://github.com/vibhorjoshi/AI-File-Management-System-Advanced/discussions)
- **Email**: [Contact](mailto:your-email@example.com)

---

**Made with ❤️ and AI** 🤖

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?logo=typescript&logoColor=white)](https://typescriptlang.org/)
[![Next.js](https://img.shields.io/badge/Next.js-000000?logo=next.js&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://python.org/)