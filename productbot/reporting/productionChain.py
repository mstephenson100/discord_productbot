#!/usr/bin/python3

import sys
import os
import json
import time
import os.path
import configparser


config_file = "/home/bios/productbot/productbot.conf"

if os.path.exists(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    product_json = config.get('production', 'json')
else:
    raise Exception(config_file)


def getBuildingScore(input_id, product_data):

    extractor_score = int(0)
    refinery_score = int(1)
    factory_score = int(1)
    shipyard_score = int(1)
    bioreactor_score = int(1)
    spaceport_score = int(0)
    marketplace_score = int(0)
    habitat_score = int(0)

    if product_data['product_type'] == 'Raw Material':
        building_score = extractor_score
    elif product_data['product_type'] == 'Refined Material':
        building_score = refinery_score
    elif product_data['product_type'] == 'Refined Metal':
        building_score = refinery_score
    elif product_data['product_type'] == 'Component':
        building_score = factory_score
    elif product_data['product_type'] == 'Ship Component':
        building_score = shipyard_score
    elif product_data['product_type'] == 'Finished Good':
        building_score = factory_score
    elif product_data['product_type'] == 'Ship':
        building_score = shipyard_score
    elif product_data['product_type'] == 'Building':
        building_score = 0


    return building_score


def getBuildingScore2(building_name):

    if building_name == "Extractor":
        building_score = int(0)
    elif building_name == "Refinery":
        building_score = int(1)
    elif building_name == "Factory":
        building_score = int(1)
    elif building_name == "Shipyard":
        building_score = int(1)
    elif building_name == "Bioreactor":
        building_score = int(1)
    else:
        building_score = int(0)

    return building_score


def processScore(missed_materials, finished_materials, product_scores, sorted_list, product_type):

    for row in sorted_list:
        if row['product_type'] == product_type:
            product_id = row['product_id']
            product_name = row['product_name']
            product_type = row['product_type']
            building_score = row['building_score']
            product_score = building_score
            inputs = row['inputs']
            count = 0
            for input_row in inputs:
                input_id = input_row['input_id']
                input_name = input_row['input_name']
                input_type = input_row['input_type']
                if input_id in product_scores:
                    product_score+=product_scores[input_id]
                else:
                    count+=1
                    missed_materials.append(input_id)

            if count == 0:
                if product_id not in product_scores:
                    product_scores.update({product_id: product_score})
                    finished_materials.append(product_id)
                    if product_id == missed_materials:
                        missed_materials.remove(product_id)

            else:
                missed_materials.append(product_id)

    return missed_materials, finished_materials, product_scores


def getProducts(category_name):

    f = open('production_chains.json')
    data = json.load(f)
    for key, value in data.items():
        if key == "buildings":
            buildings = value
        elif key == "products":
            products = value
        else:
            processes = value

    building_list = []
    for row in buildings:
        building_id = row['id']
        building_name = row['name']
        score = 0
        if building_name == 'Refinery':
            score = int(1)
        elif building_name == 'Factory':
            score = int(2)
        elif building_name == 'Shipyard':
            score = int(2)
        elif building_name == 'Bioreactor':
            score = int(2)

        building_list.append({"building_id": building_id, "building_name": building_name, "building_score": score})

    input_weights = {}
    product_list = []

    for row in products:
        if row['type'] == category_name:
            product_id = row['id']
            product_name = row['name']
            product_category = row['category']
            massKilogramsPerUnit = row['massKilogramsPerUnit']
            volumeLitersPerUnit = row['volumeLitersPerUnit']
            quantized = row['quantized']
            product_list.append({"product_id": product_id, "product_name": product_name, "category": product_category, "weight": massKilogramsPerUnit, "volume": volumeLitersPerUnit, "quantized": quantized})

    return product_list


def getProductName(product_id):

    product_name = None
    f = open('production_chains.json')
    data = json.load(f)
    for key, value in data.items():
        if key == "products":
            products = value

    for row in products:
        if row['id'] == product_id:
            product_name = row['name']

    return product_name


def searchProducts(search_str):

    f = open('production_chains.json')
    data = json.load(f)
    for key, value in data.items():
        if key == "products":
            products = value

    search_str = search_str.lower()
    product_list = []
    for row in products:
        product_name = row['name']
        product_id = row['id']
        product_category = row['category']
        massKilogramsPerUnit = row['massKilogramsPerUnit']
        volumeLitersPerUnit = row['volumeLitersPerUnit']
        quantized = row['quantized']
        lower_product_name = product_name.lower()
        if search_str in lower_product_name:
            product_list.append({"product_id": product_id, "product_name": product_name, "category": product_category, "weight": massKilogramsPerUnit, "volume": volumeLitersPerUnit, "quantized": quantized})

    return product_list


def findProducts(search_input_id):

    f = open('production_chains.json')
    data = json.load(f)
    for key, value in data.items():
        if key == "buildings":
            buildings = value
        elif key == "products":
            products = value
        elif key == "processes":
            processes = value

    u_dict = {}
    u_list = []
    master_product_list, product_process_list, product_dict, product_list, unrefined_processes = getMasterLists()
    for row in master_product_list:
        if row['product_id'] == search_input_id:
            product_record = row
            used_in = row['used_in']
            for u_row in used_in:
                u_product_id = u_row['product_id']
                u_product_name = u_row['product_name']
                u_product_type = u_row['product_type']
                u_product_category = u_row['category']
                u_massKilogramsPerUnit = u_row['massKilogramsPerUnit']
                u_volumeLitersPerUnit = u_row['volumeLitersPerUnit']
                u_quantized = u_row['quantized']
                u_dict = {"product_id": u_product_id, "product_name": u_product_name, "product_type": u_product_type, "category": u_product_category, "weight": u_massKilogramsPerUnit, "volume": u_volumeLitersPerUnit, "quantized": u_quantized}
                u_list.append(u_dict)

    product_dupes = []
    return_dict = {}
    return_list = []
    for row in u_list:
        product_id = row['product_id']
        product_name = row['product_name']
        product_type = row['product_type']
        product_category = row['category']
        massKilogramsPerUnit = row['weight']
        volumeLitersPerUnit = row['volume']
        quantized = row['quantized']

        for record in master_product_list:
            if record['product_id'] == product_id:
                product_score = record['product_score']

        return_dict = {"product_id": product_id, "product_name": product_name, "product_type": product_type, "product_score": product_score, "category": product_category, "weight": massKilogramsPerUnit, "volume": volumeLitersPerUnit, "quantized": quantized}

        if product_id not in product_dupes:
            return_list.append(return_dict)
            product_dupes.append(product_id)

    sorted_return_list = sorted(return_list, key = lambda i: i['product_id'])
    return sorted_return_list


def getComponents(component_id):

    master_product_list, product_process_list, product_dict, product_list, unrefined_processes = getMasterLists()

    for key, value in product_dict.items():
        if key == component_id:
            processes = value['processes']

    for i_row in product_list:
        for i_key, i_value in i_row.items():
            if i_key == component_id:
                product_data = i_value

    revised_process_list = []
    for process_row in processes:
        p_inputs_list = []
        process_dict = {}
        process_id = process_row['process_id']
        process_name = process_row['process_name']
        mAdalianHoursPerSR = process_row['mAdalianHoursPerSR']
        bAdalianHoursPerAction = process_row['bAdalianHoursPerAction']
        process_dupes = []
        for pp_row in product_process_list:
            if pp_row['process_id'] == process_id:
                if process_id not in process_dupes:
                    process_dupes.append(process_id)
                    revised_process_list.append(pp_row)

    finalized_production_chains = []
    for row in revised_process_list:
        r_process_name = row['process_name']
        r_process_id = row['process_id']
        r_building_id = row['building_id']
        r_building_name = row['building_name']
        r_mAdalianHoursPerSR = row['mAdalianHoursPerSR']
        r_bAdalianHoursPerAction = row['bAdalianHoursPerAction']
        inputs = row['inputs']
        process_inputs = []
        process_score = 0
        for input_row in inputs:
            mp_dupes = []
            r_input_id = input_row['input_id']
            r_input_name = input_row['input_name']
            r_input_type = input_row['input_type']
            r_input_category = input_row['category']
            r_input_weight = input_row['weight']
            r_input_volume = input_row['volume']
            r_input_quantized = input_row['quantized']
            r_input_unitsPerSR = input_row['unitsPerSR']

            for mp_row in master_product_list:
                if mp_row['product_id'] == r_input_id:
                    mp_product_score = mp_row['product_score']
                    mp_dupes.append({"product_id": r_input_id, "product_score": mp_product_score})

            sorted_mp_dupes = sorted(mp_dupes, key = lambda i: i['product_score'])
            r_product_score = sorted_mp_dupes[0]['product_score']
            process_score+=r_product_score
            process_inputs.append({"product_id": r_input_id, "product_name": r_input_name, "product_type": r_input_type, "product_category": r_input_category, "product_weight": r_input_weight, "product_volume": r_input_volume, "product_score": sorted_mp_dupes[0]['product_score'], "unitsPerSR": r_input_unitsPerSR, "product_quantized": r_input_quantized })


        for u_row in unrefined_processes:
            if u_row['id'] == r_process_id:
                add_outputs = []
                additional_outputs = u_row['outputs']
                for add_output_row in additional_outputs:
                    add_output_id = add_output_row['productId']
                    add_unitsPerSR = add_output_row['unitsPerSR']
                    for add_product_row in product_list:
                        for add_key, add_value in add_product_row.items():
                            if add_key == add_output_id:
                                add_product_name = add_value['product_name']
                                add_product_type = add_value['product_type']
                                add_product_category = add_value['category']
                                add_product_weight = add_value['weight']
                                add_product_volume = add_value['volume']
                                add_outputs.append({"product_id": add_output_id, "product_name": add_product_name, "product_type": add_product_type, "weight": add_product_weight, "volume": add_product_volume, "unitsPerSR": add_unitsPerSR, "product_category": add_product_category})

        finalized_production_chains.append({"process_id": r_process_id, "process_name": r_process_name, "building_id": r_building_id, "building_name": r_building_name, "mAdalianHoursPerSR": r_mAdalianHoursPerSR, "bAdalianHoursPerAction": r_bAdalianHoursPerAction, "process_score": process_score, "inputs": process_inputs, "outputs": add_outputs})

    return product_data, finalized_production_chains


def updateProductDict(product_dict, processes_per_product):

    new_product_dict={}
    for key, value in product_dict.items():
        product_id = key
        product_name = value['product_name']
        product_type = value['product_type']
        meh_process_id = value['process_id']
        meh_process_name = value['process_name']
        building_id = value['building_id']
        building_name = value['building_name']
        inputs = value['inputs']
        meh_mAdalianHoursPerSR = value['mAdalianHoursPerSR']
        meh_bAdalianHoursPerAction = value['bAdalianHoursPerAction']
        components = value['components']
        processes = []
        for row in processes_per_product:
            if row['product_id'] == product_id:
                process_id = row['process_id']
                process_name = row['process_name']
                building_id = row['building_id']
                building_name = row['building_name']
                mAdalianHoursPerSR = row['mAdalianHoursPerSR']
                bAdalianHoursPerAction = row['bAdalianHoursPerAction']
                processes.append({"process_id": process_id, "process_name": process_name, "building_id": building_id, "building_name": building_name, "mAdalianHoursPerSR": mAdalianHoursPerSR, "bAdalianHoursPerAction": bAdalianHoursPerAction})

        new_product_dict[product_id] = {"product_id": product_id, "product_name": product_name, "product_type": product_type, "process_id": meh_process_id, "process_name": meh_process_name, "building_id": building_id, "building_name": building_name, "inputs": inputs, "mAdalianHoursPerSR": meh_mAdalianHoursPerSR, "bAdalianHoursPerAction": meh_bAdalianHoursPerAction, "components": components, "processes": processes}

    return new_product_dict


def updateDiscoList(disco_list, processes_per_product):

    return disco_list


def getMasterLists():

    f = open('production_chains.json')
    data = json.load(f)
    for key, value in data.items():
        if key == "buildings":
            buildings = value
        elif key == "products":
            products = value
        elif key == "processes":
            processes = value

    category_dict = {}
    kilo_dict = {}
    liter_dict = {}
    quantized_dict = {}
    building_list = []
    for row in buildings:
        building_id = row['id']
        building_name = row['name']
        building_list.append({"building_id": building_id, "building_name": building_name})

    product_list = []
    for row in products:
        product_id = row['id']
        product_name = row['name']
        product_type = row['type']
        product_category = row['category']
        massKilogramsPerUnit = row['massKilogramsPerUnit']
        volumeLitersPerUnit = row['volumeLitersPerUnit']
        quantized = row['quantized']
        product_list.append({product_id: {"product_name": product_name, "product_type": product_type, "category": product_category, "weight": massKilogramsPerUnit, "volume": volumeLitersPerUnit, "quantized": quantized}})

        category_dict.update({product_id: product_category})
        kilo_dict.update({product_id: massKilogramsPerUnit})
        liter_dict.update({product_id: volumeLitersPerUnit})
        quantized_dict.update({product_id: quantized})

    process_list = []
    product_process_list = []
    product_dict = {}
    output_dupes = {}
    disco_list = []
    process_id = None
    process_name = None
    for row in processes:
        process_id = row['id']
        process_name = row['name']
        building_id = row['buildingId']
        mAdalianHoursPerSR = row['mAdalianHoursPerSR']
        bAdalianHoursPerAction =row['bAdalianHoursPerAction']
        inputs = row['inputs']
        outputs = row['outputs']

        for building in building_list:
            if building['building_id'] == building_id:
                building_name = building['building_name']

        input_list=[]
        output_list=[]
        for product_input in inputs:
            input_id=product_input['productId']
            product_score = int(0)
            unitsPerSR = product_input['unitsPerSR']
            for product_row in product_list:
                for key, value in product_row.items():
                    if key == input_id:
                        building_score=int(getBuildingScore(input_id, value))
                        input_category = category_dict[input_id]
                        input_massKilogramsPerUnit = kilo_dict[input_id]
                        input_volumeLitersPerUnit = liter_dict[input_id]
                        input_quantized = quantized_dict[input_id]
                        input_list.append({"input_id": input_id, "input_name": value['product_name'], "input_type": value['product_type'], "building_score": building_score, "product_score": product_score, "category": input_category, "weight": input_massKilogramsPerUnit, "volume": input_volumeLitersPerUnit, "quantized": input_quantized, "unitsPerSR": unitsPerSR})

        for product_output in outputs:
            output_id = product_output['productId']
            unitsPerSR = product_output['unitsPerSR']
            for product_row in product_list:
                for key, value in product_row.items():
                    if key == output_id:
                        if output_id in output_dupes:
                            output_dupes[output_id]+=1
                        else:
                            output_dupes.update({output_id: 1})

                        output_category = category_dict[output_id]
                        output_massKilogramsPerUnit = kilo_dict[output_id]
                        output_volumeLitersPerUnit = liter_dict[output_id]
                        output_quantized = quantized_dict[output_id]
                        output_list.append({"output_id": output_id, "output_name": value['product_name'], "output_type": value['product_type'], "category": output_category, "weight": output_massKilogramsPerUnit, "volume": output_volumeLitersPerUnit, "quantized": output_quantized, "unitsPerSR": unitsPerSR})

        output_id = None
        for row in output_list:
            output_id = row['output_id']
            building_score=getBuildingScore2(building_name)

            process_list.append({row['output_id']: {"product_id": row['output_id'], "product_name": row['output_name'], "product_type": row['output_type'], "process_id": process_id, "process_name": process_name, "building_id": building_id, "building_name": building_name, "inputs": input_list, "outputs": output_list, "mAdalianHoursPerSR": mAdalianHoursPerSR, "bAdalianHoursPerAction": bAdalianHoursPerAction}})
            disco_list.append({"output_id": row['output_id'], "product_id": row['output_id'], "product_name": row['output_name'], "product_type": row['output_type'], "process_id": process_id, "process_name": process_name, "building_id": building_id, "building_name": building_name, "building_score": building_score, "inputs": input_list, "mAdalianHoursPerSR": mAdalianHoursPerSR, "bAdalianHoursPerAction": bAdalianHoursPerAction})
            product_dict[output_id] = {"product_id": row['output_id'], "product_name": row['output_name'], "product_type": row['output_type'], "process_id": process_id, "process_name": process_name, "building_id": building_id, "building_name": building_name, "inputs": input_list, "mAdalianHoursPerSR": mAdalianHoursPerSR, "bAdalianHoursPerAction": bAdalianHoursPerAction}
            product_dict[output_id]['components'] = {}
            product_process_list.append(product_dict[output_id])


    processes_per_product = []
    for product_row in products:
        product_id = product_row['id']
        product_name = product_row['name']
        for row in process_list:
            for process_key, process_value in row.items():
                if process_value['product_id'] == product_id:
                    ex_process_id = process_value['process_id']
                    ex_process_name = process_value['process_name']
                    ex_product_type = process_value['product_type']
                    ex_building_id = process_value['building_id']
                    ex_building_name = process_value['building_name']
                    ex_mAdalianHoursPerSR = process_value['mAdalianHoursPerSR']
                    ex_bAdalianHoursPerAction = process_value['bAdalianHoursPerAction']
                    processes_per_product.append({"product_id": product_id, "process_id": ex_process_id, "process_name": ex_process_name, "building_id": ex_building_id, "building_name": ex_building_name, "mAdalianHoursPerSR": ex_mAdalianHoursPerSR, "bAdalianHoursPerAction": ex_bAdalianHoursPerAction})

    product_dict = updateProductDict(product_dict, processes_per_product)
    finished_materials = []
    product_scores = {}
    process_scores = {}
    sorted_disco_list = sorted(disco_list, key = lambda i: i['output_id'])
    for row in sorted_disco_list:
        process_id = row['process_id']
        if row['product_type'] == 'Raw Material':
            product_id = row['product_id']
            building_score = row['building_score']
            if product_id not in product_scores:
                product_scores.update({product_id: (building_score + 1)})
                finished_materials.append(product_id)

    missed_materials = []

    # process refined materials
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Refined Material')
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Refined Material')
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Refined Material')
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Refined Material')
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Refined Material')

    # process refined metals
    missed_materials = []
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Refined Metal')
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Refined Metal')

    # process components
    missed_materials = []
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Component')
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Component')
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Component')
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Component')

    # process ship components
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Ship Component')
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Ship Component')

    # process ships
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Ship')
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Ship')

    # process finished goods
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Finished Good')
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Finished Good')

    # process buildings
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Building')
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Building')

    # one more pass
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Refined Material')
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Refined Metal')
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Component')
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Ship Component')
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Ship')
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Finished Good')
    missed_materials, finished_materials, product_score = processScore(missed_materials, finished_materials, product_scores, sorted_disco_list, 'Building')


    master_process_dict = {}
    for row in process_list:
        process_id = None
        process_name = None
        for key, value in row.items():
            input_dict = {}
            output_dict = {}
            output_list = []
            input_list = []
            output_dupes = []
            total_input_score = 0
            total_output_score = 0
            product_id = value['product_id']
            product_name = value['product_name']
            product_type = value['product_type']
            process_id = value['process_id']
            process_name = value['process_name']
            building_name = value['building_name']
            building_id = value['building_id']
            mAdalianHoursPerSR = value['mAdalianHoursPerSR']
            bAdalianHoursPerAction = value['bAdalianHoursPerAction']
            inputs = value['inputs']
            outputs = value['outputs']
            for input_data in inputs:
                input_id = input_data['input_id']
                input_name = input_data['input_name']
                input_type = input_data['input_type']
                input_category = input_data['category']
                input_massKilogramsPerUnit = input_data['weight']
                input_volumeLitersPerUnit = input_data['volume']
                input_quantized = input_data['quantized']
                input_unitsPerSR = input_data['unitsPerSR']
                input_score = product_scores[input_id]
                total_input_score+=input_score
                input_dict = {"input_id": input_id, "input_name": input_name, "input_type": input_type, "input_score": int(input_score), "input_category": input_category, "input_massKilogramsPerUnit": input_massKilogramsPerUnit, "input_volumeLitersPerUnit": input_volumeLitersPerUnit, "input_quantized": input_quantized, "input_unitsPerSR": input_unitsPerSR}
                input_list.append(input_dict)
                input_dict = {}
            for output_data in outputs:
                output_id = output_data['output_id']
                output_name = output_data['output_name']
                output_type = output_data['output_type']
                output_category = output_data['category']
                output_massKilogramsPerUnit = output_data['weight']
                output_volumeLitersPerUnit = output_data['volume']
                output_quantized = output_data['quantized']
                output_unitsPerSR = output_data['unitsPerSR']
                output_score = product_scores[output_id]
                if output_id not in output_dupes:
                    total_output_score+=output_score
                    output_dupes.append(output_id)
                output_dict = {"output_id": output_id, "output_name": output_name, "input_type": output_type, "output_score": int(output_score), "output_category": output_category, "output_massKilogramsPerUnit": output_massKilogramsPerUnit, "output_volumeLitersPerUnit": output_volumeLitersPerUnit, "output_quantized": output_quantized, "output_unitsPerSR": output_unitsPerSR}
                output_list.append(output_dict)
                output_dict = {}

        master_process_dict[process_id] = {"process_id": process_id, "process_name": process_name, "building_name": building_name, "building_id": int(building_id), "input_score": int(total_input_score), "inputs": input_list, "outputs": output_list, "mAdalianHoursPerSR": mAdalianHoursPerSR, "bAdalianHoursPerAction": bAdalianHoursPerAction}

    master_product_dict = {}
    master_product_list = []

    for row in sorted_disco_list:
        input_dict = {}
        input_list = []
        input_score = 0
        total_score = 0
        product_id = row['output_id']
        product_name = row['product_name']
        product_type = row['product_type']
        process_id = row['process_id']
        process_name = row['process_name']
        building_id = row['building_id']
        building_name = row['building_name']
        building_score = row['building_score']
        mAdalianHoursPerSR = row['mAdalianHoursPerSR']
        bAdalianHoursPerAction = row['bAdalianHoursPerAction']
        inputs = row['inputs']
        for input_data in inputs:
            input_id = input_data['input_id']
            input_name = input_data['input_name']
            input_type = input_data['input_type']
            input_category = input_data['category']
            input_massKilogramsPerUnit = input_data['weight']
            input_volumeLitersPerUnit = input_data['volume']
            input_quantized = input_data['quantized']
            input_unitsPerSR = input_data['unitsPerSR']
            input_score = product_scores[input_id]
            total_score+=input_score
            input_dict = {"input_id": input_id, "input_name": input_name, "input_type": input_type, "input_score": int(input_score), "input_category": input_category, "input_massKilogramsPerUnit": input_massKilogramsPerUnit, "input_volumeLitersPerUnit": input_volumeLitersPerUnit, "input_quantized": input_quantized, "input_unitsPerSR": input_unitsPerSR}
            input_list.append(input_dict)

        total_score+=building_score


        full_products = []
        full_products_list = []
        full_products_dict = {}
        for process_row in processes:
            process_id = process_row['id']
            process_name = process_row['name']
            building_id = process_row['buildingId']
            inputs = process_row['inputs']
            outputs = process_row['outputs']
            mAdalianHoursPerSR = process_row['mAdalianHoursPerSR']
            bAdalianHoursPerAction = process_row['bAdalianHoursPerAction']

            output_list=[]
            for product_input in inputs:
                input_id=product_input['productId']
                if input_id == product_id:
                    for product_output in outputs:
                        output_id=product_output['productId']
                        for product_row in product_list:
                            for key, value in product_row.items():
                                if key == output_id:
                                    product_origin_dict = value

                        p_product_type = product_origin_dict['product_type']
                        p_product_name = product_origin_dict['product_name']
                        p_category = product_origin_dict['category']
                        p_massKilogramsPerUnit = product_origin_dict['weight']
                        p_volumeLitersPerUnit = product_origin_dict['volume']
                        p_quantized = product_origin_dict['quantized']

                        full_products_list.append({"product_id": output_id, "product_name": p_product_name, "product_type": p_product_type, "category": p_category, "massKilogramsPerUnit": p_massKilogramsPerUnit, "volumeLitersPerUnit": p_volumeLitersPerUnit, "quantized": p_quantized})

        full_products_len=len(full_products_list)
        master_product_list.append({"product_id": product_id, "product_name": product_name, "product_type": product_type, "process_id": int(process_id), "process_name": process_name, "building_id": int(building_id), "building_name": building_name, "product_score": int(total_score), "usage_count": int(full_products_len), "inputs": input_list, "used_in": full_products_list})

    return master_product_list, product_process_list, product_dict, product_list, processes

