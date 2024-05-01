from script import render_message
import datetime

if __name__ == "__main__":
    import sys
    datetime_object = None
    if len(sys.argv) == 4:
        datetime_object = datetime.datetime.strptime(sys.argv[3], '%d/%m/%Y')
        
    print(render_message(sys.argv[1], sys.argv[2],datetime_object))
