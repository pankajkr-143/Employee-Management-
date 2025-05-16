import tkinter as tk
from tkinter import ttk, messagebox
from utils.db import get_db_connection
from utils.hash_util import verify_password

class LoginFrame(ttk.Frame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, padding="20")
        self.on_login_success = on_login_success
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the login form UI"""
        # Main container with background color
        self.configure(style="Login.TFrame")
        
        # Title with modern styling
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, pady=(0, 30))
        
        title_label = ttk.Label(title_frame, 
                              text="Employee Management System",
                              font=("Helvetica", 24, "bold"),
                              foreground="#2c3e50")
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame,
                                 text="Secure Login Portal",
                                 font=("Helvetica", 12),
                                 foreground="#7f8c8d")
        subtitle_label.pack(pady=(5, 0))
        
        # Login form container
        form_frame = ttk.Frame(self, style="Card.TFrame")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=50)
        
        # Username
        ttk.Label(form_frame, text="Username",
                 font=("Helvetica", 12)).pack(pady=(20, 5))
        self.username_entry = ttk.Entry(form_frame, width=30,
                                      font=("Helvetica", 12))
        self.username_entry.pack(pady=(0, 15))
        
        # Password
        ttk.Label(form_frame, text="Password",
                 font=("Helvetica", 12)).pack(pady=(0, 5))
        self.password_entry = ttk.Entry(form_frame, width=30, show="•",
                                      font=("Helvetica", 12))
        self.password_entry.pack(pady=(0, 20))
        
        # Role selection
        ttk.Label(form_frame, text="Select Role",
                 font=("Helvetica", 12)).pack(pady=(0, 5))
        self.role_var = tk.StringVar(value="employee")
        role_combo = ttk.Combobox(form_frame, textvariable=self.role_var,
                                values=["admin", "hr", "employee"],
                                state="readonly",
                                font=("Helvetica", 12),
                                width=28)
        role_combo.pack(pady=(0, 30))
        
        # Login button with modern styling
        login_button = ttk.Button(form_frame, text="Login",
                                command=self.login,
                                style="Accent.TButton",
                                width=20)
        login_button.pack(pady=(0, 20))
        
        # Bind Enter key to login
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.login())
        role_combo.bind("<Return>", lambda e: self.login())
        
        # Set focus to username entry
        self.username_entry.focus()
    
    def login(self):
        """Handle login attempt"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        role = self.role_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, password, role, employee_id 
            FROM users 
            WHERE username = ? AND role = ?
        """, (username, role))
        
        user = cursor.fetchone()
        conn.close()
        
        if user and verify_password(password, user['password']):
            self.on_login_success({
                'id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'employee_id': user['employee_id']
            })
        else:
            messagebox.showerror("Error", "Invalid credentials or role mismatch") 