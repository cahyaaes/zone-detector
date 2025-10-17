from flask import Flask, request, jsonify
import geopandas as gpd
from shapely.geometry import Point

app = Flask(__name__)

# ======== LOAD FILE KML SAAT STARTUP ========
try:
    print("Loading KML file...")
    zones = gpd.read_file("zona.kml", driver="KML").to_crs(epsg=4326)
    print(f"Loaded {len(zones)} zones.")
except Exception as e:
    print(f"Error loading zona.kml: {e}")
    zones = None


# ======== API ENDPOINT ========
@app.route("/get_zone", methods=["POST"])
def get_zone():
    """
    Terima JSON:
    {
      "latitude": -5.12345,
      "longitude": 119.45678
    }
    """
    if zones is None:
        return jsonify({"error": "Zona file not loaded"}), 500

    data = request.get_json()
    lat = data.get("latitude")
    lon = data.get("longitude")

    if lat is None or lon is None:
        return jsonify({"error": "latitude/longitude missing"}), 400

    point = Point(lon, lat)
    zone_number = None

    for _, row in zones.iterrows():
        if point.within(row.geometry):
            zone_number = row.get("NOZONE_1", None)
            break

    return jsonify({"NOZONE_1": zone_number})


@app.route("/")
def index():
    return jsonify({
        "status": "ok",
        "message": "Zone Detector API is running!",
        "usage": "POST /get_zone with JSON {latitude, longitude}"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
