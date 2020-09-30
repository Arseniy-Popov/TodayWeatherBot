npx redoc-cli bundle -o static/redoc.html spec.yaml
python swagger-yaml-to-html.py < ./spec.yaml > ./static/swagger.html
