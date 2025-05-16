import tkinter as tk
from tkinter import ttk, messagebox
from .user_management import UserManagement
from employee.crud import EmployeeCRUD

class UserManagementUI(ttk.Frame):
    def __init__(self, parent, current_user_role):
        super().__init__(parent)
        self.current_user_role = current_user_role
        self.setup_ui()
        
    def setup_ui(self):
        # Create main container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(
            header_frame,
            text="User Management",
            font=('Helvetica', 16, 'bold')
        ).pack(side=tk.LEFT)
        
        # Add User Button
        ttk.Button(
            header_frame,
            text="Add New User",
            command=self.show_add_user_dialog,
            style='Accent.TButton'
        ).pack(side=tk.RIGHT)
        
        # User List
        self.create_user_list()
        
    def create_user_list(self):
        # Create Treeview
        columns = ('ID', 'Username', 'Role', 'Employee ID', 'Created At')
        self.tree = ttk.Treeview(
            self.main_container,
            columns=columns,
            show='headings',
            style='Custom.Treeview'
        )
        
        # Configure columns
        self.tree.heading('ID', text='ID')
        self.tree.heading('Username', text='Username')
        self.tree.heading('Role', text='Role')
        self.tree.heading('Employee ID', text='Employee ID')
        self.tree.heading('Created At', text='Created At')
        
        self.tree.column('ID', width=50)
        self.tree.column('Username', width=150)
        self.tree.column('Role', width=100)
        self.tree.column('Employee ID', width=100)
        self.tree.column('Created At', width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            self.main_container,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add right-click menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Edit Role", command=self.edit_role)
        self.context_menu.add_command(label="Link Employee", command=self.link_employee)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete User", command=self.delete_user)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Load users
        self.load_users()
        
    def load_users(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Get users
        users = UserManagement.get_users(self.current_user_role)
        
        # Add users to treeview
        for user in users:
            self.tree.insert('', tk.END, values=(
                user['id'],
                user['username'],
                user['role'],
                user['employee_id'] or 'Not Linked',
                user['created_at']
            ))
            
    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def show_add_user_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add New User")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create form
        ttk.Label(dialog, text="Username:").pack(pady=(20, 5))
        username_entry = ttk.Entry(dialog, width=30)
        username_entry.pack()
        
        ttk.Label(dialog, text="Password:").pack(pady=(10, 5))
        password_entry = ttk.Entry(dialog, width=30, show="*")
        password_entry.pack()
        
        ttk.Label(dialog, text="Role:").pack(pady=(10, 5))
        role_var = tk.StringVar()
        role_combo = ttk.Combobox(
            dialog,
            textvariable=role_var,
            values=['hr', 'employee'] if self.current_user_role == 'admin' else ['employee'],
            state='readonly'
        )
        role_combo.pack()
        
        def create_user():
            username = username_entry.get()
            password = password_entry.get()
            role = role_var.get()
            
            success, message = UserManagement.create_user(
                username,
                password,
                role,
                current_user_role=self.current_user_role
            )
            
            if success:
                messagebox.showinfo("Success", message)
                dialog.destroy()
                self.load_users()
            else:
                messagebox.showerror("Error", message)
                
        # Add buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(
            button_frame,
            text="Create",
            command=create_user,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        
    def edit_role(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        user_id = self.tree.item(selected[0])['values'][0]
        current_role = self.tree.item(selected[0])['values'][2]
        
        dialog = tk.Toplevel(self)
        dialog.title("Edit User Role")
        dialog.geometry("300x150")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        ttk.Label(dialog, text="New Role:").pack(pady=(20, 5))
        role_var = tk.StringVar(value=current_role)
        role_combo = ttk.Combobox(
            dialog,
            textvariable=role_var,
            values=['hr', 'employee'] if self.current_user_role == 'admin' else ['employee'],
            state='readonly'
        )
        role_combo.pack()
        
        def update_role():
            new_role = role_var.get()
            success, message = UserManagement.update_user_role(
                user_id,
                new_role,
                self.current_user_role
            )
            
            if success:
                messagebox.showinfo("Success", message)
                dialog.destroy()
                self.load_users()
            else:
                messagebox.showerror("Error", message)
                
        # Add buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(
            button_frame,
            text="Update",
            command=update_role,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        
    def link_employee(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        user_id = self.tree.item(selected[0])['values'][0]
        
        dialog = tk.Toplevel(self)
        dialog.title("Link Employee")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create employee list
        ttk.Label(dialog, text="Select Employee:").pack(pady=(20, 5))
        
        employee_frame = ttk.Frame(dialog)
        employee_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Create Treeview for employees
        columns = ('ID', 'Name', 'Department', 'Position')
        tree = ttk.Treeview(
            employee_frame,
            columns=columns,
            show='headings',
            style='Custom.Treeview'
        )
        
        # Configure columns
        tree.heading('ID', text='ID')
        tree.heading('Name', text='Name')
        tree.heading('Department', text='Department')
        tree.heading('Position', text='Position')
        
        tree.column('ID', width=50)
        tree.column('Name', width=150)
        tree.column('Department', width=100)
        tree.column('Position', width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            employee_frame,
            orient=tk.VERTICAL,
            command=tree.yview
        )
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load employees
        employees = EmployeeCRUD.get_all_employees()
        for employee in employees:
            tree.insert('', tk.END, values=(
                employee['id'],
                employee['name'],
                employee['department'],
                employee['position']
            ))
            
        def link_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showerror("Error", "Please select an employee")
                return
                
            employee_id = tree.item(selected[0])['values'][0]
            success, message = UserManagement.link_employee(
                user_id,
                employee_id,
                self.current_user_role
            )
            
            if success:
                messagebox.showinfo("Success", message)
                dialog.destroy()
                self.load_users()
            else:
                messagebox.showerror("Error", message)
                
        # Add buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(
            button_frame,
            text="Link",
            command=link_selected,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
        
    def delete_user(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        user_id = self.tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this user?"
        ):
            success, message = UserManagement.delete_user(
                user_id,
                self.current_user_role
            )
            
            if success:
                messagebox.showinfo("Success", message)
                self.load_users()
            else:
                messagebox.showerror("Error", message) 