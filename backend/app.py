
from flask import Flask, jsonify, request
import database
import requests
app = Flask(__name__)
@app.route("/api/location-search", methods=["GET"])
def location_search():
    name = request.args.get("name")

    if not name or len(name.strip()) < 2:
        return jsonify({
            "status": "error",
            "message": "Please enter a valid village name"
        }), 400

    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"

        params = {
            "name": name.strip(),
            "count": 5,
            "language": "en",
            "countryCode": "IN"
        }

        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()

        results = response.json().get("results", [])

        if not results:
            return jsonify({
                "status": "error",
                "message": "Location not found"
            }), 404

        locations = []

        for place in results:
            locations.append({
                "name": place["name"],
                "state": place.get("admin1"),
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "country": place.get("country")
            })

        return jsonify({
            "status": "success",
            "locations": locations
        })

    except requests.RequestException:
        return jsonify({
            "status": "error",
            "message": "Location service is unavailable"
        }), 502

@app.route("/")
def home():
    return jsonify({
        "message": "AI-Powered Smart Agriculture Assistant Backend is running!"
    })

@app.route("/api/health")
def health():
    return jsonify({
        "status": "success",
        "message": "Backend is working"
    })

@app.route("/api/db-test")
def db_test():
    try:
        conn = database.get_connection()
        conn.close()
        return {"status": "success", "message": "MySQL connected!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route("/api/farmers", methods=["GET"])
def get_farmers():
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM farmers")
        farmers = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "farmers": farmers
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
@app.route("/api/farms", methods=["POST"])
def register_farm():
    data = request.get_json()

    try:
        conn = database.get_connection()
        cursor = conn.cursor()

        sql = """
        INSERT INTO farms
        (farmer_id, farm_name, crop_name, soil_type, area_acres)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            data["farmer_id"],
            data["farm_name"],
            data["crop_name"],
            data["soil_type"],
            data["area_acres"]
        )

        cursor.execute(sql, values)
        conn.commit()

        farm_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Farm registered successfully",
            "farm_id": farm_id
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
@app.route("/api/farms", methods=["GET"])
def get_farms():
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM farms")
        farms = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "farms": farms
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True)
