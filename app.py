from flask import Flask, render_template, request
import pandas as pd
import os
from threading import Thread

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLANT_FOLDER = os.path.join(BASE_DIR, "Plants")

# In-memory database
parts_db = {}

def load_excel_data():
    global parts_db
    parts_db = {}

    if not os.path.exists(PLANT_FOLDER):
        print("Plants folder not found")
        return

    for file in os.listdir(PLANT_FOLDER):
        if file.endswith(".xlsx"):

            plant = file.replace(".xlsx", "")
            path = os.path.join(PLANT_FOLDER, file)

            print("Loading:", path)

            df = pd.read_excel(path, dtype={'Date': str})
            df.columns = df.columns.str.strip()

            df["Part No"] = df["Part No"].astype(str).str.strip().str.upper()
            df["Location Type"] = df["Location Type"].astype(str).str.strip().str.lower()

            for _, row in df.iterrows():
                part = row["Part No"]
                location = str(row["Location"]).strip()
                loc_type = row["Location Type"]

                date = str(row["Date"]).strip()
                qty = str(row["Qty"]).strip()

                location_info = f"{date} | {location} | {qty}"

                if part not in parts_db:
                    parts_db[part] = {
                        "plant": plant,
                        "primary": [],
                        "secondary": []
                    }

                if loc_type == "primary":
                    parts_db[part]["primary"].append(location_info)

                elif loc_type == "secondary":
                    parts_db[part]["secondary"].append(location_info)

    print("Total parts loaded:", len(parts_db))


# 🔥 Run loading in background
def start_background_loading():
    thread = Thread(target=load_excel_data)
    thread.daemon = True
    thread.start()


@app.route("/", methods=["GET", "POST"])
def index():

    searched_part = ""
    plant_name = ""
    primary_locations = []
    secondary_locations = []
    message = ""

    if request.method == "POST":

        searched_part = request.form["part_no"].strip().upper()

        if searched_part in parts_db:

            plant_name = parts_db[searched_part]["plant"]
            primary_locations = parts_db[searched_part]["primary"]
            secondary_locations = parts_db[searched_part]["secondary"]

        else:
            message = "Enter correct part no or its location is not updated"

    return render_template(
        "index.html",
        searched_part=searched_part,
        plant_name=plant_name,
        primary_locations=primary_locations,
        secondary_locations=secondary_locations,
        message=message
    )


# 🔥 Start background loading when app boots
start_background_loading()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
