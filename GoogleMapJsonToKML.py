import json
import simplekml

# --------------------------
# File Paths
# Process :　json -> geojson -> kml
# --------------------------
source_json = r"C:\Users\Ian\Downloads\timeline.json"
output_kml = r"C:\Users\Ian\Downloads\output.kml"
# output_geojson (Optional)= r"C:\Users\Ian\Downloads\output.geojson"  


# --------------------------
# Main Function
# --------------------------
# Load JSON data
with open(source_json, "r", encoding="utf-8") as file:
    data = json.load(file)                                    

# Convert JSON to GeoJSON format
geojson = {
    "type": "FeatureCollection",
    "features": []
}

for segment in data.get("semanticSegments", []):
    # ---- Visit ----
    if "visit" in segment:
        visit = segment["visit"]
        loc = visit["topCandidate"]["placeLocation"]["latLng"].replace("°", "").split(", ")
        lat, lon = map(float, loc)
        geojson["features"].append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "type": "visit",
                "semanticType": visit["topCandidate"].get("semanticType", "Unknown"),
                "startTime": segment.get("startTime"),
                "endTime": segment.get("endTime")
            }
        })

    # ---- Activity Record ----
    if "activityRecord" in segment:
        act = segment["activityRecord"]
        activities = act.get("probableActivities", [])
        if activities:
            best = max(activities, key=lambda x: x["confidence"])
            geojson["features"].append({
                "type": "Feature",
                "geometry": None,  # None target
                "properties": {
                    "type": "activity",
                    "timestamp": act.get("timestamp"),
                    "bestActivity": best["type"],
                    "confidence": best["confidence"]
                }
            })

    # ---- Timeline Path ----
    if "timelinePath" in segment:
        coords = []
        for point in segment["timelinePath"]:
            lat, lon = map(float, point["point"].replace("°", "").split(", "))
            coords.append([lon, lat])
        if coords:
            geojson["features"].append({
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": coords},
                "properties": {"type": "path"}
            })

# Save the GeoJSON file (Optional)
# output_geojson = r"C:\Users\Ian\Downloads\output.geojson"
# with open(output_geojson, "w", encoding="utf-8") as geojson_file:
#     json.dump(geojson, geojson_file, indent=4)

# print(f"GeoJSON file saved to: {output_geojson}")


# --------------------------
# GeoJSON → KML 
# --------------------------
kml = simplekml.Kml()

for feature in geojson["features"]:
    geom = feature["geometry"]
    props = feature["properties"]

    if geom is None:  # activity
        kml.newpoint(
            name=f"Activity: {props['bestActivity']}",
            description=f"Confidence: {props['confidence']}<br>Time: {props.get('timestamp')}"
        )

    elif geom["type"] == "Point":
        lon, lat = geom["coordinates"]
        kml.newpoint(
            name=f"Visit ({props.get('semanticType')})",
            coords=[(lon, lat)],
            description=f"Start: {props.get('startTime')}<br>End: {props.get('endTime')}"
        )

    elif geom["type"] == "LineString":
        coords = geom["coordinates"]
        kml.newlinestring(
            name="Path",
            coords=coords,
            description="Timeline Path"
        )

# Save KML
output_kml = r"C:\Users\Ian\Downloads\output.kml"
kml.save(output_kml)

print(f"KML file saved to: {output_kml}")