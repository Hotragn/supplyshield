"""
generate_data.py - Generates synthetic supply chain data for SupplyShield.

Seed 42 for reproducibility. Writes JSON files to data/sample_data/.
Run from the project root: python data/generate_data.py
"""

import json
import os
import random
from datetime import datetime, timedelta, timezone

random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

NOW = datetime.now(timezone.utc)


def placeholder_embedding():
    """Generate a small non-zero placeholder vector (not semantically meaningful)."""
    return [round(random.uniform(0.001, 0.01), 6) for _ in range(384)]


def rnd_date(days_back_min=0, days_back_max=30):
    offset = timedelta(days=random.uniform(days_back_min, days_back_max))
    return (NOW - offset).strftime("%Y-%m-%dT%H:%M:%SZ")


def future_date(days_min=5, days_max=60):
    offset = timedelta(days=random.uniform(days_min, days_max))
    return (NOW + offset).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# SUPPLIERS
# ---------------------------------------------------------------------------

suppliers = []

# 3 key Shenzhen suppliers (the disrupted ones)
shenzhen_suppliers = [
    {
        "supplier_id": "SUP-SZ-001",
        "supplier_name": "Shenzhen Microtech Components",
        "region": "East Asia",
        "country": "China",
        "origin_port": "Shenzhen",
        "capabilities": ["microcontrollers", "system-on-chip", "pcb-assemblies"],
        "reliability_score": 88.5,
        "capacity_score": 92.0,
        "lead_time_days": 14,
        "active": True,
        "location": {"lat": 22.5329, "lon": 113.9283}
    },
    {
        "supplier_id": "SUP-SZ-002",
        "supplier_name": "GreenCell Battery Shenzhen",
        "region": "East Asia",
        "country": "China",
        "origin_port": "Shenzhen",
        "capabilities": ["battery-cells", "lithium-ion-packs", "battery-management"],
        "reliability_score": 85.0,
        "capacity_score": 88.0,
        "lead_time_days": 16,
        "active": True,
        "location": {"lat": 22.5460, "lon": 113.9155}
    },
    {
        "supplier_id": "SUP-SZ-003",
        "supplier_name": "Shenzhen Optolink Displays",
        "region": "East Asia",
        "country": "China",
        "origin_port": "Shenzhen",
        "capabilities": ["oled-displays", "lcd-panels", "touch-sensors"],
        "reliability_score": 82.0,
        "capacity_score": 79.0,
        "lead_time_days": 18,
        "active": True,
        "location": {"lat": 22.5200, "lon": 113.9100}
    }
]
suppliers.extend(shenzhen_suppliers)

# 5 alternative suppliers in other regions (recovery options)
alt_suppliers = [
    {
        "supplier_id": "SUP-VN-001",
        "supplier_name": "Viet Components Manufacturing",
        "region": "Southeast Asia",
        "country": "Vietnam",
        "origin_port": "Ho Chi Minh City",
        "capabilities": ["microcontrollers", "pcb-assemblies", "system-on-chip"],
        "reliability_score": 84.0,
        "capacity_score": 86.0,
        "lead_time_days": 18,
        "active": True,
        "location": {"lat": 10.8231, "lon": 106.6297}
    },
    {
        "supplier_id": "SUP-MY-001",
        "supplier_name": "Penang TechFab Industries",
        "region": "Southeast Asia",
        "country": "Malaysia",
        "origin_port": "Port Klang",
        "capabilities": ["microcontrollers", "memory-modules", "pcb-assemblies"],
        "reliability_score": 87.0,
        "capacity_score": 80.0,
        "lead_time_days": 21,
        "active": True,
        "location": {"lat": 5.4141, "lon": 100.3288}
    },
    {
        "supplier_id": "SUP-IN-001",
        "supplier_name": "Bangalore Precision Electronics",
        "region": "South Asia",
        "country": "India",
        "origin_port": "Chennai",
        "capabilities": ["battery-cells", "lithium-ion-packs", "power-management"],
        "reliability_score": 79.0,
        "capacity_score": 83.0,
        "lead_time_days": 24,
        "active": True,
        "location": {"lat": 12.9716, "lon": 77.5946}
    },
    {
        "supplier_id": "SUP-TH-001",
        "supplier_name": "Thai Optics and Display Co",
        "region": "Southeast Asia",
        "country": "Thailand",
        "origin_port": "Laem Chabang",
        "capabilities": ["oled-displays", "lcd-panels", "touch-sensors"],
        "reliability_score": 81.0,
        "capacity_score": 76.0,
        "lead_time_days": 20,
        "active": True,
        "location": {"lat": 13.7563, "lon": 100.5018}
    },
    {
        "supplier_id": "SUP-VN-002",
        "supplier_name": "Hanoi ElectroParts Ltd",
        "region": "Southeast Asia",
        "country": "Vietnam",
        "origin_port": "Haiphong",
        "capabilities": ["battery-cells", "battery-management", "power-management"],
        "reliability_score": 76.0,
        "capacity_score": 81.0,
        "lead_time_days": 22,
        "active": True,
        "location": {"lat": 21.0285, "lon": 105.8542}
    }
]
suppliers.extend(alt_suppliers)

