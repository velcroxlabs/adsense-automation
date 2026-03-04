#!/usr/bin/env python3
"""
Check if system is ready for deployment.
Run this before deploying to ensure everything works.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_website_build():
    """Check if website builds successfully."""
    print("🔍 Checking website build...")
    success, stdout, stderr = run_command("npm run build", cwd="website")
    if success:
        print("   ✅ Website builds successfully")
        # Check build output
        if os.path.exists("website/dist/index.html"):
            print("   ✅ Build output exists (website/dist/)")
            return True
        else:
            print("   ❌ Build output missing")
            return False
    else:
        print(f"   ❌ Build failed: {stderr[:100]}")
        return False

def check_database():
    """Check database connection."""
    print("🔍 Checking database connection...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not key:
            print("   ❌ Missing Supabase credentials in .env")
            return False
        
        # Check if we can import supabase
        try:
            import supabase
            print("   ✅ Supabase client available")
        except ImportError:
            print("   ❌ Supabase not installed")
            print("   Run: pip install supabase python-dotenv")
            return False
            
        print(f"   ✅ Credentials found: {url[:20]}...")
        return True
    except Exception as e:
        print(f"   ❌ Error checking database: {e}")
        return False

def check_git_status():
    """Check git repository status."""
    print("🔍 Checking git status...")
    
    # Check if we're in a git repo
    success, stdout, stderr = run_command("git status")
    if not success:
        print("   ❌ Not in a git repository or git not installed")
        return False
    
    # Check for uncommitted changes
    success, stdout, stderr = run_command("git diff --quiet")
    if not success:
        print("   ⚠️  There are uncommitted changes")
        # Check what files are changed
        success, stdout, stderr = run_command("git status --short")
        if success and stdout:
            print(f"   Files changed:\n{stdout[:200]}")
    else:
        print("   ✅ No uncommitted changes")
    
    # Check remote
    success, stdout, stderr = run_command("git remote -v")
    if success and stdout:
        print("   ✅ Git remote configured")
        print(f"   Remotes:\n{stdout}")
    else:
        print("   ⚠️  No git remotes configured")
        print("   You'll need to add a remote for GitHub")
    
    return True

def check_python_deps():
    """Check Python dependencies."""
    print("🔍 Checking Python dependencies...")
    
    deps = ["dotenv", "supabase", "pandas"]
    missing = []
    
    for dep in deps:
        try:
            if dep == "dotenv":
                import dotenv
            elif dep == "supabase":
                import supabase
            elif dep == "pandas":
                import pandas
            print(f"   ✅ {dep} installed")
        except ImportError:
            print(f"   ❌ {dep} missing")
            missing.append(dep)
    
    if missing:
        print(f"   Install missing: pip install {' '.join(missing)}")
        return False
    
    return True

def main():
    """Run all checks."""
    print("="*60)
    print("🚀 DEPLOYMENT READINESS CHECK")
    print("="*60)
    
    checks = []
    
    # Change to project directory
    project_dir = Path(__file__).parent.parent
    os.chdir(project_dir)
    print(f"📁 Working in: {os.getcwd()}")
    
    # Run checks
    checks.append(("Website build", check_website_build()))
    checks.append(("Python dependencies", check_python_deps()))
    checks.append(("Database connection", check_database()))
    checks.append(("Git status", check_git_status()))
    
    print("\n" + "="*60)
    print("📊 CHECK RESULTS")
    print("="*60)
    
    passed = 0
    total = len(checks)
    
    for name, success in checks:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Score: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🚀 **READY FOR DEPLOYMENT!**")
        print("\nNext steps:")
        print("1. Create GitHub repo: https://github.com/new")
        print("2. Push code: git add . && git commit -m 'Deploy ready' && git push")
        print("3. Deploy on Vercel: https://vercel.com/new")
    else:
        print(f"\n⚠️  **NOT READY** - Fix {total - passed} issue(s) above")
    
    return passed == total

if __name__ == "__main__":
    try:
        ready = main()
        sys.exit(0 if ready else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Check interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)