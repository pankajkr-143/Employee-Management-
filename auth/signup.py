import tkinter as tk
from tkinter import ttk, messagebox
from utils.db import get_db_connection
from utils.hash_util import hash_password

class SignupFrame(ttk.Frame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, padding="20")
        self.on_login_success = on_login_success
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the signup form UI"""
        # Title
        title_label = ttk.Label(self, 
                              text="Create New Account",
                              font=("Helvetica", 16, "bold"),
                              foreground="#2c3e50")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Username
        ttk.Label(self, text="Username:",
                 font=("Helvetica", 10)).grid(row=1, column=0, pady=5)
        self.username_entry = ttk.Entry(self, width=30,
                                      font=("Helvetica", 10))
        self.username_entry.grid(row=1, column=1, pady=5)
        
        # Password
        ttk.Label(self, text="Password:",
                 font=("Helvetica", 10)).grid(row=2, column=0, pady=5)
        self.password_entry = ttk.Entry(self, width=30, show="*",
                                      font=("Helvetica", 10))
        self.password_entry.grid(row=2, column=1, pady=5)
        
        # Confirm Password
        ttk.Label(self, text="Confirm Password:",
                 font=("Helvetica", 10)).grid(row=3, column=0, pady=5)
        self.confirm_password_entry = ttk.Entry(self, width=30, show="*",
                                             font=("Helvetica", 10))
        self.confirm_password_entry.grid(row=3, column=1, pady=5)
        
        # Role
        ttk.Label(self, text="Role:",
                 font=("Helvetica", 10)).grid(row=4, column=0, pady=5)
        self.role_var = tk.StringVar(value="employee")
        role_combo = ttk.Combobox(self, textvariable=self.role_var,
                                values=["employee", "hr"],
                                state="readonly",
                                font=("Helvetica", 10))
        role_combo.grid(row=4, column=1, pady=5)
        
        # Signup button
        signup_button = ttk.Button(self, text="Sign Up",
                                 command=self.signup,
                                 style="Accent.TButton")
        signup_button.grid(row=5, column=0, columnspan=2, pady=20)
        
        # Login link
        login_link = ttk.Label(self,
                             text="Already have an account? Login",
                             cursor="hand2",
                             foreground="blue")
        login_link.grid(row=6, column=0, columnspan=2)
        login_link.bind("<Button-1>", lambda e: self.show_login())
    
    def signup(self):
        """Handle signup attempt"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        role = self.role_var.get()
        
        if not username or not password or not confirm_password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        # Hash the password
        hashed_password = hash_password(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            """, (username, hashed_password, role))
            conn.commit()
            messagebox.showinfo("Success", "Account created successfully!")
            self.show_login()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        finally:
            conn.close()
    
    def show_login(self):
        """Show login form"""
        from auth.login import LoginFrame
        self.place_forget()
        LoginFrame(self.master, self.on_login_success).place(relx=0.5, rely=0.5, anchor="center") 