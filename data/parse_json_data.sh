#!/bin/bash

jq -c '[ .features[] | select(.properties.feedType == "warning") | { id: (.properties.id|tonumber), title: (.properties.sourceTitle | ascii_upcase), location: .properties.location, category: .properties.cap.category, event: (.properties.cap.event | ascii_upcase), senderAgency: .properties.cap.senderName, action: (.properties.action | ascii_upcase), urgency: .properties.cap.urgency, severity: .properties.cap.severity, certainty: .properties.cap.certainty, text: ((.properties.text | split("moreinfo\n")[0]) + "moreinfo"), url: ("https://emergency.vic.gov.au/respond/#!/warning/" + .properties.sourceId + "/moreinfo"), created: .properties.created, updated: .properties.updated } ]' $(pwd)/response.json | jq -r .[].text > $(pwd)/output.txt

# > formatted_response.json


# DATA=$(jq -c '.[]' $(pwd)/formatted_response.json)



# echo "${DATA[@]}"

# | jq -r .[].text > $(pwd)/output.txt

# for entry in "${DATA[@]}"
# do
#     entry_id=$(jq '.id' <<< "$entry")
#     # echo "Processing entry $entry_id"
#     echo $entry
#     echo ""
#     echo ""
#     echo "---------------------"
#     echo ""
#     # echo $entry > "$(pwd)/data/$entry_id.json"
# done

# jq '.|sort_by(.[].id)' |

# jq '[ .features[] | select(.properties.feedType == "warning") | { id: .properties.id, title: (.properties.sourceTitle | ascii_upcase), location: .properties.location, category: .properties.cap.category, event: (.properties.cap.event | ascii_upcase), senderAgency: .properties.cap.senderName, action: (.properties.action | ascii_upcase), urgency: .properties.cap.urgency, severity: .properties.cap.severity, certainty: .properties.cap.certainty, text: ((.properties.text | split("moreinfo\n")[0]) + "moreinfo"), url: ("https://emergency.vic.gov.au/respond/#!/warning/" + .properties.sourceId + "/moreinfo"), created: .properties.created, updated: .properties.updated } ]' $(pwd)/response.json | jq -r '((if .[].title == "Advice" then "⚠️ " elif .[].title == "Emergency Warning" then "🔴" else "" end) + .[].text)' > $(pwd)/output.txt