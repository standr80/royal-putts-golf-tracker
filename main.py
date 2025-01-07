from app import app
import socket

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('0.0.0.0', port))
            return False
        except socket.error:
            return True

if __name__ == "__main__":
    port = 5000
    # Try alternate ports if 5000 is in use
    while is_port_in_use(port) and port < 5010:
        port += 1

    if port < 5010:
        app.run(host="0.0.0.0", port=port, debug=True)
    else:
        print("Could not find an available port between 5000-5009")
        exit(1)