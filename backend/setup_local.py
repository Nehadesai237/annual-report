#!/usr/bin/env python3
"""
Local setup script for Annual Report Portal Backend
This script helps set up and test the backend configuration
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)

def check_mongodb():
    """Check if MongoDB is installed and running"""
    print_header("Checking MongoDB")
    
    try:
        result = subprocess.run(['mongosh', '--version'], 
                              capture_output=True, 
                              text=True,
                              timeout=5)
        if result.returncode == 0:
            print("✅ MongoDB shell (mongosh) is installed")
            print(f"   {result.stdout.strip()}")
        else:
            print("⚠️  MongoDB shell not working properly")
            return False
    except FileNotFoundError:
        print("❌ MongoDB shell (mongosh) not found")
        print("   Install MongoDB from: https://www.mongodb.com/try/download/community")
        return False
    except Exception as e:
        print(f"⚠️  Could not check MongoDB: {e}")
        return False
    
    # Try to connect to MongoDB
    print("\n🔄 Testing MongoDB connection...")
    try:
        result = subprocess.run(['mongosh', '--eval', 'db.runCommand("ping")'],
                              capture_output=True,
                              text=True,
                              timeout=5)
        if "ok" in result.stdout or result.returncode == 0:
            print("✅ MongoDB is running")
            return True
        else:
            print("⚠️  MongoDB might not be running")
            print(f"   Error: {result.stderr}")
            print("\n   Try starting MongoDB:")
            print("   Windows: Check Windows Services for MongoDB")
            print("   Linux/Mac: sudo systemctl start mongod")
            return False
    except Exception as e:
        print(f"⚠️  Could not connect to MongoDB: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print_header("Creating Directories")
    
    directories = [
        'uploads',
        'reports',
        '__pycache__'
    ]
    
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Created/verified: {dir_name}/")

def setup_env_file():
    """Setup .env file if it doesn't exist"""
    print_header("Checking Environment Configuration")
    
    if os.path.exists('.env'):
        print("✅ .env file exists")
    else:
        print("⚠️  .env file not found")
        
        if os.path.exists('../env.example'):
            print("📋 Creating .env from env.example...")
            
            # Read the example file
            with open('../env.example', 'r') as f:
                content = f.read()
            
            # Write the new .env file
            with open('.env', 'w') as f:
                f.write(content)
            
            print("✅ Created .env file")
            print("⚠️  Please review and edit .env if needed")
        else:
            print("❌ env.example not found")
            print("   Creating basic .env file...")
            
            basic_env = """# Database Configuration
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
"""
            
            with open('.env', 'w') as f:
                f.write(basic_env)
            
            print("✅ Created basic .env file")

def install_dependencies():
    """Install Python dependencies"""
    print_header("Installing Python Dependencies")
    
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False
    
    print("🔄 Installing dependencies from requirements.txt...")
    
    try:
        # Check if we're in a virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        
        if not in_venv:
            print("⚠️  You're not in a virtual environment!")
            print("   It's recommended to use a virtual environment:")
            print("   python -m venv venv")
            print("   venv\\Scripts\\activate  (Windows)")
            print("   source venv/bin/activate  (Linux/Mac)")
        
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def test_connection():
    """Test MongoDB connection using test script"""
    print_header("Testing MongoDB Connection")
    
    if os.path.exists('test_mongodb.py'):
        try:
            result = subprocess.run([sys.executable, 'test_mongodb.py'],
                                  capture_output=True,
                                  text=True)
            print(result.stdout)
            if result.returncode == 0:
                return True
            else:
                print(result.stderr)
                return False
        except Exception as e:
            print(f"❌ Error running test: {e}")
            return False
    else:
        print("⚠️  test_mongodb.py not found")
        return False

def main():
    """Main setup function"""
    print_header("Annual Report Portal - Backend Setup")
    
    print("\nThis script will help you set up the backend locally.")
    print("Make sure you have:")
    print("  - MongoDB installed and running")
    print("  - Python 3.9+ installed")
    print("  - (Recommended) A virtual environment activated")
    
    input("\nPress Enter to continue...")
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    results = {
        'mongodb': False,
        'directories': False,
        'env_file': False,
        'dependencies': False,
        'connection': False
    }
    
    # Step 1: Check MongoDB
    results['mongodb'] = check_mongodb()
    
    # Step 2: Create directories
    try:
        create_directories()
        results['directories'] = True
    except Exception as e:
        print(f"❌ Error creating directories: {e}")
    
    # Step 3: Setup .env file
    try:
        setup_env_file()
        results['env_file'] = True
    except Exception as e:
        print(f"❌ Error setting up .env: {e}")
    
    # Step 4: Install dependencies
    response = input("\nInstall Python dependencies? (y/n): ")
    if response.lower() == 'y':
        results['dependencies'] = install_dependencies()
    else:
        print("⏭️  Skipping dependency installation")
    
    # Step 5: Test connection
    response = input("\nTest MongoDB connection? (y/n): ")
    if response.lower() == 'y':
        results['connection'] = test_connection()
    else:
        print("⏭️  Skipping connection test")
    
    # Summary
    print_header("Setup Summary")
    
    for check, status in results.items():
        status_symbol = "✅" if status else "❌"
        print(f"{status_symbol} {check.replace('_', ' ').title()}: {'PASS' if status else 'FAIL'}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 Setup completed successfully!")
        print("\nTo start the backend, run:")
        print("  python -m uvicorn app.main:app --reload")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)

