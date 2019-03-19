# -*- coding: utf-8 -*-

"""
    Detects conflicts between features based on a threshold table.
    
    Inputs:
    1. TBD
    
    Outputs:
    1. A table of conflicts.
    
    Authors:       Alan Armstrong
                Zoltan Kalnay
                Whitney Pala
                Hassan Saleem
                Chris Sinclair
                Erin Turnbull
                
    Created:    Feb 22, 2019
    Modified:    Feb 26, 2019
               
"""
import arcpy
import sys
import os
import csv

# Dataset 
# Spatial Reference

# -> five feature classes in a feature data set
# Fields (dataset):
#  - Layer name
#  - Handle, LyrHandle
#  - Diam(CM)

# Table of threshold values
# Layer to check against (RunningLine)

def message(msg):
    arcpy.AddMessage(msg)
    print(msg)
    

def convert(units, from_unit, to_unit = 'm'):
    X_TO_METERS = {
        # Smart units
        'mm': 0.001,
        'dm': 0.1,
        'cm': 0.01,
        'm': 1,
        'dam': 10,
        'hm': 100,
        'km': 1000,
        'Mm': 1000000,
        # Silly units
        'in': 0.0254,
        'ft': 0.3048,
        'yd': 0.9144,
        'fur': 201.168,
        'mi': 1609.344,
        # Sea units
        'lea': 4828.032,
        'ftm': 1.852,
        'nmi': 1852,
        # Surveying units
        'link': 0.201168,
        'rod': 5.0292
    }
    conversion_factor = 1
    if from_unit in X_TO_METERS:
        conversion_factor *= X_TO_METERS[from_unit]
    if to_unit in X_TO_METERS:
        conversion_factor /= X_TO_METERS[to_unit]
    return units * conversion_factor

def createOutput(conflicting_features):
    output_table = "Conflicts"
    output_location = geodatabase + "\\" + output_table
    arcpy.CreateTable_management(geodatabase,output_table)
    fields = ['RLine_OID','RLine_Handle','FClass','OID','Con_Handle',
              'Con_Type','Distance_m']
    output_shapes = {}
    for shape in RELEVANT_SHAPE_TYPES:
        output_shape = 'conflicting' + shape
        template = arcpy.ListFeatureClasses(feature_type = shape.capitalize(),
                                            feature_dataset = dataset)[0]
        output_shapes[shape] = arcpy.CreateFeatureclass_management(geodatabase,
                     output_shape, shape.capitalize(), template)
    for field in fields:
        arcpy.AddField_management(output_table, field, "TEXT")
    outputFile = open(geodatabase +'\\output.csv',"w")
    writer = csv.writer(outputFile, delimiter=',', quotechar='"',
                        quoting=csv.QUOTE_ALL)
    writer.writerow(fields)
    with arcpy.da.InsertCursor(output_location, fields) as cursor:
        for row in conflicting_features:
            for item in row[2]:
                rowOutput = [row[0], row[1], item[0], item[1], item[2],
                             item[3], item[4]]
                cursor.insertRow(rowOutput)
                writer.writerow(rowOutput)
    outputFile.close()
    del cursor
    found = set()
    for row in conflicting_features:
        for item in row[2]:
            found.add(item[1])
    oid_list = ""
    for feature in found:
        oid_list += ", " + format(feature)
    oid_list = oid_list[2:]
    whereclause = 'OBJECTID in (' + oid_list + ')'
    for shape_type in RELEVANT_SHAPE_TYPES:
            bs = shape_type.capitalize()
            feature_classes = arcpy.ListFeatureClasses(feature_type=bs,
                                                       feature_dataset=dataset)
            for feature_class in feature_classes:
                template = arcpy.ListFeatureClasses(feature_type=bs,
                                                    feature_dataset=dataset)[0]
                temp_layer = arcpy.MakeFeatureLayer_management(template,
                                                               "in_memory")
                arcpy.SelectLayerByAttribute_management(temp_layer,
                                                        "NEW_SELECTION",
                                                        whereclause)
                arcpy.CopyFeatures_management(temp_layer,
                                              output_shapes[shape_type])

message("Calling file {0}...".format(sys.argv[0]))

