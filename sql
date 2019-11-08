
create database devices;
create table users(id INT(11) AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100), username VARCHAR(30), password VARCHAR(100), register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
create table nw_devices(id INT(11) AUTO_INCREMENT PRIMARY KEY, model VARCHAR(100), hostname VARCHAR(100), ip_address VARCHAR(30), user VARCHAR(30), passw VARCHAR(100), added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