# 25+ background suppliers globally
background_supplier_data = [
    ("SUP-TW-001", "Taiwan Semiconductor Supply", "East Asia", "Taiwan", "Kaohsiung", ["memory-modules", "flash-storage", "dram"], 91.0, 88.0, 16, {"lat": 22.6273, "lon": 120.3014}),
    ("SUP-TW-002", "Taipei Circuit Works", "East Asia", "Taiwan", "Keelung", ["pcb-assemblies", "memory-modules"], 89.0, 85.0, 14, {"lat": 25.1276, "lon": 121.7392}),
    ("SUP-KR-001", "Seoul Display Technologies", "East Asia", "South Korea", "Busan", ["oled-displays", "amoled-panels"], 93.0, 90.0, 12, {"lat": 37.5665, "lon": 126.9780}),
    ("SUP-KR-002", "Incheon Battery Systems", "East Asia", "South Korea", "Incheon", ["battery-cells", "lithium-ion-packs"], 90.0, 87.0, 13, {"lat": 37.4563, "lon": 126.7052}),
    ("SUP-JP-001", "Osaka Precision Parts", "East Asia", "Japan", "Osaka", ["microcontrollers", "sensors"], 95.0, 82.0, 11, {"lat": 34.6937, "lon": 135.5023}),
    ("SUP-JP-002", "Tokyo Electronic Materials", "East Asia", "Japan", "Yokohama", ["rare-earth-magnets", "sensors"], 94.0, 78.0, 10, {"lat": 35.6762, "lon": 139.6503}),
    ("SUP-ID-001", "Jakarta Industrial Parts", "Southeast Asia", "Indonesia", "Tanjung Priok", ["pcb-assemblies", "plastic-housings"], 72.0, 88.0, 25, {"lat": -6.2088, "lon": 106.8456}),
    ("SUP-PH-001", "Manila Electronics Assembly", "Southeast Asia", "Philippines", "Manila", ["pcb-assemblies", "cable-harnesses"], 74.0, 84.0, 22, {"lat": 14.5995, "lon": 120.9842}),
    ("SUP-MX-001", "Monterrey TechAssembly", "North America", "Mexico", "Manzanillo", ["pcb-assemblies", "plastic-housings", "cable-harnesses"], 83.0, 91.0, 8, {"lat": 25.6866, "lon": -100.3161}),
    ("SUP-MX-002", "Tijuana Precision Mfg", "North America", "Mexico", "Ensenada", ["microcontrollers", "pcb-assemblies"], 80.0, 86.0, 9, {"lat": 32.5149, "lon": -117.0382}),
    ("SUP-PL-001", "Wroclaw Electronics GmbH", "Europe", "Poland", "Gdansk", ["microcontrollers", "pcb-assemblies"], 88.0, 80.0, 7, {"lat": 51.1079, "lon": 17.0385}),
    ("SUP-CZ-001", "Prague Circuit Supplies", "Europe", "Czech Republic", "Hamburg", ["memory-modules", "pcb-assemblies"], 87.0, 77.0, 8, {"lat": 50.0755, "lon": 14.4378}),
    ("SUP-TR-001", "Istanbul TechParts", "Europe", "Turkey", "Mersin", ["plastic-housings", "cable-harnesses"], 75.0, 82.0, 12, {"lat": 41.0082, "lon": 28.9784}),
    ("SUP-MA-001", "Casablanca Industrial Electronics", "Africa", "Morocco", "Casablanca", ["cable-harnesses", "plastic-housings"], 70.0, 79.0, 14, {"lat": 33.5731, "lon": -7.5898}),
    ("SUP-SG-001", "Singapore Logistics Hub", "Southeast Asia", "Singapore", "Singapore", ["logistics", "pcb-assemblies"], 96.0, 75.0, 5, {"lat": 1.3521, "lon": 103.8198}),
    ("SUP-HK-001", "Hong Kong Components Ltd", "East Asia", "Hong Kong", "Hong Kong", ["microcontrollers", "memory-modules"], 89.0, 73.0, 9, {"lat": 22.3193, "lon": 114.1694}),
    ("SUP-AU-001", "Sydney Tech Supplies", "Oceania", "Australia", "Sydney", ["sensors", "power-management"], 91.0, 60.0, 18, {"lat": -33.8688, "lon": 151.2093}),
    ("SUP-BR-001", "Sao Paulo Electronics", "South America", "Brazil", "Santos", ["plastic-housings", "cable-harnesses"], 68.0, 85.0, 28, {"lat": -23.5505, "lon": -46.6333}),
    ("SUP-US-001", "Texas Semiconductor Supply", "North America", "USA", "Houston", ["microcontrollers", "sensors", "memory-modules"], 92.0, 70.0, 6, {"lat": 29.7604, "lon": -95.3698}),
    ("SUP-DE-001", "Munich Precision Systems", "Europe", "Germany", "Hamburg", ["sensors", "pcb-assemblies", "power-management"], 93.0, 72.0, 7, {"lat": 48.1351, "lon": 11.5820}),
    ("SUP-IN-002", "Mumbai Component Hub", "South Asia", "India", "JNPT Mumbai", ["plastic-housings", "cable-harnesses", "pcb-assemblies"], 73.0, 88.0, 20, {"lat": 19.0760, "lon": 72.8777}),
    ("SUP-KR-003", "Suwon Advanced Materials", "East Asia", "South Korea", "Busan", ["lcd-panels", "touch-sensors"], 88.0, 83.0, 14, {"lat": 37.2636, "lon": 127.0286}),
    ("SUP-MY-002", "Johor BahruTech Manufacturing", "Southeast Asia", "Malaysia", "Port of Tanjung Pelepas", ["pcb-assemblies", "plastic-housings"], 77.0, 90.0, 19, {"lat": 1.4927, "lon": 103.7414}),
    ("SUP-TH-002", "Chonburi Electronics Park", "Southeast Asia", "Thailand", "Laem Chabang", ["microcontrollers", "power-management"], 79.0, 85.0, 21, {"lat": 13.3611, "lon": 100.9847}),
    ("SUP-TW-003", "Taichung Advanced Semiconductors", "East Asia", "Taiwan", "Taichung", ["system-on-chip", "flash-storage"], 90.0, 84.0, 13, {"lat": 24.1477, "lon": 120.6736}),
]

