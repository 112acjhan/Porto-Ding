import gspread
from google.oauth2.service_account import Credentials
from app.models.schemas import InventoryItem, InventoryUpdate, Order, OrderStatusUpdate, Customer

class GoogleSheetsService:
    def __init__(self):
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file("semiotic-vial-479900-f1-fd82833f6af5.json", scopes=scope)
        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open("Operational Ledger")
        
        self.inventory_sheet = self.spreadsheet.worksheet("Inventory")
        self.sales_sheet     = self.spreadsheet.worksheet("Sales / Orders")
        self.customers_sheet = self.spreadsheet.worksheet("Customer")

    # ─── INVENTORY METHODS ───────────────────────────────────────────
    def get_all_inventory(self):
        return self.inventory_sheet.get_all_records()

    def add_inventory_row(self, item: InventoryItem):
        self.inventory_sheet.append_row([item.item_id, item.item_name, item.stock_level, item.reorder_point, item.unit_price])

    def update_inventory_row(self, item_id: str, updates: InventoryUpdate):
        records = self.inventory_sheet.get_all_records()
        for i, row in enumerate(records):
            if str(row.get("item_id")) == str(item_id):
                sheet_row = i + 2
                if updates.item_name: self.inventory_sheet.update_cell(sheet_row, 2, updates.item_name)
                if updates.stock_level is not None: self.inventory_sheet.update_cell(sheet_row, 3, updates.stock_level)
                if updates.reorder_point is not None: self.inventory_sheet.update_cell(sheet_row, 4, updates.reorder_point)
                if updates.unit_price is not None: self.inventory_sheet.update_cell(sheet_row, 5, updates.unit_price)
                return True
        return False

    def delete_inventory_row(self, item_id: str):
        records = self.inventory_sheet.get_all_records()
        for i, row in enumerate(records):
            if str(row.get("item_id")) == str(item_id):
                self.inventory_sheet.delete_rows(i + 2)
                return True
        return False

    # ─── ORDERS METHODS ──────────────────────────────────────────────
    def get_all_orders(self):
        return self.sales_sheet.get_all_records()

    def add_order_row(self, order: Order):
        self.sales_sheet.append_row([order.order_id, order.timestamp, order.customer_name, order.total_amount, order.status])

    def update_order_status_row(self, order_id: str, status: str):
        records = self.sales_sheet.get_all_records()
        for i, row in enumerate(records):
            if str(row.get("order_id")) == str(order_id):
                self.sales_sheet.update_cell(i + 2, 5, status)
                return True
        return False

    def delete_order_row(self, order_id: str):
        records = self.sales_sheet.get_all_records()
        for i, row in enumerate(records):
            if str(row.get("order_id")) == str(order_id):
                self.sales_sheet.delete_rows(i + 2)
                return True
        return False

    # ─── CUSTOMER METHODS ────────────────────────────────────────────
    def get_all_customers(self):
        return self.customers_sheet.get_all_records()

    def add_customer_row(self, customer: Customer):
        self.customers_sheet.append_row([customer.customer_id, customer.contact_person, customer.masked_bank_details, customer.masked_ic_number])

    def delete_customer_row(self, customer_id: str):
        records = self.customers_sheet.get_all_records()
        for i, row in enumerate(records):
            if str(row.get("customer_id")) == str(customer_id):
                self.customers_sheet.delete_rows(i + 2)
                return True
        return False