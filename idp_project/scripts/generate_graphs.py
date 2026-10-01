"""Generate publication-grade SVG and PNG graphs for IEEE Paper.

Graphs:
1. Fig. 6: Review Threshold Operating Curve (Curl / Trade-off Curve)
   - X-axis: Confidence Threshold (theta) from 0.50 to 0.95
   - Y-axis (Left): Error Capture Rate (%) [Target: 100%]
   - Y-axis (Right): Human Review Rate (% Flagged)
   - Highlights operating point theta = 0.70.

2. Fig. 7: Classification Accuracy & Processing Latency per Document Type
   - Dual-axis bar & line chart across 5 document categories.

3. Fig. 8: Baseline Model Comparison (Accuracy vs Latency vs Data Privacy)
   - Bar chart comparing Tesseract OCR, DigitCNN, Hosted Gemini, and Proposed Local Qwen VLM.
"""

import os

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "graphs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_svg_threshold_curve():
    """Generate SVG for Fig 6: Review Threshold Operating Curve."""
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="800" height="500" style="background:#ffffff; font-family: Arial, sans-serif;">
  <rect width="100%" height="100%" fill="#ffffff" />
  
  <!-- Title & Subtitle -->
  <text x="400" y="30" text-anchor="middle" font-size="18" font-weight="bold" fill="#003366">Fig. 6: Human Review Threshold (θ) Operating Curve</text>
  <text x="400" y="50" text-anchor="middle" font-size="13" fill="#555555">Error Capture Rate vs. Flagged Human Review Rate across 344 Test Fields</text>
  
  <!-- Grid Lines -->
  <line x1="80" y1="400" x2="720" y2="400" stroke="#dddddd" stroke-width="1"/>
  <line x1="80" y1="330" x2="720" y2="330" stroke="#eeeeee" stroke-width="1"/>
  <line x1="80" y1="260" x2="720" y2="260" stroke="#eeeeee" stroke-width="1"/>
  <line x1="80" y1="190" x2="720" y2="190" stroke="#eeeeee" stroke-width="1"/>
  <line x1="80" y1="120" x2="720" y2="120" stroke="#eeeeee" stroke-width="1"/>
  
  <!-- Axes -->
  <line x1="80" y1="400" x2="720" y2="400" stroke="#333333" stroke-width="2"/>
  <line x1="80" y1="80" x2="80" y2="400" stroke="#003366" stroke-width="2"/>
  <line x1="720" y1="80" x2="720" y2="400" stroke="#d9534f" stroke-width="2"/>
  
  <!-- Y-Axis 1 Labels (Left - Error Capture %) -->
  <text x="70" y="405" text-anchor="end" font-size="11" fill="#003366">0%</text>
  <text x="70" y="335" text-anchor="end" font-size="11" fill="#003366">25%</text>
  <text x="70" y="265" text-anchor="end" font-size="11" fill="#003366">50%</text>
  <text x="70" y="195" text-anchor="end" font-size="11" fill="#003366">75%</text>
  <text x="70" y="125" text-anchor="end" font-size="11" fill="#003366" font-weight="bold">100%</text>
  <text x="30" y="240" text-anchor="middle" font-size="13" font-weight="bold" fill="#003366" transform="rotate(-90, 30, 240)">Error Capture Rate (%)</text>
  
  <!-- Y-Axis 2 Labels (Right - Flagged Review %) -->
  <text x="730" y="405" text-anchor="start" font-size="11" fill="#d9534f">0%</text>
  <text x="730" y="335" text-anchor="start" font-size="11" fill="#d9534f">20%</text>
  <text x="730" y="265" text-anchor="start" font-size="11" fill="#d9534f">40%</text>
  <text x="730" y="195" text-anchor="start" font-size="11" fill="#d9534f">60%</text>
  <text x="730" y="125" text-anchor="start" font-size="11" fill="#d9534f">80%</text>
  <text x="770" y="240" text-anchor="middle" font-size="13" font-weight="bold" fill="#d9534f" transform="rotate(90, 770, 240)">Flagged for Review (%)</text>
  
  <!-- X-Axis Labels (Threshold theta) -->
  <!-- 0.50 -> x=140, 0.60 -> x=250, 0.70 -> x=360, 0.80 -> x=470, 0.90 -> x=580, 0.95 -> x=660 -->
  <text x="140" y="425" text-anchor="middle" font-size="12" fill="#333333">0.50</text>
  <text x="250" y="425" text-anchor="middle" font-size="12" fill="#333333">0.60</text>
  <text x="360" y="425" text-anchor="middle" font-size="12" font-weight="bold" fill="#008000">0.70 (Optimal)</text>
  <text x="470" y="425" text-anchor="middle" font-size="12" fill="#333333">0.80</text>
  <text x="580" y="425" text-anchor="middle" font-size="12" fill="#333333">0.90</text>
  <text x="660" y="425" text-anchor="middle" font-size="12" fill="#333333">0.95</text>
  <text x="400" y="460" text-anchor="middle" font-size="14" font-weight="bold" fill="#333333">Confidence Threshold Score (θ)</text>
  
  <!-- Curve 1: Error Capture Rate (Blue Line) -->
  <!-- Points: (0.50, 62.5% -> y=225), (0.60, 87.5% -> y=155), (0.70, 100% -> y=120), (0.80, 100% -> y=120), (0.90, 100% -> y=120), (0.95, 100% -> y=120) -->
  <polyline points="140,225 250,155 360,120 470,120 580,120 660,120" fill="none" stroke="#003366" stroke-width="4"/>
  
  <!-- Points on Curve 1 -->
  <circle cx="140" cy="225" r="5" fill="#003366"/>
  <circle cx="250" cy="155" r="5" fill="#003366"/>
  <circle cx="360" cy="120" r="7" fill="#008000" stroke="#ffffff" stroke-width="2"/>
  <circle cx="470" cy="120" r="5" fill="#003366"/>
  <circle cx="580" cy="120" r="5" fill="#003366"/>
  <circle cx="660" cy="120" r="5" fill="#003366"/>
  
  <!-- Curve 2: Flagged for Review % (Red Line) -->
  <!-- Points: (0.50, 7.0% -> y=372), (0.60, 7.3% -> y=371), (0.70, 8.7% -> y=365), (0.80, 13.1% -> y=348), (0.90, 19.8% -> y=321), (0.95, 66.3% -> y=135) -->
  <polyline points="140,372 250,371 360,365 470,348 580,321 660,135" fill="none" stroke="#d9534f" stroke-width="4" stroke-dasharray="6,4"/>
  
  <!-- Points on Curve 2 -->
  <circle cx="140" cy="372" r="5" fill="#d9534f"/>
  <circle cx="250" cy="371" r="5" fill="#d9534f"/>
  <circle cx="360" cy="365" r="7" fill="#008000" stroke="#ffffff" stroke-width="2"/>
  <circle cx="470" cy="348" r="5" fill="#d9534f"/>
  <circle cx="580" cy="321" r="5" fill="#d9534f"/>
  <circle cx="660" cy="135" r="5" fill="#d9534f"/>

  <!-- Operating Point Highlight Line -->
  <line x1="360" y1="80" x2="360" y2="400" stroke="#008000" stroke-width="2" stroke-dasharray="4,4"/>
  
  <!-- Callout Box for Operating Point theta=0.70 -->
  <rect x="380" y="140" width="220" height="90" fill="#f0fff0" stroke="#008000" stroke-width="2" rx="6"/>
  <text x="390" y="162" font-size="12" font-weight="bold" fill="#008000">Selected Point: θ = 0.70</text>
  <text x="390" y="182" font-size="11" fill="#333333">✓ 100.0% Error Capture Rate</text>
  <text x="390" y="200" font-size="11" fill="#333333">✓ 8.7% Human Review Burden</text>
  <text x="390" y="218" font-size="11" fill="#333333">✓ 0 Missed Errors</text>

  <!-- Legend -->
  <rect x="180" y="470" width="440" height="25" fill="#f9f9f9" stroke="#cccccc" stroke-width="1" rx="4"/>
  <line x1="200" y1="482" x2="230" y2="482" stroke="#003366" stroke-width="3"/>
  <circle cx="215" cy="482" r="4" fill="#003366"/>
  <text x="240" y="486" font-size="11" fill="#333333">Error Capture Rate (%)</text>

  <line x1="400" y1="482" x2="430" y2="482" stroke="#d9534f" stroke-width="3" stroke-dasharray="4,3"/>
  <circle cx="415" cy="482" r="4" fill="#d9534f"/>
  <text x="440" y="486" font-size="11" fill="#333333">Flagged for Review (%)</text>