for row in background_supplier_data:
    sid, name, region, country, port, caps, rel, cap, lead, loc = row
    suppliers.append({
        "supplier_id": sid,
        "supplier_name": name,
        "region": region,
        "country": country,
        "origin_port": port,
        "capabilities": caps,
        "reliability_score": rel,
        "capacity_score": cap,
        "lead_time_days": lead,
        "active": True,
        "location": loc
    })

print(f"Generated {len(suppliers)} suppliers")


# ---------------------------------------------------------------------------
# PRODUCTS (10)
# ---------------------------------------------------------------------------

products = [
    {
        "product_id": "PRD-001",
        "product_name": "SmartWatch Pro",
        "category": "wearables",
        "components": ["microcontrollers", "oled-displays", "battery-cells", "sensors", "touch-sensors"],
        "primary_supplier_id": "SUP-SZ-001",
        "backup_supplier_ids": ["SUP-VN-001", "SUP-MY-001"]
    },
    {
        "product_id": "PRD-002",
        "product_name": "Wireless Earbuds X",
        "category": "audio",
        "components": ["microcontrollers", "battery-cells", "battery-management", "sensors"],
        "primary_supplier_id": "SUP-SZ-002",
        "backup_supplier_ids": ["SUP-IN-001", "SUP-VN-002"]
    },
    {
        "product_id": "PRD-003",
        "product_name": "UltraTab 10",
        "category": "tablets",
        "components": ["system-on-chip", "lcd-panels", "battery-cells", "memory-modules", "touch-sensors"],
        "primary_supplier_id": "SUP-SZ-003",
        "backup_supplier_ids": ["SUP-TH-001", "SUP-KR-001"]
    },
    {
        "product_id": "PRD-004",
        "product_name": "HomeHub Controller",
        "category": "smart-home",
        "components": ["microcontrollers", "sensors", "pcb-assemblies"],
        "primary_supplier_id": "SUP-SZ-001",
        "backup_supplier_ids": ["SUP-VN-001", "SUP-PL-001"]
    },
    {
        "product_id": "PRD-005",
        "product_name": "FitTrack Band",
        "category": "wearables",
        "components": ["microcontrollers", "battery-cells", "oled-displays", "sensors"],
        "primary_supplier_id": "SUP-SZ-002",
        "backup_supplier_ids": ["SUP-IN-001", "SUP-KR-002"]
    },
    {
        "product_id": "PRD-006",
        "product_name": "StreamBox 4K",
        "category": "media",
        "components": ["system-on-chip", "memory-modules", "flash-storage", "pcb-assemblies"],
        "primary_supplier_id": "SUP-TW-001",
        "backup_supplier_ids": ["SUP-KR-001", "SUP-JP-001"]
    },
    {
        "product_id": "PRD-007",
        "product_name": "AirPure Monitor",
        "category": "smart-home",
        "components": ["sensors", "lcd-panels", "microcontrollers"],
        "primary_supplier_id": "SUP-JP-001",
        "backup_supplier_ids": ["SUP-KR-003", "SUP-TH-001"]
    },
    {
        "product_id": "PRD-008",
        "product_name": "SecureCam 360",
        "category": "security",
        "components": ["sensors", "memory-modules", "pcb-assemblies", "plastic-housings"],
        "primary_supplier_id": "SUP-KR-001",
        "backup_supplier_ids": ["SUP-TW-002", "SUP-MX-001"]
    },
    {
        "product_id": "PRD-009",
        "product_name": "PortaCharge Max",
        "category": "accessories",
        "components": ["battery-cells", "lithium-ion-packs", "power-management", "plastic-housings"],
        "primary_supplier_id": "SUP-SZ-002",
        "backup_supplier_ids": ["SUP-IN-001", "SUP-VN-002"]
    },
    {
        "product_id": "PRD-010",
        "product_name": "NovaPad Slim",
        "category": "tablets",
        "components": ["system-on-chip", "oled-displays", "battery-cells", "flash-storage"],
        "primary_supplier_id": "SUP-SZ-003",
        "backup_supplier_ids": ["SUP-TH-001", "SUP-TW-003"]
    }
]

