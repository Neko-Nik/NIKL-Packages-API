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
