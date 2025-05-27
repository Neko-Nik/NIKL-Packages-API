# Package Management

- Create new package (login required)
    - Upload package file (tar.gz only for now)
    - Validate package file (check for tar.gz format, check for required files)
    - Save package details in the database and the file in the S3 bucket

- Get package details by package name (public)

...


# DB Tables

> Note: The following tables are not exhaustive and are meant to provide a basic structure for the package management system (and its not finalized yet).

Users -> For user based information
base_packages -> For base packages and its details (like name, description, registered date, metadata, dependencyss, dependents, etc.) [Relationship with single user]
versioned_packages -> For versioned packages and its details (like version, package name, file path, metadata, etc.) [Relationship with single base package]
