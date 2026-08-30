"""
Enterprise Authentication Module with SSO (SAML/OIDC) and RBAC.
Provides role-based access control for fraud analysts, managers, and admins.
"""
import os
import logging
from functools import wraps
from typing import Optional, Dict, List
from flask_session import Session
from authlib.integrations.flask_client import OAuth
from flask import Flask, session, redirect, url_for, request, abort

logger = logging.getLogger(__name__)

# Role Definitions
ROLES = {
    "ANALYST": {
        "level": 1,
        "permissions": ["view_cases", "submit_recommendation", "view_dashboard"]
    },
    "SENIOR_ANALYST": {
        "level": 2,
        "permissions": ["view_cases", "submit_recommendation", "view_dashboard", 
                       "approve_case", "escalate_case"]
    },
    "MANAGER": {
        "level": 3,
        "permissions": ["view_cases", "submit_recommendation", "view_dashboard",
                       "approve_case", "escalate_case", "block_transaction", 
                       "view_analytics", "export_reports"]
    },
    "ADMIN": {
        "level": 4,
        "permissions": ["*"]  # Full access
    }
}

class EnterpriseAuth:
    def __init__(self, app: Flask = None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize authentication with Flask app."""
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-prod')
        app.config['SESSION_TYPE'] = 'filesystem'
        
        # Initialize Session
        Session(app)
        
        # Initialize OAuth for SSO
        oauth = OAuth(app)
        
        # Configure SSO Provider (Azure AD / Okta / Keycloak)
        sso_provider = os.getenv('SSO_PROVIDER', 'azure_ad')
        
        if sso_provider == 'azure_ad':
            oauth.register(
                name='azure_ad',
                client_id=os.getenv('AZURE_CLIENT_ID'),
                client_secret=os.getenv('AZURE_CLIENT_SECRET'),
                server_metadata_url=f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}/v2.0/.well-known/openid-configuration",
                client_kwargs={'scope': 'openid email profile'}
            )
        elif sso_provider == 'okta':
            oauth.register(
                name='okta',
                client_id=os.getenv('OKTA_CLIENT_ID'),
                client_secret=os.getenv('OKTA_CLIENT_SECRET'),
                server_metadata_url=os.getenv('OKTA_ISSUER_URL') + '/.well-known/openid-configuration',
                client_kwargs={'scope': 'openid email profile'}
            )
        elif sso_provider == 'keycloak':
            oauth.register(
                name='keycloak',
                client_id=os.getenv('KEYCLOAK_CLIENT_ID'),
                client_secret=os.getenv('KEYCLOAK_CLIENT_SECRET'),
                server_metadata_url=os.getenv('KEYCLOAK_ISSUER_URL') + '/.well-known/openid-configuration',
                client_kwargs={'scope': 'openid email profile'}
            )
        
        self.oauth = oauth
        self.app.oauth = oauth
    
    def login_required(self, f):
        """Decorator to require authentication."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def role_required(self, required_role: str):
        """Decorator to require specific role or higher."""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                user = session.get('user')
                if not user:
                    return redirect(url_for('login'))
                
                user_role = user.get('role', 'ANALYST')
                if ROLES.get(user_role, {}).get('level', 0) < ROLES.get(required_role, {}).get('level', 999):
                    abort(403)  # Forbidden
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def permission_required(self, permission: str):
        """Decorator to require specific permission."""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                user = session.get('user')
                if not user:
                    return redirect(url_for('login'))
                
                user_role = user.get('role', 'ANALYST')
                user_permissions = ROLES.get(user_role, {}).get('permissions', [])
                
                if '*' not in user_permissions and permission not in user_permissions:
                    abort(403)
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current authenticated user from session."""
        return session.get('user')
    
    def get_current_user_id(self) -> Optional[str]:
        """Get current user ID for audit logging."""
        user = self.get_current_user()
        return user.get('sub') if user else None
    
    def map_claims_to_role(self, claims: Dict) -> str:
        """Map SSO claims to internal roles based on groups/roles."""
        # Example: Map Azure AD groups to Clerivon roles
        groups = claims.get('groups', [])
        
        if 'clerivon-admins' in groups:
            return 'ADMIN'
        elif 'clerivon-managers' in groups:
            return 'MANAGER'
        elif 'clerivon-senior-analysts' in groups:
            return 'SENIOR_ANALYST'
        else:
            return 'ANALYST'  # Default role
    
    def handle_auth_callback(self, provider: str = 'azure_ad'):
        """Handle OAuth callback from SSO provider."""
        oauth = self.oauth
        client = oauth.create_client(provider)
        
        try:
            token = client.authorize_access_token()
            user_info = client.get('userinfo').json()
            
            # Map claims to internal role
            role = self.map_claims_to_role(token.get('userinfo', {}))
            
            # Store user in session
            session['user'] = {
                'sub': user_info.get('sub'),
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'role': role,
                'groups': token.get('userinfo', {}).get('groups', [])
            }
            
            logger.info(f"User logged in: {user_info.get('email')} as {role}")
            return redirect(url_for('dashboard'))
        
        except Exception as e:
            logger.error(f"SSO callback error: {str(e)}")
            return redirect(url_for('login_error'))

# Routes for Flask integration (example)
def create_auth_routes(app: Flask, auth: EnterpriseAuth):
    """Create authentication routes."""
    
    @app.route('/login')
    def login():
        """Redirect to SSO provider."""
        provider = os.getenv('SSO_PROVIDER', 'azure_ad')
        oauth = app.oauth
        client = oauth.create_client(provider)
        return client.authorize_redirect(
            redirect_uri=url_for('auth_callback', _external=True)
        )
    
    @app.route('/auth/callback')
    def auth_callback():
        """Handle SSO callback."""
        return auth.handle_auth_callback()
    
    @app.route('/logout')
    def logout():
        """Clear session and redirect to SSO logout."""
        session.clear()
        return redirect(os.getenv('SSO_LOGOUT_URL', '/'))
    
    @app.route('/login-error')
    def login_error():
        return "Authentication failed. Please contact your administrator.", 401

# Initialize auth instance
enterprise_auth = EnterpriseAuth()
