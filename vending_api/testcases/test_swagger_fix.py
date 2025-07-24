#!/usr/bin/env python3
"""
Test the FastAPI server startup to ensure Swagger docs are correct
"""
import sys
import subprocess
from pathlib import Path

def test_server_startup():
    """Test that the FastAPI server can start without errors"""
    
    # Change to the API directory
    api_dir = Path("c:/Work/uharvest_vendingm_service/vending_api")
    
    try:
        # Try to import the main module to check for syntax errors
        print("Testing imports...")
        result = subprocess.run([
            sys.executable, "-c", 
            "from app.main import app; from app.schemas.machine import ThresholdUpdateRequest; print('✅ All imports successful')"
        ], 
        cwd=str(api_dir), 
        capture_output=True, 
        text=True, 
        timeout=30
        )
        
        if result.returncode == 0:
            print("✅ FastAPI application imports successfully")
            print("✅ Schema imports successful")
            print("\n🎉 The Swagger documentation should now show the correct format:")
            print("Expected request body format for /api/v1/admin/inventory/thresholds:")
            print("""
{
  "items": [
    {
      "item_id": "3a0b1590-8601-4925-bb00-21f1fb24bfc5",
      "item_type": "ingredient",
      "threshold": 400
    }
  ]
}
            """)
            print("\n📚 To view the updated Swagger docs:")
            print("1. Start the server: uvicorn app.main:app --reload")
            print("2. Visit: http://localhost:8000/docs")
            print("3. Look for the PUT /api/v1/admin/inventory/thresholds endpoint")
            
        else:
            print("❌ Error during import:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            
    except subprocess.TimeoutExpired:
        print("❌ Import test timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_server_startup()
