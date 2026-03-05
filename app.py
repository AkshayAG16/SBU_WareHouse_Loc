from flask import Flask, render_template, request
import pandas as pd
import os

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

            plant = file.replace(".xlsx","")
            path = os.path.join(PLANT_FOLDER, file)

            print("Loading:", path)

            df = pd.read_excel(path)
            df.columns = df.columns.str.strip()

            df["Part No"] = df["Part No"].astype(str).str.strip().str.upper()
            df["Location Type"] = df["Location Type"].astype(str).str.strip().str.lower()

            for _, row in df.iterrows():

                part = row["Part No"]
                location = str(row["Location"]).strip()
                loc_type = row["Location Type"]

                if part not in parts_db:
                    parts_db[part] = {
                        "plant": plant,
                        "primary": [],
                        "secondary": []
                    }

                if loc_type == "primary":
                    parts_db[part]["primary"].append(location)

                elif loc_type == "secondary":
                    parts_db[part]["secondary"].append(location)

    print("Total parts loaded:", len(parts_db))


# Load Excel when server starts
load_excel_data()


@app.route("/", methods=["GET","POST"])
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
