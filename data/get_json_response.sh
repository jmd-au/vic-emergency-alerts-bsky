#!/bin/bash

SOURCE_URL="https://emergency.vic.gov.au/public/events-geojson.json"

function get_json_response() {
    local path=$1
    curl -X GET \
        $SOURCE_URL \
        -o $path/response.json
}

get_json_response "$(pwd)"