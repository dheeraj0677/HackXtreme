"""Generate realistic, diverse XML feeds for GlobalSentry demo."""
import uuid
from datetime import datetime, timedelta
import random
import xml.etree.ElementTree as ET
from xml.dom import minidom

# ═══════════════════════════════════════════════════════════════════════
# EPIDEMIC HEADLINES — realistic WHO/CDC/ProMED style
# ═══════════════════════════════════════════════════════════════════════
EPI_HEADLINES = [
    # Cholera
    "WHO confirms cholera outbreak in Mozambique's Zambezia province — 2,400 cases in 3 weeks",
    "Cholera death toll in Haiti surpasses 180 as clean water access remains critically limited",
    "South Sudan declares cholera emergency in Upper Nile state following severe flooding",
    "Cholera cases spike 340% in Malawi; WHO deploys emergency oral vaccine stockpile",
    "Bangladesh reports cholera surge in Cox's Bazar refugee camps — 1,100 cases since March",
    # Dengue
    "Brazil records worst dengue season in a decade — 4.2 million suspected cases in 2026",
    "Dengue hemorrhagic fever kills 47 in Philippines as El Niño shifts mosquito habitats",
    "India's Karnataka state reports 8,500 dengue cases amid unseasonal monsoon rains",
    "Peru declares health emergency in Lima as dengue cases overwhelm hospital capacity",
    "Thailand reports drug-resistant dengue strain circulating in Chiang Mai province",
    # Respiratory
    "Novel H5N1 avian influenza cluster detected in Egyptian poultry workers — 6 confirmed human cases",
    "CDC investigating unusual pneumonia cluster in Minnesota — 23 cases, pathogen unidentified",
    "WHO monitoring H7N9 resurgence in Guangdong province — 3 fatal cases in healthcare workers",
    "MERS-CoV cases reported in Saudi Arabia ahead of Hajj pilgrimage season",
    "Tuberculosis outbreak in South African gold mines — multi-drug resistant strain confirmed",
    # Ebola/Hemorrhagic
    "DRC reports new Ebola cluster in North Kivu — 14 confirmed cases near conflict zone",
    "Marburg virus case confirmed in Tanzania near Kagera border — contact tracing underway",
    "Guinea confirms Lassa fever cases in Nzérékoré — cross-border surveillance activated",
    "Crimean-Congo hemorrhagic fever cases rise 200% in Turkey's eastern provinces",
    "Uganda's Ebola containment under strain as 3 new cases emerge outside quarantine zone",
    # Measles/Polio
    "Measles outbreak in Pakistan's Punjab province — 12,000 cases; vaccination coverage at 58%",
    "Polio detected in London wastewater for first time since 2022 — booster campaign launched",
    "Afghanistan reports 28 new wild poliovirus cases as immunization campaign faces security threats",
    "Measles kills 140 children in Samoa amid vaccination hesitancy crisis",
    "Nigeria's Kano state sees measles surge — MSF sets up emergency treatment centers",
    # AMR / Novel threats
    "WHO warns of pan-resistant Klebsiella pneumoniae spreading in Southeast Asian ICUs",
    "Candida auris outbreak in 4 US hospitals; CDC classifies as urgent antimicrobial threat",
    "Nipah virus seropositive bats detected near Dhaka — Bangladesh heightens surveillance",
    "Mpox clade Ib spreading in eastern DRC with sustained human-to-human transmission",
    "Unidentified febrile illness kills 9 in rural Bolivia — samples sent to CDC Atlanta",
    # Waterborne
    "Typhoid fever outbreak in Karachi linked to contaminated water supply — 3,200 cases",
    "Hepatitis E surge in South Sudan IDP camps — UNICEF calls for emergency sanitation funding",
    "Cryptosporidiosis cases triple in UK following record summer rainfall and flooding",
    "Acute watery diarrhea kills 56 children in Somalia's Bay region — MSF responds",
    "Leptospirosis spike in Kerala after severe flooding — 420 confirmed cases this month",
    # Vaccine/Supply
    "Yellow fever vaccine stockpile critically low as outbreaks hit 8 African nations simultaneously",
    "India's BCG vaccine shortage impacts newborn immunization across 12 states",
    "Cold chain failure in Madagascar destroys 500,000 doses of pentavalent vaccine",
    "WHO prequalifies new oral cholera vaccine but manufacturing capacity remains bottleneck",
    "Routine childhood immunization coverage drops to 78% globally — lowest since 2008",
    # Zoonotic
    "Anthrax outbreak among Siberian reindeer herders linked to thawing permafrost",
    "Rift Valley fever confirmed in Kenya's Garissa county — livestock trade suspended",
    "Rabies deaths surge in India's Uttar Pradesh despite free vaccination policy",
    "Plague cases reported in Madagascar's central highlands ahead of rainy season",
    "Brucellosis cluster in China's Inner Mongolia linked to illegal livestock trade",
    # Surveillance signals
    "ProMED alert: Unexplained neurological syndrome in Vietnamese children — 18 cases under investigation",
    "ECDC raises risk assessment for West Nile virus in southern Europe to HIGH",
    "HealthMap detects anomalous respiratory illness tweets clustering in Jakarta",
    "GOARN deploys rapid response team to investigate mystery fever in rural Peru",
    "WHO Disease Outbreak News: Diphtheria cases surging in Venezuela amid healthcare collapse",
]

