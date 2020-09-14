npx redoc-cli bundle -o today_weather/docs/redoc.html spec.yaml
python swagger-yaml-to-html.py < ./spec.yaml > ./today_weather/docs/swagger.html