</svg>
"""
    file_path = os.path.join(OUTPUT_DIR, "fig6_threshold_curl_curve.svg")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated: {file_path}")


def create_svg_type_accuracy_latency():
    """Generate SVG for Fig 7: Document Type Accuracy & Latency."""
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="800" height="500" style="background:#ffffff; font-family: Arial, sans-serif;">
  <rect width="100%" height="100%" fill="#ffffff" />
  
  <!-- Title & Subtitle -->
  <text x="400" y="30" text-anchor="middle" font-size="18" font-weight="bold" fill="#003366">Fig. 7: Classification Accuracy &amp; Latency per Document Type</text>
  <text x="400" y="50" text-anchor="middle" font-size="13" fill="#555555">Local Qwen2.5-VL 7B Evaluation across 5 Document Categories</text>
  
  <!-- Grid Lines -->
  <line x1="100" y1="380" x2="700" y2="380" stroke="#dddddd" stroke-width="1"/>
  <line x1="100" y1="310" x2="700" y2="310" stroke="#eeeeee" stroke-width="1"/>
  <line x1="100" y1="240" x2="700" y2="240" stroke="#eeeeee" stroke-width="1"/>
  <line x1="100" y1="170" x2="700" y2="170" stroke="#eeeeee" stroke-width="1"/>
  <line x1="100" y1="100" x2="700" y2="100" stroke="#eeeeee" stroke-width="1"/>
  
  <!-- Axes -->
  <line x1="100" y1="380" x2="700" y2="380" stroke="#333333" stroke-width="2"/>
  <line x1="100" y1="80" x2="100" y2="380" stroke="#003366" stroke-width="2"/>
  <line x1="700" y1="80" x2="700" y2="380" stroke="#ff9900" stroke-width="2"/>
  
  <!-- Y1 Labels (Left - Accuracy %) -->
  <text x="90" y="385" text-anchor="end" font-size="11" fill="#003366">0%</text>
  <text x="90" y="315" text-anchor="end" font-size="11" fill="#003366">25%</text>
  <text x="90" y="245" text-anchor="end" font-size="11" fill="#003366">50%</text>
  <text x="90" y="175" text-anchor="end" font-size="11" fill="#003366">75%</text>
  <text x="90" y="105" text-anchor="end" font-size="11" fill="#003366" font-weight="bold">100%</text>
  <text x="45" y="230" text-anchor="middle" font-size="13" font-weight="bold" fill="#003366" transform="rotate(-90, 45, 230)">Classification Accuracy (%)</text>
  
  <!-- Y2 Labels (Right - Latency s) -->
  <text x="710" y="385" text-anchor="start" font-size="11" fill="#ff9900">0.0 s</text>
  <text x="710" y="315" text-anchor="start" font-size="11" fill="#ff9900">1.25 s</text>
  <text x="710" y="245" text-anchor="start" font-size="11" fill="#ff9900">2.50 s</text>
  <text x="710" y="175" text-anchor="start" font-size="11" fill="#ff9900">3.75 s</text>
  <text x="710" y="105" text-anchor="start" font-size="11" fill="#ff9900" font-weight="bold">5.00 s</text>
  <text x="755" y="230" text-anchor="middle" font-size="13" font-weight="bold" fill="#ff9900" transform="rotate(90, 755, 230)">Processing Latency (seconds)</text>
  
  <!-- Bars (Accuracy): 
       Mark Sheet (91.7% -> h=256 -> y=124)
       Invoice (90.0% -> h=252 -> y=128)
       Certificate (100.0% -> h=280 -> y=100)
       ID Card (100.0% -> h=280 -> y=100)
       Attendance Register (90.0% -> h=252 -> y=128)
  -->
  <!-- Mark Sheet: x=130 -->
  <rect x="130" y="124" width="50" height="256" fill="#003366" rx="3"/>
  <text x="155" y="115" text-anchor="middle" font-size="11" font-weight="bold" fill="#003366">91.7%</text>
  
  <!-- Invoice: x=250 -->
  <rect x="250" y="128" width="50" height="252" fill="#003366" rx="3"/>
  <text x="275" y="119" text-anchor="middle" font-size="11" font-weight="bold" fill="#003366">90.0%</text>
  
  <!-- Certificate: x=370 -->
  <rect x="370" y="100" width="50" height="280" fill="#003366" rx="3"/>
  <text x="395" y="91" text-anchor="middle" font-size="11" font-weight="bold" fill="#003366">100%</text>

  <!-- ID Card: x=490 -->
  <rect x="490" y="100" width="50" height="280" fill="#003366" rx="3"/>
  <text x="515" y="91" text-anchor="middle" font-size="11" font-weight="bold" fill="#003366">100%</text>

  <!-- Attendance Register: x=610 -->
  <rect x="610" y="128" width="50" height="252" fill="#003366" rx="3"/>
  <text x="635" y="119" text-anchor="middle" font-size="11" font-weight="bold" fill="#003366">90.0%</text>

  <!-- Latency Line (Orange):
       Mark Sheet (3.5s -> y=184)
       Invoice (3.2s -> y=201)
       Certificate (3.1s -> y=206)
       ID Card (2.8s -> y=223)
       Attendance Register (4.2s -> y=145)
  -->
  <polyline points="155,184 275,201 395,206 515,223 635,145" fill="none" stroke="#ff9900" stroke-width="4"/>
  <circle cx="155" cy="184" r="6" fill="#ff9900" stroke="#ffffff" stroke-width="2"/>
  <text x="155" y="172" text-anchor="middle" font-size="10" font-weight="bold" fill="#cc7a00">3.5s</text>

  <circle cx="275" cy="201" r="6" fill="#ff9900" stroke="#ffffff" stroke-width="2"/>
  <text x="275" y="189" text-anchor="middle" font-size="10" font-weight="bold" fill="#cc7a00">3.2s</text>

  <circle cx="395" cy="206" r="6" fill="#ff9900" stroke="#ffffff" stroke-width="2"/>
  <text x="395" y="194" text-anchor="middle" font-size="10" font-weight="bold" fill="#cc7a00">3.1s</text>

  <circle cx="515" cy="223" r="6" fill="#ff9900" stroke="#ffffff" stroke-width="2"/>
  <text x="515" y="211" text-anchor="middle" font-size="10" font-weight="bold" fill="#cc7a00">2.8s</text>

  <circle cx="635" cy="145" r="6" fill="#ff9900" stroke="#ffffff" stroke-width="2"/>
  <text x="635" y="133" text-anchor="middle" font-size="10" font-weight="bold" fill="#cc7a00">4.2s</text>

  <!-- X-Axis Labels -->
  <text x="155" y="405" text-anchor="middle" font-size="11" font-weight="bold" fill="#333333">Mark Sheet</text>
  <text x="275" y="405" text-anchor="middle" font-size="11" font-weight="bold" fill="#333333">Invoice</text>
  <text x="395" y="405" text-anchor="middle" font-size="11" font-weight="bold" fill="#333333">Certificate</text>
  <text x="515" y="405" text-anchor="middle" font-size="11" font-weight="bold" fill="#333333">ID Card</text>
  <text x="635" y="405" text-anchor="middle" font-size="11" font-weight="bold" fill="#333333">Attendance Reg.</text>

  <!-- Legend -->
  <rect x="230" y="445" width="340" height="30" fill="#f9f9f9" stroke="#cccccc" stroke-width="1" rx="4"/>
  <rect x="250" y="455" width="16" height="12" fill="#003366" rx="2"/>
  <text x="275" y="465" font-size="11" fill="#333333">Classification Accuracy (%)</text>
  
  <line x1="430" y1="461" x2="460" y2="461" stroke="#ff9900" stroke-width="3"/>
  <circle cx="445" cy="461" r="4" fill="#ff9900"/>
  <text x="470" y="465" font-size="11" fill="#333333">Latency (seconds)</text>
</svg>
"""
    file_path = os.path.join(OUTPUT_DIR, "fig7_type_accuracy_latency.svg")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated: {file_path}")


