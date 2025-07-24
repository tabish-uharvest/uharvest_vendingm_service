#!/usr/bin/env python3
"""
Quick test script using curl commands for machine endpoints
"""

import subprocess
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def run_curl(method, url, data=None, headers=None):
    """Run a curl command and return the response"""
    cmd = ["curl", "-s", "-X", method, url]
    
    if headers:
        for header in headers:
            cmd.extend(["-H", header])
    
    if data:
        cmd.extend(["-H", "Content-Type: application/json"])
        cmd.extend(["-d", json.dumps(data)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)

def test_machine_endpoints():
    """Test machine admin endpoints"""
    print("Testing Machine Admin Endpoints")
    print("=" * 50)
    
    # 1. Test machine creation
    print("\n1. Creating a machine...")
    machine_data = {
        "location": "Test Machine Location",
        "status": "active",
        "cups_qty": 100,
        "bowls_qty": 50
    }
    
    code, response, error = run_curl("POST", f"{BASE_URL}/admin/machines", machine_data)
    print(f"Status Code: {code}")
    print(f"Response: {response}")
    if error:
        print(f"Error: {error}")
    
    if code == 0:
        try:
            machine_response = json.loads(response)
            machine_id = machine_response.get("id")
            print(f"✅ Machine created with ID: {machine_id}")
            
            # 2. Test machine status update
            print(f"\n2. Updating machine status...")
            status_data = {"status": "maintenance"}
            code, response, error = run_curl("PUT", f"{BASE_URL}/admin/machines/{machine_id}/status", status_data)
            print(f"Status Update - Code: {code}, Response: {response}")
            
            # 3. Test container update
            print(f"\n3. Updating containers...")
            container_data = {"cups_qty": 150, "bowls_qty": 75}
            code, response, error = run_curl("PUT", f"{BASE_URL}/admin/machines/{machine_id}/containers", container_data)
            print(f"Container Update - Code: {code}, Response: {response}")
            
            # 4. Test admin inventory
            print(f"\n4. Getting admin inventory...")
            code, response, error = run_curl("GET", f"{BASE_URL}/admin/machines/{machine_id}/inventory?include_out_of_stock=true")
            print(f"Admin Inventory - Code: {code}")
            if response:
                try:
                    inventory = json.loads(response)
                    print(f"Inventory Location: {inventory.get('machine_location')}")
                    print(f"Ingredients: {len(inventory.get('ingredients', []))}")
                    print(f"Addons: {len(inventory.get('addons', []))}")
                except json.JSONDecodeError:
                    print(f"Response: {response}")
            
            # 5. Test machine list
            print(f"\n5. Listing machines...")
            code, response, error = run_curl("GET", f"{BASE_URL}/admin/machines")
            print(f"Machine List - Code: {code}")
            if response:
                try:
                    machines = json.loads(response)
                    print(f"Total machines: {len(machines)}")
                except json.JSONDecodeError:
                    print(f"Response: {response}")
            
            # 6. Clean up - delete the test machine
            print(f"\n6. Cleaning up test machine...")
            code, response, error = run_curl("DELETE", f"{BASE_URL}/admin/machines/{machine_id}")
            print(f"Delete - Code: {code}, Response: {response}")
            
        except json.JSONDecodeError:
            print(f"❌ Failed to parse machine creation response: {response}")
    else:
        print(f"❌ Failed to create machine")

if __name__ == "__main__":
    test_machine_endpoints()
