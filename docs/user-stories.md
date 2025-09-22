# user-stories.md

## 1. Register for an Account

**Persona:**
Sofia, a first-time user who wants to use the chat service.

**Story:**
As a new user, I want to register for an account using the registration API, so I can access the chat service after logging in.

**Goal:**
Enable new users to securely and easily create an account.

**Acceptance Criteria:**
**Given** I am not registered,
  **When** I send a `POST /api/v1/users/register` request with my registration details (name, email, password),
  **Then** my account is created and I receive a confirmation response.
    - **Status Code:** `201 Created`
    - **Validation:**
      - All fields are required: name (not empty), email (valid format), password (minimum 8 characters, contains both letters and numbers, **and at least one symbol** such as `!@#$%^&*`).
      - If email is already in use, API responds with **`409 Conflict`** and a specific error message ("Email is already registered.").
      - If any field is missing or invalid, API returns `422 Unprocessable Entity` with a clear error message indicating which field needs correction.

**Mapped Endpoint:**
`POST /api/v1/users/register`

---

## 2. Log In to My Account

**Persona:**
Pedro, a returning user who wants to access the chat service.

**Story:**
As a returning user, I want to log in using the login API so I can use the chat service.

**Goal:**
Allow existing users to authenticate and obtain access to the chat.

**Acceptance Criteria:**
**Given** I have an existing account,
  **When** I send a `POST /api/v1/users/login` request with my email and password,
  **Then** I receive a response confirming successful authentication, with a **JWT token** included in the response.
    - **Status Code:** `200 OK` (on success)
    - **Validation:**
      - Both email and password are required.
      - Email must be in valid format.
      - If credentials are correct, API returns a **JWT token** and a secure random refresh token (not JWT) and `200 OK`.
      - Multiple sessions/devices supported (no global revocation on login)
      - Refresh token is stored with session metadata (user agent, IP)
      - If credentials are incorrect (either email or password), API responds with `401 Unauthorized` and a generic error message only:
        > "Email or password incorrect."
        - *Do not indicate which field was wrong.*
      - If fields are missing or email is invalid, API responds with `422 Unprocessable Entity` and a specific message ("Email format invalid", "Password is required", etc.).

**Mapped Endpoint:**
`POST /api/v1/users/login`


## 2a. Refresh Access Token

**Persona:**
Pedro, a returning user whose access token has expired.

**Story:**
As an authenticated user with an expired access token, I want to use my refresh token to obtain a new access token without re-entering my credentials.

**Goal:**
Allow users to securely refresh their access token using a refresh token.

**Acceptance Criteria:**
**Given** my access token has expired,
  **When** I send a `POST /api/v1/users/refresh-token` request with my refresh token,
  **Then** I receive a new access token (JWT) and a new refresh token.
    - **Status Code:** `200 OK` (on success)
    - **Validation:**
  - Request must include a valid refresh token (from cookie or header).
  - If refresh token is valid and not expired, API returns a new access token and a new refresh token.
  - Previous refresh token is invalidated and cannot be reused (single-use).
  - Sliding expiration: expiry is extended on rotation, up to a configurable max lifetime (e.g., 30 days).
  - Only one valid refresh token exists per user/session/device. Refresh tokens are tied to session metadata (user agent, IP).
  - Suspicious activity logging: all invalid, expired, revoked token use, and user agent/IP anomalies are logged
  - If no valid refresh token is provided, or the token is invalid/expired/reused, API responds with `401 Unauthorized` and a generic error message ("Invalid or expired refresh token.").

**Mapped Endpoint:**
`POST /api/v1/users/refresh-token`

---


## 2b. Log Out of a Specific Session (Device)

**Persona:**
Pedro, a user who wants to securely log out from one device or session.

**Story:**
As an authenticated user, I want to log out from a specific device or session so that my refresh token for that session is revoked and cannot be used to obtain new access tokens.

**Goal:**
Allow users to securely log out from a single session/device, invalidating only the refresh token for that session.

