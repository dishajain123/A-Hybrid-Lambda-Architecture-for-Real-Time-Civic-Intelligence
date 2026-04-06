"""
Comprehensive dummy data — same schema as the real API (all fields covered).
"""
from datetime import datetime, timedelta
import random

random.seed(42)

# ──────────────────────────────────────────────────────────────────────────────
# ARTICLE POOL — matches bronze-layer search_news / top_news article schema
# ──────────────────────────────────────────────────────────────────────────────
ARTICLES = [
    {
        "id": 100001,
        "title": "Trump confirms India-US trade deal; tariffs slashed from 25% to 18%",
        "text": "US President Donald Trump announced a reduced reciprocal tariff on India from 25% to 18% following a phone call with PM Modi. Markets reacted positively — GIFT Nifty jumped 800 points. PM Modi called it a 'wonderful announcement' on behalf of 1.4 billion Indians.",
        "summary": "US-India trade deal finalised; tariffs cut to 18%, markets rally 800 points.",
        "url": "https://www.financialexpress.com/business/india-us-trade-deal/",
        "image": "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=800&q=80", "width": 800, "height": 450, "title": "US-India handshake"},
            {"url": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=800&q=80", "width": 800, "height": 533, "title": "Trade deal signing"},
        ],
        "video": None, "publish_date": "2026-02-02 18:13:48",
        "author": "Economic Desk", "authors": ["Economic Desk"],
        "language": "en", "category": "politics", "source_country": "in", "sentiment": 0.472,
        "entities": [
            {"type": "PER", "name": "Donald Trump", "description": "45th and 47th President of the United States", "full_name": "Donald Trump", "image": "https://upload.wikimedia.org/wikipedia/commons/5/56/Donald_Trump_official_portrait.jpg"},
            {"type": "PER", "name": "Narendra Modi", "description": "Prime Minister of India", "full_name": "Narendra Modi", "image": "https://upload.wikimedia.org/wikipedia/commons/c/c0/Narendra_Modi_portrait.jpg"},
            {"type": "ORG", "name": "GIFT Nifty", "description": "Indian stock exchange futures index", "full_name": "GIFT Nifty"},
            {"type": "LOC", "name": "India", "latitude": 20.0, "longitude": 77.0, "location_type": "COUNTRY"},
            {"type": "LOC", "name": "United States", "latitude": 37.09, "longitude": -95.71, "location_type": "COUNTRY"},
        ],
    },
    {
        "id": 100002,
        "title": "Budget 2026: Income tax exemption raised to ₹12 lakh — middle class cheers",
        "text": "Finance Minister Nirmala Sitharaman presented Union Budget 2026-27, raising income tax exemption to ₹12 lakh under the new regime. Capital expenditure allocation rose 15% to ₹11.1 lakh crore.",
        "summary": "Budget 2026 raises tax exemption to ₹12 lakh; capex up 15% to ₹11.1L crore.",
        "url": "https://www.financialexpress.com/budget-2026/highlights/",
        "image": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=800&q=80", "width": 800, "height": 533, "title": "Budget 2026 presentation"},
        ],
        "video": None, "publish_date": "2026-02-01 11:00:00",
        "author": "Finance Desk", "authors": ["Finance Desk"],
        "language": "en", "category": "business", "source_country": "in", "sentiment": 0.65,
        "entities": [
            {"type": "PER", "name": "Nirmala Sitharaman", "description": "Finance Minister of India", "full_name": "Nirmala Sitharaman"},
            {"type": "ORG", "name": "Government of India", "description": "Central government of India", "full_name": "Government of India"},
            {"type": "LOC", "name": "New Delhi", "latitude": 28.61, "longitude": 77.23, "location_type": "CITY"},
        ],
    },
    {
        "id": 100003,
        "title": "Air India grounds Boeing 787 after fuel-switch malfunction on London-Bengaluru flight",
        "text": "An Air India pilot reported a fuel-switch malfunction on a Boeing 787-8 after landing from London. The aircraft has been grounded pending examination. DGCA has sought a report from the airline.",
        "summary": "Air India 787 grounded after fuel-switch malfunction; DGCA seeks report.",
        "url": "https://www.thehindu.com/business/Industry/air-india-fuel-switch/",
        "image": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=800&q=80", "width": 800, "height": 532, "title": "Air India Boeing 787"},
            {"url": "https://images.unsplash.com/photo-1474514644254-7584d0f86b5a?w=800&q=80", "width": 800, "height": 450, "title": "Aircraft maintenance"},
        ],
        "video": None, "publish_date": "2026-02-02 23:05:00",
        "author": "Aviation Desk", "authors": ["Aviation Desk"],
        "language": "en", "category": "general", "source_country": "in", "sentiment": -0.18,
        "entities": [
            {"type": "ORG", "name": "Air India", "description": "Indian national airline", "full_name": "Air India"},
            {"type": "ORG", "name": "DGCA", "description": "Directorate General of Civil Aviation, India", "full_name": "Directorate General of Civil Aviation"},
            {"type": "ORG", "name": "Boeing", "description": "American aerospace manufacturer", "full_name": "The Boeing Company"},
            {"type": "LOC", "name": "London", "latitude": 51.51, "longitude": -0.13, "location_type": "CITY"},
            {"type": "LOC", "name": "Bengaluru", "latitude": 12.97, "longitude": 77.59, "location_type": "CITY"},
        ],
    },
    {
        "id": 100004,
        "title": "MP doctor arrested: toxic cough syrup with 48× permissible limit kills 14 children",
        "text": "Dr Praveen Soni was arrested after an FIR was filed in Chhindwara. Tests revealed the syrup contained 48.6% of a substance whose limit is 1%. Four renal biopsies confirmed kidney failure. CM announced ₹4 lakh ex-gratia per family.",
        "summary": "Doctor arrested in MP after toxic cough syrup kills 14 children; syrup had 48× toxic limit.",
        "url": "https://www.news18.com/india/mp-toxic-cough-syrup-14-children/",
        "image": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&q=80", "width": 800, "height": 533, "title": "Medicine bottles"},
        ],
        "video": None, "publish_date": "2026-01-28 09:30:00",
        "author": "Anushka Vats", "authors": ["Anushka Vats", "News18"],
        "language": "en", "category": "health", "source_country": "in", "sentiment": -0.82,
        "entities": [
            {"type": "PER", "name": "Praveen Soni", "description": "Doctor arrested in Chhindwara cough syrup case", "full_name": "Dr Praveen Soni"},
            {"type": "ORG", "name": "Sresan Pharmaceuticals", "description": "Pharmaceutical company linked to toxic syrup", "full_name": "Sresan Pharmaceuticals"},
            {"type": "LOC", "name": "Chhindwara", "latitude": 22.06, "longitude": 78.94, "location_type": "CITY"},
            {"type": "LOC", "name": "Madhya Pradesh", "latitude": 23.47, "longitude": 77.95, "location_type": "STATE"},
        ],
    },
    {
        "id": 100005,
        "title": "ISRO launches GSAT-20 aboard LVM3; to deliver broadband to remote India",
        "text": "ISRO successfully placed GSAT-20, a high-throughput communication satellite, in geostationary orbit using LVM3-M4 from Sriharikota. The satellite will provide 48 Gbps capacity across India.",
        "summary": "GSAT-20 launched by ISRO aboard LVM3; 48 Gbps broadband for remote India.",
        "url": "https://www.thehindu.com/sci-tech/science/isro-gsat-20-lvm3/",
        "image": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=800&q=80", "width": 800, "height": 533, "title": "Rocket launch"},
            {"url": "https://images.unsplash.com/photo-1614642264762-d0a3b8bf3700?w=800&q=80", "width": 800, "height": 450, "title": "Satellite in orbit"},
        ],
        "video": None, "publish_date": "2026-01-25 14:00:00",
        "author": "Science Desk", "authors": ["Science Desk"],
        "language": "en", "category": "technology", "source_country": "in", "sentiment": 0.78,
        "entities": [
            {"type": "ORG", "name": "ISRO", "description": "Indian Space Research Organisation", "full_name": "Indian Space Research Organisation"},
            {"type": "LOC", "name": "Sriharikota", "latitude": 13.72, "longitude": 80.23, "location_type": "CITY"},
            {"type": "LOC", "name": "India", "latitude": 20.0, "longitude": 77.0, "location_type": "COUNTRY"},
        ],
    },
    {
        "id": 100006,
        "title": "IPL 2026 mega auction: Mumbai Indians retain Rohit Sharma for ₹16 cr",
        "text": "Mumbai Indians retained skipper Rohit Sharma for ₹16 crore at the IPL 2026 mega auction in Jeddah. Total spend across franchises crossed ₹5,400 crore. Rishabh Pant became the most expensive buy at ₹27 crore.",
        "summary": "Rohit retained for ₹16 cr; Pant becomes priciest buy at ₹27 cr in IPL 2026 auction.",
        "url": "https://www.timesnownews.com/sports/cricket/ipl-2026-mega-auction/",
        "image": "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=800&q=80", "width": 800, "height": 533, "title": "Cricket stadium"},
        ],
        "video": None, "publish_date": "2026-01-20 16:45:00",
        "author": "Sports Desk", "authors": ["Sports Desk"],
        "language": "en", "category": "sports", "source_country": "in", "sentiment": 0.55,
        "entities": [
            {"type": "PER", "name": "Rohit Sharma", "description": "Indian cricketer, Mumbai Indians captain", "full_name": "Rohit Sharma"},
            {"type": "PER", "name": "Rishabh Pant", "description": "Indian cricketer and wicket-keeper", "full_name": "Rishabh Pant"},
            {"type": "ORG", "name": "Mumbai Indians", "description": "IPL franchise", "full_name": "Mumbai Indians"},
            {"type": "ORG", "name": "BCCI", "description": "Board of Control for Cricket in India", "full_name": "Board of Control for Cricket in India"},
            {"type": "LOC", "name": "Jeddah", "latitude": 21.49, "longitude": 39.19, "location_type": "CITY"},
        ],
    },
    {
        "id": 100007,
        "title": "Delhi air quality reaches 'Good' for the first time in three years",
        "text": "Delhi's AQI dropped to 42 — classified as 'Good' — for the first time since January 2023. Winter rains and stricter enforcement of emission norms under GRAP-IV contributed to the improvement.",
        "summary": "Delhi AQI falls to 'Good' category (42) for the first time in 3 years.",
        "url": "https://www.thehindu.com/news/cities/Delhi/delhi-aqi-good/",
        "image": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=800&q=80", "width": 800, "height": 533, "title": "Delhi skyline"},
        ],
        "video": None, "publish_date": "2026-01-15 08:30:00",
        "author": "Environment Desk", "authors": ["Environment Desk"],
        "language": "en", "category": "general", "source_country": "in", "sentiment": 0.61,
        "entities": [
            {"type": "LOC", "name": "Delhi", "latitude": 28.70, "longitude": 77.10, "location_type": "CITY"},
            {"type": "ORG", "name": "CPCB", "description": "Central Pollution Control Board", "full_name": "Central Pollution Control Board"},
        ],
    },
    {
        "id": 100008,
        "title": "Bengaluru fintech NeoFinance raises $200M Series D, valued at $2.1 billion",
        "text": "NeoFinance, a Bengaluru-based B2B lending platform, raised $200 million in Series D led by Tiger Global and Sequoia India. The round pushes its valuation to $2.1 billion, making it India's 112th unicorn.",
        "summary": "NeoFinance becomes India's 112th unicorn with $200M Series D at $2.1B valuation.",
        "url": "https://www.financialexpress.com/business/startup/neofinance-series-d/",
        "image": "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=800&q=80", "width": 800, "height": 533, "title": "Fintech startup office"},
        ],
        "video": None, "publish_date": "2026-01-12 10:00:00",
        "author": "Tech Desk", "authors": ["Tech Desk"],
        "language": "en", "category": "business", "source_country": "in", "sentiment": 0.72,
        "entities": [
            {"type": "ORG", "name": "NeoFinance", "description": "Bengaluru B2B fintech unicorn", "full_name": "NeoFinance Pvt Ltd"},
            {"type": "ORG", "name": "Tiger Global", "description": "US-based investment firm", "full_name": "Tiger Global Management"},
            {"type": "ORG", "name": "Sequoia India", "description": "Venture capital firm", "full_name": "Sequoia Capital India"},
            {"type": "LOC", "name": "Bengaluru", "latitude": 12.97, "longitude": 77.59, "location_type": "CITY"},
        ],
    },
    {
        "id": 100009,
        "title": "Mumbai hit by unseasonal rains; 200+ flights delayed, suburban trains disrupted",
        "text": "Intense unseasonal rainfall — 94 mm in 6 hours — paralysed Mumbai, flooding Kurla, Dadar and Andheri. Over 200 flights at CSIA were delayed. Western and Central Railway reported 45-minute delays.",
        "summary": "94mm rain in 6 hrs floods Mumbai; 200+ flights delayed, trains disrupted.",
        "url": "https://www.news18.com/india/mumbai-unseasonal-floods/",
        "image": "https://images.unsplash.com/photo-1516912481808-3406841bd33c?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1516912481808-3406841bd33c?w=800&q=80", "width": 800, "height": 533, "title": "Mumbai flooding"},
        ],
        "video": None, "publish_date": "2026-01-10 22:00:00",
        "author": "City Desk", "authors": ["City Desk", "News18"],
        "language": "en", "category": "general", "source_country": "in", "sentiment": -0.45,
        "entities": [
            {"type": "LOC", "name": "Mumbai", "latitude": 19.08, "longitude": 72.88, "location_type": "CITY"},
            {"type": "LOC", "name": "Kurla", "latitude": 19.07, "longitude": 72.88, "location_type": "LANDMARK"},
            {"type": "ORG", "name": "Western Railway", "description": "Indian Railways zone", "full_name": "Western Railway"},
            {"type": "ORG", "name": "CSIA", "description": "Chhatrapati Shivaji Maharaj International Airport", "full_name": "Chhatrapati Shivaji Maharaj International Airport"},
        ],
    },
    {
        "id": 100010,
        "title": "India-EU Free Trade Agreement signed in Brussels — Modi calls it 'mother of all deals'",
        "text": "India and the EU signed a landmark FTA at a ceremony in Brussels. The deal eliminates 95% of tariff lines over 10 years and includes chapters on digital trade and sustainability.",
        "summary": "India-EU FTA signed; $700B market opened, PM Modi calls it 'mother of all deals'.",
        "url": "https://www.thehindu.com/business/Economy/india-eu-fta-brussels/",
        "image": "https://images.unsplash.com/photo-1520695287272-b7f8af46d367?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1520695287272-b7f8af46d367?w=800&q=80", "width": 800, "height": 450, "title": "EU India flags"},
        ],
        "video": None, "publish_date": "2026-01-08 15:00:00",
        "author": "Diplomatic Correspondent", "authors": ["Diplomatic Correspondent"],
        "language": "en", "category": "politics", "source_country": "in", "sentiment": 0.68,
        "entities": [
            {"type": "PER", "name": "Narendra Modi", "description": "Prime Minister of India", "full_name": "Narendra Modi"},
            {"type": "ORG", "name": "European Union", "description": "Political and economic union", "full_name": "European Union"},
            {"type": "LOC", "name": "Brussels", "latitude": 50.85, "longitude": 4.35, "location_type": "CITY"},
            {"type": "LOC", "name": "India", "latitude": 20.0, "longitude": 77.0, "location_type": "COUNTRY"},
        ],
    },
    {
        "id": 100011,
        "title": "Rajasthan coal mine collapse: 12 miners trapped near Barmer; NDRF deployed",
        "text": "A sudden roof collapse at a coal mine in Barmer trapped 12 miners. NDRF teams are using drilling equipment to reach survivors. Chief Minister has spoken to families and promised full assistance.",
        "summary": "12 miners trapped in Rajasthan mine collapse; NDRF rescue op underway.",
        "url": "https://www.timesnownews.com/india/rajasthan-barmer-mine-collapse/",
        "image": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800&q=80", "width": 800, "height": 533, "title": "Mine rescue operation"},
        ],
        "video": None, "publish_date": "2026-01-05 13:00:00",
        "author": "State Desk", "authors": ["State Desk"],
        "language": "en", "category": "general", "source_country": "in", "sentiment": -0.71,
        "entities": [
            {"type": "ORG", "name": "NDRF", "description": "National Disaster Response Force", "full_name": "National Disaster Response Force"},
            {"type": "LOC", "name": "Barmer", "latitude": 25.75, "longitude": 71.39, "location_type": "CITY"},
            {"type": "LOC", "name": "Rajasthan", "latitude": 27.02, "longitude": 74.22, "location_type": "STATE"},
        ],
    },
    {
        "id": 100012,
        "title": "Chandrayaan-4 achieves lunar orbit insertion — India set to bring back moon samples",
        "text": "ISRO's Chandrayaan-4 spacecraft successfully entered lunar orbit after a 28-day transit. The mission will attempt a soft landing, collect 3 kg of regolith, and return samples to Earth.",
        "summary": "Chandrayaan-4 enters lunar orbit; will attempt sample return, a first for India.",
        "url": "https://www.thehindu.com/sci-tech/science/chandrayaan-4-lunar-orbit/",
        "image": "https://images.unsplash.com/photo-1614642264762-d0a3b8bf3700?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1614642264762-d0a3b8bf3700?w=800&q=80", "width": 800, "height": 450, "title": "Moon surface"},
            {"url": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=800&q=80", "width": 800, "height": 533, "title": "ISRO launch"},
        ],
        "video": None, "publish_date": "2025-12-28 20:00:00",
        "author": "ISRO Correspondent", "authors": ["ISRO Correspondent"],
        "language": "en", "category": "technology", "source_country": "in", "sentiment": 0.88,
        "entities": [
            {"type": "ORG", "name": "ISRO", "description": "Indian Space Research Organisation", "full_name": "Indian Space Research Organisation"},
            {"type": "LOC", "name": "Sriharikota", "latitude": 13.72, "longitude": 80.23, "location_type": "CITY"},
            {"type": "LOC", "name": "Moon", "latitude": 0.0, "longitude": 0.0, "location_type": "LANDMARK"},
        ],
    },
    {
        "id": 100013,
        "title": "UPI crosses 18 billion transactions in December 2025 — new all-time record",
        "text": "UPI processed 18.07 billion transactions worth ₹25.4 lakh crore in December 2025. NPCI attributed growth to festive shopping and tier-2/3 city adoption.",
        "summary": "UPI records 18 billion transactions (₹25.4L crore) in December 2025.",
        "url": "https://www.financialexpress.com/business/banking/upi-december-record/",
        "image": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=800&q=80", "width": 800, "height": 533, "title": "UPI payment"},
        ],
        "video": None, "publish_date": "2026-01-03 12:00:00",
        "author": "Finance Desk", "authors": ["Finance Desk"],
        "language": "en", "category": "business", "source_country": "in", "sentiment": 0.76,
        "entities": [
            {"type": "ORG", "name": "NPCI", "description": "National Payments Corporation of India", "full_name": "National Payments Corporation of India"},
            {"type": "ORG", "name": "UPI", "description": "Unified Payments Interface", "full_name": "Unified Payments Interface"},
            {"type": "LOC", "name": "India", "latitude": 20.0, "longitude": 77.0, "location_type": "COUNTRY"},
        ],
    },
    {
        "id": 100014,
        "title": "AAP wins Delhi assembly election with 42 seats; Kejriwal to be CM again",
        "text": "The Aam Aadmi Party secured 42 of 70 assembly seats in Delhi, returning Arvind Kejriwal to power for a third term. BJP won 26 seats. Turnout was 65.4%.",
        "summary": "AAP wins 42 seats in Delhi polls; Kejriwal returns as CM for third term.",
        "url": "https://www.news18.com/politics/delhi-election-2025-results/",
        "image": "https://images.unsplash.com/photo-1540910419892-4a36d2c3266c?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1540910419892-4a36d2c3266c?w=800&q=80", "width": 800, "height": 533, "title": "Election results"},
        ],
        "video": None, "publish_date": "2025-12-15 20:00:00",
        "author": "Political Desk", "authors": ["Political Desk", "News18"],
        "language": "en", "category": "politics", "source_country": "in", "sentiment": 0.22,
        "entities": [
            {"type": "PER", "name": "Arvind Kejriwal", "description": "AAP leader, Delhi Chief Minister", "full_name": "Arvind Kejriwal"},
            {"type": "ORG", "name": "AAP", "description": "Aam Aadmi Party", "full_name": "Aam Aadmi Party"},
            {"type": "ORG", "name": "BJP", "description": "Bharatiya Janata Party", "full_name": "Bharatiya Janata Party"},
            {"type": "LOC", "name": "Delhi", "latitude": 28.70, "longitude": 77.10, "location_type": "CITY"},
        ],
    },
    {
        "id": 100015,
        "title": "India achieves 300 GW renewable energy — two years ahead of 2030 target",
        "text": "India crossed the 300 GW renewable energy milestone set for 2030. Solar alone contributes 195 GW, wind at 55 GW and hydro at 50 GW. India is now 3rd globally in renewable capacity.",
        "summary": "India hits 300 GW renewable energy goal 2 years early; 3rd globally.",
        "url": "https://www.thehindu.com/news/national/india-300gw-renewable/",
        "image": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800&q=80", "width": 800, "height": 533, "title": "Solar panels India"},
        ],
        "video": None, "publish_date": "2025-11-30 10:00:00",
        "author": "Environment Correspondent", "authors": ["Environment Correspondent"],
        "language": "en", "category": "technology", "source_country": "in", "sentiment": 0.82,
        "entities": [
            {"type": "ORG", "name": "Ministry of New and Renewable Energy", "description": "Indian government ministry", "full_name": "Ministry of New and Renewable Energy"},
            {"type": "LOC", "name": "India", "latitude": 20.0, "longitude": 77.0, "location_type": "COUNTRY"},
        ],
    },
    {
        "id": 100016,
        "title": "Manipur: Fresh ethnic violence kills 8, injures 23; Army deployed",
        "text": "Ethnic clashes between Meitei and Kuki communities in Churachandpur left 8 dead and 23 injured. Army deployed and indefinite curfew imposed in five districts. Internet services suspended.",
        "summary": "8 killed in Manipur ethnic violence; Army deployed, curfew across 5 districts.",
        "url": "https://www.thehindu.com/news/national/other-states/manipur-ethnic-violence/",
        "image": "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&q=80", "width": 800, "height": 533, "title": "Northeast India"},
        ],
        "video": None, "publish_date": "2025-11-20 16:00:00",
        "author": "Northeast Correspondent", "authors": ["Northeast Correspondent"],
        "language": "en", "category": "general", "source_country": "in", "sentiment": -0.76,
        "entities": [
            {"type": "LOC", "name": "Manipur", "latitude": 24.66, "longitude": 93.91, "location_type": "STATE"},
            {"type": "LOC", "name": "Churachandpur", "latitude": 24.34, "longitude": 93.68, "location_type": "CITY"},
            {"type": "ORG", "name": "Indian Army", "description": "Military branch of India", "full_name": "Indian Army"},
        ],
    },
    {
        "id": 100017,
        "title": "Hyderabad Pharma City: PM Modi lays foundation stone for 19,333-acre SEZ",
        "text": "PM Modi laid the foundation stone for Hyderabad Pharma City, expected to be the world's largest pharma manufacturing cluster. The SEZ will create 30,000 direct and 100,000 indirect jobs.",
        "summary": "PM Modi inaugurates Hyderabad Pharma City; 30,000 jobs, world's largest pharma SEZ.",
        "url": "https://www.financialexpress.com/business/industry/hyderabad-pharma-city/",
        "image": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=800&q=80", "width": 800, "height": 533, "title": "Pharma manufacturing"},
        ],
        "video": None, "publish_date": "2025-11-10 11:00:00",
        "author": "Industry Desk", "authors": ["Industry Desk"],
        "language": "en", "category": "business", "source_country": "in", "sentiment": 0.69,
        "entities": [
            {"type": "PER", "name": "Narendra Modi", "description": "Prime Minister of India", "full_name": "Narendra Modi"},
            {"type": "LOC", "name": "Hyderabad", "latitude": 17.39, "longitude": 78.49, "location_type": "CITY"},
            {"type": "LOC", "name": "Telangana", "latitude": 18.11, "longitude": 79.02, "location_type": "STATE"},
        ],
    },
    {
        "id": 100018,
        "title": "Cyclone Dana batters Chennai coast; 3 dead, 15,000 evacuated",
        "text": "Cyclone Dana, packing 120 km/h winds, made landfall near Mahabalipuram and inundated coastal Chennai. Three deaths were reported and 15,000 residents moved to relief camps.",
        "summary": "Cyclone Dana kills 3 in Chennai, 15,000 evacuated; ₹500 crore crop damage.",
        "url": "https://www.news18.com/india/cyclone-dana-chennai-landfall/",
        "image": "https://images.unsplash.com/photo-1519692933481-e162a57d6721?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1519692933481-e162a57d6721?w=800&q=80", "width": 800, "height": 533, "title": "Storm waves"},
        ],
        "video": None, "publish_date": "2025-10-30 08:00:00",
        "author": "South India Desk", "authors": ["South India Desk"],
        "language": "en", "category": "general", "source_country": "in", "sentiment": -0.62,
        "entities": [
            {"type": "LOC", "name": "Chennai", "latitude": 13.08, "longitude": 80.27, "location_type": "CITY"},
            {"type": "LOC", "name": "Mahabalipuram", "latitude": 12.62, "longitude": 80.19, "location_type": "LANDMARK"},
            {"type": "ORG", "name": "IMD", "description": "India Meteorological Department", "full_name": "India Meteorological Department"},
        ],
    },
    {
        "id": 100019,
        "title": "Virat Kohli retires from Test cricket: 'The hardest decision of my life'",
        "text": "Virat Kohli announced his retirement from Test cricket via a heartfelt letter. He ends his Test career with 9,230 runs in 113 matches at an average of 48.58. He will continue in ODIs and T20Is.",
        "summary": "Kohli retires from Tests with 9,230 runs; continues in white-ball formats.",
        "url": "https://www.timesnownews.com/sports/cricket/virat-kohli-test-retirement/",
        "image": "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=800&q=80", "width": 800, "height": 533, "title": "Cricket match"},
        ],
        "video": None, "publish_date": "2025-10-15 12:00:00",
        "author": "Sports Desk", "authors": ["Sports Desk"],
        "language": "en", "category": "sports", "source_country": "in", "sentiment": -0.15,
        "entities": [
            {"type": "PER", "name": "Virat Kohli", "description": "Indian international cricketer", "full_name": "Virat Kohli"},
            {"type": "ORG", "name": "BCCI", "description": "Board of Control for Cricket in India", "full_name": "Board of Control for Cricket in India"},
            {"type": "ORG", "name": "Team India", "description": "Indian national cricket team", "full_name": "Indian Cricket Team"},
        ],
    },
    {
        "id": 100020,
        "title": "India GDP grows 7.8% in Q2 FY2026, beats IMF forecast of 7.2%",
        "text": "India's GDP expanded 7.8% in Q2 FY2026 driven by 9.2% growth in manufacturing and 8.4% in services. The government attributed the performance to PLI scheme benefits and strong urban consumption.",
        "summary": "India GDP at 7.8% in Q2 FY26, beating IMF forecast; manufacturing leads at 9.2%.",
        "url": "https://www.financialexpress.com/business/economy/india-gdp-q2-fy2026/",
        "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80", "width": 800, "height": 533, "title": "Economic growth chart"},
        ],
        "video": None, "publish_date": "2025-10-01 09:00:00",
        "author": "Economy Desk", "authors": ["Economy Desk"],
        "language": "en", "category": "business", "source_country": "in", "sentiment": 0.75,
        "entities": [
            {"type": "ORG", "name": "IMF", "description": "International Monetary Fund", "full_name": "International Monetary Fund"},
            {"type": "ORG", "name": "Ministry of Statistics", "description": "Indian government ministry for statistics", "full_name": "Ministry of Statistics and Programme Implementation"},
            {"type": "LOC", "name": "India", "latitude": 20.0, "longitude": 77.0, "location_type": "COUNTRY"},
        ],
    },
    {
        "id": 100021,
        "title": "Grammy 2026: Indian fusion artist Ricky Kej wins third Grammy",
        "text": "Bengaluru-based ambient artist Ricky Kej won his third Grammy at the 68th Grammy Awards in Los Angeles, in the Best New Age, Ambient or Chant Album category for 'Shanti Samsara II'.",
        "summary": "Ricky Kej wins third Grammy at 68th Grammy Awards for 'Shanti Samsara II'.",
        "url": "https://www.news18.com/entertainment/grammy-2026-ricky-kej-wins/",
        "image": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800&q=80", "width": 800, "height": 533, "title": "Grammy Awards stage"},
        ],
        "video": None, "publish_date": "2026-02-02 07:00:00",
        "author": "Entertainment Desk", "authors": ["Entertainment Desk", "News18"],
        "language": "en", "category": "entertainment", "source_country": "in", "sentiment": 0.84,
        "entities": [
            {"type": "PER", "name": "Ricky Kej", "description": "Indian Grammy-winning musician", "full_name": "Ricky Kej"},
            {"type": "ORG", "name": "Grammy Awards", "description": "Annual music industry awards", "full_name": "Recording Academy Grammy Awards"},
            {"type": "LOC", "name": "Los Angeles", "latitude": 34.05, "longitude": -118.24, "location_type": "CITY"},
            {"type": "LOC", "name": "Bengaluru", "latitude": 12.97, "longitude": 77.59, "location_type": "CITY"},
        ],
    },
    {
        "id": 100022,
        "title": "Ahmedabad metro Phase 2 inaugurated; 28 km stretch adds 4 new corridors",
        "text": "PM Modi inaugurated Phase 2 of the Ahmedabad Metro Rail Project, extending the network to 71 km. The 28 km extension covers the GIFT City corridor and connects Bopal to Motera Stadium.",
        "summary": "Ahmedabad Metro Phase 2 inaugurated; 28 km extension adds GIFT City corridor.",
        "url": "https://www.financialexpress.com/infrastructure/ahmedabad-metro-phase-2/",
        "image": "https://images.unsplash.com/photo-1474487548417-781cb71495f3?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1474487548417-781cb71495f3?w=800&q=80", "width": 800, "height": 533, "title": "Metro train"},
        ],
        "video": None, "publish_date": "2026-01-26 12:00:00",
        "author": "Infrastructure Desk", "authors": ["Infrastructure Desk"],
        "language": "en", "category": "general", "source_country": "in", "sentiment": 0.71,
        "entities": [
            {"type": "LOC", "name": "Ahmedabad", "latitude": 23.02, "longitude": 72.57, "location_type": "CITY"},
            {"type": "LOC", "name": "GIFT City", "latitude": 23.16, "longitude": 72.68, "location_type": "LANDMARK"},
            {"type": "ORG", "name": "Ahmedabad Metro Rail Corp", "description": "Metro operator", "full_name": "Ahmedabad Metro Rail Corporation"},
        ],
    },
    {
        "id": 100023,
        "title": "TCS, Infosys post record Q3 profits; IT sector adds 80,000 jobs in FY26",
        "text": "TCS reported Q3 net profit of ₹13,200 crore (+18% YoY) and Infosys ₹8,900 crore (+14% YoY). The Indian IT sector added 80,000 net jobs in FY26.",
        "summary": "TCS profit up 18%, Infosys up 14% in Q3; IT sector adds 80,000 jobs in FY26.",
        "url": "https://www.financialexpress.com/business/it/tcs-infosys-q3-results/",
        "image": "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800&q=80", "width": 800, "height": 533, "title": "IT company office"},
        ],
        "video": None, "publish_date": "2026-01-22 17:00:00",
        "author": "Tech Desk", "authors": ["Tech Desk"],
        "language": "en", "category": "technology", "source_country": "in", "sentiment": 0.67,
        "entities": [
            {"type": "ORG", "name": "TCS", "description": "Tata Consultancy Services", "full_name": "Tata Consultancy Services"},
            {"type": "ORG", "name": "Infosys", "description": "Indian multinational IT company", "full_name": "Infosys Limited"},
            {"type": "LOC", "name": "Bengaluru", "latitude": 12.97, "longitude": 77.59, "location_type": "CITY"},
        ],
    },
    {
        "id": 100024,
        "title": "Pune sees 40% rise in dengue cases; PMC launches emergency fogging drive",
        "text": "Pune Municipal Corporation reported 1,840 dengue cases in January, a 40% rise over last year. PMC has launched an emergency fogging drive across 15 wards and set up 30 ORS centres.",
        "summary": "Dengue cases up 40% in Pune; PMC launches fogging drive, 30 ORS centres opened.",
        "url": "https://www.news18.com/india/pune-dengue-surge-pmc/",
        "image": "https://images.unsplash.com/photo-1584036553516-bf83210aa16c?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1584036553516-bf83210aa16c?w=800&q=80", "width": 800, "height": 533, "title": "Public health"},
        ],
        "video": None, "publish_date": "2026-01-18 10:00:00",
        "author": "Health Desk", "authors": ["Health Desk"],
        "language": "en", "category": "health", "source_country": "in", "sentiment": -0.54,
        "entities": [
            {"type": "ORG", "name": "PMC", "description": "Pune Municipal Corporation", "full_name": "Pune Municipal Corporation"},
            {"type": "LOC", "name": "Pune", "latitude": 18.52, "longitude": 73.86, "location_type": "CITY"},
        ],
    },
    {
        "id": 100025,
        "title": "Kolkata bridge repairs cause 3-km traffic jam; commuters stranded 5 hours",
        "text": "Emergency repair works on Vidyasagar Setu forced closure of two lanes, creating a 3-km traffic jam on NH-12. Thousands of commuters were stranded for over 5 hours.",
        "summary": "Vidyasagar Setu repairs strand thousands in 5-hour Kolkata traffic jam.",
        "url": "https://www.thehindu.com/news/cities/kolkata/bridge-repair-traffic/",
        "image": "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=800&q=80", "width": 800, "height": 533, "title": "City bridge"},
        ],
        "video": None, "publish_date": "2026-01-30 09:00:00",
        "author": "City Desk", "authors": ["City Desk"],
        "language": "en", "category": "general", "source_country": "in", "sentiment": -0.38,
        "entities": [
            {"type": "LOC", "name": "Kolkata", "latitude": 22.57, "longitude": 88.36, "location_type": "CITY"},
            {"type": "LOC", "name": "Vidyasagar Setu", "latitude": 22.56, "longitude": 88.32, "location_type": "LANDMARK"},
        ],
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# EXTRACTED LINKS (matches extract_news_links bronze schema)
# ──────────────────────────────────────────────────────────────────────────────
EXTRACTED_LINKS = {
    "extracted_urls": [
        "https://economictimes.indiatimes.com/news/economy/finance/india-us-trade-deal-latest-updates",
        "https://www.thehindu.com/business/Economy/budget-2026-income-tax-highlights",
        "https://www.financialexpress.com/business/aviation/air-india-dgca-report",
        "https://www.news18.com/india/isro-gsat-20-satellite-broadband",
        "https://www.timesnownews.com/sports/cricket/ipl-2026-auction-full-list",
        "https://economictimes.indiatimes.com/news/economy/indicators/india-gdp-q2-fy26",
        "https://www.thehindu.com/sci-tech/science/chandrayaan-4-lunar-mission-update",
        "https://www.financialexpress.com/business/banking-finance/upi-record-18-billion",
        "https://www.latestly.com/agency-news/top-10-startups-india-2026",
    ],
    "count": 9,
    "ingestion_time": "2026-02-02T18:27:54.643508",
    "source": "world_news_api",
    "layer": "speed",
}

