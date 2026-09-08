-- Phase 3: Database & Table Setup

CREATE DATABASE IF NOT EXISTS retail_orders_project;

USE retail_orders_project;

-- Drop the old table to ensure a clean rebuild
DROP TABLE IF EXISTS retail_orders;

CREATE TABLE retail_orders (
    OrderID              VARCHAR(20),
    OrderDate            DATE,
    CustomerID           VARCHAR(20),
    CustomerName         VARCHAR(100),
    Email                VARCHAR(150),
    Region               VARCHAR(20),
    Country              VARCHAR(50),
    ProductCategory      VARCHAR(50),
    ProductName          VARCHAR(50),
    Quantity             FLOAT,
    UnitPrice            FLOAT,
    Discount             FLOAT,
    ShippingCost         FLOAT,
    PaymentMethod        VARCHAR(20),
    OrderStatus          VARCHAR(20),
    SignupDate           DATE,
    order_before_signup  BOOLEAN
);

-- Confirm you're in the right database and check the structure
SELECT DATABASE();
DESCRIBE retail_orders;

SHOW CREATE TABLE retail_orders;

LOAD DATA LOCAL INFILE '/Users/joshuaaldo/Desktop/Projects/retail_orders_cleaned.csv'
INTO TABLE retail_orders
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY ','
LINES TERMINATED BY ','
IGNORE 1 ROWS
(OrderId, OrderDate, CustomerID, CustomerName, Email, Region, Country, ProductCategory, ProductName, Quantity, UnitPrice, Discount, ShippingCost, PaymentMethod, OrderStatus, SignupDate, orders_before_signup);

SHOW VARIABLES LIKE 'secure_file_priv';

SELECT COUNT(*) FROM retail_orders;

SELECT * FROM retail_orders LIMIT 10;

-- Find total revenue for each month
SELECT 
    DATE_FORMAT(OrderDate, '%Y-%m') AS OrderMonth,
    ROUND(SUM(Quantity * UnitPrice * (1 - Discount)), 2) AS TotalRevenue
FROM retail_orders
GROUP BY OrderMonth
ORDER BY OrderMonth;

--Revenue and order count by region
SELECT 
    Region,
    ROUND(SUM(Quantity * UnitPrice * (1 - Discount)), 2) AS TotalRevenue,
    COUNT(DISTINCT OrderID) AS TotalOrders,
    ROUND(SUM(Quantity * UnitPrice * (1 - Discount)) / COUNT(DISTINCT OrderID), 2) AS AvgRevenuePerOrder
FROM retail_orders
GROUP BY Region
ORDER BY TotalRevenue DESC;


--Classify customers as repeat vs one-time buyers; Get order count and revenue per customer first
SELECT 
    CASE 
        WHEN OrderCount = 1 THEN 'One-Time Buyer'
        ELSE 'Repeat Buyer'
    END AS CustomerType,
    COUNT(*) AS NumberOfCustomers,
    ROUND(SUM(CustomerRevenue), 2) AS TotalRevenue
FROM (
    SELECT 
        CustomerID,
        COUNT(DISTINCT OrderID) AS OrderCount,
        SUM(Quantity * UnitPrice * (1 - Discount)) AS CustomerRevenue
    FROM retail_orders
    GROUP BY CustomerID
) AS customer_summary
GROUP BY CustomerType;


--Order counts and % share by status (fulfillment/returns)
SELECT 
    OrderStatus,
    COUNT(*) AS OrderCount,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM retail_orders), 1) AS PercentOfTotalOrders
FROM retail_orders
GROUP BY OrderStatus
ORDER BY OrderCount DESC;


--Revenue and order share by payment method
SELECT 
    PaymentMethod,
    COUNT(*) AS OrderCount,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM retail_orders), 1) AS PercentOfOrders,
    ROUND(SUM(Quantity * UnitPrice * (1 - Discount)), 2) AS TotalRevenue
FROM retail_orders
GROUP BY PaymentMethod
ORDER BY TotalRevenue DESC;


--Data quality summary for README
SELECT
    (SELECT COUNT(*) FROM retail_orders) AS TotalRows,
    (SELECT COUNT(*) FROM retail_orders WHERE OrderDate IS NULL) AS MissingOrderDates,
    (SELECT COUNT(*) FROM retail_orders WHERE Email IS NULL) AS MissingEmails,
    (SELECT COUNT(*) FROM retail_orders WHERE order_before_signup = 1) AS OrdersBeforeSignupFlagged;