**Acceptance Criteria:**
**Given** I am authenticated on a device or session,
  **When** I send a `POST /api/v1/users/logout` request with my refresh token (from header or cookie),
  **Then** my refresh token for that session is revoked and cannot be used again.
    - **Status Code:** `204 No Content` (on success)
    - **Validation:**
      - Only the current session's refresh token is revoked; other sessions/devices remain active.
      - Suspicious activity logging for invalid, expired, or revoked token use.
      - If no valid refresh token is provided, or the token is invalid/expired/revoked, API responds with `401 Unauthorized` and a generic error message ("No active session or already logged out.").
      - After logout, the user must re-authenticate on that device to obtain new tokens.

**Mapped Endpoint:**
`POST /api/v1/users/logout`

---

## 2c. Log Out of All Sessions (All Devices)

**Persona:**
Pedro, a user who wants to securely log out from all devices and sessions at once.

**Story:**
As an authenticated user, I want to log out everywhere so that all my refresh tokens are revoked and I am signed out from all devices and sessions.

**Goal:**
Allow users to securely log out from all sessions/devices, invalidating all refresh tokens for the user.

**Acceptance Criteria:**
**Given** I am authenticated,
  **When** I send a `POST /api/v1/users/logout-all` request,
  **Then** all my refresh tokens are revoked and cannot be used again on any device or session.
    - **Status Code:** `204 No Content` (on success)
    - **Validation:**
      - All sessions/devices are logged out; all refresh tokens for the user are revoked.
      - Suspicious activity logging for invalid, expired, or revoked token use.
      - If no valid refresh tokens exist, API responds with `401 Unauthorized` and a generic error message ("No active sessions or already logged out everywhere.").
      - After logout-all, the user must re-authenticate on any device to obtain new tokens.

**Mapped Endpoint:**
`POST /api/v1/users/logout-all`

---

## 3. Chat with the AI Bot (Authenticated)

**Persona:**
Maria, a logged-in user seeking help or conversation via chat.

**Story:**
As an authenticated user, I want to send chat messages via the API, so I can receive help, ask questions, or simply converse with the AI bot.

**Goal:**
Allow authenticated users to interact with the chat service.

**Acceptance Criteria:**
**Given** I am authenticated (by providing a valid **JWT token** in the request header),
  **When** I send a `POST /api/v1/chat` request with my message,
  **Then** the chatbot responds politely and helpfully, maintaining context.
    - **Status Code:** `200 OK` (on success)
    - **Validation:**
      - Request must include a valid **JWT token** in the `Authorization` header as a Bearer token; otherwise, access is denied.
        - **Status Code:** `401 Unauthorized` (if missing/invalid token)
      - Chat message must not be empty or only whitespace.
        - **Status Code:** `422 Unprocessable Entity` (if empty or missing)
      - If the message exceeds the allowed length (**4,096 characters**), API returns:
        - **Status Code:** `422 Unprocessable Entity` with a clear error message ("Message too long. Maximum allowed is 4096 characters. Please shorten your message.")
      - If the bot cannot answer, API still returns `200 OK` but with a polite message and possible suggestions.

**Mapped Endpoint:**
`POST /api/v1/chat`

---

## 4. Prompt for Login or Registration (Unauthenticated User)

**Persona:**
Carlos, a visitor who tries to use the chat without being logged in.

**Story:**
As an unauthenticated user, I want to receive clear instructions if I try to use the chat API without logging in, so I understand I must register or log in first.

**Goal:**
Guide anonymous users to become authenticated to access chat features.

**Acceptance Criteria:**
**Given** I am not authenticated,
  **When** I send a `POST /api/v1/chat` request without a valid **JWT token**,
  **Then** the API responds with an error indicating authentication is required, and provides guidance to log in or register.
    - **Status Code:** `401 Unauthorized`
**Given** I continue to send chat requests unauthenticated,
  **When** I do so,
  **Then** the API continues to deny access until I am authenticated, always responding with `401 Unauthorized`.

**Mapped Endpoint:**
`POST /api/v1/chat` (authentication with JWT required)

---
