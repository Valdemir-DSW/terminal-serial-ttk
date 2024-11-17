import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
from datetime import datetime
import threading

class SerialTerminal:
    def __init__(self, root):
        self.root = root
        self.root.title("Terminal Serial")
      
        # Configurações de Serial
        self.serial_port = None
        self.running = False

        # Combobox para portas seriais
        self.port_label = tk.Label(root, text="Porta Serial:")
        self.port_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.port_combo = ttk.Combobox(root, values=self.get_serial_ports(), state="readonly")
        self.port_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Caixa de marcação para exibir a hora de chegada
        self.timestamp_var = tk.BooleanVar()
        self.timestamp_check = ttk.Checkbutton(root, text="Exibir Hora de Chegada", variable=self.timestamp_var)
        self.timestamp_check.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        # Caixa de marcação para exibir o que foi enviado
        self.show_sent_var = tk.BooleanVar()
        self.show_sent_check = ttk.Checkbutton(root, text="Exibir Dados Enviados", variable=self.show_sent_var)
        self.show_sent_check.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Área de exibição de dados recebidos
        self.output_text = tk.Text(root, wrap='word', height=15, width=50)
        self.output_text.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        
        # Entrada de dados para envio
        self.input_entry = ttk.Entry(root, width=40)
        self.input_entry.grid(row=4, column=0, padx=5, pady=5)
        self.send_button = ttk.Button(root, text="Enviar", command=self.send_data)
        self.send_button.grid(row=4, column=1, padx=5, pady=5)

        # Botão para iniciar/parar comunicação serial
        self.connect_button = ttk.Button(root, text="Conectar", command=self.toggle_connection)
        self.connect_button.grid(row=5, column=0, columnspan=2, pady=5)

    def get_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [f"{port.device} - {port.description}" for port in ports]

    def toggle_connection(self):
        if self.running:
            self.stop_serial()
            self.connect_button.config(text="Conectar")
        else:
            self.start_serial()
            self.connect_button.config(text="Desconectar")

    def start_serial(self):
        selected_port = self.port_combo.get().split(" - ")[0]
        try:
            self.serial_port = serial.Serial(selected_port, 9600, timeout=1)
            self.running = True
            self.read_thread = threading.Thread(target=self.read_data, daemon=True)
            self.read_thread.start()
        except serial.SerialException as e:
            self.output_text.insert(tk.END, f"Erro ao conectar: {e}\n")

    def stop_serial(self):
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

    def read_data(self):
        while self.running:
            if self.serial_port.in_waiting > 0:
                data = self.serial_port.readline().decode('utf-8').strip()
                if data:
                    timestamp = datetime.now().strftime("%H:%M:%S") if self.timestamp_var.get() else ""
                    message = f"{timestamp} - {data}" if timestamp else data
                    self.output_text.insert(tk.END, f"> {message}\n")
                    self.output_text.see(tk.END)

    def send_data(self):
        data = self.input_entry.get()
        if self.serial_port and self.serial_port.is_open and data:
            self.serial_port.write(data.encode('utf-8'))
            if self.show_sent_var.get():
                timestamp = datetime.now().strftime("%H:%M:%S") if self.timestamp_var.get() else ""
                message = f"{timestamp} - {data}" if timestamp else data
                self.output_text.insert(tk.END, f"< {message}\n")
                self.output_text.see(tk.END)
            self.input_entry.delete(0, tk.END)

    def on_closing(self):
        self.stop_serial()
        self.root.destroy()

# Inicialização da interface
root = tk.Tk()
app = SerialTerminal(root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()
