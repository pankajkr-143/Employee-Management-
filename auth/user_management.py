import tkinter as tk
from tkinter import ttk, messagebox
from utils.db import get_db_connection
from utils.hash_util import hash_password

class UserManagement:
    @staticmethod
    def create_user(username, password, role, employee_id=None, current_user_role=None):
        """Create a new user with role-based validation"""
        # Validate role permissions
        if current_user_role == 'admin':
            if role not in ['hr', 'employee']:
                return False, "Admin can only create HR and Employee accounts"
        elif current_user_role == 'hr':
            if role != 'employee':
                return False, "HR can only create Employee accounts"
        else:
            return False, "Unauthorized to create users"
        
        # Validate input
        if not username or not password or not role:
            return False, "Please fill in all required fields"
        
        # Hash password
        hashed_password = hash_password(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO users (username, password, role, employee_id)
                VALUES (?, ?, ?, ?)
            """, (username, hashed_password, role, employee_id))
            conn.commit()
            return True, "User created successfully!"
        except sqlite3.IntegrityError:
            return False, "Username already exists"
        finally:
            conn.close()
    
    @staticmethod
    def get_users(current_user_role):
        """Get users based on role permissions"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if current_user_role == 'admin':
            cursor.execute("""
                SELECT id, username, role, employee_id, created_at
                FROM users
                ORDER BY role, username
            """)
        elif current_user_role == 'hr':
            cursor.execute("""
                SELECT id, username, role, employee_id, created_at
                FROM users
                WHERE role = 'employee'
                ORDER BY username
            """)
        else:
            return []
        
        users = cursor.fetchall()
        conn.close()
        return users
    
    @staticmethod
    def delete_user(user_id, current_user_role):
        """Delete a user with role-based validation"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user to be deleted
        cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return False, "User not found"
        
        # Validate role permissions
        if current_user_role == 'admin':
            if user['role'] == 'admin':
                return False, "Cannot delete admin users"
        elif current_user_role == 'hr':
            if user['role'] != 'employee':
                return False, "HR can only delete employee accounts"
        else:
            return False, "Unauthorized to delete users"
        
        try:
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return True, "User deleted successfully!"
        except sqlite3.Error as e:
            return False, f"Failed to delete user: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def update_user_role(user_id, new_role, current_user_role):
        """Update user role with role-based validation"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user to be updated
        cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return False, "User not found"
        
        # Validate role permissions
        if current_user_role == 'admin':
            if user['role'] == 'admin':
                return False, "Cannot modify admin users"
            if new_role not in ['hr', 'employee']:
                return False, "Admin can only set roles to HR or Employee"
        elif current_user_role == 'hr':
            if user['role'] != 'employee' or new_role != 'employee':
                return False, "HR can only manage employee accounts"
        else:
            return False, "Unauthorized to update user roles"
        
        try:
            cursor.execute("UPDATE users SET role = ? WHERE id = ?",
                         (new_role, user_id))
            conn.commit()
            return True, "User role updated successfully!"
        except sqlite3.Error as e:
            return False, f"Failed to update user role: {str(e)}"
        finally:
            conn.close()
    
    @staticmethod
    def link_employee(user_id, employee_id, current_user_role):
        """Link a user to an employee record"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user to be updated
        cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return False, "User not found"
        
        # Validate role permissions
        if current_user_role == 'admin':
            if user['role'] == 'admin':
                return False, "Cannot modify admin users"
        elif current_user_role == 'hr':
            if user['role'] != 'employee':
                return False, "HR can only manage employee accounts"
        else:
            return False, "Unauthorized to link employees"
        
        try:
            cursor.execute("UPDATE users SET employee_id = ? WHERE id = ?",
                         (employee_id, user_id))
            conn.commit()
            return True, "Employee linked successfully!"
        except sqlite3.Error as e:
            return False, f"Failed to link employee: {str(e)}"
        finally:
            conn.close() 