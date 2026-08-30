"""
Clerivon MCP Server for Fraud Detection Tools.
Exposes fraud detection capabilities as standard MCP resources/tools.
"""
import asyncio
import logging
from typing import Any
from mcp.server.fastmcp import FastMCP

# Initialize MCP Server
mcp = FastMCP("clerivon-fraud-tools")

# Singleton server instance for testing
server = mcp

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("clerivon-mcp")

# --- Mock Data Services (Replace with real DB connections in Prod) ---
def get_customer_profile_mock(customer_id: str) -> dict:
    return {
        "customer_id": customer_id,
        "risk_tier": "Gold",
        "home_location": {"lat": 51.5074, "lon": -0.1278, "city": "London"},
        "account_age_days": 1200,
        "avg_transaction_value": 150.00
    }

def get_device_history_mock(device_id: str) -> dict:
    return {
        "device_id": device_id,
        "is_known_device": True,
        "last_seen_location": {"lat": 51.5074, "lon": -0.1278},
        "fraud_flags": 0
    }

def calculate_geo_velocity_mock(loc1: dict, loc2: dict, time_diff_minutes: float) -> dict:
    # Simple Haversine approximation for demo
    lat1, lon1 = loc1.get('lat', 0), loc1.get('lon', 0)
    lat2, lon2 = loc2.get('lat', 0), loc2.get('lon', 0)
    
    # Rough distance calc (not precise haversine, just for demo logic)
    distance_km = ((lat2 - lat1)**2 + (lon2 - lon1)**2)**0.5 * 111
    speed_kmh = (distance_km / time_diff_minutes) * 60 if time_diff_minutes > 0 else 0
    
    is_impossible = speed_kmh > 800  # Jet speed threshold
    
    return {
        "distance_km": round(distance_km, 2),
        "time_minutes": time_diff_minutes,
        "estimated_speed_kmh": round(speed_kmh, 2),
        "is_impossible_travel": is_impossible
    }

def check_merchant_risk_mock(mcc_code: str) -> dict:
    high_risk_mccs = ["7995", "6012", "5967"]
    return {
        "mcc_code": mcc_code,
        "risk_score": 85 if mcc_code in high_risk_mccs else 15,
        "category": "Gambling" if mcc_code == "7995" else "Retail"
    }

# --- MCP Tools Definition ---

@mcp.tool()
async def get_customer_profile(customer_id: str) -> dict:
    """Retrieves customer risk profile and home location."""
    logger.info(f"MCP Call: get_customer_profile for {customer_id}")
    return get_customer_profile_mock(customer_id)

@mcp.tool()
async def get_device_history(device_id: str) -> dict:
    """Checks device reputation and history."""
    logger.info(f"MCP Call: get_device_history for {device_id}")
    return get_device_history_mock(device_id)

@mcp.tool()
async def calculate_geo_velocity(
    prev_lat: float, prev_lon: float, 
    curr_lat: float, curr_lon: float, 
    time_diff_minutes: float
) -> dict:
    """Calculates velocity between two points to detect impossible travel."""
    logger.info(f"MCP Call: calculate_geo_velocity")
    loc1 = {"lat": prev_lat, "lon": prev_lon}
    loc2 = {"lat": curr_lat, "lon": curr_lon}
    return calculate_geo_velocity_mock(loc1, loc2, time_diff_minutes)

@mcp.tool()
async def check_merchant_risk(mcc_code: str) -> dict:
    """Evaluates merchant category code risk."""
    logger.info(f"MCP Call: check_merchant_risk for {mcc_code}")
    return check_merchant_risk_mock(mcc_code)

@mcp.tool()
async def get_recent_transactions(customer_id: str, limit: int = 5) -> list:
    """Fetches recent transaction history for pattern analysis."""
    logger.info(f"MCP Call: get_recent_transactions for {customer_id}")
    return [
        {"id": f"tx_{i}", "amount": 120.50, "merchant": "Amazon", "status": "CLEARED"}
        for i in range(limit)
    ]

@mcp.tool()
async def check_sanctions_list(name: str) -> dict:
    """Checks name against global sanctions lists (OFAC, UN)."""
    logger.info(f"MCP Call: check_sanctions_list for {name}")
    return {"is_sanctioned": False, "match_score": 0.0}

@mcp.tool()
async def submit_case_decision(case_id: str, decision: str, analyst_id: str) -> bool:
    """Submits human adjudication decision back to the system."""
    logger.info(f"MCP Call: submit_case_decision for {case_id}: {decision}")
    # In prod, this writes to DB and triggers Flywheel update
    return True

if __name__ == "__main__":
    # Run the MCP server using stdio transport
    mcp.run()
