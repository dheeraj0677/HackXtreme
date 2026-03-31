import uuid, datetime
path = 'eco_feed.xml'
title='GlobalSentry Ecological Threat Feed'
link='https://globalsentry.com/eco-feed'
desc='Real-time updates on global ecological threats and environmental emergencies.'
node_desc='GlobalSentry Ecological Threat Feed - Monitoring global environmental threats and ecological crises.'
start = datetime.datetime(2025,1,1,1,50,2)
items = []
for i in range(1,401):
    pub = start + datetime.timedelta(days=i*2)
    tid = str(uuid.uuid4())
    evts = ['Deforestation','Coral bleaching','Biodiversity loss','Oil spill','Wildfire crisis','Flooding','Water pollution','Species extinction','Drought','Soil degradation','Climate change impact','Air pollution','Habitat destruction','Desertification','Pesticide contamination','Ocean acidification','Environmental disaster','Ecosystem collapse','Invasive species','Toxic waste','Forest fire','Plastic pollution','Marine damage','Coastal erosion','Agricultural contamination','Catastrophic flooding','Public health crisis','Wildlife disease spillover']
    regs = ['Amazon Basin','Pacific Islands','West Africa','Nigeria','Southeast Asia','East Asia','Siberia','Volta River basin','Middle East','Mediterranean','Sahel','Remote regions','Istanbul','Gaza Strip','Chad']
    srcs = ['ReliefWeb','CDC','Red Cross','GOARN','ProMED','UNICEF','WHO','ECDC','Médecins Sans Frontières']
    evt = evts[(i-1) % len(evts)]
    region = regs[(i-1) % len(regs)]
    source = srcs[(i-1) % len(srcs)]
    title_item = f"{evt} in {region} reported by {source}"
    link_item = f"https://globalsentry.com/eco-alert/{tid}"
    items.append((title_item, link_item, node_desc, pub.strftime('%a, %d %b %Y %H:%M:%S GMT'), tid))
with open(path,'w', encoding='utf-8') as f:
    f.write('<?xml version="1.0" encoding="utf-8"?>\n<rss version="2.0">\n  <channel>\n')
    f.write(f'    <title>{title}</title>\n')
    f.write(f'    <link>{link}</link>\n')
    f.write(f'    <description>{desc}</description>\n')
    f.write('    <language>en-us</language>\n')
    f.write(f'    <lastBuildDate>{datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")}</lastBuildDate>\n')
    for t,l,d,p,g in items:
        f.write('    <item>\n')
        f.write(f'      <title>{t}</title>\n')
        f.write(f'      <link>{l}</link>\n')
        f.write(f'      <description>{d}</description>\n')
        f.write(f'      <pubDate>{p}</pubDate>\n')
        f.write(f'      <guid>{g}</guid>\n')
        f.write('    </item>\n')
    f.write('  </channel>\n</rss>\n')
print('wrote', path, 'items', len(items))
