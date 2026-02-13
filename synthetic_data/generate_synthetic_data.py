import random
import time

def generate_data():
    while True:
        data = {"sensor_id": "sensor-1", "value": random.random()}
        print(f"Generated: {data}")
        time.sleep(1)

if __name__ == "__main__":
    generate_data()
