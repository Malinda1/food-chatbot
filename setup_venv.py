#!/usr/bin/env python3
"""
Virtual Environment Setup Script
This script creates a virtual environment and installs the required packages.
"""

import os
import sys
import subprocess
import venv
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr}")
        return None

def create_venv():
    """Create a virtual environment."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("Virtual environment already exists at 'venv'")
        return True
    
    print("Creating virtual environment...")
    try:
        venv.create("venv", with_pip=True)
        print("Virtual environment created successfully!")
        return True
    except Exception as e:
        print(f"Error creating virtual environment: {e}")
        return False

def install_requirements():
    """Install requirements from requirements.txt."""
    if not Path("requirements.txt").exists():
        print("requirements.txt not found!")
        return False
    
    # Determine the pip path based on OS
    if sys.platform == "win32":
        pip_path = "venv\\Scripts\\pip"
    else:
        pip_path = "venv/bin/pip"
    
    print("Installing requirements...")
    result = run_command(f"{pip_path} install -r requirements.txt")
    
    if result:
        print("Requirements installed successfully!")
        return True
    else:
        print("Failed to install requirements.")
        return False

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path(".env")
    env_template = Path("env_template.txt")
    
    if env_file.exists():
        print(".env file already exists")
        return True
    
    if env_template.exists():
        print("Creating .env file from template...")
        try:
            with open(env_template, 'r') as template:
                content = template.read()
            
            with open(env_file, 'w') as env:
                env.write(content)
            
            print(".env file created successfully!")
            print("Please update the .env file with your actual configuration values.")
            return True
        except Exception as e:
            print(f"Error creating .env file: {e}")
            return False
    else:
        print("env_template.txt not found. Creating basic .env file...")
        try:
            basic_env_content = """# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=food_chatbot
DB_USER=root
DB_PASSWORD=your_password_here

# FastAPI Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
APP_NAME=Food Chatbot
APP_VERSION=1.0.0
"""
            with open(env_file, 'w') as env:
                env.write(basic_env_content)
            
            print(".env file created successfully!")
            print("Please update the .env file with your actual configuration values.")
            return True
        except Exception as e:
            print(f"Error creating .env file: {e}")
            return False

def main():
    """Main function to set up the project."""
    print("=== Food Chatbot Project Setup ===")
    print()
    
    # Create virtual environment
    if not create_venv():
        print("Failed to create virtual environment. Exiting.")
        return
    
    # Install requirements
    if not install_requirements():
        print("Failed to install requirements. Exiting.")
        return
    
    # Create .env file
    create_env_file()
    
    print()
    print("=== Setup Complete! ===")
    print()
    print("To activate the virtual environment:")
    if sys.platform == "win32":
        print("  venv\\Scripts\\activate")
    else:
        print("  source venv/bin/activate")
    print()
    print("To run your FastAPI application:")
    print("  uvicorn main:app --reload")
    print()
    print("Don't forget to:")
    print("1. Update the .env file with your actual configuration")
    print("2. Create your main.py file with your FastAPI application")

if __name__ == "__main__":
    main() 