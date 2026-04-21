from flask import Flask, jsonify, request
from flask_cors import CORS
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)
CORS(app)

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "semiotic-vial-479900-f1-fd82833f6af5.json",
    scopes=scope
)

client = gspread.authorize(creds)
spreadsheet = client.open("Operational Ledger")
inventory_sheet = spreadsheet.worksheet("Iventory")


@app.route("/api/inventory", methods=["GET"])
def get_inventory():
    try:
        data = inventory_sheet.get_all_records()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/inventory", methods=["POST"])
def add_inventory():
    try:
        body = request.json
        row = [
            body.get("item_id", ""),
            body.get("item_name", ""),
            body.get("stock_level", ""),
            body.get("reorder_point", ""),
            body.get("unit_price", ""),
        ]
        inventory_sheet.append_row(row)
        return jsonify({"success": True, "inserted": row}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/inventory/<item_id>", methods=["DELETE"])
def delete_inventory(item_id):
    try:
        records = inventory_sheet.get_all_records()
        for i, row in enumerate(records):
            if str(row.get("item_id")) == str(item_id):  # ← fixed key
                inventory_sheet.delete_rows(i + 2)
                return jsonify({"success": True, "deleted_id": item_id}), 200
        return jsonify({"error": f"item_id '{item_id}' not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/inventory/<item_id>", methods=["PUT"])
def update_inventory(item_id):
    try:
        body = request.json
        records = inventory_sheet.get_all_records()
        for i, row in enumerate(records):
            if str(row.get("item_id")) == str(item_id):  # ← fixed key
                sheet_row = i + 2
                inventory_sheet.update_cell(sheet_row, 1, body.get("item_id",      row["item_id"]))
                inventory_sheet.update_cell(sheet_row, 2, body.get("item_name",    row["item_name"]))
                inventory_sheet.update_cell(sheet_row, 3, body.get("stock_level",  row["stock_level"]))
                inventory_sheet.update_cell(sheet_row, 4, body.get("reorder_point",row["reorder_point"]))
                inventory_sheet.update_cell(sheet_row, 5, body.get("unit_price",   row["unit_price"]))
                return jsonify({"success": True}), 200
        return jsonify({"error": f"item_id '{item_id}' not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "sheet": "Operational Ledger"}), 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)