import tkinter as tk
from tkinter import ttk, messagebox
import os
from auth.login import LoginFrame
from dashboards.admin_dashboard import AdminDashboard
from dashboards.employee_dashboard import EmployeeDashboard
from utils.db import init_database, get_db_connection, create_default_admin
from utils.hash_util import hash_password

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Initialize database
        init_database()
        
        # Create default admin if not exists
        create_default_admin(hash_password("admin123"))
        
        # Configure window
        self.title("Employee Management System")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        
        # Configure styles
        self.setup_styles()
        
        # Center window on screen
        self.center_window()
        
        # Initialize UI
        self.setup_ui()
    
    def setup_styles(self):
        """Configure custom styles for the application"""
        style = ttk.Style()
        
        # Configure theme colors
        style.configure(".",
                       background="#f5f6fa",
                       foreground="#2c3e50",
                       font=("Helvetica", 10))
        
        # Login frame style
        style.configure("Login.TFrame",
                       background="#f5f6fa")
        
        # Card style for login form
        style.configure("Card.TFrame",
                       background="white",
                       relief="solid",
                       borderwidth=1)
        
        # Accent button style
        style.configure("Accent.TButton",
                       background="#3498db",
                       foreground="white",
                       font=("Helvetica", 12),
                       padding=10)
        
        # Configure hover effects
        style.map("Accent.TButton",
                 background=[("active", "#2980b9")])
    
    def center_window(self):
        """Center the window on the screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_ui(self):
        """Setup the main UI"""
        # Create main container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Show login screen
        self.show_login()
    
    def show_login(self):
        """Show the login screen"""
        # Clear main container
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Create and show login frame
        login_frame = LoginFrame(self.main_container, self.on_login_success)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
    
    def on_login_success(self, user_data):
        """Handle successful login"""
        # Clear main container
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Show appropriate dashboard based on role
        if user_data['role'] == 'admin':
            dashboard = AdminDashboard(self.main_container, user_data, self.show_login)
        else:
            dashboard = EmployeeDashboard(self.main_container, user_data, self.show_login)
        
        dashboard.pack(fill=tk.BOTH, expand=True)

def main():
    # Start application
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main() 