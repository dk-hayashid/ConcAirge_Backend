from datetime import datetime
def return_age(inp: str):
    dt_now = datetime.now()
    dt_inp = datetime.strptime(inp.split('T')[0], '%Y-%m-%d')
    td = dt_now - dt_inp
    age = int(td.days/365)
    return age