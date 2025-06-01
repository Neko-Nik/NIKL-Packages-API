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


# Package Index Structure

This is the file/folder structure `/m/math/1.0.0.tar.gz` and it represents a **NIKL package index file path**

---

## 📦 Tree View

```
/
└── m/
    └── math/
        └── 1.0.0.tar.gz
        └── 2.1.0.tar.gz
```

---

## 🧠 Explanation

| Part           | Description                                                                             |
| -------------- | --------------------------------------------------------------------------------------- |
| `/`            | Root of the package server or index                                                     |
| `m/`           | A **first-letter directory** – used to categorize packages by their name's first letter |
| `math/`        | Directory named after the actual **package name**                                       |
| `1.0.0.tar.gz` | A **distribution file** (source tarball) for the package version `1.0.0`                |


---

## ✅ Summary

* **`m/`** is a directory for all packages starting with the letter `m`.
* **`math/`** is the package name directory.
* **`1.0.0.tar.gz`** is the source archive for version `1.0.0` of `math`.

This organization enables `nikl` and similar tools to efficiently index and retrieve packages.



# Package DB Schema


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


```sql
CREATE TABLE base_packages (
    id UUID PRIMARY KEY,
    package_name VARCHAR(100) NOT NULL UNIQUE,
    package_description TEXT,
    latest_version_id VARCHAR(20) REFERENCES versioned_packages(id) ON DELETE SET NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB, -- stores additional metadata about the package
    user_id UUID NOT NULL REFERENCES users(id)
);

CREATE INDEX idx_base_packages_package_name ON base_packages (package_name);
CREATE INDEX idx_base_packages_registered_at ON base_packages (registered_at);
CREATE INDEX idx_base_packages_user_id ON base_packages (user_id);
```

```sql
CREATE TABLE versioned_packages (
    id UUID PRIMARY KEY,
    base_package_id UUID NOT NULL REFERENCES base_packages(id),
    version VARCHAR(20) NOT NULL,
    file_path TEXT NOT NULL, -- path to the package file in local storage or S3
    metadata JSONB, -- stores additional metadata about the versioned package
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_versioned_packages_base_package_id ON versioned_packages (base_package_id);
CREATE INDEX idx_versioned_packages_version ON versioned_packages (version);
CREATE INDEX idx_versioned_packages_created_at ON versioned_packages (created_at);
```