# ──────────────────────────────────────────────────────────────────────────────
# RSS FEED INFO (matches feed_rss bronze schema)
# ──────────────────────────────────────────────────────────────────────────────
RSS_FEED = {
    "source_url": "https://www.thehindu.com",
    "content_length": 51138,
    "preview": '<rss version="2.0"><channel><title>The Hindu: Latest News</title><link>https://www.thehindu.com</link><item><title>India-US trade deal confirmed, tariffs at 18%</title></item><item><title>Budget 2026: Tax exemption raised to Rs 12 lakh</title></item><item><title>ISRO GSAT-20 launch successful</title></item><item><title>Air India Boeing 787 grounded in Bengaluru</title></item></channel></rss>',
    "ingestion_time": "2026-02-02T18:27:54.422981",
    "layer": "speed",
    "source": "world_news_api",
}

# ──────────────────────────────────────────────────────────────────────────────
# SEARCH NEWS PAGINATION (matches search_news bronze schema)
# ──────────────────────────────────────────────────────────────────────────────
SEARCH_PAGINATION = {
    "offset": 0,
    "number": 25,
    "available": 4894,
}

# ──────────────────────────────────────────────────────────────────────────────
# GEO LOCATIONS
# ──────────────────────────────────────────────────────────────────────────────
GEO_LOCATIONS = [
    {"city": "Mumbai, Maharashtra",    "latitude": 19.0760, "longitude": 72.8777, "article_count": 14, "avg_sentiment":  0.15, "region": "Maharashtra",    "country": "India"},
    {"city": "New Delhi",              "latitude": 28.7041, "longitude": 77.1025, "article_count": 21, "avg_sentiment":  0.22, "region": "Delhi",          "country": "India"},
    {"city": "Bengaluru, Karnataka",   "latitude": 12.9628, "longitude": 77.5773, "article_count": 11, "avg_sentiment":  0.45, "region": "Karnataka",      "country": "India"},
    {"city": "Chennai, Tamil Nadu",    "latitude": 13.0827, "longitude": 80.2707, "article_count":  9, "avg_sentiment": -0.12, "region": "Tamil Nadu",     "country": "India"},
    {"city": "Hyderabad, Telangana",   "latitude": 17.3850, "longitude": 78.4867, "article_count":  8, "avg_sentiment":  0.38, "region": "Telangana",      "country": "India"},
    {"city": "Kolkata, West Bengal",   "latitude": 22.5726, "longitude": 88.3639, "article_count":  6, "avg_sentiment":  0.05, "region": "West Bengal",    "country": "India"},
    {"city": "Pune, Maharashtra",      "latitude": 18.5204, "longitude": 73.8567, "article_count":  5, "avg_sentiment":  0.28, "region": "Maharashtra",    "country": "India"},
    {"city": "Jaipur, Rajasthan",      "latitude": 26.9124, "longitude": 75.7873, "article_count":  4, "avg_sentiment": -0.25, "region": "Rajasthan",      "country": "India"},
    {"city": "Ahmedabad, Gujarat",     "latitude": 23.0225, "longitude": 72.5714, "article_count":  7, "avg_sentiment":  0.32, "region": "Gujarat",        "country": "India"},
    {"city": "Lucknow, Uttar Pradesh", "latitude": 26.8467, "longitude": 80.9462, "article_count":  4, "avg_sentiment":  0.10, "region": "Uttar Pradesh",  "country": "India"},
    {"city": "Bhopal, Madhya Pradesh", "latitude": 23.2599, "longitude": 77.4126, "article_count":  5, "avg_sentiment": -0.42, "region": "Madhya Pradesh", "country": "India"},
    {"city": "Srinagar, J&K",          "latitude": 34.0837, "longitude": 74.7973, "article_count":  3, "avg_sentiment": -0.18, "region": "J&K",            "country": "India"},
    {"city": "Kochi, Kerala",          "latitude":  9.9312, "longitude": 76.2673, "article_count":  4, "avg_sentiment":  0.35, "region": "Kerala",         "country": "India"},
    {"city": "Bhubaneswar, Odisha",    "latitude": 20.2961, "longitude": 85.8245, "article_count":  2, "avg_sentiment":  0.15, "region": "Odisha",         "country": "India"},
    {"city": "Chandigarh",             "latitude": 30.7333, "longitude": 76.7794, "article_count":  3, "avg_sentiment":  0.20, "region": "Punjab",         "country": "India"},
    {"city": "Patna, Bihar",           "latitude": 25.5941, "longitude": 85.1376, "article_count":  3, "avg_sentiment": -0.08, "region": "Bihar",          "country": "India"},
    {"city": "Imphal, Manipur",        "latitude": 24.8170, "longitude": 93.9368, "article_count":  4, "avg_sentiment": -0.65, "region": "Manipur",        "country": "India"},
    {"city": "Barmer, Rajasthan",      "latitude": 25.7470, "longitude": 71.3925, "article_count":  3, "avg_sentiment": -0.71, "region": "Rajasthan",      "country": "India"},
    {"city": "Sriharikota, AP",        "latitude": 13.7200, "longitude": 80.2300, "article_count":  2, "avg_sentiment":  0.82, "region": "Andhra Pradesh", "country": "India"},
    {"city": "Brussels",               "latitude": 50.8503, "longitude":  4.3517, "article_count":  2, "avg_sentiment":  0.68, "region": "Brussels Capital","country":"Belgium"},
    {"city": "London",                 "latitude": 51.5085, "longitude": -0.1257, "article_count":  2, "avg_sentiment": -0.10, "region": "England",        "country": "UK"},
]

