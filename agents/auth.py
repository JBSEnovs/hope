import os
import json
import uuid
import hashlib
import datetime
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

# Initialize Bcrypt
bcrypt = Bcrypt()

class User(UserMixin):
    """User class for authentication"""
    
    def __init__(self, user_id, username, email, role, name=None, profile=None):
        self.id = user_id
        self.username = username
        self.email = email
        self.role = role
        self.name = name or username
        self.profile = profile or {}
        self.created_at = datetime.datetime.utcnow().isoformat()
        self.last_login = None
    
    def get_id(self):
        """Return the user ID as a string for Flask-Login"""
        return str(self.id)
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'name': self.name,
            'profile': self.profile,
            'created_at': self.created_at,
            'last_login': self.last_login
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create user object from dictionary"""
        user = cls(
            user_id=data['id'],
            username=data['username'],
            email=data['email'],
            role=data['role'],
            name=data.get('name'),
            profile=data.get('profile', {})
        )
        user.created_at = data.get('created_at', user.created_at)
        user.last_login = data.get('last_login')
        return user

class UserManager:
    """Manages user authentication and storage"""
    
    def __init__(self, storage_path=None):
        """Initialize the user manager"""
        self.storage_path = storage_path or os.path.join(os.getcwd(), 'data', 'users.json')
        self.users = {}
        self.load_users()
    
    def load_users(self):
        """Load users from storage"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            # Create file if it doesn't exist
            if not os.path.exists(self.storage_path):
                with open(self.storage_path, 'w') as f:
                    json.dump({}, f)
                return
            
            # Load users from file
            with open(self.storage_path, 'r') as f:
                user_data = json.load(f)
                
            # Create user objects
            for user_id, data in user_data.items():
                self.users[user_id] = User.from_dict(data)
                
        except Exception as e:
            print(f"Error loading users: {e}")
    
    def save_users(self):
        """Save users to storage"""
        try:
            # Convert user objects to dictionaries
            user_data = {}
            for user_id, user in self.users.items():
                user_data[user_id] = user.to_dict()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            # Save to file
            with open(self.storage_path, 'w') as f:
                json.dump(user_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def register_user(self, username, email, password, role='patient', name=None, profile=None):
        """
        Register a new user
        
        Args:
            username: Username for the new user
            email: Email address
            password: Plain text password
            role: User role (patient, doctor, admin)
            name: Display name (optional)
            profile: Additional profile data (optional)
            
        Returns:
            Dictionary with success status and user data or error
        """
        try:
            # Check if username or email already exists
            for user in self.users.values():
                if user.username == username:
                    return {
                        'success': False,
                        'error': 'Username already exists'
                    }
                if user.email == email:
                    return {
                        'success': False,
                        'error': 'Email already exists'
                    }
            
            # Create user ID
            user_id = str(uuid.uuid4())
            
            # Hash password
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            
            # Create user object
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                role=role,
                name=name,
                profile=profile
            )
            
            # Add password hash to profile
            user.profile['password_hash'] = password_hash
            
            # Store user
            self.users[user_id] = user
            
            # Save to storage
            self.save_users()
            
            # Return user data (without password)
            user_dict = user.to_dict()
            if 'password_hash' in user_dict['profile']:
                del user_dict['profile']['password_hash']
                
            return {
                'success': True,
                'user': user_dict
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def authenticate(self, username_or_email, password):
        """
        Authenticate a user
        
        Args:
            username_or_email: Username or email address
            password: Plain text password
            
        Returns:
            Dictionary with success status and user data or error
        """
        try:
            # Find user by username or email
            user = None
            for u in self.users.values():
                if u.username == username_or_email or u.email == username_or_email:
                    user = u
                    break
            
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Check password
            password_hash = user.profile.get('password_hash')
            if not password_hash or not bcrypt.check_password_hash(password_hash, password):
                return {
                    'success': False,
                    'error': 'Invalid password'
                }
            
            # Update last login
            user.last_login = datetime.datetime.utcnow().isoformat()
            self.save_users()
            
            # Return user data (without password)
            user_dict = user.to_dict()
            if 'password_hash' in user_dict['profile']:
                del user_dict['profile']['password_hash']
                
            return {
                'success': True,
                'user': user_dict
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user(self, user_id):
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None
        """
        return self.users.get(user_id)
    
    def get_user_by_email(self, email):
        """
        Get user by email
        
        Args:
            email: Email address
            
        Returns:
            User object or None
        """
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def get_user_by_username(self, username):
        """
        Get user by username
        
        Args:
            username: Username
            
        Returns:
            User object or None
        """
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def update_user(self, user_id, data):
        """
        Update user data
        
        Args:
            user_id: User ID
            data: Dictionary with updated data
            
        Returns:
            Dictionary with success status and user data or error
        """
        try:
            # Get user
            user = self.get_user(user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Update user data
            if 'name' in data:
                user.name = data['name']
            if 'email' in data:
                # Check if email already exists
                for u in self.users.values():
                    if u.id != user_id and u.email == data['email']:
                        return {
                            'success': False,
                            'error': 'Email already exists'
                        }
                user.email = data['email']
            if 'role' in data:
                user.role = data['role']
            if 'profile' in data:
                # Update profile without overwriting password_hash
                password_hash = user.profile.get('password_hash')
                user.profile.update(data['profile'])
                if password_hash:
                    user.profile['password_hash'] = password_hash
            
            # Save changes
            self.save_users()
            
            # Return updated user data (without password)
            user_dict = user.to_dict()
            if 'password_hash' in user_dict['profile']:
                del user_dict['profile']['password_hash']
                
            return {
                'success': True,
                'user': user_dict
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def change_password(self, user_id, current_password, new_password):
        """
        Change user password
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            Dictionary with success status or error
        """
        try:
            # Get user
            user = self.get_user(user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Check current password
            password_hash = user.profile.get('password_hash')
            if not password_hash or not bcrypt.check_password_hash(password_hash, current_password):
                return {
                    'success': False,
                    'error': 'Invalid current password'
                }
            
            # Hash new password
            new_password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
            
            # Update password hash
            user.profile['password_hash'] = new_password_hash
            
            # Save changes
            self.save_users()
            
            return {
                'success': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_user(self, user_id):
        """
        Delete user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with success status or error
        """
        try:
            # Check if user exists
            if user_id not in self.users:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Delete user
            del self.users[user_id]
            
            # Save changes
            self.save_users()
            
            return {
                'success': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def reset_password(self, email, new_password):
        """
        Reset user password (for admin use or password recovery)
        
        Args:
            email: User email
            new_password: New password
            
        Returns:
            Dictionary with success status or error
        """
        try:
            # Find user by email
            user = self.get_user_by_email(email)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Hash new password
            new_password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
            
            # Update password hash
            user.profile['password_hash'] = new_password_hash
            
            # Save changes
            self.save_users()
            
            return {
                'success': True
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            } 