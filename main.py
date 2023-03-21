from flask import Flask, send_file, render_template, Response, request, Response
import os
import csv
from werkzeug.security import check_password_hash


app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")
password_hash = "pbkdf2:sha256:260000$E5JkMcO1xPv6jTOs$c8d222f76b1f70af9fa01577e5ebd877d19d5e0623dfcf512d5fb50de40f03b7"


def get_properties():
     return os.listdir(app.config["PROPERTY_PATH"])

@app.route("/")
def index():
    return render_template("index.html", requested_properties=get_properties())


@app.route('/get_data', methods=["POST"])
def get_data():
    if "password" in request.form:
        try:
            user_pwd = request.form["password"]

            if check_password_hash(password_hash, user_pwd):
                for data_file in os.listdir(app.config["SCRAPER_PATH"]):
                    if "data" in data_file:
                        return send_file(app.config["SCRAPER_PATH"] + data_file, as_attachment=True)

                return render_template("index.html", scraper_status="The data was not found. Try again later or contact the developer.")
            return render_template("index.html", password_status="Password is wrong.", requested_properties=get_properties())

        except Exception:
                return render_template("index.html", scraper_status="The data was not found. Try again later or contact the developer.", requested_properties=get_properties())
    return render_template("index.html", password_status="Type password.", requested_properties=get_properties())


@app.route('/request_property', methods=["POST"])
def request_property():
    if "password" in request.form:
        try:
            user_pwd = request.form["password"]

            if check_password_hash(password_hash, user_pwd):
                if ("property_number" not in request.form):
                     return render_template("index.html", property_status="Write the property number", requested_properties=get_properties())

                if not request.form["property_number"].isnumeric():
                    return render_template("index.html", property_status="The property number is not valid.", requested_properties=get_properties())

                with open('requested_properties.txt', 'a+') as f:
                    f.write(f"{request.form['property_number']}\n")

                return render_template("index.html", property_status="The property data are requested. Come back tommorow.", requested_properties=get_properties())

            return render_template("index.html", password_status="Password is wrong.", requested_properties=get_properties())

        except Exception:
                return render_template("index.html", property_status="The data was not found. Try again later or contact the developer.", requested_properties=get_properties())
    return render_template("index.html", password_status="Type password.", requested_properties=get_properties())


@app.route('/get_property', methods=["POST", "GET"])
def get_property():
    if "password" in request.form:
        try:
            user_pwd = request.form["password"]
            if check_password_hash(password_hash, user_pwd):

                if "property_delete_name" in request.form:
                    # Delete method
                    property_name = request.form["property_delete_name"]
                    print(f"Deleting {property_name}")

                    os.remove(app.config["PROPERTY_PATH"] + property_name)
                    return render_template("index.html", property_status="Deleted succesfully", requested_properties=get_properties())

                print(request.form["property_name"])
                for data_file in os.listdir(app.config["PROPERTY_PATH"]):
                    if request.form["property_name"] in data_file:
                        return send_file(app.config["PROPERTY_PATH"] + request.form["property_name"], as_attachment=True)
                return render_template("index.html", property_status="The data was not found. Try again later or contact the developer.", requested_properties=get_properties())

            return render_template("index.html", password_status="Password is wrong.", requested_properties=get_properties())

        except Exception as e:
                print(e)
                return render_template("index.html", property_status="The data was not found. Try again later or contact the developer.", requested_properties=get_properties())
    return render_template("index.html", password_status="Type password.", requested_properties=get_properties())