print(f"Generated {len(products)} products")


# ---------------------------------------------------------------------------
# SHIPMENTS (200+)
# ---------------------------------------------------------------------------

PORT_COORDS = {
    "Shenzhen":          {"lat": 22.3964, "lon": 113.9170},
    "Ho Chi Minh City":  {"lat": 10.6553, "lon": 106.5977},
    "Port Klang":        {"lat": 3.0000,  "lon": 101.4072},
    "Kaohsiung":         {"lat": 22.5710, "lon": 120.2800},
    "Busan":             {"lat": 35.1040, "lon": 129.0350},
    "Osaka":             {"lat": 34.6492, "lon": 135.4320},
    "Incheon":           {"lat": 37.4802, "lon": 126.6152},
    "Yokohama":          {"lat": 35.4545, "lon": 139.6547},
    "Tanjung Priok":     {"lat": -6.1000, "lon": 106.8500},
    "Manila":            {"lat": 14.5764, "lon": 120.9688},
    "Manzanillo":        {"lat": 19.0522, "lon": -104.3148},
    "Laem Chabang":      {"lat": 13.0882, "lon": 100.9126},
    "Keelung":           {"lat": 25.1500, "lon": 121.7333},
    "Chen.ai":           {"lat": 13.0827, "lon": 80.2707},
    "Los Angeles":       {"lat": 33.7701, "lon": -118.1937},
    "Rotterdam":         {"lat": 51.9225, "lon": 4.4792},
    "Hamburg":           {"lat": 53.5511, "lon": 9.9937},
    "Long Beach":        {"lat": 33.7701, "lon": -118.1895},
    "Singapore":         {"lat": 1.2966,  "lon": 103.8506},
    "Hong Kong":         {"lat": 22.2855, "lon": 114.1577},
    "Haiphong":          {"lat": 20.8449, "lon": 106.6881},
    "Chennai":           {"lat": 13.0827, "lon": 80.2707},
}

DEST_PORTS = ["Los Angeles", "Long Beach", "Rotterdam", "Hamburg", "Singapore"]

shipments = []

# 14 pre-planted delayed shipments from Shenzhen
shenzhen_suppliers_for_delay = [
    ("SUP-SZ-001", "PRD-001"),
    ("SUP-SZ-001", "PRD-004"),
    ("SUP-SZ-001", "PRD-001"),
    ("SUP-SZ-001", "PRD-004"),
    ("SUP-SZ-001", "PRD-001"),
    ("SUP-SZ-002", "PRD-002"),
    ("SUP-SZ-002", "PRD-005"),
    ("SUP-SZ-002", "PRD-009"),
    ("SUP-SZ-002", "PRD-002"),
    ("SUP-SZ-002", "PRD-005"),
    ("SUP-SZ-003", "PRD-003"),
    ("SUP-SZ-003", "PRD-010"),
    ("SUP-SZ-003", "PRD-003"),
    ("SUP-SZ-003", "PRD-010"),
]