# ──────────────────────────────────────────────────────────────────────────────
# TIME SERIES
# ──────────────────────────────────────────────────────────────────────────────
def _generate_time_series(days: int = 60):
    base = datetime.now()
    rows = []
    prev = 0.1
    for i in range(days, 0, -1):
        dt    = base - timedelta(days=i)
        delta = random.uniform(-0.12, 0.12)
        val   = max(-0.9, min(0.9, prev + delta))
        prev  = val
        total = random.randint(20, 90)
        pos   = max(0, int(total * (0.4 + val * 0.2)))
        neg   = max(0, int(total * (0.25 - val * 0.1)))
        neu   = max(0, total - pos - neg)
        rows.append({
            "date":          dt.strftime("%Y-%m-%d"),
            "avg_sentiment": round(val, 3),
            "article_count": total,
            "positive":      pos,
            "negative":      neg,
            "neutral":       neu,
        })
    return rows

TIME_SERIES = _generate_time_series(60)

# ──────────────────────────────────────────────────────────────────────────────
# AGGREGATES
# ──────────────────────────────────────────────────────────────────────────────
CATEGORY_BREAKDOWN = {
    "politics": 28, "business": 24, "technology": 19, "general": 22,
    "health": 12,  "sports": 15,   "entertainment": 9, "lifestyle": 6,
}

