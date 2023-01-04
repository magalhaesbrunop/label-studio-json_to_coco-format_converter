import json

coco_format = {}
images = []
categories = []
annotations = []
bbox = []
area = []

def format_to_coco(json_file_path):
    
    with open(json_file_path, 'r') as file:
        contents = json.loads(file.read())

    for index_annotation in range(len(contents)):
        # Variavél que possibilita checar se houve skip na anotação
        result = contents[index_annotation]['annotations'][0]['was_cancelled']

        # Checando se skip na anotação
        if result == False:

            # O valor da largura da imagem
            width_from_json = contents[index_annotation]["annotations"][0]["result"][0]["original_width"]

            # Extraindo a altura da imagem do arquivo JSON
            height_from_json = contents[index_annotation]["annotations"][0]["result"][0]["original_height"]

            # id da imagem
            image_id = contents[index_annotation]["id"]

            # nome do arquivo imagem
            image_json_name = contents[index_annotation]["data"]['image'].split('/')[-1]

            # Categoria
            category = contents[index_annotation]['annotations'][0]['result'][0]['value']['polygonlabels'][0]

            # Pontos da segmentação do arquivo JSON
            polygon_segmentation_points = contents[index_annotation]["annotations"][0]["result"][0]["value"]["points"]

            # Conversão das coordenadas x e y do JSON de porcentagem para pixel
            pixels_coordenates = convert_coordinate_percent_to_pixels(polygon_segmentation_points, width_from_json, height_from_json)

            # Organizando as coordenadas x e y para uma lista  
            organized_pixels_coordenates = organizing_coordenates(pixels_coordenates)

            # Coordenadas do bbox
            total_area_bbox = total_area_bounding_box(pixels_coordenates)

            # Calculo da área de poligono irregular
            #total_area_polygon = irregular_polygon_calculation(pixels_coordenates)

            # Formatando para COCO e salvando em JSON
            images.append(
                {
                    "width": width_from_json, "height": height_from_json, "id": index_annotation, "file_name": image_json_name
                }
            )

            categories.append({"id": index_annotation, "name": category})
            dict_categories = set_categories(categories)
            
            annotations.append(
                {
                    "id": index_annotation,
                    "image_id": image_id,
                    "category_id": index_annotation,
                    "segmentation": organized_pixels_coordenates,
                    "bbox": total_area_bbox[0][0:-1],
                    "area": total_area_bbox[0][-1]
                }
            )
            data = {"imagens": images, "categories": dict_categories, "annotations": annotations}

        saving_json(data)

def saving_json(list_data):

    with open(f"coco_format_files/coco_file.json", "w") as out_file:
                json.dump(list_data, out_file, ensure_ascii=False, indent=4)

def set_categories(categories):

    set_categories = []
    list_data = []

    for index in range(len(categories)):
        set_categories.append(categories[index]['name'])

    index_set = sorted(list(set(set_categories)))

    for index in range(len(index_set)):
        data = {'id': index, 'name': index_set[index]}  
        list_data.append(data)

    return list_data

# Conversão das coordenadas x e y do JSON de porcentagem para pixel
def convert_coordinate_percent_to_pixels(polygon_segmentation_points, width_from_json, height_from_json):
    
    pixels_coordenates = []
    
    for index in range(0, len(polygon_segmentation_points)):
        
        x_pixel_coordinate = polygon_segmentation_points[index][0] * width_from_json / 100.0
        y_pixel_coordinate = polygon_segmentation_points[index][1] * height_from_json / 100.0

        pixels_coordenates.append([x_pixel_coordinate, y_pixel_coordinate])

    return pixels_coordenates


# Colocando as coordenadas x e y em uma só lista
def organizing_coordenates(pixels_coordenates):
    x_y_coordinates = []

    for index in range(0, len(pixels_coordenates)):
        x_y_coordinates.append(pixels_coordenates[index][0])
        x_y_coordinates.append(pixels_coordenates[index][1])
        
    return x_y_coordinates


# Cálculando a área do bounding box
def total_area_bounding_box(pixels_coordenates):
    x_coordinates = []
    y_coordinates = []
    result = []

    for index in range(len(pixels_coordenates)):

        x_coordinates.append(pixels_coordenates[index][0])
        y_coordinates.append(pixels_coordenates[index][1])

    x_min, y_min, x_max, y_max = (min(x_coordinates), min(y_coordinates), max(x_coordinates), max(y_coordinates))
    area_segmentation = (x_max - x_min) * (y_max - y_min)
    result.append([x_min, y_min, x_max, y_max, area_segmentation])
    
    return result

# Calculo de área de polígonos irregulares - Método de Gauss
# def irregular_polygon_calculation(pixels_coordenates):
#     right_multiplication = []
#     left_multiplication = []

#     for index in range(len(pixels_coordenates)):

#         if pixels_coordenates[index + 1][1] == pixels_coordenates[-1][1] or pixels_coordenates[index + 1][0] == pixels_coordenates[-1][0]:
#             right_multiplication.append(pixels_coordenates[index][0] * pixels_coordenates[-1][1])
#             left_multiplication.append(pixels_coordenates[-1][0] * pixels_coordenates[index][1])
#             break
#         else:
#             right_multiplication.append(pixels_coordenates[index][0] * pixels_coordenates[index + 1][1])
#             left_multiplication.append(pixels_coordenates[index + 1][0] * pixels_coordenates[index][1])

#     right_multiplication.append(pixels_coordenates[-1][0] * pixels_coordenates[0][1])
#     left_multiplication.append(pixels_coordenates[0][0] * pixels_coordenates[-1][1])

#     total_polygon_area = (sum(right_multiplication) - sum(left_multiplication)) / 2

#     return total_polygon_area

#format_to_coco('project-22-at-2022-12-05-16-23-de7b066b.json')   
format_to_coco('coco_food_train_2017/project-19-at-2022-12-27-15-35-cc6833ff.json')
#format_to_coco('imagem_pao_com_geleia/project-20-at-2022-11-24-16-10-16d9a976.json')
    