import json
import copy

GEOJSON_TEMPLATE = {
    "type": "Feature",
    "geometry": {
        "type": "Point",
        "coordinates": [0, 0],
    },
    "properties": {
        "challenge_id": 0,
        "event": "",
        "challenge_type": "",
    },
}


def geojson_serialize(queryset):
    final_data = []
    for challenge in queryset:
        geojson = json_to_geojson(challenge)
        #import pdb;pdb.set_trace()
        final_data.append(geojson)
    final_data = json.dumps(final_data)
    return final_data
    
def json_to_geojson(data):
    geojson_template = copy.deepcopy(GEOJSON_TEMPLATE)
    geojson_template["geometry"]["coordinates"] = data.longitude, data.latitude
    geojson_template["properties"]["challenge_id"] = data.id
    geojson_template["properties"]["event"] = data.event_id
    geojson_template["properties"]["challenge_type"] = data.challenge_type
    return geojson_template