METRICS_SUMMARY = {
    "total_articles":    847,
    "avg_sentiment":     0.18,
    "positive_pct":      52.3,
    "negative_pct":      28.1,
    "neutral_pct":       19.6,
    "articles_today":    43,
    "trending_category": "politics",
    "top_source":        "The Hindu",
    "pipeline_health":   "operational",
    "kafka_lag":         0,
    "minio_objects":     1284,
    "bronze_objects":    624,
    "silver_objects":    420,
    "gold_objects":      240,
    "last_ingestion":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "kafka_throughput":  "142 msg/min",
    "api_latency_ms":    87,
    "flink_jobs_active": 3,
    "search_available":  SEARCH_PAGINATION["available"],
    "search_offset":     SEARCH_PAGINATION["offset"],
    "search_number":     SEARCH_PAGINATION["number"],
}

# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────
def get_articles(limit=50, category=None, sentiment_min=-1.0, sentiment_max=1.0):
    arts = ARTICLES.copy()
    if category and category not in ("all","All",""):
        arts = [a for a in arts if a.get("category","") == category]
    arts = [a for a in arts if sentiment_min <= a.get("sentiment",0) <= sentiment_max]
    return arts[:limit]

def get_geo_data():           return GEO_LOCATIONS
def get_top_news(limit=10):   return sorted(ARTICLES, key=lambda x: abs(x.get("sentiment",0)), reverse=True)[:limit]
def get_time_series():        return TIME_SERIES
def get_metrics():            return METRICS_SUMMARY
def get_category_breakdown(): return CATEGORY_BREAKDOWN
def get_rss_feed():           return RSS_FEED
def get_extracted_links():    return EXTRACTED_LINKS
def get_search_pagination():  return SEARCH_PAGINATION

def get_article_by_id(article_id):
    for a in ARTICLES:
        if str(a.get("id")) == str(article_id):
            return a
    return ARTICLES[0] if ARTICLES else {}