for i, (sup_id, prd_id) in enumerate(shenzhen_suppliers_for_delay, 1):
    delay = random.uniform(48, 336)
    status = random.choice(["delayed", "delayed", "at_port"])
    origin_coords = PORT_COORDS["Shenzhen"]
    dest_port = random.choice(DEST_PORTS)
    dest_coords = PORT_COORDS.get(dest_port, {"lat": 33.77, "lon": -118.19})
    ts = rnd_date(1, 14)  # Within the last 2 weeks

    shipments.append({
        "shipment_id": f"SHP-SZ-{i:04d}",
        "supplier_id": sup_id,
        "product_id": prd_id,
        "status": status,
        "origin_port": "Shenzhen",
        "destination_port": dest_port,
        "origin_location": origin_coords,
        "destination_location": dest_coords,
        "delay_hours": round(delay, 1),
        "quantity": random.randint(50, 500),
        "@timestamp": ts,
        "estimated_arrival": future_date(1, 20),
        "actual_arrival": None
    })

# 200 background shipments from various ports
background_ports = [
    ("Kaohsiung", "SUP-TW-001"),
    ("Kaohsiung", "SUP-TW-002"),
    ("Busan", "SUP-KR-001"),
    ("Busan", "SUP-KR-002"),
    ("Osaka", "SUP-JP-001"),
    ("Yokohama", "SUP-JP-002"),
    ("Tanjung Priok", "SUP-ID-001"),
    ("Manila", "SUP-PH-001"),
    ("Manzanillo", "SUP-MX-001"),
    ("Laem Chabang", "SUP-TH-001"),
    ("Ho Chi Minh City", "SUP-VN-001"),
    ("Haiphong", "SUP-VN-002"),
    ("Chennai", "SUP-IN-001"),
    ("Singapore", "SUP-SG-001"),
    ("Hong Kong", "SUP-HK-001"),
]

all_product_ids = [p["product_id"] for p in products]

for i in range(1, 201):
    port, sup_id = random.choice(background_ports)
    prd_id = random.choice(all_product_ids)

    roll = random.random()
    if roll < 0.15:
        delay = random.uniform(12, 48)
        status = "delayed"
    elif roll < 0.35:
        delay = random.uniform(0, 12)
        status = "in_transit"
    else:
        delay = 0.0
        status = random.choice(["delivered", "in_transit", "on_time"])

    origin_coords = PORT_COORDS.get(port, {"lat": 0.0, "lon": 0.0})
    dest_port = random.choice(DEST_PORTS)
    dest_coords = PORT_COORDS.get(dest_port, {"lat": 33.77, "lon": -118.19})

    shipments.append({
        "shipment_id": f"SHP-BG-{i:04d}",
        "supplier_id": sup_id,
        "product_id": prd_id,
        "status": status,
        "origin_port": port,
        "destination_port": dest_port,
        "origin_location": origin_coords,
        "destination_location": dest_coords,
        "delay_hours": round(delay, 1),
        "quantity": random.randint(20, 1000),
        "@timestamp": rnd_date(0, 30),
        "estimated_arrival": future_date(1, 45),
        "actual_arrival": rnd_date(0, 5) if status == "delivered" else None
    })

print(f"Generated {len(shipments)} shipments ({len(shenzhen_suppliers_for_delay)} Shenzhen delayed)")


# ---------------------------------------------------------------------------
# ORDERS (300)
# ---------------------------------------------------------------------------

CUSTOMERS = [
    ("CUST-001", "Northwind Electronics"),
    ("CUST-002", "Contoso Retail"),
    ("CUST-003", "Fabrikam Devices"),
    ("CUST-004", "Tailspin Consumer Tech"),
    ("CUST-005", "Alpine Gadgets"),
    ("CUST-006", "Bellwether Commerce"),
    ("CUST-007", "Coho Technology"),
    ("CUST-008", "Relecloud Wholesale"),
    ("CUST-009", "Trey Research"),
    ("CUST-010", "VanArsdel Ltd"),
    ("CUST-011", "Proseware Inc"),
    ("CUST-012", "Lucerne Publishing"),
]

orders = []
for i in range(1, 301):
    cust_id, cust_name = random.choice(CUSTOMERS)
    prd = random.choice(products)
    priority = random.choice(["standard", "standard", "high", "critical"])

    # About 60% active
    status = random.choices(["active", "fulfilled", "cancelled"], weights=[60, 35, 5])[0]
    revenue = round(random.uniform(500, 175000), 2)
    qty = random.randint(1, 200)

    days_until_due = random.uniform(3, 90)
    required_date = (NOW + timedelta(days=days_until_due)).strftime("%Y-%m-%dT%H:%M:%SZ")

    orders.append({
        "order_id": f"ORD-{i:05d}",
        "customer_id": cust_id,
        "customer_name": cust_name,
        "product_id": prd["product_id"],
        "status": status,
        "priority": priority,
        "revenue_value": revenue,
        "quantity": qty,
        "required_date": required_date,
        "@timestamp": rnd_date(5, 60)
    })

print(f"Generated {len(orders)} orders")


# ---------------------------------------------------------------------------
# NEWS (18)
# ---------------------------------------------------------------------------

