#!/usr/bin/env python3
"""
Comprehensive test script for Urban Harvest Vending Machine API
Tests all major endpoints and database schema alignment
"""
import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, Any, List


class VendingAPITester:
    """Test suite for the vending machine API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)
        self.test_results = []
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Urban Harvest Vending Machine API Tests")
        print("=" * 60)
        
        try:
            await self.test_health_check()
            await self.test_machine_endpoints()
            await self.test_product_endpoints()
            await self.test_order_flow()
            await self.test_admin_endpoints()
            await self.test_dashboard_endpoints()
            
            # Print summary
            self.print_test_summary()
            
        except Exception as e:
            print(f"❌ Test suite failed with error: {e}")
        finally:
            await self.client.aclose()
    
    async def test_health_check(self):
        """Test health check endpoint"""
        print("\n🏥 Testing Health Check...")
        
        try:
            response = await self.client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            self.log_success("Health check")
        except Exception as e:
            self.log_failure("Health check", str(e))
    
    async def test_machine_endpoints(self):
        """Test machine-related endpoints"""
        print("\n🏭 Testing Machine Endpoints...")
        
        # Test get machines
        try:
            response = await self.client.get("/api/v1/admin/machines")
            if response.status_code == 200:
                machines = response.json()
                if machines:
                    machine_id = machines[0]["id"]
                    await self.test_machine_inventory(machine_id)
                    await self.test_machine_metrics(machine_id)
                self.log_success("Get machines")
            else:
                self.log_failure("Get machines", f"Status: {response.status_code}")
        except Exception as e:
            self.log_failure("Get machines", str(e))
    
    async def test_machine_inventory(self, machine_id: str):
        """Test machine inventory endpoint"""
        try:
            response = await self.client.get(f"/api/v1/machines/{machine_id}/inventory")
            if response.status_code == 200:
                inventory = response.json()
                assert "ingredients" in inventory
                assert "addons" in inventory
                self.log_success("Machine inventory")
            else:
                self.log_failure("Machine inventory", f"Status: {response.status_code}")
        except Exception as e:
            self.log_failure("Machine inventory", str(e))
    
    async def test_machine_metrics(self, machine_id: str):
        """Test machine metrics endpoint"""
        try:
            response = await self.client.get(f"/api/v1/admin/machines/{machine_id}/metrics")
            if response.status_code == 200:
                metrics = response.json()
                self.log_success("Machine metrics")
            else:
                self.log_failure("Machine metrics", f"Status: {response.status_code}")
        except Exception as e:
            self.log_failure("Machine metrics", str(e))
    
    async def test_product_endpoints(self):
        """Test product-related endpoints"""
        print("\n🥗 Testing Product Endpoints...")
        
        endpoints = [
            "/api/v1/ingredients",
            "/api/v1/addons", 
            "/api/v1/presets"
        ]
        
        for endpoint in endpoints:
            try:
                response = await self.client.get(endpoint)
                if response.status_code == 200:
                    self.log_success(f"GET {endpoint}")
                else:
                    self.log_failure(f"GET {endpoint}", f"Status: {response.status_code}")
            except Exception as e:
                self.log_failure(f"GET {endpoint}", str(e))
    
    async def test_order_flow(self):
        """Test order creation flow"""
        print("\n📦 Testing Order Flow...")
        
        # First, get a machine and its inventory
        try:
            machines_response = await self.client.get("/api/v1/admin/machines")
            if machines_response.status_code != 200:
                self.log_failure("Order flow", "Cannot get machines")
                return
            
            machines = machines_response.json()
            if not machines:
                self.log_failure("Order flow", "No machines available")
                return
            
            machine_id = machines[0]["id"]
            
            # Get inventory
            inventory_response = await self.client.get(f"/api/v1/machines/{machine_id}/inventory")
            if inventory_response.status_code != 200:
                self.log_failure("Order flow", "Cannot get inventory")
                return
            
            inventory = inventory_response.json()
            ingredients = inventory.get("ingredients", [])
            addons = inventory.get("addons", [])
            
            if not ingredients:
                self.log_failure("Order flow", "No ingredients available")
                return
            
            # Create a test order
            order_data = {
                "machine_id": machine_id,
                "ingredients": [
                    {
                        "ingredient_id": ingredients[0]["id"],
                        "grams_used": 100
                    }
                ],
                "addons": [],
                "payment_method": "card",
                "notes": "Test order"
            }
            
            response = await self.client.post("/api/v1/orders", json=order_data)
            if response.status_code == 201:
                order = response.json()
                assert "id" in order
                assert "status" in order
                self.log_success("Create order")
                
                # Test get order
                order_id = order["id"]
                get_response = await self.client.get(f"/api/v1/admin/orders/{order_id}")
                if get_response.status_code == 200:
                    self.log_success("Get order")
                else:
                    self.log_failure("Get order", f"Status: {get_response.status_code}")
                
            else:
                self.log_failure("Create order", f"Status: {response.status_code}, Body: {response.text}")
                
        except Exception as e:
            self.log_failure("Order flow", str(e))
    
    async def test_admin_endpoints(self):
        """Test admin endpoints"""
        print("\n👨‍💼 Testing Admin Endpoints...")
        
        endpoints = [
            "/api/v1/admin/orders",
            "/api/v1/admin/ingredients",
            "/api/v1/admin/addons",
            "/api/v1/admin/presets"
        ]
        
        for endpoint in endpoints:
            try:
                response = await self.client.get(endpoint)
                if response.status_code == 200:
                    self.log_success(f"GET {endpoint}")
                else:
                    self.log_failure(f"GET {endpoint}", f"Status: {response.status_code}")
            except Exception as e:
                self.log_failure(f"GET {endpoint}", str(e))
    
    async def test_dashboard_endpoints(self):
        """Test dashboard endpoints"""
        print("\n📊 Testing Dashboard Endpoints...")
        
        endpoints = [
            "/api/v1/admin/dashboard",
            "/api/v1/admin/reports/sales?start_date=2024-01-01&end_date=2024-12-31",
            "/api/v1/admin/reports/inventory"
        ]
        
        for endpoint in endpoints:
            try:
                response = await self.client.get(endpoint)
                if response.status_code == 200:
                    self.log_success(f"GET {endpoint}")
                else:
                    self.log_failure(f"GET {endpoint}", f"Status: {response.status_code}")
            except Exception as e:
                self.log_failure(f"GET {endpoint}", str(e))
    
    def log_success(self, test_name: str):
        """Log a successful test"""
        print(f"  ✅ {test_name}")
        self.test_results.append({"test": test_name, "status": "PASS"})
    
    def log_failure(self, test_name: str, error: str):
        """Log a failed test"""
        print(f"  ❌ {test_name}: {error}")
        self.test_results.append({"test": test_name, "status": "FAIL", "error": error})
    
    def print_test_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "0.0%")
        
        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test']}: {result.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 60)


async def main():
    """Run the test suite"""
    tester = VendingAPITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
