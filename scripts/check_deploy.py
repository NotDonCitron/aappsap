#!/usr/bin/env python3
"""Check if project is ready for Railway deployment."""
import os
import sys

def check_file_exists(path, required=True):
    exists = os.path.exists(path)
    status = "✅" if exists else ("❌" if required else "⚠️")
    req_text = "(required)" if required else "(optional)"
    print(f"{status} {path} {req_text}")
    return exists or not required

def main():
    print("=" * 50)
    print("Railway Deployment Readiness Check")
    print("=" * 50)
    
    all_good = True
    
    print("\n📁 Required Files:")
    all_good &= check_file_exists("requirements.txt")
    all_good &= check_file_exists("Procfile")
    all_good &= check_file_exists("wsgi.py")
    all_good &= check_file_exists("railway.toml")
    
    print("\n📁 Optional Files:")
    check_file_exists("runtime.txt", required=False)
    check_file_exists("nixpacks.toml", required=False)
    check_file_exists(".env.example", required=False)
    
    print("\n🔧 Configuration:")
    
    # Check requirements.txt has gunicorn
    if os.path.exists("requirements.txt"):
        with open("requirements.txt") as f:
            content = f.read()
            has_gunicorn = "gunicorn" in content
            has_psycopg2 = "psycopg2" in content
            print(f"{'✅' if has_gunicorn else '❌'} gunicorn in requirements.txt")
            print(f"{'✅' if has_psycopg2 else '❌'} psycopg2 in requirements.txt")
            all_good &= has_gunicorn
    
    # Check git status
    print("\n📦 Git Status:")
    git_dir = os.path.exists(".git")
    print(f"{'✅' if git_dir else '❌'} Git repository initialized")
    
    if git_dir:
        import subprocess
        try:
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True)
            uncommitted = result.stdout.strip()
            if uncommitted:
                print("⚠️  Uncommitted changes detected:")
                print(uncommitted[:500])
            else:
                print("✅ All changes committed")
        except Exception as e:
            print(f"⚠️  Could not check git status: {e}")
    
    print("\n" + "=" * 50)
    if all_good:
        print("✅ Ready for Railway deployment!")
        print("\nNext steps:")
        print("1. Push to GitHub: git push origin main")
        print("2. Go to https://railway.app")
        print("3. Create new project → Deploy from GitHub")
        print("4. Add PostgreSQL plugin")
        print("5. Set environment variables")
    else:
        print("❌ Fix issues above before deploying")
        sys.exit(1)
    print("=" * 50)

if __name__ == "__main__":
    main()
