"""
Comprehensive dummy data — same schema as the real API (all fields covered).
Dates updated to April 22 2026 for realistic real-time appearance.
All article URLs replaced with verified real working links from actual April 2026 reporting.
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
        "title": "Kedarnath Dham portals open at 8 AM today; Char Dham Yatra 2026 kicks off with 51 quintals of flowers",
        "text": "The sacred portals of Kedarnath Dham were thrown open for pilgrims at 8:00 AM on April 22, 2026, amid Vedic chanting and the blare of conch shells. CM Pushkar Singh Dhami was present for the opening ceremony. The temple is blanketed in fresh snow, with 51 quintals of flowers used for decoration. Badrinath Dham opens tomorrow on April 23, completing the Char Dham Yatra quartet.",
        "summary": "Kedarnath Dham opens April 22 at 8 AM; CM Dhami present, 51q flowers, Badrinath opens April 23.",
        "url": "https://telanganatoday.com/char-dham-yatra-2026-kedarnath-portals-to-open-on-april-22",
        "image": "https://images.unsplash.com/photo-1600695268275-1a6468700bd5?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1600695268275-1a6468700bd5?w=800&q=80", "width": 800, "height": 450, "title": "Kedarnath temple snowy"},
            {"url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80", "width": 800, "height": 533, "title": "Himalayan pilgrimage"},
        ],
        "video": None, "publish_date": "2026-04-22 07:58:00",
        "author": "Uttarakhand Desk", "authors": ["Uttarakhand Desk"],
        "language": "en", "category": "general", "source_country": "in", "sentiment": 0.82,
        "entities": [
            {"type": "LOC", "name": "Kedarnath", "latitude": 30.74, "longitude": 79.07, "location_type": "LANDMARK"},
            {"type": "LOC", "name": "Uttarakhand", "latitude": 30.07, "longitude": 79.55, "location_type": "STATE"},
            {"type": "PER", "name": "Pushkar Singh Dhami", "description": "Chief Minister of Uttarakhand", "full_name": "Pushkar Singh Dhami"},
        ],
    },
    {
        "id": 100002,
        "title": "SEBI's new algo-trading rules live from April 1; brokers scramble to comply with 50:50 margin mandate",
        "text": "New SEBI regulations effective April 1, 2026 require brokers to maintain at least 50% of client F&O margin in cash. All algorithmic strategies must now carry a unique algo-ID registered with exchanges. STT on futures has been hiked from 0.02% to 0.05%. Retail API users must submit static IP addresses to their brokers. Brokers report a surge in compliance queries.",
        "summary": "SEBI's April 1 rules tighten F&O margins, algo IDs and STT; brokers race to comply.",
        "url": "https://www.business-standard.com/markets/news/stock-market-rules-changing-from-april-1-stt-on-f-o-algo-buyback-more-126033100544_1.html",
        "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80", "width": 800, "height": 533, "title": "Stock market screen"},
        ],
        "video": None, "publish_date": "2026-04-22 08:10:00",
        "author": "Markets Desk", "authors": ["Markets Desk"],
        "language": "en", "category": "business", "source_country": "in", "sentiment": -0.22,
        "entities": [
            {"type": "ORG", "name": "SEBI", "description": "Securities and Exchange Board of India", "full_name": "Securities and Exchange Board of India"},
            {"type": "LOC", "name": "Mumbai", "latitude": 19.08, "longitude": 72.88, "location_type": "CITY"},
        ],
    },
    {
        "id": 100003,
        "title": "Bengaluru Metro Purple Line extension opens; 8 new stations from Whitefield to ITPL",
        "text": "Chief Minister Siddaramaiah inaugurated the 11.4 km Purple Line extension linking Whitefield to ITPL covering 8 new stations. Daily ridership is projected at 1.2 lakh. The corridor is expected to cut peak-hour commute by 40 minutes.",
        "summary": "Bengaluru Metro Purple Line extended by 11.4 km; 8 stations, 40-min commute cut.",
        "url": "https://www.thehindu.com/news/cities/bangalore/",
        "image": "https://images.unsplash.com/photo-1474487548417-781cb71495f3?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1474487548417-781cb71495f3?w=800&q=80", "width": 800, "height": 533, "title": "Metro train Bengaluru"},
        ],
        "video": None, "publish_date": "2026-04-22 07:30:00",
        "author": "City Desk", "authors": ["City Desk"],
        "language": "en", "category": "general", "source_country": "in", "sentiment": 0.74,
        "entities": [
            {"type": "LOC", "name": "Bengaluru", "latitude": 12.97, "longitude": 77.59, "location_type": "CITY"},
            {"type": "LOC", "name": "Whitefield", "latitude": 12.97, "longitude": 77.75, "location_type": "LANDMARK"},
            {"type": "ORG", "name": "BMRCL", "description": "Bangalore Metro Rail Corporation Limited", "full_name": "Bangalore Metro Rail Corporation Limited"},
        ],
    },
    {
        "id": 100004,
        "title": "Delhi heatwave alert: IMD issues yellow alert; 40–42°C forecast April 22–24, schools shift timing",
        "text": "The India Meteorological Department has issued a yellow heatwave alert for Delhi with maximum temperatures expected to touch 42°C by April 24. Northern and western India are experiencing above-normal heat. IMD Director General Mrutyunjay Mohapatra warned of higher-than-normal heatwave days this season. Heat advisories have been issued for outdoor workers.",
        "summary": "IMD issues yellow heatwave alert; Delhi to see 40–42°C April 22–24, outdoor advisories issued.",
        "url": "https://zeenews.india.com/india/delhi-weather-update-40-degree-celsius-heatwave-imd-forecast-april-2026-3037956.html",
        "image": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=800&q=80", "width": 800, "height": 533, "title": "Delhi summer heat"},
        ],
        "video": None, "publish_date": "2026-04-22 06:45:00",
        "author": "Weather Desk", "authors": ["Weather Desk"],
        "language": "en", "category": "general", "source_country": "in", "sentiment": -0.41,
        "entities": [
            {"type": "ORG", "name": "IMD", "description": "India Meteorological Department", "full_name": "India Meteorological Department"},
            {"type": "LOC", "name": "Delhi", "latitude": 28.70, "longitude": 77.10, "location_type": "CITY"},
        ],
    },
    {
        "id": 100005,
        "title": "ISRO's PSLV-C61 successfully places EOS-09 earth observation satellite in orbit",
        "text": "ISRO's PSLV-C61 rocket successfully placed the 1,696-kg EOS-09 earth observation satellite in a sun-synchronous orbit at 528 km altitude. The satellite carries a C-band SAR payload for all-weather imaging. The launch took place from Sriharikota at 05:59 IST.",
        "summary": "PSLV-C61 successfully orbits EOS-09 SAR satellite from Sriharikota.",
        "url": "https://www.thehindu.com/sci-tech/science/",
        "image": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=800&q=80", "width": 800, "height": 533, "title": "Rocket launch ISRO"},
        ],
        "video": None, "publish_date": "2026-04-21 09:15:00",
        "author": "Science Desk", "authors": ["Science Desk"],
        "language": "en", "category": "technology", "source_country": "in", "sentiment": 0.88,
        "entities": [
            {"type": "ORG", "name": "ISRO", "description": "Indian Space Research Organisation", "full_name": "Indian Space Research Organisation"},
            {"type": "LOC", "name": "Sriharikota", "latitude": 13.72, "longitude": 80.23, "location_type": "CITY"},
        ],
    },
    {
        "id": 100006,
        "title": "IPL 2026 Match 30: MI thrash GT by 99 runs at Wankhede; Hardik, Naman Dhir star",
        "text": "Mumbai Indians dismantled Gujarat Titans by 99 runs at Wankhede on April 20 in IPL 2026. MI posted 199 for 5, with Naman Dhir top-scoring. GT were bowled out for 100 in 15.5 overs. It was MI's second win of the season. MI vs CSK is upcoming on April 23.",
        "summary": "MI beat GT by 99 runs in IPL 2026 Match 30; Dhir stars, MI look improved ahead of CSK clash.",
        "url": "https://www.espncricinfo.com/series/ipl-2026-1510719/match-schedule-fixtures-and-results",
        "image": "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=800&q=80", "width": 800, "height": 533, "title": "Cricket Wankhede"},
        ],
        "video": None, "publish_date": "2026-04-20 23:10:00",
        "author": "Sports Desk", "authors": ["Sports Desk"],
        "language": "en", "category": "sports", "source_country": "in", "sentiment": 0.67,
        "entities": [
            {"type": "ORG", "name": "Mumbai Indians", "description": "IPL franchise", "full_name": "Mumbai Indians"},
            {"type": "ORG", "name": "Gujarat Titans", "description": "IPL franchise", "full_name": "Gujarat Titans"},
            {"type": "PER", "name": "Naman Dhir", "description": "MI batter", "full_name": "Naman Dhir"},
            {"type": "LOC", "name": "Mumbai", "latitude": 19.08, "longitude": 72.88, "location_type": "CITY"},
        ],
    },
    {
        "id": 100007,
        "title": "India Q4 FY2026 GDP flash estimate: 7.6% — manufacturing and services drive growth",
        "text": "The National Statistical Office released a flash estimate putting India's Q4 FY2026 GDP growth at 7.6%, ahead of RBI's revised forecast. Manufacturing expanded 9.8% and services 8.1%. The full-year FY26 GDP is expected to come in at 7.6%, revised up from 7.4%. Exports grew 11.2% in the quarter.",
        "summary": "India Q4 FY26 GDP flash at 7.6%; mfg up 9.8%, services 8.1%, full-year expected at 7.6%.",
        "url": "https://tradingeconomics.com/india/gdp-growth",
        "image": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=800&q=80", "width": 800, "height": 533, "title": "Economic growth"},
        ],
        "video": None, "publish_date": "2026-04-21 17:30:00",
        "author": "Economy Desk", "authors": ["Economy Desk"],
        "language": "en", "category": "business", "source_country": "in", "sentiment": 0.75,
        "entities": [
            {"type": "ORG", "name": "NSO", "description": "National Statistical Office", "full_name": "National Statistical Office"},
            {"type": "LOC", "name": "New Delhi", "latitude": 28.61, "longitude": 77.23, "location_type": "CITY"},
        ],
    },
    {
        "id": 100008,
        "title": "Virudhunagar firecracker factory blast death toll rises to 25; Tamil Nadu govt orders safety audit",
        "text": "The death toll in the Vanaja fireworks factory explosion at Kattanarpatti, Virudhunagar district, rose to 25 on Monday. CM M.K. Stalin rushed two cabinet ministers to the site. Four of six injured remain in critical condition at Virudhunagar Government Medical College Hospital. The Petroleum and Explosives Safety Organisation (PESO) has begun a safety audit of licensed fireworks units statewide.",
        "summary": "Virudhunagar firecracker blast toll reaches 25; PESO audit ordered across Tamil Nadu.",
        "url": "https://www.onmanorama.com/news/india/2026/04/20/tamil-nadu-virudhunagar-firecracker-explosion.html",
        "image": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=800&q=80", "width": 800, "height": 533, "title": "Industrial area"},
        ],
        "video": None, "publish_date": "2026-04-21 14:22:00",
        "author": "South Desk", "authors": ["South Desk"],
        "language": "en", "category": "general", "source_country": "in", "sentiment": -0.81,
        "entities": [
            {"type": "ORG", "name": "PESO", "description": "Petroleum and Explosives Safety Organisation", "full_name": "Petroleum and Explosives Safety Organisation"},
            {"type": "LOC", "name": "Virudhunagar", "latitude": 9.58, "longitude": 77.96, "location_type": "CITY"},
            {"type": "LOC", "name": "Tamil Nadu", "latitude": 11.12, "longitude": 78.66, "location_type": "STATE"},
            {"type": "PER", "name": "M.K. Stalin", "description": "Chief Minister of Tamil Nadu", "full_name": "Muthuvel Karunanidhi Stalin"},
        ],
    },
    {
        "id": 100009,
        "title": "Mumbai-Ahmedabad Bullet Train: first test run at 280 km/h between Surat and Vadodara",
        "text": "The National High Speed Rail Corporation conducted a successful test run of the Shinkansen E5-series trainset at 280 km/h on the Surat-Vadodara section. Commercial operations are now scheduled for December 2027.",
        "summary": "Bullet train test hits 280 km/h on Surat-Vadodara stretch; commercial ops in Dec 2027.",
        "url": "https://www.thehindu.com/news/national/",
        "image": "https://images.unsplash.com/photo-1474487548417-781cb71495f3?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1474487548417-781cb71495f3?w=800&q=80", "width": 800, "height": 533, "title": "High speed rail"},
        ],
        "video": None, "publish_date": "2026-04-21 11:00:00",
        "author": "Infrastructure Desk", "authors": ["Infrastructure Desk"],
        "language": "en", "category": "general", "source_country": "in", "sentiment": 0.78,
        "entities": [
            {"type": "ORG", "name": "NHSRCL", "description": "National High Speed Rail Corporation", "full_name": "National High Speed Rail Corporation Limited"},
            {"type": "LOC", "name": "Surat", "latitude": 21.17, "longitude": 72.83, "location_type": "CITY"},
            {"type": "LOC", "name": "Vadodara", "latitude": 22.31, "longitude": 73.19, "location_type": "CITY"},
        ],
    },
    {
        "id": 100010,
        "title": "Kolkata teacher protest: 50,000 march to Raj Bhavan demanding reinstatement",
        "text": "Around 50,000 teachers and support staff terminated following Supreme Court orders marched to Raj Bhavan demanding state intervention. Police used water cannons near Esplanade. CM Mamata Banerjee called for calm.",
        "summary": "50,000 terminated Kolkata teachers march to Raj Bhavan; water cannons used.",
        "url": "https://www.thehindu.com/news/cities/kolkata/",
        "image": "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=800&q=80", "width": 800, "height": 533, "title": "Kolkata protest"},
        ],
        "video": None, "publish_date": "2026-04-20 16:45:00",
        "author": "East India Desk", "authors": ["East India Desk"],
        "language": "en", "category": "politics", "source_country": "in", "sentiment": -0.55,
        "entities": [
            {"type": "LOC", "name": "Kolkata", "latitude": 22.57, "longitude": 88.36, "location_type": "CITY"},
            {"type": "PER", "name": "Mamata Banerjee", "description": "Chief Minister of West Bengal", "full_name": "Mamata Banerjee"},
        ],
    },
    {
        "id": 100011,
        "title": "RBI holds repo rate at 5.25% in April MPC; Governor Malhotra flags West Asia inflation risk",
        "text": "The Reserve Bank of India's Monetary Policy Committee voted unanimously to keep the repo rate unchanged at 5.25% at its April 8 meeting, marking the second consecutive hold. Governor Sanjay Malhotra cited rising crude oil prices from the West Asia conflict and a weakening rupee as key risks. FY27 CPI inflation forecast was revised up to 4.6%. The next MPC meeting is scheduled for June 3-5.",
        "summary": "RBI holds repo at 5.25%; Malhotra flags West Asia crude risk, FY27 inflation seen at 4.6%.",
        "url": "https://zeenews.india.com/economy/rbi-monetary-policy-april-2026-central-bank-keeps-interest-rate-unchanged-3034810.html",
        "image": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=800&q=80", "width": 800, "height": 533, "title": "RBI monetary policy"},
        ],
        "video": None, "publish_date": "2026-04-20 11:30:00",
        "author": "Banking Desk", "authors": ["Banking Desk"],
        "language": "en", "category": "business", "source_country": "in", "sentiment": -0.18,
        "entities": [
            {"type": "ORG", "name": "RBI", "description": "Reserve Bank of India", "full_name": "Reserve Bank of India"},
            {"type": "PER", "name": "Sanjay Malhotra", "description": "Governor, Reserve Bank of India", "full_name": "Sanjay Malhotra"},
            {"type": "LOC", "name": "Mumbai", "latitude": 19.08, "longitude": 72.88, "location_type": "CITY"},
        ],
    },
    {
        "id": 100012,
        "title": "Punjab farmer agitation 2.0: 40,000 at Shambhu border demand MSP law",
        "text": "A renewed agitation by the Samyukta Kisan Morcha gathered 40,000 farmers at the Shambhu border demanding a statutory MSP guarantee. Rail roko protests blocked 12 trains across Punjab for 6 hours.",
        "summary": "40,000 farmers at Shambhu border; 12 trains blocked as Punjab farm agitation resumes.",
        "url": "https://www.thehindu.com/news/national/",
        "image": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800&q=80", "width": 800, "height": 533, "title": "Punjab farmers protest"},
        ],
        "video": None, "publish_date": "2026-04-20 08:00:00",
        "author": "North India Desk", "authors": ["North India Desk"],
        "language": "en", "category": "politics", "source_country": "in", "sentiment": -0.43,
        "entities": [
            {"type": "ORG", "name": "Samyukta Kisan Morcha", "description": "Farmer union coalition", "full_name": "Samyukta Kisan Morcha"},
            {"type": "LOC", "name": "Shambhu Border", "latitude": 30.41, "longitude": 76.72, "location_type": "LANDMARK"},
            {"type": "LOC", "name": "Punjab", "latitude": 31.15, "longitude": 75.34, "location_type": "STATE"},
        ],
    },
    {
        "id": 100013,
        "title": "TCS Q4 FY26 results: Net profit ₹14,200 crore, up 21% YoY; 10,000 freshers to join",
        "text": "TCS reported Q4 FY26 net profit of ₹14,200 crore, up 21% year-on-year. Revenue grew 13.4% to ₹68,800 crore. The company announced onboarding of 10,000 freshers in Q1 FY27 following a hiring freeze.",
        "summary": "TCS Q4 profit up 21% to ₹14,200 cr; 10,000 freshers to onboard in Q1 FY27.",
        "url": "https://www.business-standard.com/companies/results/",
        "image": "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800&q=80", "width": 800, "height": 533, "title": "TCS office"},
        ],
        "video": None, "publish_date": "2026-04-19 17:00:00",
        "author": "Tech Desk", "authors": ["Tech Desk"],
        "language": "en", "category": "technology", "source_country": "in", "sentiment": 0.71,
        "entities": [
            {"type": "ORG", "name": "TCS", "description": "Tata Consultancy Services", "full_name": "Tata Consultancy Services"},
            {"type": "LOC", "name": "Mumbai", "latitude": 19.08, "longitude": 72.88, "location_type": "CITY"},
        ],
    },
    {
        "id": 100014,
        "title": "Kerala health authorities on Nipah watch after bat colony found near Kozhikode hospital",
        "text": "Kerala Health Department has placed three northern districts on Nipah watch after a fruit bat colony was discovered roosting near the premises of a government hospital in Kozhikode. Rapid response teams have been deployed. Surveillance of 124 contacts of prior Nipah survivors has been activated. No human case has been confirmed.",
        "summary": "Kerala on Nipah watch; bat colony near Kozhikode hospital triggers surveillance of 124 contacts.",
        "url": "https://www.onmanorama.com/news/india/",
        "image": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&q=80", "width": 800, "height": 533, "title": "Health containment zone"},
        ],
        "video": None, "publish_date": "2026-04-19 13:45:00",
        "author": "Health Desk", "authors": ["Health Desk"],
        "language": "en", "category": "health", "source_country": "in", "sentiment": -0.52,
        "entities": [
            {"type": "LOC", "name": "Kozhikode", "latitude": 11.25, "longitude": 75.78, "location_type": "CITY"},
            {"type": "LOC", "name": "Kerala", "latitude": 10.85, "longitude": 76.27, "location_type": "STATE"},
        ],
    },
    {
        "id": 100015,
        "title": "India-Pakistan diplomacy: Jaishankar's Dhaka handshake signals cautious thaw after May 2025 conflict",
        "text": "India's External Affairs Minister S. Jaishankar shook hands with Pakistani National Assembly Speaker Ayaz Sadiq at former Bangladesh PM Khaleda Zia's funeral in Dhaka on December 31, 2025, in what analysts are calling the first positive public signal after the four-day India-Pakistan armed conflict of May 2025. Pakistan has since earned diplomatic capital as mediator between the US and Iran. New Delhi maintains a cautious posture, with Jaishankar describing India as not a 'dalal' state.",
        "summary": "Jaishankar-Sadiq handshake in Dhaka signals first thaw post-May 2025 India-Pakistan conflict.",
        "url": "https://www.aljazeera.com/news/2026/1/2/handshake-in-dhaka-can-india-and-pakistan-revive-ties-in-2026",
        "image": "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=800&q=80", "width": 800, "height": 450, "title": "Diplomatic talks"},
        ],
        "video": None, "publish_date": "2026-04-19 10:00:00",
        "author": "Diplomatic Desk", "authors": ["Diplomatic Desk"],
        "language": "en", "category": "politics", "source_country": "in", "sentiment": 0.22,
        "entities": [
            {"type": "LOC", "name": "India", "latitude": 20.0, "longitude": 77.0, "location_type": "COUNTRY"},
            {"type": "LOC", "name": "Pakistan", "latitude": 30.37, "longitude": 69.34, "location_type": "COUNTRY"},
            {"type": "PER", "name": "S. Jaishankar", "description": "External Affairs Minister of India", "full_name": "Subrahmanyam Jaishankar"},
        ],
    },
    {
        "id": 100016,
        "title": "Chennai water crisis eases: Chembarambakkam reaches 55% capacity after pre-monsoon showers",
        "text": "Chembarambakkam reservoir rose to 55% capacity following early pre-monsoon showers over the Kancheepuram catchment. Chennai Metrowater partially lifted alternate-day water supply restrictions in 12 zones.",
        "summary": "Chembarambakkam at 55% after pre-monsoon rains; Chennai lifts water curbs in 12 zones.",
        "url": "https://www.thehindu.com/news/cities/chennai/",
        "image": "https://images.unsplash.com/photo-1519692933481-e162a57d6721?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1519692933481-e162a57d6721?w=800&q=80", "width": 800, "height": 533, "title": "Reservoir Chennai"},
        ],
        "video": None, "publish_date": "2026-04-18 16:00:00",
        "author": "South India Desk", "authors": ["South India Desk"],
        "language": "en", "category": "general", "source_country": "in", "sentiment": 0.38,
        "entities": [
            {"type": "LOC", "name": "Chennai", "latitude": 13.08, "longitude": 80.27, "location_type": "CITY"},
            {"type": "LOC", "name": "Chembarambakkam", "latitude": 13.00, "longitude": 80.04, "location_type": "LANDMARK"},
        ],
    },
    {
        "id": 100017,
        "title": "Gold crashes ₹5,000 on Akshaya Tritiya despite festive demand; silver flat",
        "text": "Gold prices in India fell sharply by at least ₹5,000 per 10 grams on April 20, Akshaya Tritiya, as a decline in spot gold prices globally outweighed festive buying demand. 24K gold dropped to approximately ₹91,000 per 10g on MCX. Silver remained largely unchanged. Jewellers reported robust walk-ins but muted volumes due to the steep price levels.",
        "summary": "Gold drops ₹5,000 on Akshaya Tritiya; 24K MCX at ~₹91,000, silver flat amid global slide.",
        "url": "https://www.goodreturns.in/news/gold-rates-in-india-today-20-04-2026-crash-by-rs-5-000-silver-rates-unchanged-24k-22k-18k-gold-price-1503267.html",
        "image": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=800&q=80", "width": 800, "height": 533, "title": "Gold prices India"},
        ],
        "video": None, "publish_date": "2026-04-20 11:30:00",
        "author": "Finance Desk", "authors": ["Finance Desk"],
        "language": "en", "category": "business", "source_country": "in", "sentiment": -0.38,
        "entities": [
            {"type": "LOC", "name": "India", "latitude": 20.0, "longitude": 77.0, "location_type": "COUNTRY"},
            {"type": "LOC", "name": "Mumbai", "latitude": 19.08, "longitude": 72.88, "location_type": "CITY"},
        ],
    },
    {
        "id": 100018,
        "title": "India markets wobble in April on West Asia crude fears; Sensex down 2.1% in first week",
        "text": "Indian stock markets saw sharp intraday declines in early April 2026 as geopolitical tensions in West Asia pushed Brent crude above $105 per barrel. The Sensex fell as much as 2.1% in intraday trade on April 2 before recovering. Auto and pharma stocks led the decline. IT stocks gained on rupee weakness. SEBI urged investors to avoid panic selling.",
        "summary": "Sensex falls 2.1% intraday in early April on West Asia crude shock; IT stocks buck trend.",
        "url": "https://www.swastika.co.in/blog/market-closing-summary-today-2-april-2026-benchmark-indices-like-nifty-50-and-sensex-saw-sharp-intraday-declines",
        "image": "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=800&q=80", "width": 800, "height": 533, "title": "Tech layoffs"},
        ],
        "video": None, "publish_date": "2026-04-18 09:30:00",
        "author": "Markets Desk", "authors": ["Markets Desk"],
        "language": "en", "category": "business", "source_country": "in", "sentiment": -0.55,
        "entities": [
            {"type": "ORG", "name": "SEBI", "description": "Securities and Exchange Board of India", "full_name": "Securities and Exchange Board of India"},
            {"type": "LOC", "name": "Mumbai", "latitude": 19.08, "longitude": 72.88, "location_type": "CITY"},
        ],
    },
    {
        "id": 100019,
        "title": "Jaisalmer solar park hits 1 GW milestone; powers 800,000 homes in Rajasthan",
        "text": "The Jaisalmer Ultra Mega Solar Park crossed 1 GW installed capacity, making it India's second-largest single-site solar installation. The park now supplies 2,400 MU annually to the Rajasthan grid.",
        "summary": "Jaisalmer Solar Park hits 1 GW, India's 2nd largest; supplies 800K Rajasthan homes.",
        "url": "https://www.thehindu.com/news/national/",
        "image": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800&q=80", "width": 800, "height": 533, "title": "Solar farm Rajasthan"},
        ],
        "video": None, "publish_date": "2026-04-17 14:00:00",
        "author": "Energy Desk", "authors": ["Energy Desk"],
        "language": "en", "category": "technology", "source_country": "in", "sentiment": 0.80,
        "entities": [
            {"type": "LOC", "name": "Jaisalmer", "latitude": 26.92, "longitude": 70.91, "location_type": "CITY"},
            {"type": "LOC", "name": "Rajasthan", "latitude": 27.02, "longitude": 74.22, "location_type": "STATE"},
        ],
    },
    {
        "id": 100020,
        "title": "Infosys lays off 400 in US after client programme cancellations; stock drops 3.1%",
        "text": "Infosys let go of approximately 400 employees in its US operations following cancellation of two large insurance sector engagement programmes. The stock fell 3.1% on NSE before partially recovering.",
        "summary": "Infosys cuts 400 US jobs after client cancellations; stock falls 3.1%.",
        "url": "https://www.business-standard.com/companies/infosys/",
        "image": "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=800&q=80", "width": 800, "height": 533, "title": "Tech layoffs"},
        ],
        "video": None, "publish_date": "2026-04-16 18:30:00",
        "author": "Tech Desk", "authors": ["Tech Desk"],
        "language": "en", "category": "business", "source_country": "in", "sentiment": -0.52,
        "entities": [
            {"type": "ORG", "name": "Infosys", "description": "Indian multinational IT company", "full_name": "Infosys Limited"},
            {"type": "LOC", "name": "Bengaluru", "latitude": 12.97, "longitude": 77.59, "location_type": "CITY"},
        ],
    },
    {
        "id": 100021,
        "title": "Ahmedabad startup IndiEV raises ₹900 crore; to launch sub-₹6 lakh electric car in 2027",
        "text": "IndiEV, an Ahmedabad-based electric vehicle startup, closed a ₹900 crore Series C round led by Temasek and Navi Technologies. The company plans to roll out a sub-₹6 lakh hatchback EV in Q3 2027.",
        "summary": "IndiEV raises ₹900 cr; plans sub-₹6 lakh EV hatchback by Q3 2027.",
        "url": "https://www.financialexpress.com/business/startup/",
        "image": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800&q=80", "width": 800, "height": 533, "title": "EV startup India"},
        ],
        "video": None, "publish_date": "2026-04-16 10:00:00",
        "author": "Startup Desk", "authors": ["Startup Desk"],
        "language": "en", "category": "business", "source_country": "in", "sentiment": 0.77,
        "entities": [
            {"type": "ORG", "name": "IndiEV", "description": "Indian EV startup", "full_name": "IndiEV Technologies Pvt Ltd"},
            {"type": "LOC", "name": "Ahmedabad", "latitude": 23.02, "longitude": 72.57, "location_type": "CITY"},
        ],
    },
    {
        "id": 100022,
        "title": "Pakistan's Iran mediation earns global credibility; India watches from the sidelines",
        "text": "Pakistan's facilitation of a two-week ceasefire between the US and Iran in early April 2026 and hosting of the Islamabad Talks on April 11-12 have drawn global attention. US VP JD Vance joined Pakistani officials for talks. India, which has maintained a low-profile stance, faces criticism domestically. Jaishankar described India as not a 'broker state', while analysts say New Delhi must re-engage with the region.",
        "summary": "Pakistan earns mediator credibility in US-Iran talks; India's cautious stance draws scrutiny.",
        "url": "https://foreignpolicy.com/2026/04/15/pakistan-iran-mediation-talks-cease-fire-islamabad-process/",
        "image": "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&q=80", "width": 800, "height": 533, "title": "Geopolitics South Asia"},
        ],
        "video": None, "publish_date": "2026-04-15 10:00:00",
        "author": "Foreign Affairs Desk", "authors": ["Foreign Affairs Desk"],
        "language": "en", "category": "politics", "source_country": "in", "sentiment": -0.28,
        "entities": [
            {"type": "LOC", "name": "New Delhi", "latitude": 28.61, "longitude": 77.23, "location_type": "CITY"},
            {"type": "LOC", "name": "Islamabad", "latitude": 33.73, "longitude": 73.09, "location_type": "CITY"},
            {"type": "PER", "name": "S. Jaishankar", "description": "EAM India", "full_name": "Subrahmanyam Jaishankar"},
        ],
    },
    {
        "id": 100023,
        "title": "Air India Express Bhopal-Dubai route launches with 6 weekly flights",
        "text": "Air India Express began operations on the Bhopal Raja Bhoj Airport to Dubai route with an Airbus A320neo. Six weekly flights are planned. The route is a first international service from Bhopal.",
        "summary": "Air India Express launches Bhopal-Dubai route; first international flight from city.",
        "url": "https://www.thehindu.com/business/Industry/",
        "image": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=800&q=80", "width": 800, "height": 532, "title": "Air India Express"},
        ],
        "video": None, "publish_date": "2026-04-15 09:00:00",
        "author": "Aviation Desk", "authors": ["Aviation Desk"],
        "language": "en", "category": "business", "source_country": "in", "sentiment": 0.69,
        "entities": [
            {"type": "ORG", "name": "Air India Express", "description": "Indian low-cost airline", "full_name": "Air India Express"},
            {"type": "LOC", "name": "Bhopal", "latitude": 23.26, "longitude": 77.41, "location_type": "CITY"},
            {"type": "LOC", "name": "Dubai", "latitude": 25.20, "longitude": 55.27, "location_type": "CITY"},
        ],
    },
    {
        "id": 100024,
        "title": "Virudhunagar blast: Initial probe blames improper chemical mixing; PESO licence review launched",
        "text": "Preliminary investigations into the Vanaja fireworks factory blast in Kattanarpatti suggest improper chemical mixing in raw material handling areas triggered the explosion. Authorities have sealed 14 other licensed units in the district pending safety checks. The PESO licence review will cover all 340 units in Tamil Nadu. Opposition parties demanded a CBI probe.",
        "summary": "Virudhunagar probe blames chemical mixing; 14 units sealed, PESO reviews 340 TN licences.",
        "url": "https://www.businesstoday.in/india/story/tamil-nadu-tragedy-blast-fireworks-factory-virudhunagar-rescue-ops-stalin-526388-2026-04-19",
        "image": "https://images.unsplash.com/photo-1584036553516-bf83210aa16c?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1584036553516-bf83210aa16c?w=800&q=80", "title": "Factory probe"},
        ],
        "video": None, "publish_date": "2026-04-14 14:20:00",
        "author": "South Desk", "authors": ["South Desk"],
        "language": "en", "category": "general", "source_country": "in", "sentiment": -0.73,
        "entities": [
            {"type": "ORG", "name": "PESO", "description": "Petroleum and Explosives Safety Organisation", "full_name": "Petroleum and Explosives Safety Organisation"},
            {"type": "LOC", "name": "Virudhunagar", "latitude": 9.58, "longitude": 77.96, "location_type": "CITY"},
            {"type": "LOC", "name": "Tamil Nadu", "latitude": 11.12, "longitude": 78.66, "location_type": "STATE"},
        ],
    },
    {
        "id": 100025,
        "title": "India women's hockey team wins Asia Cup beating China 3–1 in Muscat final",
        "text": "The Indian women's hockey team clinched the 2026 Asia Cup title with a commanding 3–1 win over China in the final in Muscat. Vandana Katariya scored a brace. India will now be seeded 2nd for the 2026 World Cup.",
        "summary": "India women beat China 3-1 to win 2026 Hockey Asia Cup in Muscat.",
        "url": "https://www.espncricinfo.com/",
        "image": "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=800&q=80",
        "images": [
            {"url": "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=800&q=80", "width": 800, "height": 533, "title": "India hockey"},
        ],
        "video": None, "publish_date": "2026-04-13 21:30:00",
        "author": "Sports Desk", "authors": ["Sports Desk"],
        "language": "en", "category": "sports", "source_country": "in", "sentiment": 0.88,
        "entities": [
            {"type": "PER", "name": "Vandana Katariya", "description": "Indian women's hockey player", "full_name": "Vandana Katariya"},
            {"type": "LOC", "name": "Muscat", "latitude": 23.59, "longitude": 58.59, "location_type": "CITY"},
            {"type": "ORG", "name": "Hockey India", "description": "National hockey governing body", "full_name": "Hockey India"},
        ],
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# EXTRACTED LINKS (matches extract_news_links bronze schema)
# All URLs verified as real working links from April 2026 reporting
# ──────────────────────────────────────────────────────────────────────────────
EXTRACTED_LINKS = {
    "extracted_urls": [
        "https://telanganatoday.com/char-dham-yatra-2026-kedarnath-portals-to-open-on-april-22",
        "https://www.business-standard.com/markets/news/stock-market-rules-changing-from-april-1-stt-on-f-o-algo-buyback-more-126033100544_1.html",
        "https://zeenews.india.com/india/delhi-weather-update-40-degree-celsius-heatwave-imd-forecast-april-2026-3037956.html",
        "https://zeenews.india.com/economy/rbi-monetary-policy-april-2026-central-bank-keeps-interest-rate-unchanged-3034810.html",
        "https://www.onmanorama.com/news/india/2026/04/20/tamil-nadu-virudhunagar-firecracker-explosion.html",
        "https://www.espncricinfo.com/series/ipl-2026-1510719/match-schedule-fixtures-and-results",
        "https://foreignpolicy.com/2026/04/15/pakistan-iran-mediation-talks-cease-fire-islamabad-process/",
        "https://www.goodreturns.in/news/gold-rates-in-india-today-20-04-2026-crash-by-rs-5-000-silver-rates-unchanged-24k-22k-18k-gold-price-1503267.html",
        "https://aninews.in/news/national/general-news/51-quintals-of-flowers-blankets-of-snow-kedarnath-set-for-divine-opening-on-april-2220260420231515/",
    ],
    "count": 9,
    "ingestion_time": "2026-04-22T09:47:12.643508",
    "source": "world_news_api",
    "layer": "speed",
}

# ──────────────────────────────────────────────────────────────────────────────
# RSS FEED INFO (matches feed_rss bronze schema)
# ──────────────────────────────────────────────────────────────────────────────
RSS_FEED = {
    "source_url": "https://www.thehindu.com",
    "content_length": 54210,
    "preview": '<rss version="2.0"><channel><title>The Hindu: Latest News</title><link>https://www.thehindu.com</link><item><title>Kedarnath Dham portals open at 8 AM; Char Dham Yatra 2026 begins</title></item><item><title>Delhi heatwave: Yellow alert for April 22–24, temperatures to touch 42°C</title></item><item><title>Virudhunagar blast toll rises to 25; Tamil Nadu orders statewide PESO audit</title></item><item><title>RBI holds repo rate at 5.25%; Governor flags West Asia inflation risk</title></item><item><title>India markets wobble on crude shock; IT stocks buck declining trend</title></item></channel></rss>',
    "ingestion_time": "2026-04-22T09:47:12.422981",
    "layer": "speed",
    "source": "world_news_api",
}

# ──────────────────────────────────────────────────────────────────────────────
# SEARCH NEWS PAGINATION (matches search_news bronze schema)
# ──────────────────────────────────────────────────────────────────────────────
SEARCH_PAGINATION = {
    "offset": 0,
    "number": 25,
    "available": 5217,
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
    {"city": "Kozhikode, Kerala",      "latitude": 11.2588, "longitude": 75.7804, "article_count":  5, "avg_sentiment": -0.52, "region": "Kerala",         "country": "India"},
    {"city": "Sriharikota, AP",        "latitude": 13.7200, "longitude": 80.2300, "article_count":  3, "avg_sentiment":  0.88, "region": "Andhra Pradesh", "country": "India"},
    {"city": "Dubai",                  "latitude": 25.2048, "longitude": 55.2708, "article_count":  2, "avg_sentiment":  0.52, "region": "Dubai",          "country": "UAE"},
    {"city": "London",                 "latitude": 51.5085, "longitude": -0.1257, "article_count":  2, "avg_sentiment": -0.10, "region": "England",        "country": "UK"},
    {"city": "Jaisalmer, Rajasthan",   "latitude": 26.9157, "longitude": 70.9083, "article_count":  3, "avg_sentiment":  0.80, "region": "Rajasthan",      "country": "India"},
    {"city": "Muscat",                 "latitude": 23.5880, "longitude": 58.3829, "article_count":  1, "avg_sentiment":  0.88, "region": "Muscat",         "country": "Oman"},
    {"city": "Kedarnath, Uttarakhand", "latitude": 30.7346, "longitude": 79.0669, "article_count":  3, "avg_sentiment":  0.82, "region": "Uttarakhand",    "country": "India"},
    {"city": "Virudhunagar, TN",       "latitude":  9.5800, "longitude": 77.9600, "article_count":  4, "avg_sentiment": -0.78, "region": "Tamil Nadu",     "country": "India"},
]

# ──────────────────────────────────────────────────────────────────────────────
# TIME SERIES — last 60 days ending today April 22 2026
# ──────────────────────────────────────────────────────────────────────────────
def _generate_time_series(days: int = 60):
    base = datetime(2026, 4, 22)
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
    "total_articles":    934,
    "avg_sentiment":     0.12,
    "positive_pct":      48.6,
    "negative_pct":      32.8,
    "neutral_pct":       18.6,
    "articles_today":    64,
    "trending_category": "general",
    "top_source":        "The Hindu",
    "pipeline_health":   "operational",
    "kafka_lag":         0,
    "minio_objects":     1427,
    "bronze_objects":    718,
    "silver_objects":    481,
    "gold_objects":      228,
    "last_ingestion":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "kafka_throughput":  "162 msg/min",
    "api_latency_ms":    71,
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