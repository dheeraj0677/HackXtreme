"""View Qdrant database contents directly — writes clean output to file."""
from qdrant_client import QdrantClient

QDRANT_PATH = "./qdrant_data"
client = QdrantClient(path=QDRANT_PATH)

collections = client.get_collections().collections
lines = []
lines.append("=" * 70)
lines.append("         QDRANT DATABASE VIEWER")
lines.append("=" * 70)
lines.append(f"Collections found: {[c.name for c in collections]}")
lines.append("")

for col in collections:
    name = col.name
    info = client.get_collection(name)
    pts = info.points_count
    lines.append("=" * 70)
    lines.append(f"  Collection: {name}")
    lines.append(f"  Points: {pts} | Vector dim: {info.config.params.vectors.size} | Distance: {info.config.params.vectors.distance}")
    lines.append("=" * 70)

    if pts == 0:
        lines.append("  (empty)")
        lines.append("")
        continue

    res, _ = client.scroll(collection_name=name, limit=100, with_payload=True, with_vectors=False)
    for i, pt in enumerate(res, 1):
        p = pt.payload or {}
        if i == 1:
            lines.append(f"  Payload keys: {list(p.keys())}")
            lines.append("")

        mode = p.get("mode", "")
        if not mode and isinstance(p.get("metadata"), dict):
            mode = p["metadata"].get("mode", "")
        sev = p.get("severity", "")
        if not sev and isinstance(p.get("metadata"), dict):
            sev = p["metadata"].get("severity", "")
        text = p.get("text", p.get("page_content", p.get("content", "")))

        mode_str = str(mode).upper() if mode else "?"
        lines.append(f"  {i:>3}. [{mode_str}] sev={sev}  {str(text)[:100]}")

    if pts > len(res):
        lines.append(f"\n  ... showing {len(res)} of {pts} total points")
    lines.append("")

client.close()

output = "\n".join(lines)
with open("qdrant_dump.txt", "w", encoding="utf-8") as f:
    f.write(output)

print(output[:3000])
print(f"\nFull output saved to: qdrant_dump.txt")
