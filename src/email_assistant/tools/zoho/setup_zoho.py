"""
Zoho Inventory API Setup Script

This script helps set up the necessary OAuth credentials and configuration
for accessing the Zoho Inventory API.
"""

import os
import json
import webbrowser
from pathlib import Path
from urllib.parse import urlencode
import requests

# Configuration
ZOHO_CLIENT_ID = "1000.25GPQ4CLE4KYZASLDJJCFSQ808XECM"
ZOHO_CLIENT_SECRET = "48eac4d1c064b193e0a472f9f5971c23fb60c8806e"
ZOHO_REDIRECT_URI = "http://www.andrewmallamo.com"  # Update as needed
ZOHO_SCOPE = "ZohoInventory.FullAccess.all"

# File paths
_ROOT = Path(__file__).parent.absolute()
_SECRETS_DIR = _ROOT / ".secrets"

def setup_zoho_oauth():
    """Set up Zoho OAuth 2.0 authentication"""
    
    if not ZOHO_CLIENT_ID or not ZOHO_CLIENT_SECRET:
        print("❌ Error: ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET must be set in environment variables")
        print("\nTo set up:")
        print("1. Go to https://api-console.zoho.com/")
        print("2. Create a new application (Self Client)")
        print("3. Add your client credentials to .env file:")
        print("   ZOHO_CLIENT_ID=your_client_id")
        print("   ZOHO_CLIENT_SECRET=your_client_secret")
        return False
    
    # Create secrets directory if it doesn't exist
    _SECRETS_DIR.mkdir(exist_ok=True)
    
    # Step 1: Generate authorization URL
    auth_url = generate_auth_url()
    print(f"🔗 Opening authorization URL: {auth_url}")
    webbrowser.open(auth_url)
    
    # Step 2: Get authorization code from user
    print("\n📋 After authorizing, copy the authorization code from the redirect URL")
    auth_code = input("Enter the authorization code: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided")
        return False
    
    # Step 3: Exchange authorization code for access token
    print("🔄 Exchanging authorization code for access token...")
    tokens = get_access_token(auth_code)
    
    if tokens:
        # Save tokens to file
        token_file = _SECRETS_DIR / "zoho_tokens.json"
        with open(token_file, 'w') as f:
            json.dump(tokens, f, indent=2)
        
        print(f"✅ Tokens saved to {token_file}")
        print("🎉 Zoho Inventory API setup complete!")
        
        # Test the connection
        print("\n🧪 Testing API connection...")
        test_api_connection(tokens['access_token'])
        
        return True
    else:
        print("❌ Failed to get access tokens")
        return False

def generate_auth_url():
    """Generate the authorization URL for Zoho OAuth"""
    
    params = {
        'response_type': 'code',
        'client_id': ZOHO_CLIENT_ID,
        'scope': ZOHO_SCOPE,
        'redirect_uri': ZOHO_REDIRECT_URI,
        'access_type': 'offline'
    }
    
    base_url = "https://accounts.zoho.com/oauth/v2/auth"
    return f"{base_url}?{urlencode(params)}"

def get_access_token(auth_code):
    """Exchange authorization code for access and refresh tokens"""
    
    token_url = "https://accounts.zoho.com/oauth/v2/token"
    
    data = {
        'grant_type': 'authorization_code',
        'client_id': ZOHO_CLIENT_ID,
        'client_secret': ZOHO_CLIENT_SECRET,
        'redirect_uri': ZOHO_REDIRECT_URI,
        'code': auth_code
    }
    
    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        tokens = response.json()
        
        if 'access_token' in tokens:
            print("✅ Successfully obtained access token")
            return tokens
        else:
            print(f"❌ Error in token response: {tokens}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def refresh_access_token(refresh_token):
    """Refresh the access token using refresh token"""
    
    refresh_url = "https://accounts.zoho.com/oauth/v2/token"
    
    data = {
        'grant_type': 'refresh_token',
        'client_id': ZOHO_CLIENT_ID,
        'client_secret': ZOHO_CLIENT_SECRET,
        'refresh_token': refresh_token
    }
    
    try:
        response = requests.post(refresh_url, data=data)
        response.raise_for_status()
        
        tokens = response.json()
        
        if 'access_token' in tokens:
            print("✅ Successfully refreshed access token")
            return tokens
        else:
            print(f"❌ Error in refresh response: {tokens}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Refresh request failed: {e}")
        return None

def test_api_connection(access_token):
    """Test the API connection by fetching organization info"""
    
    headers = {
        'Authorization': f'Zoho-oauthtoken {access_token}',
        'Content-Type': 'application/json'
    }
    
    test_url = "https://inventory.zoho.com/api/v1/organizations"
    
    try:
        response = requests.get(test_url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        organizations = data.get('organizations', [])
        
        if organizations:
            print("✅ API connection successful!")
            print(f"📊 Found {len(organizations)} organization(s):")
            for org in organizations:
                print(f"   - {org.get('name', 'Unknown')} (ID: {org.get('organization_id', 'Unknown')})")
                
            # Save organization ID to environment
            org_id = organizations[0].get('organization_id')
            if org_id:
                print(f"\n💡 Add this to your .env file:")
                print(f"ZOHO_ORGANIZATION_ID={org_id}")
        else:
            print("⚠️ API connection successful but no organizations found")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API test failed: {e}")

def load_tokens():
    """Load saved tokens from file"""
    
    token_file = _SECRETS_DIR / "zoho_tokens.json"
    
    if token_file.exists():
        with open(token_file, 'r') as f:
            return json.load(f)
    
    return None

def save_tokens(tokens):
    """Save tokens to file"""
    
    _SECRETS_DIR.mkdir(exist_ok=True)
    token_file = _SECRETS_DIR / "zoho_tokens.json"
    
    with open(token_file, 'w') as f:
        json.dump(tokens, f, indent=2)

if __name__ == "__main__":
    print("🔧 Zoho Inventory API Setup")
    print("=" * 40)
    
    # Check if tokens already exist
    existing_tokens = load_tokens()
    
    if existing_tokens:
        print("📁 Found existing tokens")
        
        # Test if they still work
        print("🧪 Testing existing tokens...")
        test_api_connection(existing_tokens.get('access_token'))
        
        # Ask if user wants to refresh
        refresh = input("\n🔄 Refresh tokens? (y/n): ").strip().lower()
        
        if refresh == 'y':
            if 'refresh_token' in existing_tokens:
                new_tokens = refresh_access_token(existing_tokens['refresh_token'])
                if new_tokens:
                    save_tokens(new_tokens)
            else:
                print("❌ No refresh token found. Starting fresh setup...")
                setup_zoho_oauth()
    else:
        print("🆕 No existing tokens found. Starting setup...")
        setup_zoho_oauth() 