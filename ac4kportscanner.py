import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import socket
import threading

class ACPortScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("ac's port scanner 0.1")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        # Style configuration for black buttons
        style = ttk.Style()
        style.configure("Black.TButton",
                        background="black",
                        foreground="white",
                        borderwidth=1,
                        focusthickness=3,
                        focuscolor="none")
        style.map("Black.TButton",
                  background=[('active', '#333333'), ('pressed', '#222222')],
                  foreground=[('active', 'white'), ('pressed', 'white')])

        self.root.configure(bg='#f0f0f0')
        self.default_fg = 'blue'

        # Host input
        tk.Label(root, text="Target Host:", fg=self.default_fg, bg='#f0f0f0',
                 font=('TkDefaultFont', 10, 'bold')).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.host_entry = tk.Entry(root, width=30, fg=self.default_fg, insertbackground='blue')
        self.host_entry.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        self.host_entry.insert(0, "localhost")

        # Port range
        tk.Label(root, text="Port Range:", fg=self.default_fg, bg='#f0f0f0',
                 font=('TkDefaultFont', 10, 'bold')).grid(row=1, column=0, padx=10, pady=5, sticky='w')
        range_frame = tk.Frame(root, bg='#f0f0f0')
        range_frame.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        self.start_port = tk.Entry(range_frame, width=8, fg=self.default_fg, insertbackground='blue')
        self.start_port.pack(side='left')
        self.start_port.insert(0, "1")
        tk.Label(range_frame, text=" to ", fg=self.default_fg, bg='#f0f0f0').pack(side='left')
        self.end_port = tk.Entry(range_frame, width=8, fg=self.default_fg, insertbackground='blue')
        self.end_port.pack(side='left')
        self.end_port.insert(0, "1024")

        # Button frame with ttk buttons using Black style
        btn_frame = tk.Frame(root, bg='#f0f0f0')
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        self.scan_button = ttk.Button(btn_frame, text="Scan Ports", style="Black.TButton",
                                      command=self.start_scan)
        self.scan_button.pack(side='left', padx=5)
        self.stop_button = ttk.Button(btn_frame, text="Stop", style="Black.TButton",
                                      command=self.stop_scan)
        self.stop_button.pack(side='left', padx=5)
        self.clear_button = ttk.Button(btn_frame, text="Clear", style="Black.TButton",
                                       command=self.clear_output)
        self.clear_button.pack(side='left', padx=5)
        # Disable stop button initially
        self.stop_button.state(['disabled'])

        # Output area
        self.output = scrolledtext.ScrolledText(root, width=65, height=15, fg=self.default_fg,
                                                bg='white', insertbackground='blue',
                                                font=('Consolas', 9))
        self.output.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.scanning = False
        self.thread = None

    def scan_port(self, host, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False

    def scan_range(self, host, start, end):
        open_ports = []
        for port in range(start, end + 1):
            if not self.scanning:
                break
            if self.scan_port(host, port):
                open_ports.append(port)
                self.output.insert(tk.END, f"Port {port} : OPEN\n")
                self.output.see(tk.END)
            self.root.update_idletasks()
        return open_ports

    def start_scan(self):
        host = self.host_entry.get().strip()
        if not host:
            messagebox.showerror("Error", "Please enter a target host.")
            return
        try:
            start = int(self.start_port.get())
            end = int(self.end_port.get())
        except ValueError:
            messagebox.showerror("Error", "Port numbers must be integers.")
            return
        if start < 1 or end > 65535 or start > end:
            messagebox.showerror("Error", "Invalid port range (1-65535, start <= end).")
            return

        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, f"Scanning {host} ports {start}-{end}...\n")
        self.scanning = True
        self.scan_button.state(['disabled'])
        self.stop_button.state(['!disabled'])

        self.thread = threading.Thread(target=self._scan_thread, args=(host, start, end))
        self.thread.daemon = True
        self.thread.start()

    def _scan_thread(self, host, start, end):
        try:
            self.scan_range(host, start, end)
        except Exception as e:
            self.output.insert(tk.END, f"Error: {e}\n")
        finally:
            self.scanning = False
            self.root.after(0, self._scan_finished)

    def _scan_finished(self):
        self.scan_button.state(['!disabled'])
        self.stop_button.state(['disabled'])
        self.output.insert(tk.END, "Scan completed.\n")

    def stop_scan(self):
        self.scanning = False
        self.stop_button.state(['disabled'])

    def clear_output(self):
        self.output.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ACPortScanner(root)
    root.mainloop()