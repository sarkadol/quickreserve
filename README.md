# Quickreserve

This repository contains the source code of *Quickreserve* — a universal reservation system developed as part of my bachelor's thesis at VŠE (University of Economics, Prague).

Thesis title: *Webová aplikace univerzálního rezervačního systému*  
Available online: [VŠE Thesis Repository](https://vskp.vse.cz/92738_webova-aplikace-univerzalniho-rezervacniho-systemu?title=V&page=30)

The thesis was successfully defended in spring 2024 and contributed to obtaining my bachelor's degree (Bc.) at VŠE.

## Project Description

Quickreserve is a web-based reservation system designed to be easily adaptable for various use cases — such as booking appointments, resources, or events.

### Main features:
- User registration and autheFntication
- Role-based access control
- Managing reservation items and categories
- Making and managing reservations
- Administration interface for system configuration

## Technologies Used

- Python (Flask)
- SQLAlchemy
- SQLite (default, can be changed)
- HTML / CSS / JavaScript (Jinja2 templates)
- Bootstrap

## Running the Application

1. Clone the repository:
```bash
git clone https://github.com/sarkadol/quickreserve.git
cd quickreserve
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```
3. Install dependencies:

```bash
pip install -r requirements.txt
```
4. Run the application:

```bash
python run.py
```
5. Open in your browser:

```bash
http://127.0.0.1:5000/
```
