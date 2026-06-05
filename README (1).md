# **Software Requirements Specification (SRS)**
## **Taxi Management System**  
### *Roll No: 49–52*

---

## **1. Introduction**

### **1.1 Purpose**
This SRS document outlines the functional and non-functional requirements for the **Taxi Management System**.  
The system is designed as a Mini-DBMS project to demonstrate **Create, Read, Update, Delete (CRUD)** operations using **MySQL** and help manage taxis, drivers, bookings, and payments efficiently.

### **1.2 Scope**
The Taxi Management System will:
- Maintain records of taxis.
- Maintain driver details and assign taxis to drivers.
- Track driver daily expenses.
- Allow customers to book taxis.
- Manage payments and booking history.
- Provide an interface for admin/owner to monitor operations.

### **1.3 Definitions**
- **Taxi**: A vehicle available for rent.
- **Driver**: Person assigned to operate a taxi.
- **Booking**: A request by a customer to use a taxi.
- **Admin/Owner**: Person managing the system.

---

## **2. Overall Description**

### **2.1 Product Perspective**
This project is a standalone DBMS application using:
- **Frontend**: Any UI or CLI interface
- **Backend**: MySQL database
- **Operations**: CRUD operations for each module

### **2.2 Product Functions**
The system will allow the admin to:
- Add, update, delete taxi records.
- Add, update, delete driver details.
- Assign taxis to drivers.
- Track driver daily expenses.
- Manage customer bookings.
- Process payments.

### **2.3 User Characteristics**
- **Admin/Owner**: Basic computer knowledge, responsible for data entry and monitoring.
- **Customer**: Can book taxis (if customer-facing UI is provided).

### **2.4 Constraints**
- MySQL database is required.
- System should follow proper relational design.
- Data integrity must be maintained during CRUD operations.

---

## **3. System Features**

### **3.1 Taxi Management**
#### **Description**
Admin can add new taxis, update details, view all taxis, or delete a taxi.

#### **Functional Requirements**
- **FR1:** System shall allow adding a new taxi (Taxi No, Model, Capacity, etc.).
- **FR2:** System shall allow updating taxi information.
- **FR3:** System shall allow deleting taxi records.
- **FR4:** System shall display all taxi details.

---

### **3.2 Driver Management**
#### **Description**
Drivers are assigned taxis, and their details and expenses are tracked.

#### **Functional Requirements**
- **FR5:** System shall allow adding a new driver.
- **FR6:** System shall allow assigning a taxi to a driver.
- **FR8:** System shall display driver–taxi mapping.

---

### **3.3 Booking Management**
#### **Description**
Customers can book taxis for transportation to desired locations.

#### **Functional Requirements**
- **FR9:** System shall allow customers to book a taxi.
- **FR10:** System shall calculate fare based on distance/time.
- **FR11:** System shall store booking history.
- **FR12:** System shall allow the owner/admin to view all bookings.

---

### **3.4 Payment Management**
#### **Description**
Payments from customers are recorded for each booking.

#### **Functional Requirements**
- **FR13:** System shall record payment for each completed booking.
- **FR14:** System shall generate payment summaries.
- **FR15:** System shall display outstanding or pending payments.

---

## **4. Non-Functional Requirements**

### **4.1 Performance Requirements**
- System must execute CRUD operations efficiently.
- Database queries must respond within acceptable time (<1s for simple queries).

### **4.2 Security Requirements**
- Only admin should be able to modify taxi, driver, or booking data.
- Sensitive records must be protected from accidental deletion.

### **4.3 Usability Requirements**
- The UI/CLI must be simple and intuitive.
- Proper messages must be shown for errors and confirmations.

### **4.4 Reliability Requirements**
- System should maintain data integrity during updates or deletions.
- Backups should be possible for database recovery.

---

## **5. Database Design (High-Level)**

### **Tables**
- **Taxi(taxi_id, model, capacity, status)**  
- **Driver(driver_id, name, phone, taxi_id)**  
- **Booking(booking_id, customer_name, source, destination, taxi_id, date, fare)**  

---

## **6. Future Enhancements**
- Real-time GPS tracking.
- Integration with online payment gateways.
- Customer mobile app.
- Automated fare prediction with maps API.

---

## **7. Conclusion**
This SRS document outlines the core requirements and functionality of the **Taxi Management System**, designed as a Mini-DBMS project to demonstrate efficient management of taxis, drivers, bookings, and payments using MySQL CRUD operations.
