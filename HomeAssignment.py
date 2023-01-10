import dtlpy as dl
import datetime
from random import random
from PIL import Image
import traceback


def validate (general_list, item_to_check):
    current_items = list(general_list[i].name for i in range(len(general_list)))
    return item_to_check in current_items

try: 
    if dl.token_expired():
        dl.login()

    # Main variables: 
    project_name = "My_first_project"
    dataset_name = "first_data_set"
    images_directory = r'./images'
    if not validate(dl.projects.list(), project_name):
        dl.projects.create(project_name=project_name) # New Project
    project = dl.projects.get(project_name=project_name) # Select the project 

    if not validate(project.datasets.list(), dataset_name):
        # 1 To create new dataset: 
        project.datasets.create(dataset_name=dataset_name)
    dataset = project.datasets.get(dataset_name=dataset_name) # select a dataset

    # 2. Add three labels: 
    labels = ['class','class2','key'] 
    dataset.add_labels(label_list=labels)

    # 3. upload all items of a directory:
    dataset.items.upload(local_path=images_directory)

    # 4. Working with item metadata
    # Adding a New User Metadata Field to an Item
    pages = dataset.items.list()
    items_available = {item.name :  item.id for item in pages.all()} #dict of all list with name and id
    items_sorted = sorted(items_available.items()) #[(name_1,id_1),(name_2,id_2),...]

    item_1 = dataset.items.get(item_id=items_sorted[0][1])
    now = datetime.datetime.utcnow().isoformat()
    item_1.metadata['user'] = dict() # modify metadata for the item
    item_1.metadata['user']['dateTime'] = now # add it to the item's metadat
    item_1 = item_1.update() # update the item

    # 5 and 6. Annotation Item 1: 
    for i in range(len(items_sorted)):
        label = labels[0] if i < 2 else labels[1]
        item = dataset.items.get(item_id=items_sorted[i][1])
        builder =item.annotations.builder()
        builder.add(annotation_definition=dl.Classification(label=label))
        item.annotations.upload(builder)
            
    # 7. five Random Point Markers with label 'key' to  one item 
    item_1_name = items_sorted[0][0] #first item

    filepath = images_directory+'/'+item_1_name
    img = Image.open(filepath)
    width, height = int(img.width) , int(img.height)

    item_1 = dataset.items.get(item_id=items_sorted[0][1])
    for i in range(5):
        builder = item_1.annotations.builder()
        builder.add(annotation_definition=dl.Point(x=random()*height, y=random()*width, label=labels[2]))
        item_1.annotations.upload(builder)

    # 8. create a query that select items labeled as 'class', print item name and id. 
    my_filter = dl.Filters()
    my_filter.add_join(field='label', values='class')
    pages = dataset.items.list(filters=my_filter)
    items_filtered = {item.name :  item.id for item in pages.all()}
    for item_name, item_id in items_filtered.items():
        print('name: {0} | id: {1}'.format(item_name,item_id))
    
    # 9.Create a query that retrieves all point  annotations from the dataset and prints the item name and item id of each item, and for each item, print for each annotation the annotation id, annotation label, and position of the point (x,y)
    my_filter_point = dl.Filters()
    my_filter_point.add_join(field='type', values='point')
    pages = dataset.items.list(filters=my_filter_point)
    items_point_list = list((item.name,item.id) for item in pages.all())
    for i in range(len(items_point_list)):
        item_point = dataset.items.get(item_id=items_point_list[i][1])
        annotations_list = item_point.annotations.list()
        print('name: {} , id: {}')
        print('annotations: ')
        for a in range(len(annotations_list)):
            if annotations_list[a].type == 'point':
                output = f'annotation id: {annotations_list[a].id}, label: {annotations_list[a].label}, type: position(x,y): ({annotations_list[a].x}, {annotations_list[a].y})'
                print(output)
                
except Exception as e:
    print("an error occurred")
    print(traceback.format_exc())
