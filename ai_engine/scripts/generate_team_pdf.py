from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Team Briefing: GNSS-Denied Navigation (ISRO SIH 2026)', 0, 1, 'C')
        self.set_font('Arial', 'I', 12)
        self.cell(0, 10, 'The Dummy-Proof Guide to Our Project', 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_subtitle(self, subtitle):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, subtitle, 0, 1, 'L')
        self.ln(2)

    def chapter_body(self, text):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 8, text)
        self.ln(4)

    def add_point(self, title, description):
        self.set_font('Arial', 'B', 12)
        self.cell(10, 8, chr(149)) # bullet
        self.cell(0, 8, title, 0, 1)
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 8, "    " + description)
        self.ln(2)

pdf = PDF()
pdf.add_page()

pdf.chapter_title('1. What is the Problem?')
pdf.chapter_body('When you drive into a long tunnel, your phone loses connection to the GPS satellites in space (this is called a GNSS Blackout). When GPS is lost, map apps stop working. ISRO wants us to build an app that continues to track the car perfectly, even inside the tunnel, using only the smartphone. We cannot plug anything into the car.')

pdf.chapter_title('2. The Jargon Buster (Cheat Sheet)')
pdf.chapter_body('If a judge asks about a complex term, here is how you explain it in plain English:')

pdf.chapter_subtitle('What is an IMU?')
pdf.add_point('The Tech Definition:', 'Inertial Measurement Unit.')
pdf.add_point('The Simple Answer:', 'The chips inside every smartphone that detect movement. It includes the Accelerometer (vibrations) and Gyroscope (rotation). We use the IMU to guess where the car is going.')

pdf.chapter_subtitle('What is PCA (Gravity Alignment)?')
pdf.add_point('The Tech Definition:', 'Principal Component Analysis for sensor orientation.')
pdf.add_point('The Simple Answer:', 'If a phone is thrown in a cupholder tilted, the sensors get confused. PCA is a math trick we use to detect which way gravity is pulling, so we can digitally rotate the phone\'s sensors to lay flat with the road.')

pdf.chapter_subtitle('What is the 1D-CNN?')
pdf.add_point('The Tech Definition:', '1-Dimensional Convolutional Neural Network.')
pdf.add_point('The Simple Answer:', 'Our AI Speedometer. Using math to find speed from sensors causes huge errors. Instead, our AI listens to the physical vibrations of the car through the phone to accurately guess the speed.')

pdf.chapter_subtitle('What is the UKF?')
pdf.add_point('The Tech Definition:', 'Unscented Kalman Filter.')
pdf.add_point('The Simple Answer:', 'A Sensor Fusion algorithm. It acts like a strict manager that takes our imperfect AI speed and imperfect gyroscope direction, smooths out the spikes, and gives us a highly accurate (X, Y) coordinate.')

pdf.chapter_subtitle('What is the HMM (Map-Matching)?')
pdf.add_point('The Tech Definition:', 'Hidden Markov Model using the Viterbi Algorithm.')
pdf.add_point('The Simple Answer:', 'Over a 2-kilometer tunnel, coordinates might drift. The HMM looks at the digital map of the tunnel and mathematically snaps our drifting coordinates back into the middle of the correct lane.')

pdf.chapter_title('3. How the Whole System Flows')
flow = [
    "1. GPS Dies: The app realizes satellite connection is gone.",
    "2. Sensors Kick In: The app reads the phone's IMU.",
    "3. Gravity Fix: PCA math fixes the phone's tilted angle.",
    "4. AI Speed Guess: 1D-CNN AI feels vibrations and estimates speed.",
    "5. Gyroscope Turn: Gyroscope tracks direction changes.",
    "6. Position Calculation: UKF merges speed and direction for new location.",
    "7. Lane Snapping: HMM snaps location perfectly into the center of the lane."
]
for step in flow:
    pdf.chapter_body(step)

pdf.chapter_title('4. Why Our Solution is Better')
pdf.add_point('No Car Connection Needed:', 'Works on any car because it only relies on the smartphone.')
pdf.add_point('AI over Math:', 'Bypasses traditional error-prone Dead Reckoning by using Neural Networks.')
pdf.add_point('Battery Efficient:', 'Runs entirely on the phone\'s edge processor (ONNX) with zero internet latency.')

output_path = r'C:\Users\sarth\.gemini\antigravity-ide\brain\764d65f3-fa9a-4279-a465-a77cf4a0457a\team_briefing.pdf'
pdf.output(output_path, 'F')
print(f"PDF successfully generated at {output_path}")
