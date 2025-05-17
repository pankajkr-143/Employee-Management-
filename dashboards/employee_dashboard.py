import tkinter as tk
from tkinter import ttk, messagebox
from employee.view_profile import ProfileView
import os

class EmployeeDashboard(ttk.Frame):
    def __init__(self, parent, current_user, on_logout):
        super().__init__(parent, padding="20")
        self.current_user = current_user
        self.on_logout = on_logout
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the employee dashboard UI"""
        # HEADER
        header_frame = ttk.Frame(self, style='Card.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        from PIL import Image, ImageTk
        logo_img = Image.open('assets/images/logo.jpg')
        logo_img = logo_img.resize((80, 40), Image.Resampling.LANCZOS)
        logo = ImageTk.PhotoImage(logo_img)
        logo_label = ttk.Label(header_frame, image=logo)
        logo_label.image = logo
        logo_label.pack(side=tk.LEFT, padx=(10, 10))
        ttk.Label(header_frame, text="Employee Management System", font=("Segoe UI", 18, "bold"), foreground="black").pack(side=tk.LEFT, padx=(0, 20))
        nav_frame = ttk.Frame(header_frame)
        nav_frame.pack(side=tk.RIGHT)
        ttk.Button(nav_frame, text="View Profile", command=self.show_profile, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Logout", command=self.on_logout, style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
        
        # CONTENT
        content_frame = ttk.Frame(self)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Card-style profile view
        profile_card = ttk.Frame(content_frame, padding=30, style='Card.TFrame')
        profile_card.pack(pady=30, padx=30, fill=tk.BOTH, expand=True)
        
        # Get employee info
        employee = None
        emp = None
        if self.current_user.get('employee_id'):
            from employee.crud import EmployeeCRUD
            employee = EmployeeCRUD.get_employee(self.current_user['employee_id'])
        if not employee:
            from employee.crud import EmployeeCRUD
            all_emps = EmployeeCRUD.get_all_employees()
            for e in all_emps:
                if (e.get('email') and e.get('email') == self.current_user.get('username')) or \
                   (e.get('first_name') and e.get('first_name').lower() == self.current_user.get('username').lower()):
                    employee = e
                    break
        if employee:
            emp = dict(employee)
            # Photo
            photo_path = f"assets/photos/employee_{emp.get('id', '')}"
            photo_ext = None
            for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                if os.path.exists(photo_path + ext):
                    photo_ext = ext
                    break
            if photo_ext:
                from PIL import Image, ImageTk
                image = Image.open(photo_path + photo_ext)
                image = image.resize((140, 140), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                photo_label = ttk.Label(profile_card, image=photo)
                photo_label.image = photo
                photo_label.grid(row=0, column=0, rowspan=8, padx=(0, 30), pady=10)
            else:
                photo_label = ttk.Label(profile_card, text="No Photo", font=("Segoe UI", 12, "italic"), foreground="black")
                photo_label.grid(row=0, column=0, rowspan=8, padx=(0, 30), pady=10)
            # Details
            details = [
                ("Employee ID:", emp.get('id', '')),
                ("First Name:", emp.get('first_name', '')),
                ("Last Name:", emp.get('last_name', '')),
                ("Email:", emp.get('email', '')),
                ("Phone:", emp.get('phone', '')),
                ("Department:", emp.get('department', '')),
                ("Position:", emp.get('position', '')),
                ("Salary:", emp.get('salary', '')),
                ("Hire Date:", emp.get('hire_date', '')),
            ]
            for i, (label, value) in enumerate(details):
                ttk.Label(profile_card, text=label, font=("Segoe UI", 12, "bold"), foreground="black").grid(row=i, column=1, sticky=tk.W, pady=6)
                ttk.Label(profile_card, text=value, font=("Segoe UI", 12), foreground="black").grid(row=i, column=2, sticky=tk.W, pady=6)
        else:
            ttk.Label(profile_card, text="No employee profile found. Please contact your administrator to link your account.", font=("Segoe UI", 14), foreground="black").pack(pady=20)
        
        # FOOTER
        footer = ttk.Frame(self, style='Card.TFrame')
        footer.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Label(footer, text="© 2024 Employee Management System", font=("Segoe UI", 10), foreground="black").pack(pady=5)
    
    def show_profile(self):
        """Show user's profile"""
        if self.current_user['employee_id']:
            profile_window = tk.Toplevel(self)
            profile_window.title("My Profile")
            profile_window.geometry("400x500")
            ProfileView(profile_window, self.current_user['employee_id']).pack(fill=tk.BOTH, expand=True)
        else:
            messagebox.showinfo("Info", "No employee profile linked to this account")

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