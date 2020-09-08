from flask import Flask
from flask_marshmallow import Marshmallow


app = Flask(__name__)
ma = Marshmallow(app)


from today_weather.router import 



if __name__ == "__main__":
    main()
