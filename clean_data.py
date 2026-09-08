#Joshua Aldo: Data Analyst Project

import pandas as pd
import matplotlib.pyplot as plt 

df = pd.read_csv('retail_orders_messy.csv')

print(df.info())
print(df.isna().sum())

#Find rows where Quantity can't be converted to a number
non_numeric_quantity_qty = df[pd.to_numeric(df['Quantity'], errors = 'coerce').isna()]
print(non_numeric_quantity_qty['Quantity'].unique())

#Map spelled out quantities to numbers, then convert the rest
word_to_num = {'two': 2, 'five': 5}
df['Quantity'] = df['Quantity'].replace(word_to_num)
df['Quantity'] = pd.to_numeric(df['Quantity'], errors = 'coerce')

#Check for negative quantities
print(df[df['Quantity'] < 0]['Quantity'].unique())
print(df['Quantity'].isna().sum())

#Fix negatives, fill missing with median
df['Quantity'] = df['Quantity'].abs()
median_qty = df['Quantity'].median()
df['Quantity'] = df['Quantity'].fillna(median_qty)
print(df['Quantity'].isna().sum())

#Remove $ sign from UnitPrice, convert to numeric
df['UnitPrice'] = df['UnitPrice'].astype(str).str.replace('$', '', regex=False)
df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce')
print(df['UnitPrice'].describe())

#Check for negatives and decimal shift errors
print((df['UnitPrice'] < 0 ).sum())
print((df['UnitPrice'] > 1000).sum())

#Fix decimal shift and negatives
df.loc[df['UnitPrice'] > 1000, 'UnitPrice'] = df['UnitPrice'] / 100
df['UnitPrice'] = df['UnitPrice'].abs()
print(df['UnitPrice'].describe())

#Impute missing UnitPrice using median price per category
df['UnitPrice'] = df.groupby('ProductCategory')['UnitPrice'].transform(
    lambda x: x.fillna(x.median())
)
print(df['UnitPrice'].isna().sum())
print(df[df['UnitPrice'].isna()][['ProductCategory', 'UnitPrice']])

#Drop rows still missing UnitPrice
df = df.dropna(subset=['UnitPrice'])
print(df['UnitPrice'].isna().sum())
print(df.shape)

#Convert Discount to decimal, handle % signs
df['Discount'] = df['Discount'].astype(str)
print(df['Discount'].unique())

df['Discount'] = df['Discount'].str.rstrip('%')
df['Discount'] = pd.to_numeric(df['Discount'], errors='coerce')
df.loc[df['Discount'] > 1, 'Discount'] = df['Discount'] / 100
print(df['Discount'].unique())

#Fill missing Discounts with 0
df['Discount'] = df['Discount'].fillna(0)
print(df['Discount'].isna().sum())

#Clean up Region
df['Region'] = df['Region'].str.strip().str.title()
print(df['Region'].unique())

region_map = {
    'Est': 'East',
    'Sth': 'South',
    'Nort': 'North',
    'Centrl': 'Central'
}
df['Region'] = df['Region'].replace(region_map)
print(df['Region'].unique())

#Clean up Country
df['Country'] = df['Country'].str.strip().str.title()
print(df['Country'].unique())

country_map = {
    'Usa': 'United States',
    'Us': 'United States',
    'United States': 'United States'
}
df['Country'] = df['Country'].replace(country_map)
print(df['Country'].unique())

#Clean up ProductCategory
df['ProductCategory'] = df['ProductCategory'].str.strip().str.title()
print(df['ProductCategory'].unique())

category_map = {
    'Home&Kitchen': 'Home & Kitchen',
    'Home And Kitchen': 'Home & Kitchen',
    'Appare': 'Apparel',
    'Clothing': 'Apparel',
    'Sports And Outdoors': 'Sports & Outdoors',
    'Sports': 'Sports & Outdoors',
    'Electronic': 'Electronics',
    'Electronis': 'Electronics',
    'Toy': 'Toys',
    'Beuty': 'Beauty'
}
df['ProductCategory'] = df['ProductCategory'].replace(category_map)
print(df['ProductCategory'].unique())

#Clean up PaymentMethod
df['PaymentMethod'] = df['PaymentMethod'].str.strip().str.title()
print(df['PaymentMethod'].unique())

payment_map = {
    'Cc': 'Credit Card',
    'Credit_Card': 'Credit Card',
    'Giftcard': 'Gift Card',
    'Debit': 'Debit Card',
    'Pay Pal': 'Paypal'
}
df['PaymentMethod'] = df['PaymentMethod'].replace(payment_map)
print(df['PaymentMethod'].unique())

#Clean up OrderStatus
df['OrderStatus'] = df['OrderStatus'].str.strip().str.title()
print(df['OrderStatus'].unique())

status_map = {
    'Deliverd': 'Delivered',
    'Canceled': 'Cancelled'
}
df['OrderStatus'] = df['OrderStatus'].replace(status_map)
print(df['OrderStatus'].unique())

#Impute missing ShippingCost using median cost per region
df['ShippingCost'] = df.groupby('Region')['ShippingCost'].transform(
    lambda x: x.fillna(x.median())
)
print(df['ShippingCost'].isna().sum())

#Convert OrderDate to datetime
df['OrderDate'] = pd.to_datetime(df['OrderDate'], format='mixed', errors='coerce')
print(df['OrderDate'].isna().sum())

#Check raw values that failed to parse
raw = pd.read_csv('retail_orders_messy.csv')
failed_mask = pd.to_datetime(raw['OrderDate'], format='mixed', errors='coerce').isna()
print(raw.loc[failed_mask, 'OrderDate'].unique())

