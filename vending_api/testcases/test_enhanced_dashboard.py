#!/usr/bin/env python3
"""
Comprehensive test script for the enhanced dashboard functionality
"""
import requests
import json
from datetime import datetime, date

BASE_URL = "http://localhost:8000/api/v1/admin"

def test_enhanced_dashboard():
    """Test the enhanced dashboard endpoint"""
    print("🚀 Testing Enhanced Dashboard Functionality...")
    
    try:
        response = requests.get(f"{BASE_URL}/dashboard")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n📊 Enhanced Dashboard Analysis:")
            
            # Test metrics
            metrics = data.get('metrics', {})
            print(f"  💰 Total Revenue Today: ${metrics.get('total_revenue_today', 0)}")
            print(f"  📦 Total Orders Today: {metrics.get('total_orders_today', 0)}")
            print(f"  🏪 Active Machines: {metrics.get('active_machines', 0)}")
            print(f"  📈 Avg Order Value: ${metrics.get('avg_order_value', 0)}")
            print(f"  ✅ Completion Rate: {metrics.get('completion_rate', 0)}%")
            print(f"  ⚠️  Low Stock Alerts: {metrics.get('low_stock_alerts', 0)}")
            print(f"  🚫 Out of Stock Alerts: {metrics.get('out_of_stock_alerts', 0)}")
            
            # Test enhanced top selling items
            print("\n🏆 Enhanced Top Selling Items:")
            for item in data.get('top_selling_items', []):
                print(f"  {item.get('emoji', '📦')} {item['name']}")
                print(f"    Sales: {item['sales']} | Revenue: ${item['revenue']:.2f}")
                if 'avg_grams_per_order' in item:
                    print(f"    Avg per order: {item['avg_grams_per_order']}g | Total consumed: {item.get('total_grams_consumed', 0)}g")
                if 'growth_trend' in item:
                    trend_emoji = {"up": "📈", "down": "📉", "stable": "➡️"}.get(item['growth_trend'], "➡️")
                    print(f"    Trend: {trend_emoji} {item['growth_trend']}")
                print()
            
            # Test enhanced recent orders
            print("🕒 Enhanced Recent Orders:")
            for order in data.get('recent_orders', [])[:3]:  # Show top 3
                print(f"  Order {order['id'][:8]}...")
                print(f"    Location: {order.get('machine_location', 'Unknown')}")
                print(f"    Price: ${order['total_price']} | Calories: {order.get('total_calories', 0)}")
                print(f"    Items: {order.get('items_count', 0)} | Addons: {order.get('addons_count', 0)}")
                print(f"    Status: {order['status']} | Time: {order['created_at']}")
                print()
            
            # Test enhanced alerts
            print("🚨 System Alerts:")
            alerts = data.get('alerts', [])
            if alerts:
                for alert in alerts[:5]:  # Show top 5 alerts
                    alert_emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(alert.get('type'), "🔵")
                    print(f"  {alert_emoji} {alert.get('message', 'No message')}")
                    if alert.get('machine_location'):
                        print(f"    Location: {alert['machine_location']}")
                    print(f"    Severity: {alert.get('severity', 'unknown')} | Time: {alert.get('timestamp', 'unknown')}")
                    print()
            else:
                print("  ✅ No alerts - system running smoothly!")
            
            # Test machine summaries
            print("🏪 Machine Summaries:")
            machines = data.get('machines', [])
            for machine in machines[:3]:  # Show top 3 machines
                status_emoji = {"active": "🟢", "maintenance": "🟡", "inactive": "🔴"}.get(machine.get('status'), "⚪")
                print(f"  {status_emoji} {machine.get('location', 'Unknown Location')}")
                print(f"    Orders today: {machine.get('orders_today', 0)} | Revenue: ${machine.get('revenue_today', 0)}")
                print(f"    Low stock items: {machine.get('low_stock_items', 0)}")
                if machine.get('last_order_time'):
                    print(f"    Last order: {machine['last_order_time']}")
                print()
            
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

def test_alerts_endpoint():
    """Test the alerts summary endpoint"""
    print("\n🚨 Testing Alerts Summary Endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/alerts")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("📊 Alerts Summary:")
            print(f"  🔴 Critical: {data.get('critical_alerts', 0)}")
            print(f"  🟡 Warning: {data.get('warning_alerts', 0)}")
            print(f"  🔵 Info: {data.get('info_alerts', 0)}")
            print(f"  📊 Total: {data.get('total_alerts', 0)}")
            
            latest = data.get('latest_alerts', [])
            if latest:
                print("\n🕒 Latest Alerts:")
                for alert in latest[:3]:
                    alert_emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(alert.get('type'), "🔵")
                    print(f"  {alert_emoji} {alert.get('message', 'No message')}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_realtime_analytics():
    """Test the real-time analytics endpoint"""
    print("\n⚡ Testing Real-time Analytics Endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/analytics/realtime")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("📊 Real-time Metrics:")
            print(f"  🔄 Active Orders: {data.get('active_orders', 0)}")
            print(f"  🟢 Machines Online: {data.get('machines_online', 0)}")
            print(f"  💰 Revenue Today: ${data.get('current_revenue_today', 0)}")
            print(f"  📈 Orders/Hour: {data.get('orders_per_hour', 0)}")
            print(f"  ⚡ Avg Response Time: {data.get('avg_response_time', 0)}s")
            print(f"  💚 System Health: {data.get('system_health', 'unknown')}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Run all enhanced dashboard tests"""
    print("=" * 60)
    print("🧪 ENHANCED DASHBOARD FUNCTIONALITY TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_enhanced_dashboard,
        test_alerts_endpoint,
        test_realtime_analytics
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ PASSED\n")
            else:
                print("❌ FAILED\n")
        except Exception as e:
            print(f"❌ FAILED with exception: {e}\n")
    
    print("=" * 60)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    if passed == total:
        print("🎉 All tests passed! Enhanced dashboard is working perfectly!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    print("=" * 60)

if __name__ == "__main__":
    main()
