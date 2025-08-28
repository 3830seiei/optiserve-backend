docker run --rm -it --name optiserve-backend \
  -p 8000:8000 \
  -e DATABASE_URL="sqlite:////app/poc_optigate.db" \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/files:/app/files" \
  optiserve-backend:dev

#docker run --rm -it --name optiserve-backend \
#  -p 8000:8000 \
#  -e DATABASE_URL="sqlite:////data/poc_optigate.db" \
#  -e REPORTS_DIR="/data/reports" \
#  -e UPLOADS_DIR="/data/uploads" \
#  -v "$(pwd)/optiserve-backend:/app" \
#  optiserve-backend:dev
