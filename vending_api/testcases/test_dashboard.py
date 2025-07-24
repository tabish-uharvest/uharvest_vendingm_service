#!/usr/bin/env python3
"""Test script to check the dashboard endpoint with real top selling items"""
import requests
import json

def test_dashboard():
    """Test the dashboard endpoint"""
    print("🧪 Testing Dashboard Endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/api/v1/admin/dashboard")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n📊 Dashboard Data:")
            print(f"Total Revenue: ${data.get('total_revenue', 0)}")
            print(f"Total Orders: {data.get('total_orders', 0)}")
            print(f"Active Machines: {data.get('active_machines', 0)}")
            
            print("\n🏆 Top Selling Items:")
            for item in data.get('top_selling_items', []):
                print(f"  - {item['name']}: {item['sales']} sales, ${item['revenue']:.2f} revenue")
                
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    test_dashboard()
