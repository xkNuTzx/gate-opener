#!/bin/bash
cat > config.json <<EOF
{
  "rtsp_url": "$(read -p 'RTSP URL: ' r && echo $r)",
  "gpio_pin": 18,
  "model": "demo.tflite",
  "threshold": 0.9,
  "trigger_duration": 2,
  "cooldown": 10
}
EOF
echo "config.json created."
