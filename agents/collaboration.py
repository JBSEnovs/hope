import os
import json
import time
import uuid
from datetime import datetime
import threading
import redis

class CollaborationManager:
    """
    Manages collaborative consultation sessions between medical providers and patients.
    Handles session creation, messaging, and participant management.
    """
    
    def __init__(self, redis_url=None):
        """Initialize the collaboration manager"""
        # Connect to Redis (for message queue and session storage)
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        try:
            self.redis = redis.from_url(self.redis_url)
            self.redis_available = True
        except Exception as e:
            print(f"Redis connection failed: {e}")
            self.redis_available = False
        
        self.sessions = {}
        self.session_dir = os.path.join('data', 'sessions')
        os.makedirs(self.session_dir, exist_ok=True)
        
        # Load any existing sessions
        self._load_sessions()
        
        # Active session storage
        self.active_sessions = {}
        
        # Session cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired_sessions)
        self.cleanup_thread.daemon = True
        self.cleanup_thread.start()
    
    def create_session(self, creator_id, session_type="consultation"):
        """
        Create a new consultation session.
        
        Args:
            creator_id (str): ID of the user creating the session
            session_type (str): Type of session ("consultation", "second_opinion", etc.)
            
        Returns:
            dict: Session details or error
        """
        # Create a unique session ID
        session_id = str(uuid.uuid4())
        timestamp = int(time.time())
        
        # Session metadata
        session = {
            'session_id': session_id,
            'type': session_type,
            'creator_id': creator_id,
            'created_at': timestamp,
            'updated_at': timestamp,
            'status': 'active',
            'participants': [
                {
                    'id': creator_id,
                    'role': 'patient',  # Assume creator is patient by default
                    'joined_at': timestamp
                }
            ],
            'messages': []
        }
        
        # Store the session
        self.sessions[session_id] = session
        
        # Save to disk
        self._save_session(session_id)
        
        return {
            'success': True,
            'session': self._clean_session_data(session)
        }
    
    def join_session(self, session_id, participant_id, role="doctor"):
        """
        Join an existing consultation session.
        
        Args:
            session_id (str): ID of the session to join
            participant_id (str): ID of the user joining
            role (str): Role of the participant (e.g., "doctor", "specialist", "patient")
            
        Returns:
            dict: Success status and session info
        """
        # Check if session exists
        if session_id not in self.sessions:
            return {
                'success': False,
                'error': 'Session not found'
            }
        
        session = self.sessions[session_id]
        
        # Check if session is active
        if session['status'] != 'active':
            return {
                'success': False,
                'error': f'Session is not active (current status: {session["status"]})'
            }
        
        # Check if user is already in the session
        for participant in session['participants']:
            if participant['id'] == participant_id:
                return {
                    'success': False,
                    'error': 'User is already participating in this session'
                }
        
        # Add participant
        timestamp = int(time.time())
        session['participants'].append({
            'id': participant_id,
            'role': role,
            'joined_at': timestamp
        })
        
        # Update session timestamps
        session['updated_at'] = timestamp
        
        # Add system message
        session['messages'].append({
            'id': str(uuid.uuid4()),
            'type': 'system',
            'content': f'Participant with role "{role}" has joined the consultation',
            'sender_id': 'system',
            'timestamp': timestamp
        })
        
        # Save to disk
        self._save_session(session_id)
        
        return {
            'success': True,
            'session': self._clean_session_data(session)
        }
    
    def leave_session(self, session_id, participant_id):
        """
        Leave a consultation session.
        
        Args:
            session_id (str): ID of the session
            participant_id (str): ID of the user leaving
            
        Returns:
            dict: Success status
        """
        # Check if session exists
        if session_id not in self.sessions:
            return {
                'success': False,
                'error': 'Session not found'
            }
        
        session = self.sessions[session_id]
        
        # Check if user is in the session
        participant_found = False
        participant_role = None
        
        for i, participant in enumerate(session['participants']):
            if participant['id'] == participant_id:
                participant_found = True
                participant_role = participant['role']
                del session['participants'][i]
                break
        
        if not participant_found:
            return {
                'success': False,
                'error': 'Participant not found in session'
            }
        
        # Update session timestamps
        timestamp = int(time.time())
        session['updated_at'] = timestamp
        
        # Add system message
        session['messages'].append({
            'id': str(uuid.uuid4()),
            'type': 'system',
            'content': f'Participant with role "{participant_role}" has left the consultation',
            'sender_id': 'system',
            'timestamp': timestamp
        })
        
        # End the session if no participants left
        if not session['participants']:
            session['status'] = 'ended'
            session['ended_at'] = timestamp
        
        # Save to disk
        self._save_session(session_id)
        
        return {
            'success': True
        }
    
    def send_message(self, session_id, sender_id, content, message_type="text"):
        """
        Send a message in a consultation session.
        
        Args:
            session_id (str): ID of the session
            sender_id (str): ID of the message sender
            content (str): Message content
            message_type (str): Type of message ("text", "image", "file", etc.)
            
        Returns:
            dict: Success status and message details
        """
        # Check if session exists
        if session_id not in self.sessions:
            return {
                'success': False,
                'error': 'Session not found'
            }
        
        session = self.sessions[session_id]
        
        # Check if session is active
        if session['status'] != 'active':
            return {
                'success': False,
                'error': f'Session is not active (current status: {session["status"]})'
            }
        
        # Check if sender is a participant
        sender_found = False
        sender_role = None
        
        for participant in session['participants']:
            if participant['id'] == sender_id:
                sender_found = True
                sender_role = participant['role']
                break
        
        if not sender_found:
            return {
                'success': False,
                'error': 'Sender is not a participant in this session'
            }
        
        # Create message
        timestamp = int(time.time())
        message_id = str(uuid.uuid4())
        
        message = {
            'id': message_id,
            'type': message_type,
            'content': content,
            'sender_id': sender_id,
            'sender_role': sender_role,
            'timestamp': timestamp
        }
        
        # Add to session
        session['messages'].append(message)
        session['updated_at'] = timestamp
        
        # Save to disk
        self._save_session(session_id)
        
        return {
            'success': True,
            'message': message
        }
    
    def get_messages(self, session_id, since_timestamp=None):
        """
        Get messages from a consultation session.
        
        Args:
            session_id (str): ID of the session
            since_timestamp (int, optional): Only return messages newer than this timestamp
            
        Returns:
            dict: Success status and messages
        """
        # Check if session exists
        if session_id not in self.sessions:
            return {
                'success': False,
                'error': 'Session not found'
            }
        
        session = self.sessions[session_id]
        
        # Filter messages by timestamp if specified
        if since_timestamp is not None:
            messages = [msg for msg in session['messages'] if msg['timestamp'] > since_timestamp]
        else:
            messages = session['messages']
        
        return {
            'success': True,
            'session_id': session_id,
            'messages': messages
        }
    
    def get_active_sessions(self, participant_id=None):
        """
        Get active consultation sessions.
        
        Args:
            participant_id (str, optional): If provided, only return sessions with this participant
            
        Returns:
            dict: Success status and list of active sessions
        """
        active_sessions = []
        
        for session_id, session in self.sessions.items():
            if session['status'] == 'active':
                # If participant_id is specified, check if they're in the session
                if participant_id:
                    is_participant = any(p['id'] == participant_id for p in session['participants'])
                    if not is_participant:
                        continue
                
                # Include session in results
                active_sessions.append(self._clean_session_data(session))
        
        return {
            'success': True,
            'sessions': active_sessions
        }
    
    def end_session(self, session_id):
        """
        End a consultation session.
        
        Args:
            session_id (str): ID of the session to end
            
        Returns:
            dict: Success status
        """
        # Check if session exists
        if session_id not in self.sessions:
            return {
                'success': False,
                'error': 'Session not found'
            }
        
        session = self.sessions[session_id]
        
        # Check if session is already ended
        if session['status'] != 'active':
            return {
                'success': False,
                'error': f'Session is not active (current status: {session["status"]})'
            }
        
        # End the session
        timestamp = int(time.time())
        session['status'] = 'ended'
        session['ended_at'] = timestamp
        session['updated_at'] = timestamp
        
        # Add system message
        session['messages'].append({
            'id': str(uuid.uuid4()),
            'type': 'system',
            'content': 'The consultation has ended',
            'sender_id': 'system',
            'timestamp': timestamp
        })
        
        # Save to disk
        self._save_session(session_id)
        
        return {
            'success': True
        }
    
    def _load_sessions(self):
        """Load all session data from disk"""
        try:
            # Get all session files
            for filename in os.listdir(self.session_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.session_dir, filename)
                    with open(filepath, 'r') as f:
                        session = json.load(f)
                        self.sessions[session['session_id']] = session
        except Exception as e:
            print(f"Error loading sessions: {e}")
    
    def _save_session(self, session_id):
        """Save a session to disk"""
        try:
            session = self.sessions[session_id]
            filepath = os.path.join(self.session_dir, f"{session_id}.json")
            with open(filepath, 'w') as f:
                json.dump(session, f, indent=2)
        except Exception as e:
            print(f"Error saving session {session_id}: {e}")
    
    def _clean_session_data(self, session):
        """
        Create a clean version of session data for API responses.
        
        Args:
            session (dict): Full session data
            
        Returns:
            dict: Cleaned session data
        """
        # Create a copy to avoid modifying the original
        clean_data = {
            'session_id': session['session_id'],
            'type': session['type'],
            'creator_id': session['creator_id'],
            'created_at': session['created_at'],
            'updated_at': session['updated_at'],
            'status': session['status'],
            'participant_count': len(session['participants']),
            'participants': session['participants'],
            'message_count': len(session['messages'])
        }
        
        # Add ended_at if it exists
        if 'ended_at' in session:
            clean_data['ended_at'] = session['ended_at']
        
        return clean_data
    
    def _cleanup_expired_sessions(self):
        """Background thread to clean up expired sessions"""
        while True:
            try:
                current_time = datetime.utcnow().timestamp()
                
                # Check in-memory sessions
                sessions_to_remove = []
                for session_id, session in self.active_sessions.items():
                    if session["expires_at"] < current_time:
                        sessions_to_remove.append(session_id)
                
                # Remove expired sessions
                for session_id in sessions_to_remove:
                    del self.active_sessions[session_id]
                
                # Sleep for 5 minutes
                time.sleep(300)
                
            except Exception as e:
                print(f"Error in session cleanup: {e}")
                time.sleep(300)  # Sleep and try again
    
    def get_session_participants(self, session_id):
        """
        Get participants in a session
        
        Args:
            session_id: ID of the session
            
        Returns:
            Dictionary with participants
        """
        try:
            # Get the session
            session = self._get_session(session_id)
            
            if not session:
                return {
                    "success": False,
                    "error": "Session not found"
                }
            
            return {
                "success": True,
                "participants": session["participants"]
            }
            
        except Exception as e:
            print(f"Error getting session participants: {e}")
            return {
                "success": False,
                "error": str(e)
            } 