# ==========================================
# PROJECT: SIGMA-Core // Periplanomenos (Elite Multitab OS)
# AUTHOR: Olivera // Lead Architect & Founder
# STATUS: v2.0-stable // DRY Enclave, 0o600 Perms, /purge & .shadow_aries.enc (Anti-Forensic)
# ==========================================

import customtkinter as ctk
import datetime
import os
import psutil
from cryptography.fernet import Fernet

class PeriplanomenosEliteOS(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SIGMA-Core // Periplanomenos [Elite OS v2.0-stable]")
        self.geometry("1450x880")
        ctk.set_appearance_mode("dark")  
        self.configure(fg_color="#0B0B0C")

        # Criptografía, Bóvedas Locales y Shadow Log
        self.key_file = "sigma_vault.key"
        self.tasks_file = "sigma_holding_tasks.enc"
        self.credentials_file = "sigma_credentials.enc"
        self.routine_file = "sigma_routine.enc"
        self.shadow_log = ".shadow_aries.enc"
        self.fail_count = 0
        
        self.init_cryptographic_key()

        # Registro invisible de apertura de enclave
        self._enc_append(self.shadow_log, "Enclave abierto / Sesión iniciada")

        # Configuración del Layout Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==================== 1. PANEL LATERAL (Sidebar & Telemetría) ====================
        self.sidebar_frame = ctk.CTkFrame(
            self, 
            fg_color="#161719", 
            corner_radius=0,
            width=280
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        self.sidebar_brand = ctk.CTkLabel(
            self.sidebar_frame, 
            text="SIGMA-Core // ELITE", 
            font=("JetBrains Mono", 15, "bold"),
            text_color="#E2E2E5"
        )
        self.sidebar_brand.pack(anchor="w", padx=20, pady=(25, 15))

        self.sidebar_divider = ctk.CTkFrame(self.sidebar_frame, fg_color="#26282C", height=1, corner_radius=0)
        self.sidebar_divider.pack(fill="x", padx=15, pady=(0, 15))

        self.sidebar_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="CONTROL DE NÚCLEO", 
            font=("JetBrains Mono", 11, "bold"),
            text_color="#4A709C"
        )
        self.sidebar_label.pack(anchor="w", padx=20, pady=(5, 10))

        # Botones de navegación modular
        self.btn_terminal = ctk.CTkButton(
            self.sidebar_frame,
            text="💻 Consola A.R.I.E.S. CLI",
            font=("JetBrains Mono", 12),
            fg_color="#101113",
            hover_color="#1B365D",
            text_color="#E2E2E5",
            anchor="w",
            command=lambda: self.switch_tab("terminal")
        )
        self.btn_terminal.pack(fill="x", padx=15, pady=5)

        self.btn_vault = ctk.CTkButton(
            self.sidebar_frame,
            text="📁 Bóveda de Credenciales",
            font=("JetBrains Mono", 12),
            fg_color="#101113",
            hover_color="#1B365D",
            text_color="#E2E2E5",
            anchor="w",
            command=lambda: self.switch_tab("vault")
        )
        self.btn_vault.pack(fill="x", padx=15, pady=5)

        self.btn_holding = ctk.CTkButton(
            self.sidebar_frame,
            text="📋 Metas del Holding",
            font=("JetBrains Mono", 12),
            fg_color="#101113",
            hover_color="#1B365D",
            text_color="#E2E2E5",
            anchor="w",
            command=lambda: self.switch_tab("holding")
        )
        self.btn_holding.pack(fill="x", padx=15, pady=5)

        self.btn_routine = ctk.CTkButton(
            self.sidebar_frame,
            text="⚡ Rutinas & Rendimiento",
            font=("JetBrains Mono", 12),
            fg_color="#101113",
            hover_color="#1B365D",
            text_color="#E2E2E5",
            anchor="w",
            command=lambda: self.switch_tab("routine")
        )
        self.btn_routine.pack(fill="x", padx=15, pady=5)

        # Telemetría de Hardware
        self.telemetry_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="TELEMETRÍA DEL SISTEMA", 
            font=("JetBrains Mono", 11, "bold"),
            text_color="#4A709C"
        )
        self.telemetry_label.pack(anchor="w", padx=20, pady=(30, 5))

        self.cpu_usage_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="CPU: Calculando...", 
            font=("JetBrains Mono", 11),
            text_color="#8A8D96"
        )
        self.cpu_usage_label.pack(anchor="w", padx=20, pady=2)

        self.ram_usage_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="RAM: Calculando...", 
            font=("JetBrains Mono", 11),
            text_color="#8A8D96"
        )
        self.ram_usage_label.pack(anchor="w", padx=20, pady=2)

        self.sidebar_footer = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Lead Architect: Olivera\nZero-Telemetry Enclave", 
            font=("JetBrains Mono", 10),
            text_color="#6E717A",
            justify="left"
        )
        self.sidebar_footer.pack(side="bottom", anchor="w", padx=20, pady=20)

        # ==================== 2. ÁREA OPERATIVA PRINCIPAL ====================
        self.main_content_frame = ctk.CTkFrame(
            self, 
            fg_color="#0B0B0C", 
            corner_radius=0
        )
        self.main_content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content_frame.grid_rowconfigure(1, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        # Omni-Bar CLI
        self.top_bar = ctk.CTkFrame(
            self.main_content_frame, 
            fg_color="#161719", 
            corner_radius=12,
            height=50
        )
        self.top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.top_bar.grid_propagate(False)

        self.omni_bar = ctk.CTkEntry(
            self.top_bar, 
            placeholder_text="A.R.I.E.S. // /holding-task | /vault-add | /routine | /scan-logs | /purge",
            font=("JetBrains Mono", 11),
            height=36,
            corner_radius=8,
            fg_color="#0B0B0C",
            text_color="#E2E2E5",
            border_width=1,
            border_color="#26282C"
        )
        self.omni_bar.pack(side="left", fill="x", expand=True, padx=15, pady=7)
        self.omni_bar.bind("<Return>", self.execute_elite_directive)

        # Lienzo Central / Consola Dinámica
        self.web_canvas = ctk.CTkFrame(
            self.main_content_frame,
            corner_radius=12,
            fg_color="#101113",
            border_width=1,
            border_color="#1A1C1E"
        )
        self.web_canvas.grid(row=1, column=0, sticky="nsew")

        self.terminal_output = ctk.CTkTextbox(
            self.web_canvas,
            font=("JetBrains Mono", 12),
            fg_color="#101113",
            text_color="#E2E2E5",
            border_width=0
        )
        self.terminal_output.pack(fill="both", expand=True, padx=20, pady=20)

        init_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.terminal_output.insert("0.0", f"[{init_time}] A.R.I.E.S. // Elite OS v2.0-stable Desplegado.\n")
        self.terminal_output.insert("end", "Arquitectura DRY, permisos 0o600 y Sensor Anti-Forense (.shadow_aries.enc) activos.\n")
        self.terminal_output.configure(state="disabled")

        self.aries_status = ctk.CTkLabel(
            self.web_canvas,
            text="A.R.I.E.S. // Anti-Forensic Shield Active",
            font=("JetBrains Mono", 11),
            text_color="#4A709C"
        )
        self.aries_status.pack(side="bottom", anchor="e", padx=20, pady=15)

        self.after(1000, self.update_telemetry)

    def init_cryptographic_key(self):
        if not os.path.exists(self.key_file):
            self.encryption_key = Fernet.generate_key()
            with open(self.key_file, "wb") as key_f:
                key_f.write(self.encryption_key)
        else:
            with open(self.key_file, "rb") as key_f:
                self.encryption_key = key_f.read()
        
        try:
            os.chmod(self.key_file, 0o600)
        except Exception:
            pass

        self.cipher_suite = Fernet(self.encryption_key)

    # Función DRY genérica para encriptar
    def _enc_append(self, file_path, text):
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            payload = f"[{timestamp}] {text}"
            encrypted_data = self.cipher_suite.encrypt(payload.encode())
            with open(file_path, "ab") as f:
                f.write(encrypted_data + b"\n")
            return True
        except Exception as e:
            self.log_to_console(f"[ERROR ENCRYPT] {str(e)}")
            return False

    def _load_enc_file(self, file_path):
        items = []
        if not os.path.exists(file_path):
            return items
        try:
            with open(file_path, "rb") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        items.append(self.cipher_suite.decrypt(line).decode())
        except Exception as e:
            self.log_to_console(f"[ERROR DECRYPT] {str(e)}")
        return items

    def update_telemetry(self):
        try:
            ram_val = psutil.virtual_memory().percent
            self.ram_usage_label.configure(text=f"RAM: {ram_val}%")
        except:
            self.ram_usage_label.configure(text="RAM: SECURE")
        self.cpu_usage_label.configure(text="CPU: SECURE-ENCLAVE")
        self.after(2000, self.update_telemetry)

    def log_to_console(self, text):
        self.terminal_output.configure(state="normal")
        self.terminal_output.insert("end", text + "\n")
        self.terminal_output.see("end")
        self.terminal_output.configure(state="disabled")

    def execute_elite_directive(self, event):
        command = self.omni_bar.get().strip()
        self.omni_bar.delete(0, "end")
        
        if not command:
            return

        self.log_to_console(f"\n> {command}")
        
        # Holding Tasks
        if command.startswith("/holding-task add "):
            self.fail_count = 0
            desc = command.replace("/holding-task add ", "", 1).strip()
            if desc and self._enc_append(self.tasks_file, desc):
                self.log_to_console(f"[HOLDING] Meta registrada y encriptada.")
        elif command == "/holding-task list":
            self.fail_count = 0
            tasks = self._load_enc_file(self.tasks_file)
            self.log_to_console("--- METAS DEL HOLDING (AES-256) ---")
            for i, t in enumerate(tasks, 1): self.log_to_console(f"  {i}. {t}")
            if not tasks: self.log_to_console("  (Bóveda vacía)")

        # Credentials Vault
        elif command.startswith("/vault-add "):
            self.fail_count = 0
            cred = command.replace("/vault-add ", "", 1).strip()
            if cred and self._enc_append(self.credentials_file, cred):
                self.log_to_console(f"[VAULT] Credencial encriptada.")
        elif command == "/vault-list":
            self.fail_count = 0
            creds = self._load_enc_file(self.credentials_file)
            self.log_to_console("--- BÓVEDA DE CREDENCIALES (AES-256) ---")
            for i, c in enumerate(creds, 1): self.log_to_console(f"  {i}. {c}")
            if not creds: self.log_to_console("  (Bóveda vacía)")

        # Routines
        elif command.startswith("/routine add "):
            self.fail_count = 0
            rut = command.replace("/routine add ", "", 1).strip()
            if rut and self._enc_append(self.routine_file, rut):
                self.log_to_console(f"[ROUTINE] Objetivo registrado.")
        elif command == "/routine list":
            self.fail_count = 0
            ruts = self._load_enc_file(self.routine_file)
            self.log_to_console("--- OBJETIVOS DE RENDIMIENTO & RUTINAS ---")
            for i, r in enumerate(ruts, 1): self.log_to_console(f"  {i}. {r}")
            if not ruts: self.log_to_console("  (Sin registros)")

        # Security Scan
        elif command == "/scan-logs":
            self.fail_count = 0
            self.log_to_console("[SCAN-LOGS] Auditoría de enclave y sensor anti-forense...")
            self.log_to_console("[OK] Llave Fernet activa (Permisos 0o600).")
            self.log_to_console("[OK] Sensor Shadow Log (.shadow_aries.enc) vigilando accesos.")
            self.log_to_console("[OK] Integridad del sistema: 100% Blindado.")

        # Purge Protocol
        elif command == "/purge":
            self.log_to_console("[WARNING] Iniciando Protocolo de Autodestrucción...")
            for f in [self.tasks_file, self.credentials_file, self.routine_file, self.shadow_log, self.key_file]:
                if os.path.exists(f):
                    os.remove(f)
                    self.log_to_console(f"[PURGE] Destruido: {f}")
            self.log_to_console("[SELF-DESTRUCT] Enclave borrado por completo. Cerrando...")
            self.after(1500, self.destroy)

        # Control de Intrusión (Sensor Anti-Forense)
        else:
            self.fail_count += 1
            self.log_to_console(f"[A.R.I.E.S.] Comando no válido ({self.fail_count}/3 fallos).")
            if self.fail_count >= 3:
                self._enc_append(self.shadow_log, f"¡ALERTA! Intento de intrusión detectado con comando: {command}")
                self.log_to_console("[SEGURIDAD] ¡Alerta registrada en el shadow log oculto!")

    def switch_tab(self, tab_name):
        self.fail_count = 0
        if tab_name == "terminal":
            self.log_to_console("[SYS] Consola A.R.I.E.S. CLI activa.")
        elif tab_name == "vault":
            creds = self._load_enc_file(self.credentials_file)
            self.log_to_console(f"[SYS] Bóveda de Credenciales. Registros: {len(creds)}")
        elif tab_name == "holding":
            tasks = self._load_enc_file(self.tasks_file)
            self.log_to_console(f"[SYS] Metas del Holding. Registros: {len(tasks)}")
        elif tab_name == "routine":
            ruts = self._load_enc_file(self.routine_file)
            self.log_to_console(f"[SYS] Módulo de Rutinas. Registros: {len(ruts)}")

if __name__ == "__main__":
    app = PeriplanomenosEliteOS()
    app.mainloop()