def create_svg_baseline_comparison():
    """Generate SVG for Fig 8: Baseline Model Head-to-Head Comparison."""
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="800" height="500" style="background:#ffffff; font-family: Arial, sans-serif;">
  <rect width="100%" height="100%" fill="#ffffff" />
  
  <!-- Title & Subtitle -->
  <text x="400" y="30" text-anchor="middle" font-size="18" font-weight="bold" fill="#003366">Fig. 8: Head-to-Head Baseline Comparison</text>
  <text x="400" y="50" text-anchor="middle" font-size="13" fill="#555555">Field Extraction Accuracy &amp; Data Privacy across Evaluation Baselines</text>
  
  <!-- Grid Lines -->
  <line x1="100" y1="380" x2="720" y2="380" stroke="#dddddd" stroke-width="1"/>
  <line x1="100" y1="310" x2="720" y2="310" stroke="#eeeeee" stroke-width="1"/>
  <line x1="100" y1="240" x2="720" y2="240" stroke="#eeeeee" stroke-width="1"/>
  <line x1="100" y1="170" x2="720" y2="170" stroke="#eeeeee" stroke-width="1"/>
  <line x1="100" y1="100" x2="720" y2="100" stroke="#eeeeee" stroke-width="1"/>
  
  <!-- Axes -->
  <line x1="100" y1="380" x2="720" y2="380" stroke="#333333" stroke-width="2"/>
  <line x1="100" y1="80" x2="100" y2="380" stroke="#003366" stroke-width="2"/>
  
  <!-- Y-Axis Labels -->
  <text x="90" y="385" text-anchor="end" font-size="11" fill="#003366">0%</text>
  <text x="90" y="315" text-anchor="end" font-size="11" fill="#003366">25%</text>
  <text x="90" y="245" text-anchor="end" font-size="11" fill="#003366">50%</text>
  <text x="90" y="175" text-anchor="end" font-size="11" fill="#003366">75%</text>
  <text x="90" y="105" text-anchor="end" font-size="11" fill="#003366" font-weight="bold">100%</text>
  <text x="45" y="230" text-anchor="middle" font-size="13" font-weight="bold" fill="#003366" transform="rotate(-90, 45, 230)">Extraction Accuracy (%)</text>

  <!-- Bars:
       1. Tesseract v5 + Rules (76.4% -> h=214 -> y=166)
       2. DigitCNN (86.4% -> h=242 -> y=138)
       3. Gemini 3.6 Flash (89.5% -> h=251 -> y=129)
       4. Local Qwen2.5-VL 7B (99.4% -> h=278 -> y=102)
  -->
  <!-- Tesseract -->
  <rect x="140" y="166" width="90" height="214" fill="#7f7f7f" rx="4"/>
  <text x="185" y="155" text-anchor="middle" font-size="12" font-weight="bold" fill="#555555">76.4%</text>
  <text x="185" y="405" text-anchor="middle" font-size="11" font-weight="bold" fill="#333333">Tesseract OCR</text>
  <text x="185" y="422" text-anchor="middle" font-size="10" fill="#666666">0.8 s / page</text>
  <rect x="145" y="432" width="80" height="18" fill="#d4edda" stroke="#28a745" stroke-width="1" rx="3"/>
  <text x="185" y="445" text-anchor="middle" font-size="10" font-weight="bold" fill="#155724">Local Private</text>

  <!-- DigitCNN -->
  <rect x="290" y="138" width="90" height="242" fill="#4682b4" rx="4"/>
  <text x="335" y="127" text-anchor="middle" font-size="12" font-weight="bold" fill="#4682b4">86.4%</text>
  <text x="335" y="405" text-anchor="middle" font-size="11" font-weight="bold" fill="#333333">DigitCNN</text>
  <text x="335" y="422" text-anchor="middle" font-size="10" fill="#666666">0.005 s / cell</text>
  <rect x="295" y="432" width="80" height="18" fill="#d4edda" stroke="#28a745" stroke-width="1" rx="3"/>
  <text x="335" y="445" text-anchor="middle" font-size="10" font-weight="bold" fill="#155724">Local Private</text>

  <!-- Gemini Flash -->
  <rect x="440" y="129" width="90" height="251" fill="#ff7f0e" rx="4"/>
  <text x="485" y="118" text-anchor="middle" font-size="12" font-weight="bold" fill="#ff7f0e">89.5%</text>
  <text x="485" y="405" text-anchor="middle" font-size="11" font-weight="bold" fill="#333333">Gemini Flash (Ref)</text>
  <text x="485" y="422" text-anchor="middle" font-size="10" fill="#666666">1.2 s / page</text>
  <rect x="445" y="432" width="80" height="18" fill="#f8d7da" stroke="#dc3545" stroke-width="1" rx="3"/>
  <text x="485" y="445" text-anchor="middle" font-size="10" font-weight="bold" fill="#721c24">Cloud (API Risk)</text>

  <!-- Proposed Local Qwen -->
  <rect x="590" y="102" width="90" height="278" fill="#008000" rx="4"/>
  <text x="635" y="91" text-anchor="middle" font-size="13" font-weight="bold" fill="#008000">99.4%</text>
  <text x="635" y="405" text-anchor="middle" font-size="11" font-weight="bold" fill="#008000">Proposed Local</text>
  <text x="635" y="422" text-anchor="middle" font-size="10" font-weight="bold" fill="#008000">3.4 s / page</text>
  <rect x="595" y="432" width="80" height="18" fill="#d4edda" stroke="#28a745" stroke-width="2" rx="3"/>
  <text x="635" y="445" text-anchor="middle" font-size="10" font-weight="bold" fill="#155724">Local Private ✓</text>

  <!-- Callout box over Proposed -->
  <path d="M 635 80 L 630 65 L 640 65 Z" fill="#008000"/>
  <rect x="535" y="35" width="200" height="30" fill="#e6ffe6" stroke="#008000" stroke-width="1.5" rx="4"/>
  <text x="635" y="54" text-anchor="middle" font-size="11" font-weight="bold" fill="#008000">Highest Accuracy &amp; 100% On-Premise</text>
</svg>
"""
    file_path = os.path.join(OUTPUT_DIR, "fig8_baseline_comparison.svg")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated: {file_path}")


if __name__ == "__main__":
    create_svg_threshold_curve()
    create_svg_type_accuracy_latency()
    create_svg_baseline_comparison()
    print("\nAll SVG visual graphs successfully created in output/graphs/!")