testing = False

if testing:
    message("Testing mode with hard-coded parameters")
    geodatabase = 'C:\\Students\\101056654\\group_project\\TheProject\\TheProject.gdb'
    dataset = 'Proximity_Check2004_CADToGeo'
    threshold_table = 'C:\\Students\\101056654\\group_project\\TheProject\\TheProject.gdb\\Thresholds'
    layer_field = 'Layer'
    entity_handle = 'Handle'
    layer_handle = 'LyrHandle'
    diameter = 'Diam_CM_'
    diameter_units = 'cm'
    threshold_layer_field = 'Layer'
    threshold_distance_field = 'Threshold__m_'
    threshold_type_field = 'Output_Type'
    threshold_units = 'm'
    conflict_feature_class = 'Proximity_Check2004_CADToGeo\\Polyline'
    conflict_feature_layer = 'RunningLine'
    use_all_features = False
    find_all_conflicts = False
    results_table_name = 'Conflicts'
    results_feature_class = 'Conflicting_Features'
else:
    geodatabase = sys.argv[1]
    results_geodatabase = sys.argv[2]
    dataset = os.path.basename(sys.argv[5])
    threshold_table = sys.argv[10]
    layer_field = sys.argv[6]
    entity_handle = sys.argv[7]
    diameter =sys.argv[8]
    diameter_units = sys.argv[9]
    threshold_layer_field = sys.argv[11]
    threshold_distance_field = sys.argv[12]
    threshold_type_field = sys.argv[14]
    threshold_units = sys.argv[13]
    conflict_feature_class = sys.argv[3]
    conflict_feature_layer = sys.argv[4]
    results_featureset = os.path.basename(sys.argv[16])
    results_csv_file = sys.argv[17]
    use_all_features = sys.argv[19]
    find_all_conflicts = sys.argv[18]
    results_table_name =sys.argv[15]

RELEVANT_SHAPE_TYPES = ['point', 'polyline', 'polygon', 'multipatch']
    
threshold_distances = {}
defined_threshold_layers = {}
conflicting_features = []
for shape_type in RELEVANT_SHAPE_TYPES:
    threshold_distances[shape_type] = {}
    defined_threshold_layers[shape_type] = []

message("Loading threshold information...")

with arcpy.da.SearchCursor(threshold_table, [threshold_layer_field, threshold_distance_field, threshold_type_field]) as table_lookup:
    for row in table_lookup:
        feature_type = row[2].lower()
        if feature_type == 'line':
            feature_type = 'polyline'
        threshold_distances[feature_type][row[0]] = row[1]
        defined_threshold_layers[feature_type].append(row[0])
        message("Threshold for features of type {} is {} {}".format(row[0], row[1], threshold_units))

message("Identifying relevant feature classes")
arcpy.env.workspace = geodatabase
feature_classes = arcpy.ListFeatureClasses(feature_dataset = dataset)
message("{} classes identified".format(len(feature_classes)))
if use_all_features is True:
    message("Using all feature layers, even if they do not have threshold values set")
else:
    message("Only feature layers with threshold values defined will be used")

if find_all_conflicts:
    message("All conflicts will be reported")
else:
    message("Only the first conflict will be reported")
    
message("Checking features of type {} in feature class {} for conflicts".format(conflict_feature_layer, conflict_feature_class))

