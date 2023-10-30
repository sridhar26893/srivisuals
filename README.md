# srivisuals
**_SriVisuals Website_**

This project is a secure three-tier web application developed using Flask, a Python web framework, and various AWS services. The application is designed to run on an Amazon EC2 instance, ensuring scalability and reliability. Security measures include the use of AWS WAF (Web Application Firewall) rules to filter and monitor incoming traffic. The frontend is built using HTML, CSS, and JavaScript to create visually appealing and responsive webpages.

**Architecture Overview:**

**Presentation Tier:**
The presentation tier, responsible for interacting with users, is implemented using Flask, HTML, CSS, and JavaScript.
Flask serves a dual role as both the presentation and application tier, handling user requests and responses.

**Application Tier:**
The application tier contains the business logic and processing logic implemented within the Flask application.
Business logic includes user registration, authentication, post creation, and interactions.
DynamoDB operations, S3 interactions, and other backend tasks are part of the application tier.

**Data Tier:**
The data tier stores and manages data used by the application.
DynamoDB, a NoSQL database, is utilized for storing user registration data and post information.
S3 is employed for secure image storage.

===========================================================================<br>
**Key Features:**

**User Registration and Authentication:**
Users can securely register with a unique username, valid email, and a password hashed using bcrypt for storage in DynamoDB.
AWS WAF rules enhance security against potential threats in incoming traffic.
User Login:
Secure user login using registered email or username and password, with successful login redirecting users to their profile page.

**Profile Page:**
Dynamically generated profile pages display basic user information and a list of uploaded images.
HTML, CSS, and JavaScript create an interactive and visually appealing user interface.
Image Upload and Post Creation:

Users can securely upload images, with posts created in DynamoDB and image storage in an Amazon S3 bucket.
AWS WAF ensures the security of the application against potential web-based attacks.

Image Gallery:
The home page features a gallery of images fetched from the S3 bucket, delivered securely and quickly through Amazon CloudFront.

**Post Interaction:**
Users can securely interact with posts by liking them, with the like count updated and stored securely in DynamoDB.

**Error Handling:**
Robust error handling is implemented for scenarios such as invalid login credentials and existing usernames/emails during registration.
AWS WAF rules contribute to the overall security posture by protecting against common web exploits.

**Security Measures:**
User passwords are securely hashed using bcrypt.
AWS WAF rules are used to filter and monitor incoming traffic for security purposes.
AWS services, including DynamoDB, S3, and CloudFront, are leveraged for secure storage and content delivery.

**Flask Framework:**
The lightweight and scalable Flask web framework is used for building the backend of the application, ensuring efficient performance on the EC2 instance.

**AWS Services:**
The application is designed to run on an Amazon EC2 instance, providing scalability and reliability.
Amazon DynamoDB is utilized for NoSQL database storage.
Amazon S3 is employed for secure image storage.
Amazon CloudFront ensures fast and secure content delivery to users.
