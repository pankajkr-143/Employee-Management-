import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from utils.db import get_db_connection
from employee.crud import EmployeeCRUD
from employee.view_profile import ProfileView
from auth.user_management_ui import UserManagementUI
import csv
from datetime import datetime
import os
from PIL import Image, ImageTk
import random
import string

class AdminDashboard(ttk.Frame):
    def __init__(self, parent, current_user, logout_callback):
        super().__init__(parent)
        self.current_user = current_user
        self.logout_callback = logout_callback
        self.setup_styles()
        self.setup_ui()
        
    def setup_styles(self):
        style = ttk.Style()
        self.colors = {
            'primary': '#1976D2',
            'secondary': '#455A64',
            'success': '#388E3C',
            'warning': '#FFA000',
            'danger': '#D32F2F',
            'light': '#F5F5F5',
            'dark': '#212121'
        }
        style.configure('Header.TLabel', font=('Segoe UI', 24, 'bold'), foreground=self.colors['primary'])
        style.configure('Subheader.TLabel', font=('Segoe UI', 16), foreground=self.colors['secondary'])
        style.configure('Stats.TLabel', font=('Segoe UI', 14), foreground=self.colors['dark'])
        style.configure('Card.TFrame', background=self.colors['light'], relief='solid', borderwidth=1)
        style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'), background=self.colors['primary'], foreground='white', borderwidth=0)
        style.map('Primary.TButton', background=[('active', self.colors['primary'])], foreground=[('active', 'white')])
        style.configure('Secondary.TButton', font=('Segoe UI', 10), background=self.colors['secondary'], foreground='white', borderwidth=0)
        style.map('Secondary.TButton', background=[('active', self.colors['secondary'])], foreground=[('active', 'white')])
        
        # Configure Treeview style
        style.configure('Custom.Treeview',
                       font=('Helvetica', 10),
                       rowheight=30,
                       background=self.colors['light'],
                       fieldbackground=self.colors['light'])
        
        style.configure('Custom.Treeview.Heading',
                       font=('Helvetica', 10, 'bold'),
                       background=self.colors['primary'],
                       foreground='white')
        
    def setup_ui(self):
        # Create main container with padding
        self.main_container = ttk.Frame(self, padding="20")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header with gradient background
        header_frame = ttk.Frame(self.main_container, style='Card.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Welcome message with user info
        welcome_frame = ttk.Frame(header_frame)
        welcome_frame.pack(side=tk.LEFT, padx=20, pady=20)
        
        ttk.Label(
            welcome_frame,
            text=f"Welcome, {self.current_user['username']}",
            style='Header.TLabel'
        ).pack(anchor=tk.W)
        
        ttk.Label(
            welcome_frame,
            text="Admin Dashboard",
            style='Subheader.TLabel'
        ).pack(anchor=tk.W)
        
        # Navigation buttons with icons
        nav_frame = ttk.Frame(header_frame)
        nav_frame.pack(side=tk.RIGHT, padx=20, pady=20)
        
        ttk.Button(
            nav_frame,
            text="📊 Dashboard",
            command=self.show_dashboard,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            nav_frame,
            text="👥 Manage Users",
            command=self.show_user_management,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            nav_frame,
            text="👤 View Profile",
            command=self.show_profile,
            style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            nav_frame,
            text="🚪 Logout",
            command=self.logout_callback,
            style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        # Content area
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Show default dashboard
        self.show_dashboard()
        
    def show_dashboard(self):
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Create two-column layout
        left_frame = ttk.Frame(self.content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_frame = ttk.Frame(self.content_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Quick Stats Cards
        stats_frame = ttk.Frame(left_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Create stats cards
        self.create_stat_card(stats_frame, "Total Employees", self.get_total_employees(), "👥")
        self.create_stat_card(stats_frame, "IT Department", self.get_department_count("IT"), "💻")
        self.create_stat_card(stats_frame, "HR Department", self.get_department_count("HR"), "👔")
        self.create_stat_card(stats_frame, "Total Users", self.get_total_users(), "👤")
        
        # Employee List with all details
        list_frame = ttk.LabelFrame(left_frame, text="Employee List", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        columns = ('ID', 'First Name', 'Last Name', 'Email', 'Phone', 'Department', 'Position', 'Salary', 'Hire Date', 'Photo')
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            style='Custom.Treeview'
        )
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.column('Photo', width=80)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="👁️ View Profile", command=self.view_employee_profile)
        self.context_menu.add_command(label="✏️ Edit", command=self.edit_employee)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Delete", command=self.delete_employee)
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", lambda e: self.view_employee_profile())
        self.load_employees()
        
        # Action buttons with icons
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Button(
            button_frame,
            text="➕ Add Employee",
            command=self.add_employee,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🔍 Search",
            command=self.search_employees,
            style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="📥 Export to CSV",
            command=self.export_to_csv,
            style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
    def create_stat_card(self, parent, title, value, icon):
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Label(
            card,
            text=f"{icon} {title}",
            style='Subheader.TLabel'
        ).pack(pady=(10, 5))
        
        ttk.Label(
            card,
            text=str(value),
            style='Stats.TLabel'
        ).pack(pady=(0, 10))
        
    def get_total_employees(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM employees")
        count = cursor.fetchone()[0]
        conn.close()
        return count
        
    def get_department_count(self, department):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM employees WHERE department = ?", (department,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
        
    def get_total_users(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        conn.close()
        return count
        
    def add_employee(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add New Employee")
        dialog.geometry("1000x600")  # Increased width for horizontal layout
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create main container
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create two columns
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Photo upload in left frame
        photo_frame = ttk.LabelFrame(left_frame, text="Employee Photo", padding=10)
        photo_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.photo_path = None
        self.photo_preview = None
        
        def upload_photo():
            file_path = filedialog.askopenfilename(
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            if file_path:
                self.photo_path = file_path
                try:
                    image = Image.open(file_path)
                    image = image.resize((150, 150), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    if self.photo_preview:
                        self.photo_preview.destroy()
                    self.photo_preview = ttk.Label(photo_frame, image=photo)
                    self.photo_preview.image = photo
                    self.photo_preview.pack(pady=10)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load image: {str(e)}")
        
        ttk.Button(
            photo_frame,
            text="📷 Upload Photo",
            command=upload_photo,
            style='Primary.TButton'
        ).pack(pady=10)
        
        # Form fields in right frame
        form_frame = ttk.LabelFrame(right_frame, text="Employee Details", padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create two columns for form fields
        form_left = ttk.Frame(form_frame)
        form_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        form_right = ttk.Frame(form_frame)
        form_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        entries = {}
        departments = ['IT', 'HR', 'Finance', 'Marketing', 'Operations']
        
        # Form fields
        fields = [
            ("First Name:", "first_name", form_left),
            ("Last Name:", "last_name", form_left),
            ("Email:", "email", form_left),
            ("Phone:", "phone", form_left),
            ("Department:", "department", form_right),
            ("Position:", "position", form_right),
            ("Salary:", "salary", form_right),
            ("Hire Date (YYYY-MM-DD):", "hire_date", form_right)
        ]
        
        for label_text, field_name, parent in fields:
            ttk.Label(
                parent,
                text=label_text,
                font=('Helvetica', 10)
            ).pack(pady=(10, 5))
            
            if field_name == 'department':
                var = tk.StringVar()
                combo = ttk.Combobox(
                    parent,
                    textvariable=var,
                    values=departments,
                    state='readonly',
                    width=30
                )
                combo.pack(pady=(0, 10))
                entries[field_name] = var
            else:
                entry = ttk.Entry(parent, width=30)
                entry.pack(pady=(0, 10))
                entries[field_name] = entry
        
        # Credentials frame at the bottom
        credentials_frame = ttk.LabelFrame(main_frame, text="Login Credentials", padding=10)
        credentials_frame.pack(fill=tk.X, pady=(20, 0))
        
        username_var = tk.StringVar()
        password_var = tk.StringVar()
        
        def generate_credentials():
            first_name = entries['first_name'].get()
            last_name = entries['last_name'].get()
            phone = entries['phone'].get()
            
            if first_name and last_name:
                # Generate username (first letter of first name + last name)
                username = (first_name[0] + last_name).lower()
                username_var.set(username)
                
                # Generate password (first name + last 4 digits of phone)
                if phone and len(phone) >= 4:
                    password = first_name.lower() + phone[-4:]
                    password_var.set(password)
                else:
                    messagebox.showwarning("Warning", "Phone number is required for password generation")
        
        ttk.Button(
            credentials_frame,
            text="🔑 Generate Credentials",
            command=generate_credentials,
            style='Primary.TButton'
        ).pack(pady=10)
        
        # Credentials display in two columns
        cred_left = ttk.Frame(credentials_frame)
        cred_left.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        cred_right = ttk.Frame(credentials_frame)
        cred_right.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        ttk.Label(cred_left, text="Username:").pack(pady=(10, 5))
        ttk.Entry(
            cred_left,
            textvariable=username_var,
            state='readonly',
            width=30
        ).pack(pady=(0, 10))
        
        ttk.Label(cred_right, text="Password:").pack(pady=(10, 5))
        ttk.Entry(
            cred_right,
            textvariable=password_var,
            state='readonly',
            width=30
        ).pack(pady=(0, 10))
        
        # Buttons at the bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(
            button_frame,
            text="💾 Save",
            command=lambda: self.save_employee(dialog, entries, username_var, password_var),
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="❌ Cancel",
            command=dialog.destroy,
            style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
    def save_employee(self, dialog, entries, username_var, password_var):
        # Get values from entries
        values = {}
        for field, entry in entries.items():
            if isinstance(entry, tk.StringVar):
                values[field] = entry.get()
            else:
                values[field] = entry.get()
        
        # Validate required fields
        required_fields = ["first_name", "last_name", "email", "department", "phone"]
        if not all(values[field] for field in required_fields):
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, values['email']):
            messagebox.showerror("Error", "Please enter a valid email address")
            return
        
        # Validate salary
        if values['salary']:
            try:
                float(values['salary'])
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid salary amount")
                return
        
        # Validate hire date
        if values['hire_date']:
            import datetime
            try:
                datetime.datetime.strptime(values['hire_date'], '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid date in YYYY-MM-DD format")
                return
        
        # Add employee
        success, message = EmployeeCRUD.add_employee(values)
        
        if success:
            # Create user account if credentials are generated
            if username_var.get() and password_var.get():
                from auth.user_management import UserManagement
                UserManagement.create_user(
                    username_var.get(),
                    password_var.get(),
                    'employee',
                    current_user_role=self.current_user['role']
                )
            
            # Save photo if uploaded
            if self.photo_path:
                try:
                    # Create photos directory if it doesn't exist
                    os.makedirs('assets/photos', exist_ok=True)
                    
                    # Copy photo to assets/photos with employee ID
                    import shutil
                    employee_id = success  # Assuming add_employee returns the new employee ID
                    photo_ext = os.path.splitext(self.photo_path)[1]
                    new_photo_path = f'assets/photos/employee_{employee_id}{photo_ext}'
                    shutil.copy2(self.photo_path, new_photo_path)
                except Exception as e:
                    messagebox.showwarning("Warning", f"Failed to save photo: {str(e)}")
            
            messagebox.showinfo("Success", message)
            dialog.destroy()
            self.load_employees()
        else:
            messagebox.showerror("Error", message)
        
    def show_user_management(self):
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Show user management interface
        UserManagementUI(self.content_frame, self.current_user['role']).pack(
            fill=tk.BOTH,
            expand=True
        )
        
    def show_profile(self):
        if self.current_user.get('employee_id'):
            dialog = tk.Toplevel(self)
            dialog.title("My Profile")
            dialog.geometry("600x400")
            dialog.transient(self)
            dialog.grab_set()
            
            # Center dialog
            dialog.update_idletasks()
            width = dialog.winfo_width()
            height = dialog.winfo_height()
            x = (dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (dialog.winfo_screenheight() // 2) - (height // 2)
            dialog.geometry(f'{width}x{height}+{x}+{y}')
            
            ProfileView(dialog, self.current_user['employee_id']).pack(
                fill=tk.BOTH,
                expand=True,
                padx=20,
                pady=20
            )
        else:
            messagebox.showinfo(
                "Profile",
                "No employee profile linked to your account."
            )
            
    def load_employees(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        employees = EmployeeCRUD.get_all_employees()
        for employee in employees:
            emp = dict(employee)
            photo_path = f"assets/photos/employee_{emp.get('id', '')}"
            photo_ext = None
            for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                if os.path.exists(photo_path + ext):
                    photo_ext = ext
                    break
            photo_status = "📷" if photo_ext else "❌"
            self.tree.insert('', tk.END, values=(
                emp.get('id', ''),
                emp.get('first_name', ''),
                emp.get('last_name', ''),
                emp.get('email', ''),
                emp.get('phone', ''),
                emp.get('department', ''),
                emp.get('position', ''),
                emp.get('salary', ''),
                emp.get('hire_date', ''),
                photo_status
            ))
        
    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def view_employee_profile(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        employee_id = self.tree.item(selected[0])['values'][0]
        
        dialog = tk.Toplevel(self)
        dialog.title("Employee Profile")
        dialog.geometry("600x400")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        ProfileView(dialog, employee_id).pack(
            fill=tk.BOTH,
            expand=True,
            padx=20,
            pady=20
        )
        
    def edit_employee(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        employee_id = self.tree.item(selected[0])['values'][0]
        # TODO: Implement edit employee dialog
        
    def delete_employee(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        employee_id = self.tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this employee?"
        ):
            success, message = EmployeeCRUD.delete_employee(employee_id)
            
            if success:
                messagebox.showinfo("Success", message)
                self.load_employees()
            else:
                messagebox.showerror("Error", message)
                
    def search_employees(self):
        dialog = tk.Toplevel(self)
        dialog.title("Search Employees")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create search frame
        search_frame = ttk.Frame(dialog, padding=20)
        search_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search options
        ttk.Label(
            search_frame,
            text="Search by:",
            font=('Helvetica', 10)
        ).pack(pady=(0, 5))
        
        search_type = tk.StringVar(value="name")
        ttk.Radiobutton(
            search_frame,
            text="Name",
            variable=search_type,
            value="name"
        ).pack(anchor=tk.W)
        
        ttk.Radiobutton(
            search_frame,
            text="Department",
            variable=search_type,
            value="department"
        ).pack(anchor=tk.W)
        
        ttk.Radiobutton(
            search_frame,
            text="Position",
            variable=search_type,
            value="position"
        ).pack(anchor=tk.W)
        
        # Search entry
        ttk.Label(
            search_frame,
            text="Search term:",
            font=('Helvetica', 10)
        ).pack(pady=(10, 5))
        
        search_entry = ttk.Entry(search_frame, width=30)
        search_entry.pack(pady=(0, 10))
        
        def perform_search():
            search_term = search_entry.get().strip()
            if not search_term:
                messagebox.showerror("Error", "Please enter a search term")
                return
            
            # Search employees
            employees = EmployeeCRUD.search_employees(search_term)
            
            if employees:
                # Clear existing items
                for item in self.tree.get_children():
                    self.tree.delete(item)
                
                # Add search results
                for employee in employees:
                    self.tree.insert('', tk.END, values=(
                        employee['id'],
                        employee['name'],
                        employee['department'],
                        employee['position'],
                        employee['email']
                    ))
                
                dialog.destroy()
            else:
                messagebox.showinfo("No Results", "No employees found matching the search term")
        
        # Add buttons
        button_frame = ttk.Frame(search_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(
            button_frame,
            text="Search",
            command=perform_search,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        
    def export_to_csv(self):
        # Generate default filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"employees_{timestamp}.csv"
        
        # Ask user for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=default_filename,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            # Get all employees
            employees = EmployeeCRUD.get_all_employees()
            
            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                # Define CSV headers
                fieldnames = [
                    'ID', 'Name', 'Email', 'Phone', 'Department',
                    'Position', 'Salary', 'Hire Date'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Write employee data
                for employee in employees:
                    writer.writerow({
                        'ID': employee['id'],
                        'Name': employee['name'],
                        'Email': employee['email'],
                        'Phone': employee['phone'],
                        'Department': employee['department'],
                        'Position': employee['position'],
                        'Salary': employee['salary'],
                        'Hire Date': employee['hire_date']
                    })
            
            messagebox.showinfo(
                "Success",
                f"Employee data exported successfully to:\n{filename}"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to export data: {str(e)}"
            ) 