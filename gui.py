import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from config import Config
from services.sqlserver_service import SQLServerService
from services.firebird_service import FirebirdService
from services.api_service import APIService


class ToolTip:
    """Simple tooltip for Tkinter widgets."""

    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _event=None):
        if self.tipwindow:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 1
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT, background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=4, ipady=2)

    def hide(self, _event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


class DataSyncGUI:
    """GUI for DataSync configuration with field help and connection-string builder."""

    def __init__(self, root):
        self.root = root
        self.root.title("DataSync Configuratie")
        self.root.geometry("750x700")
        self.root.resizable(True, True)

        # Load configuration
        self.config = Config()

        # Create UI
        self.create_widgets()
        self.load_config_to_ui()

    def create_widgets(self):
        """Create all UI widgets."""
        # Create canvas and scrollbar
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Main container with padding
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        row = 0

        # SQL Server Section
        sql_frame = ttk.LabelFrame(main_frame, text="SQL Server Instellingen", padding="10")
        sql_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1

        self.sql_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(sql_frame, text="SQL Server inschakelen", variable=self.sql_enabled_var).grid(row=0, column=0, sticky=tk.W, pady=5)

        ttk.Label(sql_frame, text="Connection String:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.sql_connection_entry = ttk.Entry(sql_frame, width=80)
        self.sql_connection_entry.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        ToolTip(self.sql_connection_entry, "Voorbeeld: Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=MijnDB;Trusted_Connection=yes;")

        ttk.Button(sql_frame, text="Test SQL Server", command=self.test_sql_server).grid(row=3, column=0, sticky=tk.W, pady=5)

        # Firebird Section
        fb_frame = ttk.LabelFrame(main_frame, text="Firebird Instellingen", padding="10")
        fb_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1

        self.fb_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(fb_frame, text="Firebird inschakelen", variable=self.fb_enabled_var).grid(row=0, column=0, sticky=tk.W, pady=5)

        ttk.Label(fb_frame, text="Database Pad:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.fb_path_entry = ttk.Entry(fb_frame, width=60)
        self.fb_path_entry.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        ToolTip(self.fb_path_entry, "Volledig pad naar .fdb bestand of host:path, bijv. 192.168.1.100:C:\\data\\db.fdb")

        ttk.Label(fb_frame, text="Username:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.fb_username_entry = ttk.Entry(fb_frame, width=60)
        self.fb_username_entry.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(fb_frame, text="Password:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.fb_password_entry = ttk.Entry(fb_frame, width=60, show="*")
        self.fb_password_entry.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=5)

        ttk.Button(fb_frame, text="Test Firebird", command=self.test_firebird).grid(row=7, column=0, sticky=tk.W, pady=5)

        # API Section
        api_frame = ttk.LabelFrame(main_frame, text="API Instellingen", padding="10")
        api_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1

        ttk.Label(api_frame, text="Base URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.api_url_entry = ttk.Entry(api_frame, width=60)
        self.api_url_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        ToolTip(self.api_url_entry, "Voorbeeld: https://api.example.com/v1 (zonder trailing slash)")

        ttk.Label(api_frame, text="X-Api-Key:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.api_key_entry = ttk.Entry(api_frame, width=60, show="*")
        self.api_key_entry.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        ToolTip(self.api_key_entry, "API sleutel (geheim)")

        ttk.Label(api_frame, text="X-Tenant-ID:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.api_tenant_entry = ttk.Entry(api_frame, width=60)
        self.api_tenant_entry.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)
        ToolTip(self.api_tenant_entry, "Tenant of organisatie ID")

        ttk.Button(api_frame, text="Test API", command=self.test_api).grid(row=6, column=0, sticky=tk.W, pady=5)

        # Sync Settings Section
        sync_frame = ttk.LabelFrame(main_frame, text="Synchronisatie Instellingen", padding="10")
        sync_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1

        ttk.Label(sync_frame, text="Queries Map:").grid(row=0, column=0, sticky=tk.W, pady=5)
        queries_path_frame = ttk.Frame(sync_frame)
        queries_path_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.queries_path_entry = ttk.Entry(queries_path_frame, width=50)
        self.queries_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ToolTip(self.queries_path_entry, "Pad naar map met .sql bestanden. Standaard: queries")

        ttk.Button(queries_path_frame, text="Bladeren...", command=self.browse_queries_folder).pack(side=tk.LEFT, padx=5)

        ttk.Label(sync_frame, text="Log Level:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.log_level_combo = ttk.Combobox(sync_frame, values=["DEBUG", "INFO", "WARNING", "ERROR"], width=15, state="readonly")
        self.log_level_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        ToolTip(self.log_level_combo, "DEBUG = alles, INFO = standaard, WARNING = alleen waarschuwingen, ERROR = alleen fouten")

        ttk.Label(sync_frame, text="Batch Size:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.batch_size_spinbox = ttk.Spinbox(sync_frame, from_=10, to=10000, width=15)
        self.batch_size_spinbox.grid(row=3, column=1, sticky=tk.W, pady=5)
        ToolTip(self.batch_size_spinbox, "Aantal records per API call. Standaard: 1000. Verhoog bij grote datasets, verlaag bij timeouts.")

        self.dry_run_var = tk.BooleanVar()
        ttk.Checkbutton(sync_frame, text="Dry-run modus (test zonder API POST, genereert alleen JSON)", variable=self.dry_run_var).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        ToolTip(sync_frame.winfo_children()[-1], "Haalt data op en genereert JSON, maar POST niet naar API. Handig voor testen.")

        # Save Button
        ttk.Button(main_frame, text="Opslaan & Sluiten", command=self.save_and_close, width=20).grid(row=row, column=0, columnspan=2, pady=20)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def load_config_to_ui(self):
        """Load configuration values into UI fields."""
        # SQL Server
        self.sql_enabled_var.set(self.config.get("sql_server.enabled", False))
        self.sql_connection_entry.insert(0, self.config.get("sql_server.connection_string", ""))

        # Firebird
        self.fb_enabled_var.set(self.config.get("firebird.enabled", False))
        self.fb_path_entry.insert(0, self.config.get("firebird.database_path", ""))
        self.fb_username_entry.insert(0, self.config.get("firebird.username", ""))
        self.fb_password_entry.insert(0, self.config.get("firebird.password", ""))

        # API
        self.api_url_entry.insert(0, self.config.get("api.base_url", ""))
        self.api_key_entry.insert(0, self.config.get("api.api_key", ""))
        self.api_tenant_entry.insert(0, self.config.get("api.tenant_id", ""))

        # Sync
        self.queries_path_entry.insert(0, self.config.get("sync.queries_folder", "queries"))
        self.log_level_combo.set(self.config.get("sync.log_level", "INFO"))
        self.batch_size_spinbox.set(self.config.get("sync.batch_size", 1000))
        self.dry_run_var.set(self.config.get("sync.dry_run", False))

    def test_sql_server(self):
        """Test SQL Server connection."""
        connection_string = self.sql_connection_entry.get().strip()

        if not connection_string:
            messagebox.showerror("Fout", "Voer een connection string in")
            return

        try:
            service = SQLServerService(connection_string)
            service.test_connection()
            messagebox.showinfo("Succes", "SQL Server verbinding succesvol!")
        except Exception as e:
            messagebox.showerror("Fout", f"SQL Server verbinding mislukt:\n{str(e)}")

    def test_firebird(self):
        """Test Firebird connection."""
        db_path = self.fb_path_entry.get().strip()
        username = self.fb_username_entry.get().strip()
        password = self.fb_password_entry.get().strip()

        if not all([db_path, username, password]):
            messagebox.showerror("Fout", "Vul alle Firebird velden in")
            return

        try:
            service = FirebirdService(db_path, username, password)
            service.test_connection()
            messagebox.showinfo("Succes", "Firebird verbinding succesvol!")
        except Exception as e:
            messagebox.showerror("Fout", f"Firebird verbinding mislukt:\n{str(e)}")

    def test_api(self):
        """Test API connection."""
        base_url = self.api_url_entry.get().strip()
        api_key = self.api_key_entry.get().strip()
        tenant_id = self.api_tenant_entry.get().strip()

        if not all([base_url, api_key, tenant_id]):
            messagebox.showerror("Fout", "Vul alle API velden in")
            return

        try:
            service = APIService(base_url, api_key, tenant_id)
            service.test_connection()
            messagebox.showinfo("Succes", "API verbinding succesvol!")
        except Exception as e:
            messagebox.showerror("Fout", f"API verbinding mislukt:\n{str(e)}")

    def browse_queries_folder(self):
        """Browse for queries folder."""
        folder = filedialog.askdirectory(title="Selecteer Queries Map")
        if folder:
            # Normalize path to Windows format (backslashes)
            normalized_path = os.path.normpath(folder)
            self.queries_path_entry.delete(0, tk.END)
            self.queries_path_entry.insert(0, normalized_path)

    def save_and_close(self):
        """Save configuration and close window."""
        try:
            # Validate at least one database is enabled
            if not self.sql_enabled_var.get() and not self.fb_enabled_var.get():
                messagebox.showwarning("Waarschuwing", "Schakel minimaal één database in")
                return

            # Validate API settings
            if not all([self.api_url_entry.get().strip(), 
                       self.api_key_entry.get().strip(), 
                       self.api_tenant_entry.get().strip()]):
                messagebox.showerror("Fout", "Vul alle API velden in")
                return

            # Save SQL Server settings
            self.config.set("sql_server.enabled", self.sql_enabled_var.get())
            self.config.set("sql_server.connection_string", self.sql_connection_entry.get().strip())

            # Save Firebird settings
            self.config.set("firebird.enabled", self.fb_enabled_var.get())
            self.config.set("firebird.database_path", self.fb_path_entry.get().strip())
            self.config.set("firebird.username", self.fb_username_entry.get().strip())
            self.config.set("firebird.password", self.fb_password_entry.get().strip())

            # Save API settings
            self.config.set("api.base_url", self.api_url_entry.get().strip())
            self.config.set("api.api_key", self.api_key_entry.get().strip())
            self.config.set("api.tenant_id", self.api_tenant_entry.get().strip())

            # Save sync settings
            self.config.set("sync.queries_folder", self.queries_path_entry.get().strip())
            self.config.set("sync.log_level", self.log_level_combo.get())
            self.config.set("sync.batch_size", int(self.batch_size_spinbox.get()))
            self.config.set("sync.dry_run", self.dry_run_var.get())

            # Save to file
            self.config.save()

            messagebox.showinfo("Succes", "Configuratie opgeslagen!")
            self.root.quit()

        except Exception as e:
            messagebox.showerror("Fout", f"Fout bij opslaan:\n{str(e)}")


def main():
    """Main entry point for GUI."""
    root = tk.Tk()
    app = DataSyncGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()