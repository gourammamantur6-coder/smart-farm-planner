
def generate_irrigation_plan(weather_data, moisture_threshold=0.25):

    hourly = weather_data["hourly"]
    daily = weather_data["daily"]

    # Get modelled upper root-zone soil moisture
    soil_moisture = hourly[
        "soil_moisture_7_to_28cm"
    ][0]

    # Get today's forecast
    rainfall = daily["precipitation_sum"][0]
    rain_probability = daily[
        "precipitation_probability_max"
    ][0]

    evapotranspiration = daily[
        "et0_fao_evapotranspiration"
    ][0]

    # Make irrigation recommendation
    if soil_moisture < moisture_threshold:

        if rainfall >= 2 and rain_probability >= 60:
            recommendation = "Wait for expected rainfall"
            reason = "Soil moisture is low, but rain is forecast."

        else:
            recommendation = "Irrigation may be required"
            reason = "Soil moisture is below the prototype threshold."

    else:
        recommendation = "No immediate irrigation"
        reason = "Modelled root-zone moisture is above the prototype threshold."

    return {
        "soil_moisture": soil_moisture,
        "forecast_rainfall_mm": rainfall,
        "rain_probability_percent": rain_probability,
        "evapotranspiration_mm": evapotranspiration,
        "recommendation": recommendation,
        "reason": reason
    }