conflict_class_delimited = arcpy.AddFieldDelimiters(conflict_feature_class, layer_field)
sql = '{} = \'{}\''.format(conflict_class_delimited, conflict_feature_layer)
with arcpy.da.SearchCursor(conflict_feature_class, ['OBJECTID', 'SHAPE@', entity_handle], sql) as conflict_feature_lookup:
    for row in conflict_feature_lookup:
        message("Checking feature {} for conflicts".format(row[2]))
        conflicts = []
        for shapeType in RELEVANT_SHAPE_TYPES:
            feature_classes = arcpy.ListFeatureClasses(feature_type = shapeType.capitalize(), feature_dataset = dataset)
            for feature_class in feature_classes:
                if feature_class == 'Annotation':
                    continue
                message("- Checking in feature class {}".format(feature_class))
                sql_where_clause = ''
                if use_all_features is True:
                    sql_where_clause = conflict_class_delimited + " <> '" + conflict_feature_layer + "'"
                else:
                    if not defined_threshold_layers[shapeType]:
                        continue
                    sql_where_clause = conflict_class_delimited + " IN ('" + "', '".join(defined_threshold_layers[shapeType]) + "')"
                with arcpy.da.SearchCursor(feature_class, ['OBJECTID', 'SHAPE@', entity_handle, layer_field, diameter], sql_where_clause) as potential_conflicts:
                    for feature in potential_conflicts:
                        detection_threshold = threshold_distances[shapeType][feature[3]]
                        radius = convert(feature[4], diameter_units, threshold_units)
                        distance = row[1].distanceTo(feature[1]) - radius
                        if distance <= detection_threshold:
                            conflicts.append((feature_class, feature[0], feature[2], feature[3], max(0, distance - radius)))
                            message("-- Conflict found with feature {} of feature type {}. It is {} {} away, and must be at least {} {} away".format(feature[2], feature[3], distance, threshold_units, detection_threshold, threshold_units))
                            if not find_all_conflicts:
                                break
                if not find_all_conflicts and len(conflicts) > 0: # ugly, fix
                    break
            if not find_all_conflicts and len(conflicts) > 0:
                    break
        if len(conflicts) > 0:
            message("A total of {} conflicts were found".format(len(conflicts)))
            conflicting_features.append((row[0], row[2], conflicts))
        else:
            message("No conflicts found")
            
arcpy.env.overwriteOutput = True
fields = [
    'Interest_OID', 
    'Interest_Handle',
    'Conflict_Class',
    'Conflict_OID',
    'Conflict_Handle',
    'Conflict_Layer',
    'Conflict_Distance'
]
if results_csv_file and not(results_csv_file == '#'):
    message("Writing output to CSV file {}".format(results_csv_file))
    with open(results_csv_file, 'w') as outputFile:
        writer = csv.writer(outputFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\n')
        writer.writerow(fields)
        for row in conflicting_features:
            for item in row[2]:
                rowOutput = [row[0],row[1],item[0],item[1],item[2],item[3],item[4]]
                writer.writerow(rowOutput)
                
if results_table_name and not(results_table_name == '#'):
    message("Writing output to ArcGIS table {} in geodatabase {}".format(results_table_name, results_geodatabase))
    arcpy.CreateTable_management(results_geodatabase, results_table_name)
    fullTablePath = results_geodatabase + "\\" + results_table_name
    for field in fields:
        arcpy.AddField_management(fullTablePath, field, "TEXT")
    with arcpy.da.InsertCursor(fullTablePath, fields) as cursor:
        for row in conflicting_features:
            for item in row[2]:
                rowOutput = [row[0],row[1],item[0],item[1],item[2],item[3],item[4]]
                cursor.insertRow(rowOutput)
                
if results_featureset and not(results_featureset == '#'):
    message("Writing output to ArcGIS feature set {} in geodatabase {}".format(results_featureset, results_geodatabase))
    found = set()
    for row in conflicting_features:
        for item in row[2]:
            found.add(str(item[1]))
    whereclause = 'OBJECTID in (' + ", ".join(found) + ')'
    for shape_type in RELEVANT_SHAPE_TYPES:
        bs = shape_type.capitalize()
        feature_classes = arcpy.ListFeatureClasses(feature_type=bs,
                                                       feature_dataset=dataset)
        for feature_class in feature_classes:
            output_fc_name = results_featureset + "\\" + feature_class + "_Conflicts"
            message("Creating FC {} in database {} based on {}".format(output_fc_name, results_geodatabase, feature_class))
            output_fc = arcpy.CreateFeatureclass_management(results_geodatabase,
                     output_fc_name, shape_type.capitalize(), feature_class)
            temp_layer = arcpy.MakeFeatureLayer_management(feature_class,
                                                               "in_memory")
            arcpy.SelectLayerByAttribute_management(temp_layer,
                                                        "NEW_SELECTION",
                                                        whereclause)
            arcpy.CopyFeatures_management(temp_layer,
                                              output_fc)