news = []

# 3 pre-planted Shenzhen articles
shenzhen_articles = [
    {
        "article_id": "NEWS-SZ-001",
        "title": "Shenzhen Port Congestion Worsens as Trucking Shortage Hits Electronics Exporters",
        "body": (
            "Congestion at Shenzhen Yantian and Shekou terminals has reached critical levels this week, "
            "with vessel waiting times extending to 8-10 days according to port authority data. A combination "
            "of surging post-holiday export volumes and an acute shortage of truck drivers is creating a "
            "perfect storm for electronics manufacturers in the Pearl River Delta. Major component suppliers "
            "in the Longhua and Longgang districts are reporting that containers are taking 3-5 days longer "
            "to reach the terminal gate than normal, adding to already stretched lead times. "
            "Industry analysts estimate that approximately 340 vessels are currently waiting at anchor or "
            "slow-steaming toward Shenzhen, representing roughly 2.1 million TEUs of capacity. "
            "Electronics exports, which account for nearly 60% of Shenzhen port throughput, are particularly "
            "affected. Buyers in North America and Europe should expect delivery delays of 2-4 weeks on "
            "components already in transit, and should urgently review alternative sourcing options for "
            "critical supply chain nodes currently dependent on Pearl River Delta production."
        ),
        "regions": ["East Asia", "China"],
        "sentiment_score": -0.82,
        "disruption_type": "port_congestion",
        "severity": "high",
        "published_date": rnd_date(0, 3),
        "body_embedding": placeholder_embedding()
    },
    {
        "article_id": "NEWS-SZ-002",
        "title": "Chinese New Year Hangover: Shenzhen Freighter Delays Spike to 300+ Hours",
        "body": (
            "Two weeks after the Chinese New Year holiday ended, Shenzhen port is still struggling to clear "
            "the backlog of containers that accumulated during factory shutdowns. Freight forwarders are "
            "reporting delays of 12-14 days for containers that were ready to ship before the holiday "
            "but are only now moving through the terminal. "
            "The delay is compounded by new customs inspection requirements for electronics components "
            "announced last month, which adds an average of 18 hours per shipment for goods requiring "
            "country-of-origin documentation. Lithium battery shipments are facing additional scrutiny "
            "under updated IATA regulations, creating a secondary bottleneck at the haz-mat handling zones. "
            "ShippingLine analysts note that sailings are being blanked on key Asia-North America lanes "
            "as carriers try to reposition vessels. The rate for 40-foot containers from Shenzhen to "
            "Los Angeles has jumped 34% in the past two weeks, reflecting the supply tightening. "
            "Supply chain teams reliant on Shenzhen-based battery and display component suppliers should "
            "activate contingency sourcing plans and communicate proactively with downstream customers "
            "about potential delivery impacts."
        ),
        "regions": ["East Asia", "China", "Southeast Asia"],
        "sentiment_score": -0.75,
        "disruption_type": "port_congestion",
        "severity": "high",
        "published_date": rnd_date(1, 5),
        "body_embedding": placeholder_embedding()
    },
    {
        "article_id": "NEWS-SZ-003",
        "title": "Pearl River Delta Electronics Supply Chain Under Stress, Buyers Warned",
        "body": (
            "Supply chain risk consultants issued an advisory this morning warning electronics buyers that "
            "the Pearl River Delta manufacturing corridor is operating under significant stress. Shenzhen, "
            "Guangzhou, and Dongguan shipment delays are running 40-60% above the historical average for "
            "this time of year, according to tracking data from global logistics platforms. "
            "The disruption is concentrated in three segments: microcontroller and chip assemblies in "
            "Longhua district, display and optics components in Baoan, and battery pack manufacturers "
            "in the Shenzhen Special Economic Zone. Combined, these segments represent roughly $8.2 billion "
            "in annual exports to North American consumer electronics brands. "
            "Companies that source from single-region suppliers in southern China are being advised to "
            "run impact analyses on their open order books and pre-position safety stock where feasible. "
            "Vietnam, Malaysia, and South Korea have spare capacity in the affected component categories "
            "and represent viable short-term alternatives, though lead times will increase by 1-2 weeks."
        ),
        "regions": ["East Asia", "China", "Southeast Asia"],
        "sentiment_score": -0.70,
        "disruption_type": "port_congestion",
        "severity": "critical",
        "published_date": rnd_date(0, 2),
        "body_embedding": placeholder_embedding()
    }
]
news.extend(shenzhen_articles)