# ═══════════════════════════════════════════════════════════════════════
# ECO/CLIMATE HEADLINES — realistic UNDRR/WMO/Reuters style
# ═══════════════════════════════════════════════════════════════════════
ECO_HEADLINES = [
    # Extreme heat
    "India records 52.3°C in Rajasthan — deadliest April heatwave kills 238 in 72 hours",
    "European heat dome shatters records: Paris hits 46°C; Seville declares 'extreme danger'",
    "Pakistan's Jacobabad records wet-bulb temperature of 35°C — beyond human survivability threshold",
    "US Southwest megadrought enters 27th year; Lake Mead drops below dead pool elevation",
    "Heat stress kills 1,400 in Japan as air conditioning demand causes rolling blackouts",
    # Flooding
    "Catastrophic flooding in Libya — Derna dam collapse kills estimated 11,000 people",
    "Bangladesh experiences worst monsoon flooding in 40 years; 7.2 million displaced",
    "Germany's Rhine Valley floods cause €8.5 billion in damages; 200+ missing",
    "Nigeria's Benue river overflows displacing 2.4 million in worst flooding since records began",
    "China's Henan province hit by 'once in 1,000 years' rainfall — Zhengzhou subway flooded",
    # Hurricanes/Cyclones
    "Category 5 Hurricane Elena makes landfall in Veracruz — 185 mph winds devastate coast",
    "Cyclone Freddy breaks record as longest-lasting tropical storm at 36 days",
    "Super Typhoon Mawar causes $12 billion damage across Philippines and Taiwan",
    "Atlantic hurricane season forecast: NOAA predicts 22 named storms — highest ever projected",
    "Tropical Cyclone Mocha devastates Myanmar's Rakhine state — 400,000 in need of aid",
    # Wildfires
    "Canada's record wildfire season burns 18.4 million hectares — smoke blankets US East Coast",
    "Greece's largest-ever wildfire burns through Alexandroupolis — EU activates civil protection",
    "Hawaiian wildfires destroy historic Lahaina town — death toll rises to 115",
    "Chilean wildfires kill 131 in Valparaíso region; arson suspected in 40% of ignitions",
    "Australia's Black Summer 2.0: Victoria declares state of disaster as fires merge",
    # Sea level / Coastal
    "Tuvalu formally requests climate refugee status for entire population of 11,000",
    "Sea level rise accelerates to 4.5mm/year — Venice activates MOSE barriers 187 times this year",
    "Jakarta's land subsidence crisis worsens — city sinking 25cm/year in northern districts",
    "Marshall Islands declares coastal emergency as king tides breach freshwater aquifers",
    "Miami Beach reports 200+ tidal flooding days in 2026 — highest on record",
    # Drought / Water
    "Horn of Africa drought enters 5th consecutive failed rainy season — 23 million food insecure",
    "Amazon River hits record low water levels — river dolphins dying in unprecedented numbers",
    "Cape Town's Day Zero returns: dam levels at 13.5% as population grows beyond planning capacity",
    "Euphrates River flow drops 40% as Turkey, Syria, Iraq dispute upstream dam operations",
    "Groundwater depletion in India's Punjab threatens collapse of wheat production by 2030",
    # Glaciers / Polar
    "Antarctic sea ice hits record low — 1.9 million km² below 1981-2010 average",
    "Swiss Alps lose 10% of remaining glacier volume in single year — unprecedented retreat",
    "Greenland ice sheet melt contributes 1.2mm to global sea level in July alone",
    "Himalayan glacial lake outburst flood destroys bridge and 40 homes in Sikkim, India",
    "Arctic permafrost thaw releases methane at 3x predicted rates — climate models need revision",
    # Biodiversity
    "Great Barrier Reef suffers 4th mass bleaching in 7 years as ocean temps hit record",
    "Amazon deforestation rate surges 22% — tipping point threshold increasingly likely",
    "Insect population decline reaches 45% in temperate regions — pollination crisis imminent",
    "UN warns 1 million species face extinction — current rate 1,000x natural background",
    "Coral reefs in Caribbean experience unprecedented bleaching across all depths",
    # Compound events
    "WMO confirms 2026 as hottest year on record — 1.8°C above pre-industrial baseline",
    "Compound climate event: drought-wildfire-flood cascade hits California in 90-day window",
    "Climate attribution study links Pakistan floods to 30x increase from global warming",
    "El Niño-Southern Oscillation reaches 'super' threshold — global food prices spike 35%",
    "IPCC special report warns of simultaneous breadbasket failures within next decade",
    # Infrastructure
    "Texas power grid collapses again during extreme cold — 4.5 million without electricity",
    "European rail network forced to reduce speeds by 30% as heat warps tracks across continent",
    "Mumbai's coastal road project threatened by accelerating erosion and storm surge",
    "Water rationing imposed in Barcelona, Bogotá, and Bengaluru simultaneously",
    "Bridge collapses in Brazil during flash flood — 14 vehicles swept into river",
]

