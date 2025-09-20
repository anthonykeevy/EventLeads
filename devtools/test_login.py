import subprocess
import json
import shlex
import time

def test_login():
    """
    Tests the login endpoint with a predefined payload.
    Captures and prints the response and any errors.
    """
    # Give the server a moment to start up
    time.sleep(2)

    command = """
    curl -X 'POST' \
      'http://localhost:8000/auth/login' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "email": "ant@keevy.com",
      "password": "test1234"
    }'
    """
    
    # Use shlex to handle shell-style quoting
    args = shlex.split(command)
    
    try:
        # Execute the command
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=False  # Do not raise exception on non-zero exit codes
        )
        
        print("--- Test Runner Output ---")
        
        # Print stdout
        if result.stdout:
            print("Response:")
            try:
                # Try to pretty-print if it's JSON
                print(json.dumps(json.loads(result.stdout), indent=2))
            except json.JSONDecodeError:
                print(result.stdout)
        
        # Print stderr
        if result.stderr:
            print("\nErrors:")
            print(result.stderr)
            
        print(f"\nExit Code: {result.returncode}")
        print("--------------------------")

    except FileNotFoundError:
        print("Error: 'curl' command not found. Please ensure curl is installed and in your PATH.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_login()

