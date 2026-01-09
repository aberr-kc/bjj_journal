# BJJ Journal Connect IQ Test App Setup

## Prerequisites
- Connect IQ SDK installed
- Visual Studio Code with Connect IQ extension
- Your computer's local IP address

## Setup Steps

### 1. Find Your Computer's IP Address
```bash
# Windows
ipconfig
# Look for "IPv4 Address" under your network adapter

# Example: 192.168.1.100
```

### 2. Update IP Address in Code
Edit `source/BJJTestApp.mc` line ~95:
```
var url = "http://YOUR_IP_HERE:8000/garmin/activity";
```
Replace `YOUR_IP_HERE` with your actual IP address.

### 3. Build the App
```bash
# In the connectiq directory
monkeyc -o BJJTest.prg -m manifest.xml -z resources/drawables/drawables.xml -z resources/strings/strings.xml source/BJJTestApp.mc
```

### 4. Install to Device/Simulator
```bash
# For simulator
connectiq

# For real device (via Garmin Express)
# Copy BJJTest.prg to your watch's APPS folder
```

## Testing Flow

1. **Start your journal server**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Run the Connect IQ app** on your watch/simulator

3. **Press START button** to send test activity data

4. **Check your journal** at http://localhost:3000/frontend.html

5. **Complete the journal entry** with your BJJ details

6. **Verify the data** appears correctly

## Troubleshooting

- **Connection failed**: Check IP address and ensure both devices on same network
- **Build errors**: Ensure SDK is fully installed and API levels downloaded
- **App won't start**: Check manifest.xml device compatibility

## Real Data Testing

To get real activity data:
1. Start a "BJJ" activity on your Garmin watch
2. Train for a few minutes
3. Run this Connect IQ app while activity is still active
4. It will capture real heart rate, duration, and calories