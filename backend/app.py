
from flask import Flask, jsonify, request
import database
import requests
from ai_weather.weather_api import get_weather
from ai_weather.crop_risk import analyze_crop_risk
from ai_weather.irrigation import generate_irrigation_plan
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
    
@app.route("/api/weather", methods=["GET"])
def weather_forecast():

    latitude = request.args.get("latitude")
    longitude = request.args.get("longitude")

    if not latitude or not longitude:
        return jsonify({
            "status": "error",
            "message": "Latitude and longitude are required"
        }), 400

    try:
        weather_data = get_weather(float(latitude), float(longitude))

        return jsonify({
            "status": "success",
            "weather": weather_data
        })

    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Invalid latitude or longitude"
        }), 400

    except requests.RequestException:
        return jsonify({
            "status": "error",
            "message": "Weather service is unavailable"
        }), 502
@app.route("/api/crop-risk", methods=["GET"])
def crop_risk():

    latitude = request.args.get("latitude")
    longitude = request.args.get("longitude")

    if not latitude or not longitude:
        return jsonify({
            "status": "error",
            "message": "Latitude and longitude are required"
        }), 400

    try:
        weather_data = get_weather(float(latitude), float(longitude))
        alerts = analyze_crop_risk(weather_data)

        return jsonify({
            "status": "success",
            "crop_risk_alerts": alerts
        })

    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Invalid latitude or longitude"
        }), 400

    except requests.RequestException:
        return jsonify({
            "status": "error",
            "message": "Weather service is unavailable"
        }), 502
@app.route("/api/irrigation", methods=["GET"])
def irrigation_recommendation():

    latitude = request.args.get("latitude")
    longitude = request.args.get("longitude")

    if not latitude or not longitude:
        return jsonify({
            "status": "error",
            "message": "Latitude and longitude are required"
        }), 400

    try:
        weather_data = get_weather(float(latitude), float(longitude))

        plan = generate_irrigation_plan(weather_data)

        return jsonify({
            "status": "success",
            "irrigation_plan": plan
        })

    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Invalid latitude or longitude"
        }), 400

    except requests.RequestException:
        return jsonify({
            "status": "error",
            "message": "Weather service is unavailable"
        }), 502
@app.route("/api/save-weather", methods=["POST"])
def save_weather():

    data = request.get_json() or {}

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if latitude is None or longitude is None:
        return jsonify({
            "status": "error",
            "message": "Latitude and longitude are required"
        }), 400

    conn = None
    cursor = None

    try:
        weather_data = get_weather(float(latitude), float(longitude))
        daily = weather_data["daily"]

        conn = database.get_connection()
        cursor = conn.cursor()

        sql = """
        INSERT INTO weather_records
        (location, temperature, rainfall, forecast_date,
         rain_probability, evapotranspiration)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        location = data.get("location", f"{latitude}, {longitude}")

        records = []

        for i in range(len(daily["time"])):
            records.append((
                location,
                daily["temperature_2m_max"][i],
                daily["precipitation_sum"][i],
                daily["time"][i],
                daily["precipitation_probability_max"][i],
                daily["et0_fao_evapotranspiration"][i]
            ))

        cursor.executemany(sql, records)
        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Weather forecast saved successfully",
            "records_saved": cursor.rowcount
        })

    except (ValueError, requests.RequestException) as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
@app.route("/api/save-irrigation", methods=["POST"])
def save_irrigation():

    data = request.get_json() or {}

    latitude = data.get("latitude")
    longitude = data.get("longitude")
    farm_id = data.get("farm_id")

    if latitude is None or longitude is None or farm_id is None:
        return jsonify({
            "status": "error",
            "message": "Latitude, longitude and farm_id are required"
        }), 400

    conn = None
    cursor = None

    try:
        weather_data = get_weather(float(latitude), float(longitude))
        plan = generate_irrigation_plan(weather_data)

        conn = database.get_connection()
        cursor = conn.cursor()

        sql = """
        INSERT INTO irrigation_plans
        (farm_id, soil_moisture, forecast_rainfall,
         rain_probability, evapotranspiration,
         recommendation, reason)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            farm_id,
            plan["soil_moisture"],
            plan["forecast_rainfall_mm"],
            plan["rain_probability_percent"],
            plan["evapotranspiration_mm"],
            plan["recommendation"],
            plan["reason"]
        )

        cursor.execute(sql, values)
        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Irrigation plan saved successfully",
            "irrigation_plan": plan
        })

    except (ValueError, requests.RequestException) as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
if __name__ == "__main__":
    app.run(debug=True)
