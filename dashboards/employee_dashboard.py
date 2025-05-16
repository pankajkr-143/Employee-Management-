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
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Welcome message
        welcome_label = ttk.Label(header_frame,
                                text=f"Welcome, {self.current_user['username']}!",
                                font=("Segoe UI", 16, "bold"))
        welcome_label.pack(side=tk.LEFT)
        
        # Navigation buttons
        nav_frame = ttk.Frame(header_frame)
        nav_frame.pack(side=tk.RIGHT)
        ttk.Button(nav_frame, text="View Profile",
                  command=self.show_profile, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Logout",
                  command=self.on_logout, style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
        
        # Main content
        content_frame = ttk.Frame(self)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Card-style profile view
        profile_card = ttk.Frame(content_frame, padding=30, style='Card.TFrame')
        profile_card.pack(pady=30, padx=30, fill=tk.BOTH, expand=True)
        
        # Get employee info
        employee = None
        if self.current_user.get('employee_id'):
            from employee.crud import EmployeeCRUD
            employee = EmployeeCRUD.get_employee(self.current_user['employee_id'])
        
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
                photo_label = ttk.Label(profile_card, text="No Photo", font=("Segoe UI", 12, "italic"))
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
                ttk.Label(profile_card, text=label, font=("Segoe UI", 12, "bold")).grid(row=i, column=1, sticky=tk.W, pady=6)
                ttk.Label(profile_card, text=value, font=("Segoe UI", 12)).grid(row=i, column=2, sticky=tk.W, pady=6)
        else:
            ttk.Label(profile_card, text="No employee profile found", font=("Segoe UI", 14)).pack(pady=20)
    
    def show_profile(self):
        """Show user's profile"""
        if self.current_user['employee_id']:
            profile_window = tk.Toplevel(self)
            profile_window.title("My Profile")
            profile_window.geometry("400x500")
            ProfileView(profile_window, self.current_user['employee_id']).pack(fill=tk.BOTH, expand=True)
        else:
            messagebox.showinfo("Info", "No employee profile linked to this account") 