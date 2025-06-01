# Users related internal documentation

User is a flat object with the following properties:


## DB Schema

- `id`: The unique identifier for the user
- `name`: The name of the user
- `email`: The email address of the user
- `hashed_password`: The hashed password of the user
- `profile`: An object containing additional profile information
- `is_active`: A boolean indicating if the user is active
- `created_at`: The date and time when the user was created


Created user is not active by default, so it will not be able to login until it is activated.

User needs to be verified before logging in, that is by clicking the verification link sent to the email address.

On UI we do https://www.gravatar.com/ for user profile picture, so we don't store it in the database.


```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    profile_data JSONB, -- stores additional profile info as a JSON object
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_created_at ON users (created_at);
CREATE INDEX idx_users_is_active ON users (is_active);
```

# API Key

API key is used to publish packages to the package management system.

## DB Schema

- `id`: The unique identifier for the API key (UUID)
- `user_id`: The ID of the user who owns the API key (foreign key to `users` table)
- `key`: The actual API key (string)
- `details`: An object containing additional details about the API key like name, description, etc.
- `created_at`: The date and time when the API key was created

```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    api_key TEXT NOT NULL UNIQUE,
    details JSONB, -- stores additional details about the API key
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_api_keys_user_id ON api_keys (user_id);
CREATE INDEX idx_api_keys_api_key ON api_keys (api_key);
CREATE INDEX idx_api_keys_created_at ON api_keys (created_at);
```
