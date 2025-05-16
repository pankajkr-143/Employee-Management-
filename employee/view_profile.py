import tkinter as tk
from tkinter import ttk
from employee.crud import EmployeeCRUD

class ProfileView(ttk.Frame):
    def __init__(self, parent, employee_id):
        super().__init__(parent, padding="20")
        self.employee_id = employee_id
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the profile view UI"""
        # Get employee details
        employee = EmployeeCRUD.get_employee(self.employee_id)
        
        if employee:
            # Create profile frame
            profile_frame = ttk.LabelFrame(self, text="Employee Profile", padding="20")
            profile_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Display employee details
            details = [
                ("ID:", employee['id']),
                ("Name:", f"{employee['first_name']} {employee['last_name']}"),
                ("Email:", employee['email']),
                ("Phone:", employee['phone'] or "N/A"),
                ("Department:", employee['department'] or "N/A"),
                ("Position:", employee['position'] or "N/A"),
                ("Salary:", f"${employee['salary']:,.2f}" if employee['salary'] else "N/A"),
                ("Hire Date:", employee['hire_date'] or "N/A")
            ]
            
            for i, (label, value) in enumerate(details):
                ttk.Label(profile_frame, text=label,
                         font=("Helvetica", 10, "bold")).grid(row=i, column=0,
                                                             sticky="e", pady=5)
                ttk.Label(profile_frame, text=str(value),
                         font=("Helvetica", 10)).grid(row=i, column=1,
                                                    sticky="w", pady=5)
        else:
            ttk.Label(self, text="Employee not found",
                     font=("Helvetica", 12)).pack(pady=20) 