

docker kill $(docker ps -q)

mkdir -p graph

##osmconvert oregon-latest.osm.pbf -b=-123.043,45.246,-122.276,45.652 --complete-ways -o=graph/bage.pbf
#osmconvert sul-latest.osm.pbf -b=-54.2,-31.4,-54.0,-31.2 --complete-ways -o=graph/bage.pbf

osmconvert jf-latest.osm.pbf -b=-43.932,-22.259,-42.599,-21.468 --complete-ways -o=graph/jf.pbf

java -Xmx4G -jar ~/otp/otp-2.4.0-shaded.jar --build --serve --port 8080 ./graph
