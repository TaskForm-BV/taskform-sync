import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from config import Config
from services.sqlserver_service import SQLServerService
from services.firebird_service import FirebirdService
from services.api_service import APIService

class DataSyncGUI:
    """GUI for DataSync configuration."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("DataSync Configuratie")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # Load configuration
        self.config = Config()
        
        # Create UI
        self.create_widgets()
        self.load_config_to_ui()
    
    def create_widgets(self):
        """Create all UI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        row = 0
        
        # SQL Server Section
        sql_frame = ttk.LabelFrame(main_frame, text="SQL Server Instellingen", padding="10")
        sql_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        self.sql_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(sql_frame, text="SQL Server inschakelen", variable=self.sql_enabled_var).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(sql_frame, text="Connection String:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.sql_connection_entry = ttk.Entry(sql_frame, width=60)
        self.sql_connection_entry.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
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
        
        ttk.Label(api_frame, text="X-Api-Key:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.api_key_entry = ttk.Entry(api_frame, width=60, show="*")
        self.api_key_entry.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(api_frame, text="X-Tenant-ID:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.api_tenant_entry = ttk.Entry(api_frame, width=60)
        self.api_tenant_entry.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(api_frame, text="Test API", command=self.test_api).grid(row=6, column=0, sticky=tk.W, pady=5)
        
        # Sync Settings Section
        sync_frame = ttk.LabelFrame(main_frame, text="Synchronisatie Instellingen", padding="10")
        sync_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(sync_frame, text="Interval (minuten):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.interval_spinbox = ttk.Spinbox(sync_frame, from_=1, to=1440, width=10)
        self.interval_spinbox.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(sync_frame, text="Queries Map:").grid(row=1, column=0, sticky=tk.W, pady=5)
        queries_path_frame = ttk.Frame(sync_frame)
        queries_path_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.queries_path_entry = ttk.Entry(queries_path_frame, width=50)
        self.queries_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(queries_path_frame, text="Bladeren...", command=self.browse_queries_folder).pack(side=tk.LEFT, padx=5)
        
        # Save Button
        ttk.Button(main_frame, text="Opslaan & Sluiten", command=self.save_and_close, width=20).grid(row=row, column=0, columnspan=2, pady=20)
    
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
        self.interval_spinbox.set(self.config.get("sync.interval_minutes", 30))
        self.queries_path_entry.insert(0, self.config.get("sync.queries_folder", "queries"))
    
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
            self.queries_path_entry.delete(0, tk.END)
            self.queries_path_entry.insert(0, folder)
    
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
            self.config.set("sync.interval_minutes", int(self.interval_spinbox.get()))
            self.config.set("sync.queries_folder", self.queries_path_entry.get().strip())
            
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