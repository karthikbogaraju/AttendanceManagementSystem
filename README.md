# Attendance Management System

A full-stack **Flask + SQLite Attendance Management System** supporting Teacher & Student authentication, course management, and attendance tracking.

---

## Project Structure

```

│── backend/
│   ├── app.py
│   ├── db_setup.py
│── database/
│   ├── attendance.db
│── frontend/
│   ├── templates/
│   ├── static/
│       ├── style.css
│── README.md
```


## Use Case Diagram
![Use Case Diagram](https://github.com/karthikbogaraju/AttendanceManagementSystem/blob/main/diagrams/use%20case%20diagram%20.png)

---

## Database Diagram
![ER Diagram](https://github.com/karthikbogaraju/AttendanceManagementSystem/blob/main/diagrams/database%20Diagram.svg)

---

## System Architecture Diagram
![Architecture Diagram](https://github.com/karthikbogaraju/AttendanceManagementSystem/blob/main/diagrams/system%20architecture.jpg)
---

---

## Features

### Teacher Features
- Register & Login  
- Dashboard with assigned courses  
- Add/Edit students  
- Assign or remove student course enrollments  
- Mark attendance  
- Edit attendance  
- Edit teacher profile  

### Student Features
- Register & Login  
- Dashboard with enrolled courses  
- View attendance history  
- Edit profile  

### System Features
- SQLite database  
- Responsive clean UI  
- Organized file structure  

---

## Installation & Setup

### 1. Install dependencies
```bash
pip install flask
```

### 2. Initialize the database
```bash
python backend/db_setup.py
```

### 3. Run the application
```bash
python backend/app.py
```

Application URL:
```
http://127.0.0.1:5000/
```

---

## Default Test Accounts

### Teacher
```
Email: teacher@example.com
Password: password123
```

### Student
```
Email: student1@example.com
Password: studpass1
```

---

## Database Schema

### Tables:
- teachers  
- students  
- courses  
- teacher_courses  
- student_courses  
- attendance  

---

# Future Enhancements

- JWT Authentication  
- Admin Panel  
- Attendance Reports (PDF/Excel)  
- Attendance Analytics Charts  
- Email Notifications  
- Mobile App APIs  



