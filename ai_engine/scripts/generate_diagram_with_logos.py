import base64
import urllib.request
import json
import os

logos = {
    "cpp": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/ISO_C%2B%2B_Logo.svg/120px-ISO_C%2B%2B_Logo.svg.png",
    "pytorch": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/PyTorch_logo_icon.svg/120px-PyTorch_logo_icon.svg.png",
    "osm": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Openstreetmap_logo.svg/120px-Openstreetmap_logo.svg.png",
    "flutter": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Google-flutter-logo.png/120px-Google-flutter-logo.png"
}

b64_logos = {}

for name, url in logos.items():
    print(f"Downloading {name}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = response.read()
            b64_logos[name] = "data:image/png;base64," + base64.b64encode(data).decode('utf-8')
    except Exception as e:
        print(f"Failed to download {name}: {e}")
        b64_logos[name] = ""

mermaid_content = f"""graph LR
    classDef input fill:#2c3e50,stroke:#34495e,stroke-width:2px,color:#fff,rx:10px,ry:10px;
    classDef process fill:#2980b9,stroke:#2471a3,stroke-width:2px,color:#fff,rx:5px,ry:5px;
    classDef ai fill:#8e44ad,stroke:#732d91,stroke-width:2px,color:#fff,rx:20px,ry:20px;
    classDef filter fill:#e67e22,stroke:#d35400,stroke-width:4px,color:#fff,rx:5px,ry:5px;
    classDef output fill:#27ae60,stroke:#1e8449,stroke-width:2px,color:#fff;
    
    A([Raw Accelerometer]):::input
    B([Raw Gyroscope]):::input
    
    C{{"<img src='{b64_logos['cpp']}' width='25' height='28' style='vertical-align:middle;margin-right:5px;' /> C++ PCA Gravity Alignment"}}:::process
    D["Coordinate Rotation"]:::process
    
    E(("<img src='{b64_logos['pytorch']}' width='25' height='25' style='vertical-align:middle;margin-right:5px;' /> PyTorch 1D-CNN Velocity")):::ai
    F(("Angular Integration")):::process
    
    G["Unscented Kalman Filter"]:::filter
    H{{"<img src='{b64_logos['osm']}' width='25' height='25' style='vertical-align:middle;margin-right:5px;' /> OSM Map-Matching"}}:::filter
    
    I[/"<img src='{b64_logos['flutter']}' width='20' height='25' style='vertical-align:middle;margin-right:5px;' /> Flutter Mobile UI"/]:::output
    
    A -->|Vibration Data| C
    B -->|Rotation Data| D
    C -->|Gravity Vector| D
    
    D -->|Z/Y Axis| E
    D -->|Yaw Rates| F
    
    E -->|Predicted Speed| G
    F -->|Heading Angle| G
    
    G -->|Drifting X, Y Coordinates| H
    H -->|Lane-Snapped Output| I
"""

with open("data_flow.mmd", "w") as f:
    f.write(mermaid_content)

with open("mermaid.json", "w") as f:
    json.dump({"securityLevel": "loose", "htmlLabels": True}, f)

print("Generated data_flow.mmd with base64 logos and mermaid.json")
