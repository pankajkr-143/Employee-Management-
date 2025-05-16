import tkinter as tk
from tkinter import ttk, messagebox
from utils.db import get_db_connection

class EmployeeCRUD:
    @staticmethod
    def add_employee(values):
        """Add a new employee"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO employees (
                    first_name, last_name, email, phone, department,
                    position, salary, hire_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                values["first_name"], values["last_name"], values["email"],
                values["phone"], values["department"], values["position"],
                values["salary"] or None, values["hire_date"] or None
            ))
            conn.commit()
            return True, "Employee added successfully!"
        except sqlite3.IntegrityError:
            return False, "Email already exists"
        finally:
            conn.close()
    
    @staticmethod
    def update_employee(employee_id, values):
        """Update an existing employee"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE employees SET
                    first_name = ?, last_name = ?, email = ?,
                    phone = ?, department = ?, position = ?,
                    salary = ?, hire_date = ?
                WHERE id = ?
            """, (
                values["first_name"], values["last_name"], values["email"],
                values["phone"], values["department"], values["position"],
                values["salary"] or None, values["hire_date"] or None,
                employee_id
            ))
            conn.commit()
            return True, "Employee updated successfully!"
        except sqlite3.IntegrityError:
            return False, "Email already exists"
        finally:
            conn.close()
    
    @staticmethod
    def delete_employee(employee_id):
        """Delete an employee"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
            conn.commit()
            return True, "Employee deleted successfully!"
        except sqlite3.Error as e:
            return False, f"Failed to delete employee: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def get_employee(employee_id):
        """Get employee details"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
        employee = cursor.fetchone()
        conn.close()
        
        return employee
    
    @staticmethod
    def get_all_employees():
        """Get all employees"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, first_name || ' ' || last_name, email, department, position
            FROM employees
            ORDER BY id
        """)
        employees = cursor.fetchall()
        conn.close()
        
        return employees
    
    @staticmethod
    def search_employees(search_term):
        """Search employees by ID or name"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, first_name || ' ' || last_name, email, department, position
            FROM employees
            WHERE id LIKE ? OR first_name LIKE ? OR last_name LIKE ?
        """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        
        employees = cursor.fetchall()
        conn.close()
        
        return employees 