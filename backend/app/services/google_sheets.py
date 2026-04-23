import gspread
from google.oauth2.service_account import Credentials

# Define scope
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials
creds = Credentials.from_service_account_file(
    "semiotic-vial-479900-f1-fd82833f6af5.json",
    scopes=scope
)

# Authorize client
client = gspread.authorize(creds)

try:
    # Open the Google Sheet
    spreadsheet = client.open("Operational Ledger")

    # Access each tab
    inventory_sheet = spreadsheet.worksheet("Iventory")

    # Dummy data row
    row_data = ["I001", "Apple", "50", "10", "2.50"]

    # Append to next empty row
    inventory_sheet.append_row(row_data)

    print("Data inserted into Inventory!")

    sales_sheet = spreadsheet.worksheet("Sales / Orders")
    customer_sheet = spreadsheet.worksheet("Customer")

    # Read data
    inventory_data = inventory_sheet.get_all_values()
    sales_data = sales_sheet.get_all_values()
    customer_data = customer_sheet.get_all_values()

    print("Inventory Data:")
    print(inventory_data)

    print("\nSales Data:")
    print(sales_data)

    print("\nCustomer Data:")
    print(customer_data)

except Exception as e:
    print("Connection Failed!")
    print(e)