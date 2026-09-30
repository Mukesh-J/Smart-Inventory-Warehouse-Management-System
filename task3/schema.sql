CREATE DATABASE IF NOT EXISTS inventory_db;

USE inventory_db;


CREATE TABLE IF NOT EXISTS products (

    product_id INT AUTO_INCREMENT PRIMARY KEY,

    product_code VARCHAR(50) NOT NULL UNIQUE,

    product_name VARCHAR(150) NOT NULL,

    description TEXT,

    category VARCHAR(100) NOT NULL,

    price DECIMAL(12,2) NOT NULL,

    quantity INT NOT NULL DEFAULT 0,

    supplier_name VARCHAR(150) NOT NULL,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_product_code (product_code),

    INDEX idx_product_name (product_name),

    INDEX idx_category (category),

    INDEX idx_supplier_name (supplier_name),

    INDEX idx_is_active (is_active)

);