# 15 background articles
background_news_data = [
    ("NEWS-BG-001", "Taiwan Strait Tensions Drive Electronics Buyers to Diversify Sourcing", ["East Asia", "Taiwan"], -0.45, "geopolitical", "medium"),
    ("NEWS-BG-002", "Vietnam Manufacturing Capacity Expansion Attracts Electronics Giants", ["Southeast Asia", "Vietnam"], 0.60, "capacity_expansion", "low"),
    ("NEWS-BG-003", "Korean Battery Maker Commits $3B to New Malaysia Facility", ["Southeast Asia", "Malaysia"], 0.55, "capacity_expansion", "low"),
    ("NEWS-BG-004", "Suez Canal Delays Ease as Traffic Normalizes After Red Sea Tensions", ["Middle East", "Europe"], 0.30, "logistics", "low"),
    ("NEWS-BG-005", "Japan Semiconductor Shortage Persists Despite Government Subsidies", ["East Asia", "Japan"], -0.35, "shortage", "medium"),
    ("NEWS-BG-006", "Indian Electronics Manufacturing Sector Posts Record Quarter", ["South Asia", "India"], 0.70, "capacity_expansion", "low"),
    ("NEWS-BG-007", "Flash Storage Prices Drop 22% as NAND Supply Recovers", ["East Asia", "Global"], 0.65, "price_change", "low"),
    ("NEWS-BG-008", "Mexico Nearshoring Boom Draws Component Suppliers North", ["North America", "Mexico"], 0.50, "capacity_expansion", "low"),
    ("NEWS-BG-009", "Philippine Typhoon Season Risks Flagged for Southern Luzon Factory Corridor", ["Southeast Asia", "Philippines"], -0.50, "weather", "medium"),
    ("NEWS-BG-010", "EU Carbon Border Adjustment Mechanism to Hit Electronics Imports from Asia", ["Europe", "East Asia"], -0.30, "regulatory", "medium"),
    ("NEWS-BG-011", "Global Air Freight Capacity Tightens as Passenger Flights Fall Short", ["Global"], -0.25, "logistics", "low"),
    ("NEWS-BG-012", "Indonesia Nickel Export Restrictions Threaten Battery Supply Chains", ["Southeast Asia", "Indonesia"], -0.55, "regulatory", "high"),
    ("NEWS-BG-013", "Polish Electronics Assembly Sector Hits Capacity Limits Amid EU Demand", ["Europe", "Poland"], -0.10, "capacity", "low"),
    ("NEWS-BG-014", "South Korean Display Makers Report Record Orders for 2026", ["East Asia", "South Korea"], 0.75, "demand", "low"),
    ("NEWS-BG-015", "Rare Earth Magnet Prices Climb as China Tightens Export Controls", ["East Asia", "China", "Global"], -0.60, "regulatory", "high"),
]

