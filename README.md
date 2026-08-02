# Inkflow Publisher

A modern, Django-based Content Management System (CMS) built to demonstrate real-world backend software engineering principles, scalable application architecture, and clean development practices.

Inkflow Publisher provides a complete editorial workflow for creating, reviewing, managing, and publishing digital content while showcasing modern Django development techniques including reusable components, role-based permissions, service-oriented architecture, and maintainable code organization.

---

## Features

### Content Management
- Create, edit, and delete articles
- Rich article metadata
- Featured images
- Categories
- SEO-friendly URLs using slugs
- Draft and Published article states
- Featured article support

### Editorial Workflow
- Review articles before publication
- Publish and unpublish content
- Article moderation
- Report inappropriate articles
- Editorial approval process

### User Management
- Authentication
- Role-based permissions
- Author ownership
- Secure administrative functionality

### Responsive Interface
- Bootstrap 5 UI
- Mobile-friendly layouts
- Reusable templates
- Shared components
- Consistent design system

### Project Architecture
- Modular Django applications
- Service layer architecture
- Reusable HTML components
- Clean URL routing
- Class and function separation
- Maintainable template structure

---

# Technology Stack

## Backend

- Python
- Django
- SQLite (Development)
- MySQL (Production Ready)

## Frontend

- HTML5
- CSS3
- Bootstrap 5
- JavaScript

## Development

- Git
- GitHub
- Virtual Environment
- Django ORM

---

# Project Structure

```
Inkflow Publisher
│
├── accounts/
├── articles/
├── categories/
├── dashboard/
├── website/
│
├── templates/
│
├── static/
│
├── media/
│
├── config/
│
├── manage.py
└── requirements.txt
```

---

# Core Functionality

## Articles

- Create articles
- Edit articles
- Publish articles
- Draft articles
- Feature articles
- Category assignment
- Slug generation
- Rich metadata

## Categories

- Create categories
- Organize content
- Article filtering

## Reporting System

Users can report inappropriate or inaccurate articles.

Reports include:

- Report type
- Description
- Review workflow

Editors can review submitted reports directly from the article review page.

---

# Design Philosophy

Inkflow Publisher was designed with maintainability as the primary objective.

Key principles include:

- Reusable templates
- Separation of concerns
- Modular applications
- Clean code
- Scalable architecture
- Consistent UI components
- Service-oriented business logic

Rather than duplicating templates across pages, common UI components are shared and reused throughout the project, reducing maintenance costs and improving consistency.

---

# Installation

Clone the repository

```bash
git clone https://github.com/yourusername/inkflow-publisher.git
```

Navigate into the project

```bash
cd inkflow-publisher
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run migrations

```bash
python manage.py migrate
```

Create an administrator account

```bash
python manage.py createsuperuser
```

Run the development server

```bash
python manage.py runserver
```

---

# Future Improvements

The project roadmap includes:

- Rich text editor
- Image management
- Search functionality
- Tagging system
- Scheduled publishing
- Version history
- REST API
- Public API authentication
- Email notifications
- Analytics dashboard
- Comment moderation
- Multi-language support
- Docker deployment
- CI/CD pipeline
- Automated testing

---

# What This Project Demonstrates

This project showcases experience with:

- Django application architecture
- Database design
- Backend development
- Authentication and authorization
- CRUD application development
- Modular project organization
- Service layer implementation
- Bootstrap UI development
- Template inheritance
- Reusable frontend components
- Git version control
- Software maintainability
- Scalable application design

---

# Screenshots

> Screenshots of the application will be added as development progresses.

---

# License

This project is licensed under the MIT License.

---

# Author

**KP**

Python | Django | SQL | HTML | Bootstrap 

Building maintainable software, one project at a time.

GitHub: https://github.com/kgothatso-create
