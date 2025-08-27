docker run --rm -it --name optiserve-backend \
  -p 8000:8000 \
  -e DATABASE_URL="sqlite:////data/poc_optigate.db" \
  -e REPORTS_DIR="/data/reports" \
  -e UPLOADS_DIR="/data/uploads" \
  -v "$(pwd)/optiserve-backend:/app" \
  -v "$(pwd)/smds_core:/smds_core" \
  optiserve-backend:dev

