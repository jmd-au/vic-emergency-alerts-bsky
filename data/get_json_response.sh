#!/bin/bash

SOURCE_URL="https://emergency.vic.gov.au/public/events-geojson.json"

function get_json_response() {
    local path=$1
    curl -X GET \
        $SOURCE_URL \
        -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0" \
        -o $path/response.json
}

get_json_response "$(pwd)"