# ═══════════════════════════════════════════════════════════════════════
# SUPPLY CHAIN HEADLINES — realistic Reuters/Bloomberg/FT style
# ═══════════════════════════════════════════════════════════════════════
SUPPLY_HEADLINES = [
    # Shipping / Ports
    "Houthi missile strikes disable 3 container ships in Red Sea — global shipping reroutes via Cape of Good Hope",
    "Panama Canal reduces daily transits to 22 from 36 due to severe drought — 6-week vessel queue forms",
    "Port of Shanghai shuts down for 72 hours as Typhoon Lekima approaches — 850 vessels stranded",
    "Suez Canal blockage: grounded bulk carrier halts traffic for 4 days — $9.6B/day in trade stalled",
    "Baltimore port closure after bridge collapse disrupts East Coast auto and coal exports for months",
    # Semiconductors
    "TSMC halts production at Fab 18 after 6.4 magnitude earthquake near Hualien, Taiwan",
    "US-China chip war escalates: Beijing bans gallium and germanium exports — prices surge 400%",
    "Samsung's Austin fab contamination incident destroys 3 months of advanced chip output",
    "Global automotive chip shortage returns as ASML delays EUV lithography machine deliveries",
    "Intel postpones Ohio fab construction citing $28 billion cost overrun and demand uncertainty",
    # Energy
    "European natural gas prices spike 180% as Norway's Troll field enters emergency maintenance",
    "Russia cuts remaining gas flows through TurkStream pipeline amid new EU sanctions package",
    "Global LNG tanker shortage strands Asian buyers — spot prices hit $45/MMBtu",
    "Saudi Arabia extends OPEC+ production cuts through Q3 2026 — Brent crude crosses $105/barrel",
    "Lithium carbonate prices collapse 60% — Chilean and Australian miners halt expansion plans",
    # Food / Agriculture
    "India bans rice exports as monsoon failure threatens 40% crop shortfall",
    "Ukraine grain corridor suspended after Russian withdrawal — wheat futures surge to $9.50/bushel",
    "Brazilian coffee crop devastated by worst frost in 50 years — arabica prices hit 10-year high",
    "Fertilizer shortage in sub-Saharan Africa: 30 million hectares go unplanted this season",
    "Bird flu outbreak forces culling of 90 million poultry in US — egg prices triple",
    # Automotive
    "Toyota suspends 14 assembly lines across Japan after cyberattack on key supplier Kojima Industries",
    "Volkswagen warns of 6-week production halt as magnesium shortage from China worsens",
    "Tesla Gigafactory Berlin halted by arson attack on nearby power infrastructure",
    "Global auto production forecast cut by 4 million units as wiring harness supply from Ukraine collapses",
    "Ford recalls 500,000 EVs over battery defect linked to single CATL cell manufacturing line",
    # Pharma / Medical
    "FDA reports critical shortage of IV saline and contrast dye after Baxter plant flood damage",
    "China's API export restrictions cause global antibiotic shortage — penicillin stocks at 2-week supply",
    "Novo Nordisk rations Ozempic globally as GLP-1 demand outstrips production 3:1",
    "WHO warns of heparin shortage as global pig farming disrupted by African Swine Fever",
    "Indian generic drug exports halted at 12 plants after surprise FDA quality inspections",
    # Rare earth / Minerals
    "China restricts rare earth processing tech exports — wind turbine manufacturers scramble for alternatives",
    "Cobalt supply crisis deepens as DRC suspends mining permits in Katanga province",
    "Indonesia's nickel export ban disrupts stainless steel supply chains across Asia",
    "Myanmar's rare earth mining shutdown cuts global heavy rare earth supply by 30%",
    "Critical graphite shortage threatens EV battery production — prices up 85% year-over-year",
    # Cybersecurity
    "Ransomware attack on Maersk subsidiary disrupts container tracking across 76 port terminals worldwide",
    "MOVEit-style vulnerability exploited across 3 major freight forwarders — shipping documents compromised",
    "Colonial Pipeline-scale attack hits European fuel distribution network — 5 countries affected",
    "JBS-style cyberattack shuts down Brazil's 3 largest meatpacking plants for 10 days",
    "Port of Rotterdam's terminal operating system breached — automated cranes halted for 48 hours",
    # Labor / Geopolitical
    "US West Coast dockworkers begin indefinite strike — $1.9B/day in cargo stranded at ports",
    "South Korea's trucking strike paralyzes petrochemical and steel distribution for 2nd week",
    "Taiwan Strait tensions: insurers withdraw war-risk coverage for vessels transiting strait",
    "Red Sea crisis forces 92% of container traffic to reroute — transit times increase 14 days",
    "Ethiopian civil conflict disrupts East Africa's primary logistics corridor via Djibouti port",
    # Logistics / Last mile
    "FedEx and UPS warn of 15% capacity shortfall ahead of peak season due to pilot shortages",
    "Amazon warehouse workers strike across 7 European countries during Prime Day",
    "Global container shipping rates hit $8,200/FEU on Asia-Europe route — 4x pre-crisis levels",
    "Air cargo capacity crunch: belly hold space vanishes as airlines cut long-haul frequencies",
    "Rail freight bottleneck at US-Mexico border as new customs screening rules take effect",
]

