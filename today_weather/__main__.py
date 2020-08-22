import sys


TESTING = sys.argv[-1] == "testing"


from today_weather.bot import main


if __name__ == "__main__":
    main()
