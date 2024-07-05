import subprocess
import time

def start_server(script):
    print(f"Starting {script} server...")
    subprocess.Popen(['python', script])

if __name__ == '__main__':
    try:
        # Start product_service.py
        start_server('product_service.py')
        time.sleep(1)  # Add a delay to ensure the server starts before the next one
        
        # Start inventory_service.py
        start_server('inventory_service.py')
        time.sleep(1)  # Add a delay
        
        # Start order_service.py
        start_server('order_service.py')
        
        print("All servers started successfully.")
        
        # Keep the script running
        while True:
            time.sleep(10)  # Adjust as needed
    except KeyboardInterrupt:
        print("\nStopping servers...")