#Convert SignupDate to datetime
df['SignupDate'] = pd.to_datetime(df['SignupDate'], format='mixed', errors='coerce')
print(df['SignupDate'].isna().sum())

#Find orders that happened before signup
bad_dates = df[df['OrderDate'] < df['SignupDate']]
print(len(bad_dates))
print(bad_dates[['OrderDate', 'SignupDate']])

bad_dates = bad_dates.copy()
bad_dates['days_before_signup'] = (bad_dates['SignupDate'] - bad_dates['OrderDate']).dt.days
print(bad_dates['days_before_signup'].describe())

#Flag these orders instead of dropping them
df['order_before_signup'] = df['OrderDate'] < df['SignupDate']
print(df['order_before_signup'].sum())

#Clean up ProductName
df['ProductName'] = df['ProductName'].str.strip().str.title()
print(df['ProductName'].unique())

product_name_map = {
    'Led Desk Lamp': 'LED Desk Lamp',
    'Usb-C Cable': 'USB-C Cable',
    'Rc Car': 'RC Car',
    'Sunscreen Spf50': 'Sunscreen SPF50',
    'Puzzle 1000Pc': 'Puzzle 1000PC'
}
df['ProductName'] = df['ProductName'].replace(product_name_map)
print(df['ProductName'].unique())

#Clean up CustomerName
df['CustomerName'] = df['CustomerName'].str.strip().str.title()
print(df['CustomerName'].unique())

#Remove honorific prefixes
df['CustomerName'] = df['CustomerName'].str.replace(r'^(Mr|Mrs|Ms|Dr)\.\s*', '', regex=True)
print(df['CustomerName'].str.contains(r'^(?:Mr|Mrs|Ms|Dr)\.', regex=True).sum())

#Check which OrderIDs are missing the ORD- prefix
missing_prefix = ~df['OrderID'].str.contains('ORD-', na=False)
print(missing_prefix.sum())

df.loc[missing_prefix, 'OrderID'] = 'ORD-' + df.loc[missing_prefix, 'OrderID']
print((~df['OrderID'].str.contains('ORD-', na=False)).sum())

#Find duplicate OrderIDs
dupe_rows = df[df.duplicated(subset='OrderID', keep=False)]
print(len(dupe_rows))
print(dupe_rows.sort_values('OrderID')[['OrderID', 'CustomerID', 'OrderDate', 'ProductName', 'Quantity']])

#Check if they're true full-row duplicates or just a repeated ID
full_dupes = df[df.duplicated(keep=False)]
print(len(full_dupes))

partial_dupes = dupe_rows[~dupe_rows.index.isin(full_dupes.index)]
print(len(partial_dupes))
print(partial_dupes.sort_values('OrderID')[['OrderID', 'CustomerID', 'OrderDate', 'ProductName', 'Quantity']])

#Drop full-row duplicates, keep first occurrence
df = df.drop_duplicates(keep='first')
print(df.duplicated().sum())
print(df.shape)

#Check CustomerID for missing values and format issues
print(df['CustomerID'].isna().sum())
print(df['CustomerID'].nunique())
print(df['CustomerID'].unique())

bad_format = ~df['CustomerID'].str.contains(r'^CUST\d+$', regex=True, na=False)
print(bad_format.sum())
print(df.loc[bad_format, 'CustomerID'].unique())

#Confirm blank emails are stored as NaN
print(df['Email'].isna().sum())

#An email needs an @ symbol - check which ones don't have one
has_at_symbol = df['Email'].str.contains('@', na=False)
missing_at_symbol = df[(~has_at_symbol) & (df['Email'].notna())]
print('emails missing @ symbol:', len(missing_at_symbol))
print(missing_at_symbol['Email'].unique())

#These use '.at.' instead of '@' - fix it
df['Email'] = df['Email'].str.replace('.at.', '@', n=1, regex=False)

#Confirm the fix
has_at_symbol = df['Email'].str.contains('@', na=False)
still_missing = df[(~has_at_symbol) & (df['Email'].notna())]
print('emails still missing @ symbol:', len(still_missing))

#Save cleaned data, confirm it reloads correctly
df.to_csv('retail_orders_cleaned.csv', index=False)
check = pd.read_csv('retail_orders_cleaned.csv')
print(check.shape)
print(check.info())

#Phase 3: Load cleaned data into MySQL
#LOAD DATA LOCAL INFILE was blocked, so loading through Python/SQLAlchemy instead
from sqlalchemy import create_engine

engine = create_engine('mysql+mysqlconnector://root:@localhost:3306/retail_orders_project')
df.to_sql('retail_orders', con=engine, if_exists='replace', index=False)
print("Rows loaded into MySQL:", len(df))

#Verify the data actually landed, using the same connection just used to write it
check_count = pd.read_sql("SELECT COUNT(*) FROM retail_orders", con=engine)
print(check_count)

#Phase 4: Revenue over time chart
df['Revenue'] = df['Quantity'] * df['UnitPrice'] * (1 - df['Discount'])

#Drop rows with no date, use .copy() to avoid a pandas warning
df_with_dates = df.dropna(subset=['OrderDate']).copy()

#Shrink each date down to just year and month
df_with_dates['OrderMonth'] = df_with_dates['OrderDate'].dt.to_period('M')

#Sum revenue by month
monthly_revenue = df_with_dates.groupby('OrderMonth')['Revenue'].sum()
monthly_revenue.index = monthly_revenue.index.astype(str)

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(monthly_revenue.index, monthly_revenue.values, marker='o')
ax.set_title('Total Revenue Over Time')
ax.set_xlabel('Month')
ax.set_ylabel('Revenue ($)')
plt.xticks(rotation=45, ha='right')
plt.savefig('revenue_over_time.png')