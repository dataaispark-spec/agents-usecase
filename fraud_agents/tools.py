"""
Tools for Fraud Detection Agents
MCP-Native Architecture Ready
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Any, List


def get_customer_profile(customer_id: str) -> Dict[str, Any]:
    """
    MCP Tool: Retrieve customer profile from core banking system.
    In production, this connects to an MCP server endpoint.
    """
    # Simulated customer profiles
    profiles = {
        "CUST001": {
            "name": "John Smith",
            "risk_score": 25,
            "account_age_days": 1200,
            "avg_transaction_amount": 150.00,
            "home_city": "London",
            "home_country": "UK"
        },
        "CUST002": {
            "name": "Sarah Johnson",
            "risk_score": 45,
            "account_age_days": 365,
            "avg_transaction_amount": 500.00,
            "home_city": "New York",
            "home_country": "USA"
        },
        "CUST003": {
            "name": "Michael Chen",
            "risk_score": 15,
            "account_age_days": 2000,
            "avg_transaction_amount": 200.00,
            "home_city": "Singapore",
            "home_country": "Singapore"
        }
    }
    return profiles.get(customer_id, {"name": "Unknown", "risk_score": 50})


def geo_velocity_check(customer_id: str, current_location: str, last_transaction_time: datetime) -> Dict[str, Any]:
    """
    MCP Tool: Calculate geo-velocity to detect impossible travel.
    Returns risk score based on physical impossibility of travel.
    """
    # Simulated location data
    locations = {
        "London": {"lat": 51.5074, "lon": -0.1278, "country": "UK"},
        "Singapore": {"lat": 1.3521, "lon": 103.8198, "country": "Singapore"},
        "New York": {"lat": 40.7128, "lon": -74.0060, "country": "USA"},
        "Tokyo": {"lat": 35.6762, "lon": 139.6503, "country": "Japan"}
    }
    
    customer_profiles = {
        "CUST001": {"last_location": "London", "last_time": datetime.now() - timedelta(minutes=20)},
        "CUST002": {"last_location": "New York", "last_time": datetime.now() - timedelta(hours=2)},
        "CUST003": {"last_location": "Singapore", "last_time": datetime.now() - timedelta(days=1)}
    }
    
    cust_data = customer_profiles.get(customer_id, {})
    last_location = cust_data.get("last_location", "Unknown")
    last_time = cust_data.get("last_time", datetime.now())
    
    time_diff_minutes = (datetime.now() - last_time).total_seconds() / 60
    
    # Impossible travel detection
    if last_location != current_location and time_diff_minutes < 60:
        distance_km = random.uniform(5000, 10000)  # Simulated long distance
        required_speed = distance_km / (time_diff_minutes / 60) if time_diff_minutes > 0 else float('inf')
        
        return {
            "impossible_travel_detected": True,
            "last_location": last_location,
            "current_location": current_location,
            "time_diff_minutes": round(time_diff_minutes, 2),
            "estimated_distance_km": round(distance_km, 2),
            "required_speed_kmh": round(required_speed, 2),
            "risk_contribution": 12
        }
    
    return {
        "impossible_travel_detected": False,
        "last_location": last_location,
        "current_location": current_location,
        "time_diff_minutes": round(time_diff_minutes, 2),
        "risk_contribution": 0
    }


def get_device_history(customer_id: str) -> Dict[str, Any]:
    """
    MCP Tool: Check device fingerprint and history.
    """
    devices = {
        "CUST001": {
            "device_id": "DEV12345",
            "is_known_device": True,
            "device_age_days": 400,
            "os": "iOS",
            "browser": "Safari",
            "risk_contribution": 0
        },
        "CUST002": {
            "device_id": "DEV99999",
            "is_known_device": False,
            "device_age_days": 0,
            "os": "Android",
            "browser": "Chrome",
            "risk_contribution": 5
        },
        "CUST003": {
            "device_id": "DEV67890",
            "is_known_device": True,
            "device_age_days": 800,
            "os": "Windows",
            "browser": "Edge",
            "risk_contribution": 0
        }
    }
    return devices.get(customer_id, {"is_known_device": False, "risk_contribution": 5})


def check_merchant_risk(merchant_id: str, mcc_code: str) -> Dict[str, Any]:
    """
    MCP Tool: Assess merchant category code (MCC) risk.
    """
    mcc_risks = {
        "5411": {"category": "Grocery Stores", "risk_level": "low", "risk_contribution": 0},
        "5812": {"category": "Restaurants", "risk_level": "low", "risk_contribution": 0},
        "7995": {"category": "Gambling", "risk_level": "high", "risk_contribution": 8},
        "5944": {"category": "Jewelry Stores", "risk_level": "medium", "risk_contribution": 4},
        "4829": {"category": "Wire Transfers", "risk_level": "high", "risk_contribution": 6}
    }
    
    merchant_info = mcc_risks.get(mcc_code, {"category": "Unknown", "risk_level": "medium", "risk_contribution": 3})
    merchant_info["merchant_id"] = merchant_id
    return merchant_info


def get_transaction_history(customer_id: str, days: int = 30) -> Dict[str, Any]:
    """
    MCP Tool: Retrieve recent transaction patterns.
    """
    histories = {
        "CUST001": {
            "transaction_count": 45,
            "avg_amount": 145.50,
            "max_amount": 890.00,
            "foreign_transactions": 2,
            "night_transactions": 3,
            "risk_contribution": 2
        },
        "CUST002": {
            "transaction_count": 120,
            "avg_amount": 520.00,
            "max_amount": 2500.00,
            "foreign_transactions": 15,
            "night_transactions": 25,
            "risk_contribution": 6
        },
        "CUST003": {
            "transaction_count": 30,
            "avg_amount": 180.00,
            "max_amount": 500.00,
            "foreign_transactions": 0,
            "night_transactions": 1,
            "risk_contribution": 0
        }
    }
    return histories.get(customer_id, {"transaction_count": 0, "risk_contribution": 5})


def check_sanctions_list(name: str, country: str) -> Dict[str, Any]:
    """
    MCP Tool: Screen against OFAC/UN sanctions lists.
    In production, this connects to compliance databases.
    """
    # Simulated sanctions screening
    sanctioned_names = ["Test Sanctioned Entity", "Blocked User"]
    
    is_sanctioned = name in sanctioned_names
    
    return {
        "sanctions_match": is_sanctioned,
        "lists_checked": ["OFAC", "UN", "EU"],
        "risk_contribution": 20 if is_sanctioned else 0
    }


def calculate_behavioral_anomaly(transaction_amount: float, customer_id: str) -> Dict[str, Any]:
    """
    MCP Tool: Detect anomalies in transaction behavior.
    """
    profiles = {
        "CUST001": {"avg_amount": 150.00, "std_dev": 50.00},
        "CUST002": {"avg_amount": 500.00, "std_dev": 200.00},
        "CUST003": {"avg_amount": 200.00, "std_dev": 75.00}
    }
    
    cust_profile = profiles.get(customer_id, {"avg_amount": 200.00, "std_dev": 100.00})
    avg = cust_profile["avg_amount"]
    std = cust_profile["std_dev"]
    
    z_score = abs(transaction_amount - avg) / std if std > 0 else 0
    
    anomaly_detected = z_score > 3
    risk_contribution = min(int(z_score * 2), 10) if anomaly_detected else 0
    
    return {
        "anomaly_detected": anomaly_detected,
        "z_score": round(z_score, 2),
        "expected_range": f"${avg - 2*std:.2f} - ${avg + 2*std:.2f}",
        "actual_amount": transaction_amount,
        "risk_contribution": risk_contribution
    }