def generate_feed(feed_type, headlines, title, description, link):
    """Generate an RSS XML feed with realistic, varied headlines."""
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    
    ET.SubElement(channel, "title").text = title
    ET.SubElement(channel, "link").text = link
    ET.SubElement(channel, "description").text = description
    ET.SubElement(channel, "language").text = "en-us"
    ET.SubElement(channel, "lastBuildDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    # Generate items with dates spread across last 30 days (most recent first)
    base_date = datetime(2026, 3, 31, 1, 0, 0)
    
    for i, headline in enumerate(headlines):
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = headline
        
        guid = str(uuid.uuid4())
        ET.SubElement(item, "link").text = f"https://globalsentry.com/{feed_type}-alert/{guid}"
        ET.SubElement(item, "description").text = description
        
        # Spread dates: most recent headlines get most recent dates
        hours_ago = i * (720 / len(headlines))  # spread across ~30 days
        pub_date = base_date - timedelta(hours=hours_ago)
        ET.SubElement(item, "pubDate").text = pub_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
        ET.SubElement(item, "guid").text = guid
    
    # Pretty print
    rough = ET.tostring(rss, encoding="unicode")
    parsed = minidom.parseString(rough)
    return parsed.toprettyxml(indent="    ", encoding=None)

def write_feed(filepath, content):
    # Remove the extra xml declaration minidom adds and clean up
    lines = content.split('\n')
    # Skip first line if it's xml declaration (minidom adds one)
    if lines[0].startswith('<?xml'):
        lines[0] = '<?xml version="1.0" encoding="utf-8"?>'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

# Generate all three feeds
print("Generating epi_feed.xml...")
epi_xml = generate_feed(
    "epi", EPI_HEADLINES,
    "GlobalSentry Epidemic Threat Feed",
    "Real-time updates on global epidemic threats and health emergencies.",
    "https://globalsentry.com/epi-feed"
)
write_feed("epi_feed.xml", epi_xml)
print(f"  → {len(EPI_HEADLINES)} headlines written")

print("Generating eco_feed.xml...")
eco_xml = generate_feed(
    "eco", ECO_HEADLINES,
    "GlobalSentry Climate & Disaster Feed",
    "Real-time monitoring of climate disasters, extreme weather, and environmental threats.",
    "https://globalsentry.com/eco-feed"
)
write_feed("eco_feed.xml", eco_xml)
print(f"  → {len(ECO_HEADLINES)} headlines written")

print("Generating supply_feed.xml...")
supply_xml = generate_feed(
    "supply", SUPPLY_HEADLINES,
    "GlobalSentry Supply Chain Threat Feed",
    "Real-time intelligence on global supply chain disruptions, logistics failures, and trade risks.",
    "https://globalsentry.com/supply-feed"
)
write_feed("supply_feed.xml", supply_xml)
print(f"  → {len(SUPPLY_HEADLINES)} headlines written")

print("\n✅ All 3 feeds generated successfully!")
