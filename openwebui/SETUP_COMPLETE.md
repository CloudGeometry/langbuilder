# Google OAuth Setup Complete

✅ **Google OAuth has been successfully configured!**

## What was copied from V2:

### 1. OAuth Credentials
- **Client ID**: `your-google-client-id.apps.googleusercontent.com`
- **Client Secret**: `your-google-client-secret`
- **Redirect URI**: `http://localhost:5173/oauth/google/callback`

### 2. Service Account File
- Copied: `/home/eugene/proj/CG_OpenChatUI/open-webui_V2/secrets/google-service-account.json`
- To: `/home/eugene/proj/CG_OpenChatUI/open-webui/secrets/google-service-account.json`

### 3. Configuration Files
- ✅ Updated `.env` with all OAuth settings
- ✅ Corporate config (`corporate_config.json`) already exists
- ✅ Corporate authentication module already present

## Current Configuration

Your `.env` file now includes:

```bash
# Google OAuth
GOOGLE_CLIENT_ID='your-google-client-id.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET='your-google-client-secret'
GOOGLE_REDIRECT_URI='http://localhost:5173/oauth/google/callback'

# OAuth Settings
ENABLE_OAUTH_SIGNUP=true
OAUTH_ALLOWED_DOMAINS='*'
OAUTH_MERGE_ACCOUNTS_BY_EMAIL=true

# Application
WEBUI_NAME='ActionBridge'
OPEN_WEBUI_PORT=8000
```

## Next Steps

1. **Start/Restart OpenWebUI**:
   ```bash
   # If using Docker
   docker-compose down && docker-compose up -d

   # If running locally
   # Restart your application
   ```

2. **Test Google Sign-In**:
   - Go to `http://localhost:5173` (frontend dev server)
   - You should see "Continue with Google" button
   - Click to test the OAuth flow

3. **Important**: Make sure the redirect URI in Google Cloud Console matches:
   - `http://localhost:5173/oauth/google/callback`

## Google Cloud Console Setup

If you need to update the redirect URI in Google Cloud Console:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **APIs & Services** > **Credentials**
3. Find your OAuth 2.0 Client ID (the one you configured)
4. Add `http://localhost:5173/oauth/google/callback` to **Authorized redirect URIs**

## Corporate Authentication

The setup includes ActionBridge corporate authentication:
- Domain: `actionbridge.com`
- Admin groups: `actionbridge-admin@actionbridge.com`, `management@actionbridge.com`
- User groups: `actionbridge-users@actionbridge.com`, `engineering@actionbridge.com`

## Troubleshooting

If you encounter issues:
1. Check logs for OAuth errors
2. Verify redirect URI matches in Google Cloud Console
3. Ensure the port (`8000`) is correct for your setup
4. Check that all environment variables are loaded

Your Google OAuth integration is now ready to use! 🎉