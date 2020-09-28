npx redoc-cli bundle -o docs/redoc.html spec.yaml
python swagger-yaml-to-html.py < ./spec.yaml > ./docs/swagger.html
