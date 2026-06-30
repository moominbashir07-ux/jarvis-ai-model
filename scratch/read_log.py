with open("logs/jarvis.log", "r", encoding="utf-8") as f:
    lines = f.readlines()
print(f"Total lines: {len(lines)}")
for line in lines[-150:]:
    print(line, end="")
