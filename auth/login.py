import tkinter as tk
from tkinter import ttk, messagebox
from utils.db import get_db_connection
from utils.hash_util import verify_password
from PIL import Image, ImageTk

class LoginFrame(ttk.Frame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, padding="20")
        self.on_login_success = on_login_success
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the login form UI"""
        self.configure(style="Login.TFrame")
        # HEADER
        header_frame = ttk.Frame(self, style='Card.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        logo_img = Image.open('assets/images/logo.jpg')
        logo_img = logo_img.resize((80, 40), Image.Resampling.LANCZOS)
        logo = ImageTk.PhotoImage(logo_img)
        logo_label = ttk.Label(header_frame, image=logo)
        logo_label.image = logo
        logo_label.pack(side=tk.LEFT, padx=(10, 10))
        ttk.Label(header_frame, text="Employee Management System", font=("Segoe UI", 18, "bold"), foreground="black").pack(side=tk.LEFT, padx=(0, 20))
        # Subtitle
        subtitle_label = ttk.Label(header_frame, text="Secure Login Portal", font=("Segoe UI", 12), foreground="black")
        subtitle_label.pack(side=tk.LEFT, padx=(0, 20))
        # Login form container
        form_frame = ttk.Frame(self, style="Card.TFrame")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=50)
        ttk.Label(form_frame, text="Username", font=("Helvetica", 12), foreground="black").pack(pady=(20, 5))
        self.username_entry = ttk.Entry(form_frame, width=30, font=("Helvetica", 12))
        self.username_entry.pack(pady=(0, 15))
        ttk.Label(form_frame, text="Password", font=("Helvetica", 12), foreground="black").pack(pady=(0, 5))
        self.password_entry = ttk.Entry(form_frame, width=30, show="•", font=("Helvetica", 12))
        self.password_entry.pack(pady=(0, 20))
        ttk.Label(form_frame, text="Select Role", font=("Helvetica", 12), foreground="black").pack(pady=(0, 5))
        self.role_var = tk.StringVar(value="employee")
        role_combo = ttk.Combobox(form_frame, textvariable=self.role_var, values=["admin", "hr", "employee"], state="readonly", font=("Helvetica", 12), width=28)
        role_combo.pack(pady=(0, 30))
        login_button = ttk.Button(form_frame, text="Login", command=self.login, style="Accent.TButton", width=20)
        login_button.pack(pady=(0, 20))
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.login())
        role_combo.bind("<Return>", lambda e: self.login())
        self.username_entry.focus()
        # FOOTER
        footer = ttk.Frame(self, style='Card.TFrame')
        footer.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Label(footer, text="© 2024 Employee Management System", font=("Segoe UI", 10), foreground="black").pack(pady=5)
    
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

    def setup_styles(self):
        style = ttk.Style()
        self.colors = {
            'primary': '#2196F3',  # blue
            'success': '#4CAF50',  # green
            'danger': '#F44336',   # red
            'secondary': '#B0BEC5', # gray
            'light': '#F5F5F5',
            'dark': '#212121'
        }
        style.configure('Header.TLabel', font=('Segoe UI', 24, 'bold'), foreground='black')
        style.configure('Subheader.TLabel', font=('Segoe UI', 16), foreground='black')
        style.configure('Stats.TLabel', font=('Segoe UI', 14), foreground='black')
        style.configure('Card.TFrame', background=self.colors['light'], relief='solid', borderwidth=1)
        style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'), background=self.colors['primary'], foreground='black', borderwidth=0)
        style.map('Primary.TButton', background=[('active', self.colors['primary'])], foreground=[('active', 'black')])
        style.configure('Success.TButton', font=('Segoe UI', 10, 'bold'), background=self.colors['success'], foreground='black', borderwidth=0)
        style.map('Success.TButton', background=[('active', self.colors['success'])], foreground=[('active', 'black')])
        style.configure('Danger.TButton', font=('Segoe UI', 10, 'bold'), background=self.colors['danger'], foreground='black', borderwidth=0)
        style.map('Danger.TButton', background=[('active', self.colors['danger'])], foreground=[('active', 'black')])
        style.configure('Secondary.TButton', font=('Segoe UI', 10), background=self.colors['secondary'], foreground='black', borderwidth=0)
        style.map('Secondary.TButton', background=[('active', self.colors['secondary'])], foreground=[('active', 'black')]) 