background_bodies = [
    "Ongoing geopolitical uncertainty in the Taiwan Strait is prompting major electronics original equipment manufacturers to accelerate supply chain diversification plans. Procurement teams at several Fortune 500 companies confirmed they are expanding dual-sourcing programs to reduce single-region exposure, with Vietnam, Malaysia, and India cited as primary targets for new supplier relationships.",
    "Vietnam's manufacturing sector continues to attract significant foreign direct investment from electronics giants seeking to reduce China exposure. Industrial park occupancy rates in Binh Duong and Dong Nai provinces have reached 94%, and the government has approved three new export processing zones to meet demand. Component quality certifications are a remaining challenge for some categories.",
    "A leading South Korean battery manufacturer announced a $3 billion commitment to build a lithium-ion cell production facility in the Malaysian state of Pahang. The facility, expected to reach full production by Q3 2027, will supply cathode and anode materials along with finished cells to major consumer electronics assemblers in Southeast Asia.",
    "Shipping transit times through the Suez Canal have returned to near-normal levels following months of disruption caused by Houthi attacks on commercial vessels in the Red Sea. Average container-ship transit times on Europe-Asia routes are down to 28 days from a peak of 38 days, providing relief to electronics supply chains that had shifted to longer Cape of Good Hope routing.",
    "Japan's semiconductor and component shortage shows limited signs of resolution despite a government-backed fund aimed at boosting domestic production. Industry groups report that specialty microcontrollers and power management ICs remain on allocation, with lead times of 40-52 weeks for some categories. Buyers are urged to place forward orders to avoid gaps in 2027 production schedules.",
    "India's electronics manufacturing output hit a record quarterly high, driven by expanded assembly operations for smartphones and consumer devices. The Production Linked Incentive scheme continues to attract international component makers, with battery pack production growing 85% year over year. Analysts see India as a credible alternative source for several component categories currently dominated by China.",
    "NAND flash storage prices declined sharply in the latest spot market data, continuing a trend driven by oversupply from expanded Korean and Taiwanese fab facilities. Buyers with spot purchasing flexibility can negotiate attractive pricing on 128GB and 256GB modules, and procurement teams should consider locking in forward contracts before demand recovery tightens the market again.",
    "The nearshoring trend is transforming Mexico's electronics component sector as American and European OEMs seek suppliers within the USMCA trading bloc. Industrial parks in Monterrey, Juarez, and Guadalajara are reporting full occupancy for electronics-grade floor space, and several Tier 1 PCB assemblers are establishing new facilities to serve demand that was previously sourced from China.",
    "Weather risk assessors have flagged the upcoming Philippine typhoon season as a potential disruptor for electronics assembly operations in Luzon. Several major manufacturers have facilities in provinces historically affected by strong typhoons, and supply chain teams are advised to review business continuity plans and evaluate inventory positioning strategies ahead of the June-November risk window.",
    "The European Union's Carbon Border Adjustment Mechanism will begin applying to electronics imports from high-emission manufacturing regions starting next year. Industry groups estimate that components sourced from coal-heavy power grid regions in Asia could face effective tariff increases of 8-14%, incentivizing shifts toward suppliers operating on greener energy. Companies should begin compliance assessments now.",
    "Global air freight capacity remains tight as passenger aircraft belly-hold space fails to keep pace with express shipment demand. Electronics manufacturers using air freight for critical component restocking are seeing rates 18-22% above the five-year average. Ocean freight and pre-positioning of safety stock are being prioritized where lead times allow.",
    "Indonesia's government expanded nickel ore export restrictions to cover additional grades of processed nickel, raising concerns among battery supply chain analysts. Indonesia holds the world's largest nickel reserves, and the restrictions are intended to push value-added processing onshore. Global battery-grade nickel prices rose 11% on the announcement, affecting lithium iron phosphate and NMC cell economics.",
    "Polish electronics assembly plants are operating at near-maximum utilization as European OEM demand for locally manufactured components remains strong. Labor market tightness and energy costs are the primary constraints on further expansion, and several facility operators are investing in automation to maintain competitiveness. New capacity additions are expected in 2027 at the earliest.",
    "South Korean display manufacturers reported record order books for 2026, driven by increasing adoption of OLED panels in automotive and wearable applications. Production capacity is fully allocated through Q3, and buyers who have not locked in supply agreements for 2026 should expect extended lead times or premium pricing on spot purchases.",
    "Chinese government export licensing requirements for rare earth magnets and related materials have tightened, sending prices higher across the permanent magnet supply chain. Neodymium-iron-boron magnets, used in motors, speakers, and many consumer electronics, saw spot prices increase 18% over the past month. Electronics manufacturers with high-magnet content products should review their exposure and explore inventory hedging options."
]

for idx, (aid, title, regions, sentiment, dtype, severity) in enumerate(background_news_data):
    news.append({
        "article_id": aid,
        "title": title,
        "body": background_bodies[idx],
        "regions": regions,
        "sentiment_score": sentiment,
        "disruption_type": dtype,
        "severity": severity,
        "published_date": rnd_date(0, 21),
        "body_embedding": placeholder_embedding()
    })

print(f"Generated {len(news)} news articles")


# ---------------------------------------------------------------------------
# WRITE TO JSON FILES
# ---------------------------------------------------------------------------

def write_json(filename, data):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"  Wrote {len(data)} records to {filename}")


print("\nWriting data files...")
write_json("suppliers.json", suppliers)
write_json("products.json", products)
write_json("shipments.json", shipments)
write_json("orders.json", orders)
write_json("news.json", news)

# ---------------------------------------------------------------------------
# DEMO SUMMARY
# ---------------------------------------------------------------------------

shenzhen_delayed = [s for s in shipments if s["origin_port"] == "Shenzhen" and s["delay_hours"] > 24]
shenzhen_supplier_ids = {"SUP-SZ-001", "SUP-SZ-002", "SUP-SZ-003"}

# Find products with Shenzhen primary suppliers
szhen_product_ids = {p["product_id"] for p in products if p["primary_supplier_id"] in shenzhen_supplier_ids}

# Find active orders for those products
at_risk_orders = [o for o in orders if o["status"] == "active" and o["product_id"] in szhen_product_ids]
revenue_at_risk = sum(o["revenue_value"] for o in at_risk_orders)

print("\n" + "="*60)
print("DEMO SCENARIO SUMMARY (Shenzhen Port Congestion)")
print("="*60)
print(f"  Delayed Shenzhen shipments (>24h):    {len(shenzhen_delayed)}")
print(f"  Active orders at risk:                 {len(at_risk_orders)}")
print(f"  Customers affected:                    {len({o['customer_id'] for o in at_risk_orders})}")
print(f"  Total revenue at risk:                 ${revenue_at_risk:,.0f}")
print(f"  Alternative suppliers available:       {len(alt_suppliers)}")
print("="*60)
print("\nDone. Run: python data/load_data.py")
