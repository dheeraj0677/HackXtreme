from pathlib import Path
p = Path('c:/Users/Dheer/OneDrive/Desktop/Fresh2/HackXtreme/GlobalSentry-Web/eco_feed.xml')
print('eco_feed.xml lines', len(p.read_text(encoding='utf-8').splitlines()))
