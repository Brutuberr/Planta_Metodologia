import socket
import concurrent.futures
import multiprocessing

def check_port(ip, port):
    """Attempt to connect to a port on a given IP address."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        sock.close()
        return port if result == 0 else None
    except socket.error:
        return None

def scan_ports(ip, ports):
    """Scan a list of ports on an IP using multithreading."""
    open_ports = []
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(lambda port: check_port(ip, port), ports)
    
    for port in ports:
        if port in results:
            print(f"Port {port} is open.")
            open_ports.append(port)
        else:
            print(f"Port {port} is closed.")
    
    return open_ports

def chunked_port_scan(ip, start_port, end_port, num_processes):
    """Divide the port range into chunks and use multiprocessing for each chunk."""
    port_range = range(start_port, end_port + 1)
    chunk_size = len(port_range) // num_processes
    chunks = [port_range[i:i + chunk_size] for i in range(0, len(port_range), chunk_size)]

    with multiprocessing.Pool(num_processes) as pool:
        results = pool.starmap(scan_ports, [(ip, chunk) for chunk in chunks])

    # Flatten the results
    open_ports = [port for sublist in results for port in sublist]
    
    if open_ports:
        print(f"\nOpen ports: {open_ports}")
    else:
        print("\nNo open ports found.")

if __name__ == "__main__":
    target = input("Enter the IP address or domain to scan: ") or '201.235.180.98'
    start_port = int(input("Enter the start port (default 1): ") or 1)
    end_port = int(input("Enter the end port (default 65535): ") or 65535)
    num_processes = int(input("Enter number of processes to use (default 4): ") or 4)

    chunked_port_scan(target, start_port, end_port, num_processes)