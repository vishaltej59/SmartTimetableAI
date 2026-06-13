# Google Calendar Integration

## Authentication Flow
The application currently uses `InstalledAppFlow` from the `google_auth_oauthlib.flow` package to perform OAuth 2.0.
1. The user logs in via a web popup.
2. The `credentials.json` file is used to verify the OAuth Client ID.
3. A `token.json` file is generated to store the refresh/access tokens locally.

## Deployment Warning
**This system is single-user and NOT safe for public deployment.**
Because it relies on a local `token.json` file, if deployed to the cloud, all users of the app would share the same Google Calendar connection. 

### Path to Production
To make this public:
1. Implement Multi-Tenant Login (Google Sign-In).
2. Store each user's encrypted `refresh_token` in the `users` table of a PostgreSQL database.
3. Reconstruct the Google `Credentials` object dynamically per session using the logged-in user's token.
