from flask import Flask, render_template, request, redirect
import pandas as pd
import os

app = Flask(__name__)

PLANT_FOLDER = "Plants"

@app.route("/", methods=["GET", "POST"])
def index():

    results = []
    primary_locations = []
    secondary_locations = []
    plant_name = ""
    searched_part = ""
    message = ""

    if request.method == "POST":

        searched_part = request.form["part_no"].strip().upper()

        for file in os.listdir(PLANT_FOLDER):

            if file.endswith(".xlsx"):

                plant = file.replace(".xlsx","")
                path = os.path.join(PLANT_FOLDER,file)

                df = pd.read_excel(path)

                df["Part No"] = df["Part No"].astype(str).str.upper()

                filtered = df[df["Part No"] == searched_part]

                if not filtered.empty:

                    plant_name = plant

                    for _,row in filtered.iterrows():

                        if str(row["Location Type"]).lower() == "primary":
                            primary_locations.append(row["Location"])

                        if str(row["Location Type"]).lower() == "secondary":
                            secondary_locations.append(row["Location"])

        if len(primary_locations)==0 and len(secondary_locations)==0:
            message = "Enter correct part no or its location is not updated"

    return render_template(
        "index.html",
        searched_part=searched_part,
        plant_name=plant_name,
        primary_locations=primary_locations,
        secondary_locations=secondary_locations,
        message=message
    )


@app.route("/upload", methods=["GET","POST"])
def upload():

    if request.method == "POST":

        file = request.files["file"]

        if file.filename != "":
            path = os.path.join(PLANT_FOLDER,file.filename)
            file.save(path)

        return redirect("/")

    return render_template("upload.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

