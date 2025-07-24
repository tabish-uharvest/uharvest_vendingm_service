#!/usr/bin/env python3
"""
Test script for machine admin endpoints
"""
import requests
import json
import uuid
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def test_machine_crud():
    """Test machine CRUD operations"""
    print("=" * 60)
    print("Testing Machine CRUD Operations")
    print("=" * 60)
    
    # 1. Create a new machine
    print("\n1. Creating a new machine...")
    create_data = {
        "location": f"Test Location {datetime.now().strftime('%H:%M:%S')}",
        "status": "active",
        "cups_qty": 100,
        "bowls_qty": 50
    }
    
    response = requests.post(f"{BASE_URL}/admin/machines", json=create_data)
    print(f"Create Response Status: {response.status_code}")
    print(f"Create Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code != 201:
        print("❌ Machine creation failed!")
        return None
    
    machine_data = response.json()
    machine_id = machine_data["id"]
    print(f"✅ Machine created successfully with ID: {machine_id}")
    
    # 2. List machines to verify it's in the database
    print("\n2. Listing all machines...")
    response = requests.get(f"{BASE_URL}/admin/machines")
    print(f"List Response Status: {response.status_code}")
    machines = response.json()
    print(f"Total machines: {len(machines)}")
    
    # Find our created machine
    created_machine = next((m for m in machines if m["id"] == machine_id), None)
    if created_machine:
        print(f"✅ Created machine found in database: {created_machine['location']}")
    else:
        print("❌ Created machine NOT found in database!")
        return None
    
    # 3. Update machine status
    print("\n3. Updating machine status...")
    status_update = {"status": "maintenance"}
    response = requests.put(f"{BASE_URL}/admin/machines/{machine_id}/status", json=status_update)
    print(f"Status Update Response Status: {response.status_code}")
    print(f"Status Update Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        updated_machine = response.json()
        if updated_machine["status"] == "maintenance":
            print("✅ Machine status updated successfully!")
        else:
            print(f"❌ Status not updated correctly. Expected 'maintenance', got '{updated_machine['status']}'")
    else:
        print("❌ Machine status update failed!")
    
    # 4. Update containers
    print("\n4. Updating container quantities...")
    container_update = {"cups_qty": 150, "bowls_qty": 75}
    response = requests.put(f"{BASE_URL}/admin/machines/{machine_id}/containers", json=container_update)
    print(f"Container Update Response Status: {response.status_code}")
    print(f"Container Update Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        updated_machine = response.json()
        if updated_machine["cups_qty"] == 150 and updated_machine["bowls_qty"] == 75:
            print("✅ Container quantities updated successfully!")
        else:
            print(f"❌ Containers not updated correctly.")
    else:
        print("❌ Container update failed!")
    
    # 5. Full machine update
    print("\n5. Updating machine details...")
    update_data = {
        "location": f"Updated Test Location {datetime.now().strftime('%H:%M:%S')}",
        "status": "active",
        "cups_qty": 200,
        "bowls_qty": 100
    }
    response = requests.put(f"{BASE_URL}/admin/machines/{machine_id}", json=update_data)
    print(f"Full Update Response Status: {response.status_code}")
    print(f"Full Update Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        updated_machine = response.json()
        if updated_machine["location"] == update_data["location"]:
            print("✅ Machine details updated successfully!")
        else:
            print(f"❌ Machine details not updated correctly.")
    else:
        print("❌ Machine update failed!")
    
    return machine_id

def test_machine_inventory(machine_id):
    """Test machine inventory endpoints"""
    print("\n" + "=" * 60)
    print("Testing Machine Inventory Operations")
    print("=" * 60)
    
    # Get machine inventory
    print(f"\nGetting inventory for machine {machine_id}...")
    response = requests.get(f"{BASE_URL}/machines/{machine_id}/inventory")
    print(f"Inventory Response Status: {response.status_code}")
    if response.status_code == 200:
        inventory = response.json()
        print(f"✅ Got inventory with {len(inventory.get('ingredients', []))} ingredients and {len(inventory.get('addons', []))} addons")
    else:
        print(f"❌ Failed to get inventory: {response.text}")

def cleanup_test_machine(machine_id):
    """Clean up test machine"""
    if machine_id:
        print(f"\n🧹 Cleaning up test machine {machine_id}...")
        response = requests.delete(f"{BASE_URL}/admin/machines/{machine_id}")
        if response.status_code == 200:
            print("✅ Test machine deleted successfully!")
        else:
            print(f"❌ Failed to delete test machine: {response.text}")

if __name__ == "__main__":
    try:
        machine_id = test_machine_crud()
        if machine_id:
            test_machine_inventory(machine_id)
            cleanup_test_machine(machine_id)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
