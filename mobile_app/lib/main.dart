import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

void main() {
  runApp(const AstroNavApp());
}

class AstroNavApp extends StatelessWidget {
  const AstroNavApp({super.key});
  
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AstroNav',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark(),
      home: const NavigationScreen(),
    );
  }
}

class NavigationScreen extends StatefulWidget {
  const NavigationScreen({super.key});

  @override
  State<NavigationScreen> createState() => _NavigationScreenState();
}

class _NavigationScreenState extends State<NavigationScreen> {
  bool isGnssDenied = false;
  
  LatLng currentPosition = const LatLng(28.6139, 77.2090); // New Delhi
  double currentSpeed = 45.0; // km/h
  
  // Simulated Sensor Data
  double accelX = 0, accelY = 0, accelZ = 9.81;
  double gyroX = 0, gyroY = 0, gyroZ = 0;
  
  Timer? sensorTimer;
  Timer? movementTimer;
  final Random random = Random();

  @override
  void initState() {
    super.initState();
    _startSimulation();
  }

  void _startSimulation() {
    sensorTimer = Timer.periodic(const Duration(milliseconds: 100), (timer) {
      if (!mounted) return;
      if (isGnssDenied) {
        setState(() {
          // Simulate raw high-frequency IMU vibrations
          accelX = (random.nextDouble() - 0.5) * 2;
          accelY = (random.nextDouble() - 0.5) * 2;
          accelZ = 9.81 + (random.nextDouble() - 0.5) * 1.5;
          
          gyroX = (random.nextDouble() - 0.5) * 0.1;
          gyroY = (random.nextDouble() - 0.5) * 0.1;
          gyroZ = (random.nextDouble() - 0.5) * 0.05;
        });
      }
    });

    movementTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (!mounted) return;
      setState(() {
        // Move slightly to simulate driving
        currentPosition = LatLng(
          currentPosition.latitude + 0.0001,
          currentPosition.longitude + 0.0001,
        );
      });
    });
  }

  @override
  void dispose() {
    sensorTimer?.cancel();
    movementTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // 1. Base Map Layer
          FlutterMap(
            options: MapOptions(
              initialCenter: currentPosition,
              initialZoom: 16.0,
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'com.sih.astronav',
              ),
              MarkerLayer(
                markers: [
                  Marker(
                    point: currentPosition,
                    width: 40,
                    height: 40,
                    child: Container(
                      decoration: BoxDecoration(
                        color: isGnssDenied ? Colors.red.withOpacity(0.3) : Colors.blue.withOpacity(0.3),
                        shape: BoxShape.circle,
                      ),
                      child: Center(
                        child: Container(
                          width: 15,
                          height: 15,
                          decoration: BoxDecoration(
                            color: isGnssDenied ? Colors.red : Colors.blue,
                            shape: BoxShape.circle,
                            border: Border.all(color: Colors.white, width: 2),
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),

          // 2. GNSS-Denied Warning Banner
          if (isGnssDenied)
            Positioned(
              top: 100,
              left: 20,
              right: 20,
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.shade900.withOpacity(0.9),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.redAccent),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.warning_amber_rounded, color: Colors.white),
                    SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        "GPS SIGNAL LOST\nSWITCHING TO INERTIAL DEAD RECKONING",
                        style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
              ),
            ),

          // 3. Top Toggle
          Positioned(
            top: 40,
            left: 0,
            right: 0,
            child: Center(
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: Colors.black87,
                  borderRadius: BorderRadius.circular(30),
                  boxShadow: const [BoxShadow(color: Colors.black54, blurRadius: 10)],
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Text("GPS", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                    const SizedBox(width: 8),
                    Switch(
                      value: isGnssDenied,
                      activeColor: Colors.red,
                      inactiveThumbColor: Colors.blue,
                      inactiveTrackColor: Colors.blue.withOpacity(0.5),
                      onChanged: (val) {
                        setState(() {
                          isGnssDenied = val;
                        });
                      },
                    ),
                    const SizedBox(width: 8),
                    const Text("AI INERTIAL", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  ],
                ),
              ),
            ),
          ),

          // 4. Live Sensor Overlay
          if (isGnssDenied)
            Positioned(
              bottom: 120,
              left: 20,
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.black.withOpacity(0.85),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.greenAccent.withOpacity(0.5)),
                  boxShadow: [BoxShadow(color: Colors.greenAccent.withOpacity(0.2), blurRadius: 10)],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Text("LIVE RAW IMU FEED", style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 12)),
                    const SizedBox(height: 8),
                    Text("ACCEL_X: ${accelX.toStringAsFixed(3)} m/s²", style: const TextStyle(color: Colors.white, fontFamily: 'monospace')),
                    Text("ACCEL_Y: ${accelY.toStringAsFixed(3)} m/s²", style: const TextStyle(color: Colors.white, fontFamily: 'monospace')),
                    Text("ACCEL_Z: ${accelZ.toStringAsFixed(3)} m/s²", style: const TextStyle(color: Colors.white, fontFamily: 'monospace')),
                    const SizedBox(height: 4),
                    Text("GYRO_X:  ${gyroX.toStringAsFixed(3)} rad/s", style: const TextStyle(color: Colors.white, fontFamily: 'monospace')),
                    Text("GYRO_Y:  ${gyroY.toStringAsFixed(3)} rad/s", style: const TextStyle(color: Colors.white, fontFamily: 'monospace')),
                    Text("GYRO_Z:  ${gyroZ.toStringAsFixed(3)} rad/s", style: const TextStyle(color: Colors.white, fontFamily: 'monospace')),
                  ],
                ),
              ),
            ),

          // 5. Bottom HUD
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: Container(
              height: 100,
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.bottomCenter,
                  end: Alignment.topCenter,
                  colors: [Colors.black, Colors.black.withOpacity(0.0)],
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(isGnssDenied ? "AI PREDICTED SPEED" : "GPS SPEED", style: const TextStyle(color: Colors.grey, fontSize: 12, fontWeight: FontWeight.bold)),
                      Text("${currentSpeed.toInt()} km/h", style: const TextStyle(color: Colors.white, fontSize: 32, fontWeight: FontWeight.bold)),
                    ],
                  ),
                  Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      const Text("LATENCY", style: TextStyle(color: Colors.grey, fontSize: 12, fontWeight: FontWeight.bold)),
                      Text(isGnssDenied ? "12 ms (Edge NPU)" : "450 ms (Sat)", style: TextStyle(color: isGnssDenied ? Colors.greenAccent : Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
