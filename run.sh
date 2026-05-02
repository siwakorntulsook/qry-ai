sudo docker run --name qry-ai \
    -e POSTGRES_PASSWORD=1234 \
    -e POSTGRES_USER=1234 \
    -p 5432:5432 \
    -d postgres \
    -v $(pwd)/init.sql:/docker-entrypoint-initdb.d/init.sql