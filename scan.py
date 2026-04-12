import socket
import tkinter as tk
import concurrent.futures
import threading

common_ports = [21, 22, 25, 80, 443, 8080]

def scan_ports():
    target = entry_target.get()
    start_str = entry_start.get()
    end_str = entry_end.get()

    if not start_str.isdigit() or not end_str.isdigit():
        result_box.insert(tk.END, "Invalid port numbers. Please enter valid integers.\n")
        return

    start_port = int(start_str)
    end_port = int(end_str)

    if start_port < 0 or end_port > 65535 or start_port > end_port:
        result_box.insert(tk.END, "Invalid port range 0-65535\n")
        return

    try:
        target_ip = socket.gethostbyname(target)
    except:
        result_box.insert(tk.END, "Invalid target\n")
        return

    result_box.delete(1.0, tk.END)

    total_ports = end_port - start_port + 1
    scanned = 0
    lock = threading.Lock()

    def run_scan():
        nonlocal scanned

        def scan_port(port):
            nonlocal scanned

            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.2)

                result = sock.connect_ex((target_ip, port))

                if result == 0:
                    banner = "Unknown"

                    try:
                        if port in common_ports:
                            sock.send(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
                            banner = sock.recv(1024).decode(errors="ignore")
                    except:
                        pass

                    root.after(0, lambda p=port, b=banner:
                        result_box.insert(tk.END, f"[OPEN] {p} | {b[:50]}\n"))

                sock.close()

            except socket.error:
                pass

            with lock:
                scanned += 1

            root.after(0, lambda:
                progress_label.config(text=f"Progresso: {scanned}/{total_ports}")
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            executor.map(scan_port, range(start_port, end_port + 1))

    threading.Thread(target=run_scan, daemon=True).start()

# GUI
root = tk.Tk()
root.title("Port Scanner")

tk.Label(root, text="Target").pack()
entry_target = tk.Entry(root)
entry_target.pack()

tk.Label(root, text="Start Port").pack()
entry_start = tk.Entry(root)
entry_start.pack()

tk.Label(root, text="End Port").pack()
entry_end = tk.Entry(root)
entry_end.pack()

tk.Button(root, text="Scan", command=scan_ports).pack()

progress_label = tk.Label(root, text="Progress: 0/0")
progress_label.pack()

result_box = tk.Text(root, height=15, width=50)
result_box.pack()


root.mainloop()