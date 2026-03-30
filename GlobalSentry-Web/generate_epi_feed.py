import random
import uuid
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Define lists for generating headlines
TOPICS = [
    "Outbreak", "Pandemic", "Epidemic", "Disease surge", "Vaccine shortage", "Quarantine", "Health alert",
    "Infection spike", "Pathogen detection", "Public health emergency", "Zoonotic spillover", "Antibiotic resistance",
    "Vector-borne disease", "Respiratory illness", "Gastroenteritis outbreak", "Hemorrhagic fever", "Measles resurgence",
    "Polio vaccination", "Meningitis cases", "Anthrax incident", "Onchocerciasis re-emergence", "Legionnaires' disease"
]

LOCATIONS = [
    "Haiti", "Bangladesh", "Nepal", "Yemen", "Somalia", "Gaza Strip", "Siberia", "Volta River basin", "India",
    "Nigeria", "Niger", "Chad", "Istanbul", "Mediterranean", "Sahel countries", "Pacific Islands", "Middle East",
    "East Asia", "Southeast Asia", "West Africa", "South Asia", "Remote regions"
]

ORGANIZATIONS = [
    "WHO", "CDC", "ECDC", "GOARN", "ProMED", "ReliefWeb", "HealthMap", "UNICEF", "Red Cross", "Médecins Sans Frontières"
]

def generate_headline():
    topic = random.choice(TOPICS)
    location = random.choice(LOCATIONS)
    organization = random.choice(ORGANIZATIONS)
    return f"{topic} in {location} reported by {organization}"

def generate_description():
    return "GlobalSentry Epidemic Threat Feed - Monitoring global health threats and outbreaks."

def generate_pubdate():
    # Generate a random date within the last year
    start_date = datetime.now() - timedelta(days=365)
    random_date = start_date + timedelta(days=random.randint(0, 365))
    return random_date.strftime("%a, %d %b %Y %H:%M:%S GMT")

# Create the root element
rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss, "channel")

# Add channel metadata
ET.SubElement(channel, "title").text = "GlobalSentry Epidemic Threat Feed"
ET.SubElement(channel, "link").text = "https://globalsentry.com/epi-feed"
ET.SubElement(channel, "description").text = "Real-time updates on global epidemic threats and health emergencies."
ET.SubElement(channel, "language").text = "en-us"
ET.SubElement(channel, "lastBuildDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")

# Generate 500 items
for _ in range(500):
    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = generate_headline()
    item_id = str(uuid.uuid4())
    ET.SubElement(item, "link").text = f"https://globalsentry.com/epi-alert/{item_id}"
    ET.SubElement(item, "description").text = generate_description()
    ET.SubElement(item, "pubDate").text = generate_pubdate()
    ET.SubElement(item, "guid").text = item_id

# Convert to string and pretty print
rough_string = ET.tostring(rss, 'utf-8')
reparsed = minidom.parseString(rough_string)
pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8")

# Write to file
with open("epi_feed.xml", "wb") as f:
    f.write(pretty_xml)

print("epi_feed.xml generated with 500 items.")