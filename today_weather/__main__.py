import sys


TESTING = sys.argv[-1] == "testing"


from today_weather.__init__ import main


main()