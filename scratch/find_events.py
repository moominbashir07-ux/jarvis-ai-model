with open("logs/jarvis.log", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("Last events:")
for line in lines:
    # Filter lines that have events published
    if "Publishing event" in line or "Received input" in line or "Wake word matched" in line or "CommandRegistry matched" in line or "Selected AI Provider" in line:
        # Check if it was after our startup timestamp
        if "2026-06-26 00:2" in line:
            print(line, end="")
