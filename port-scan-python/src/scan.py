import socket
import tkinter as tk
import concurrent.futures
import threading

def scan_ports():
    target = entry_target.get()
    start_str = entry_start.get()
    end_str = entry_end.get()

    # validation
    if not start_str.isdigit() or not end_str.isdigit():
        result_box.insert(tk.END, "Invalid port numbers they must be positive integer\n")
        return

    start_port = int(start_str)
    end_port = int(end_str)

    if start_port < 0 or end_port > 65535 or start_port > end_port:
        result_box.insert(tk.END, "Invalid port range (0 - 65535)\n")
        return

    MAX_PORTS = 65536
    if (end_port - start_port + 1) > MAX_PORTS:
        result_box.insert(tk.END, f"Maximum of {MAX_PORTS} ports per scan\n")
        return

    result_box.delete(1.0, tk.END)

    total_ports = end_port - start_port + 1
    scanned = 0

    def run_scan():
        nonlocal scanned

        def scan_port(port):
            nonlocal scanned
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.2)

                result = sock.connect_ex((target, port))
                sock.close()

                if result == 0:
                    root.after(0, lambda p=port: result_box.insert(tk.END, f"[OPEN] {p}\n"))

            except:
                pass

            scanned += 1
            root.after(0, lambda: progress_label.config(
                text=f"Progresso: {scanned}/{total_ports}"
            ))

        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            executor.map(scan_port, range(start_port, end_port + 1))

    threading.Thread(target=run_scan, daemon=True).start()


# GUI
root = tk.Tk()
root.title("Port Scanner")

tk.Label(root, text="Target (IP or Domain)").pack()
entry_target = tk.Entry(root)
entry_target.pack()

tk.Label(root, text="Initial port:").pack()
entry_start = tk.Entry(root)
entry_start.pack()

tk.Label(root, text="Final port:").pack()
entry_end = tk.Entry(root)
entry_end.pack()

scan_button = tk.Button(root, text="Scan", command=scan_ports)
scan_button.pack()

progress_label = tk.Label(root, text="Progress: 0/0")
progress_label.pack()

result_box = tk.Text(root, height=15, width=50)
result_box.pack()

root.mainloop()