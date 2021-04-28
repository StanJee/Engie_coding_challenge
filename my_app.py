from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/')
def index():
    return 'home page'

@app.route('/productionplan', methods=["POST"])
def productionplan():
    data = request.get_json()
    #Getting basic data from .json
    expected_load = data["load"]
    gas_price = data["fuels"]["co2(euro/ton)"]
    kerosine_price = data["fuels"]["kerosine(euro/MWh)"]
    wind = data["fuels"]["wind(%)"]

    #separating windturbines from other powerplants (because windturbines will always be the first to be use)
    windturbines = []
    rest = []
    turbojets = []

    for powerplant in data["powerplants"]:
        if powerplant["type"] == "windturbine":
            windturbines.append(powerplant)
        else:
            rest.append(powerplant)

    windturbines.sort(key=lambda x: x.get('pmax'), reverse = True)

    #sorting other powerplants by cost (efficiency/price) (imagine a world where kerosine is cheaper than gas)
    #then sort by pmax (so the powerplant with the lower cost and the higher pmax works in priority)
    def getPrice(powerplant):
        if powerplant.get('type') == "gasfired" and gas_price != 0:
            return powerplant.get('efficiency') / gas_price
        elif powerplant.get('type') == "turbojet" and kerosine_price != 0:
            return powerplant.get('efficiency') / kerosine_price

    rest.sort(key=lambda x: (getPrice(x), x.get('pmax')), reverse = True)

    #now powerplants = merit_ordered powerplants
    if wind == 0:
        rest.extend(windturbines)
        powerplants = rest
    else:
        windturbines.extend(rest)
        powerplants = windturbines

    def getPower(powerplant):
        if powerplant.get('type') == "windturbine":
            return powerplant.get('pmax') * wind / 100
        else:
            return powerplant.get('pmax')

    #function used to fill the rest of the powerplants with 0 power when the expected load is reached
    def fill_dict(result, powerplants, i):
        for j in range (i, len(powerplants)):
            result[powerplants[j].get('name')] = 0
        return result

    #algo
    def calculate_power(powerplants, load):
        result = {}
        tmp_load = 0
        for i in range (len(powerplants)):
            if tmp_load == load:
                return fill_dict(result, powerplants, i + 1)
            if getPower(powerplants[i]) + tmp_load <= load:
                tmp_load += getPower(powerplants[i])
                result[powerplants[i].get('name')] = getPower(powerplants[i])
            elif getPower(powerplants[i]) + tmp_load > load:
                needed_power = load - tmp_load
                if (powerplants[i].get('type') == "gasfired" and needed_power < powerplants[i].get('pmin')):
                    reduce_power = (powerplants[i].get('pmin') + tmp_load) - load
                    result[powerplants[i].get('name')] = reduce_power + needed_power
                    for j in range (i - 1, -1, -1):
                        if result[powerplants[j].get('name')] - reduce_power >= powerplants[j].get('pmin'):
                            result[powerplants[j].get('name')] = round(result[powerplants[j].get('name')] - reduce_power, 1)
                            reduce_power = 0
                        elif result[powerplants[j].get('name')] - reduce_power < powerplants[j].get('pmin'):
                            tmp = result[powerplants[j].get('name')]
                            result[powerplants[j].get('name')] = 0
                            reduce_power -= tmp
                    return fill_dict(result, powerplants, i + 1)
                else:
                    tmp_load += needed_power
                    result[powerplants[i].get('name')] = round(needed_power, 1)
                    if tmp_load == load:
                        return fill_dict(result, powerplants, i + 1)
        return result

    def generate_output_file(result):
        with open("response.json", "w") as outfile:
            json.dump(result, outfile)

    generate_output_file(calculate_power(powerplants, expected_load))
    with open('response.json') as x:
        output = json.load(x)

    return output

if __name__ == '__main__':
    app.run(host="localhost", port=8888, debug=True)