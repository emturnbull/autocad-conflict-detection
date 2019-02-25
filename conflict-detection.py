# -*- coding: utf-8 -*-

"""
	Detects conflicts between features based on a threshold table.
	
	Inputs:
	1. TBD
	
	Outputs:
	1. A table of conflicts.
	
	Authors:   	Alan Armstrong
				Zoltan Kalnay
				Whitney Pala
				Hassan Saleem
				Chris Sinclair
				Erin Turnbull
				
	Created:	Feb 22, 2019
	Modified:	Feb 25, 2019
			   
"""
import arcpy
import sys

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
        conversion_factor = 1
        if from_unit == 'cm':
            conversion_factor *= 0.01
        if to_unit == 'cm':
            conversion_factor *= 100
        return units * conversion_factor

arcpy.AddMessage("Calling file {0}...".format(sys.argv[0]))


testing = True

if testing:
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
    
RELEVANT_SHAPE_TYPES = ['point', 'polyline', 'polygon', 'multipatch']
    
threshold_distances = {}
defined_threshold_layers = {}
for shape_type in RELEVANT_SHAPE_TYPES:
    threshold_distances[shape_type] = {}
    defined_threshold_layers[shape_type] = []

with arcpy.da.SearchCursor(threshold_table, [threshold_layer_field, threshold_distance_field, threshold_type_field]) as table_lookup:
    for row in table_lookup:
        feature_type = row[2].lower()
        if feature_type == 'line':
            feature_type = 'polyline'
        threshold_distances[feature_type][row[0]] = row[1]
        defined_threshold_layers[feature_type].append(row[0])
        
print(threshold_distances)
print(dataset)
arcpy.env.workspace = geodatabase
feature_classes = arcpy.ListFeatureClasses(feature_dataset = dataset)

print(feature_classes)

conflict_class_delimited = arcpy.AddFieldDelimiters(conflict_feature_class, layer_field)
sql = '{} = \'{}\''.format(conflict_class_delimited, conflict_feature_layer)

conflicting_features = []
with arcpy.da.SearchCursor(conflict_feature_class, ['OBJECTID', 'SHAPE@', entity_handle], sql) as conflict_feature_lookup:
    for row in conflict_feature_lookup:
        conflicts = []
        for shapeType in RELEVANT_SHAPE_TYPES:
            feature_classes = arcpy.ListFeatureClasses(feature_type = shapeType.capitalize(), feature_dataset = dataset)
            for feature_class in feature_classes:
                if feature_class == 'Annotation':
                    continue
                sql_where_clause = ''
                if use_all_features:
                    sql_where_clause = conflict_class_delimited + " <> '" + conflict_feature_layer
                else:
                    sql_where_clause = conflict_class_delimited + " IN ('" + "', '".join(defined_threshold_layers[shapeType]) + "')"
                with arcpy.da.SearchCursor(feature_class, ['OBJECTID', 'SHAPE@', entity_handle, layer_field, diameter], sql_where_clause) as potential_conflicts:
                    for feature in potential_conflicts:
                        detection_threshold = threshold_distances[shapeType][feature[3]]
                        radius = convert(feature[4], diameter_units, threshold_units)
                        detection_threshold += radius
                        distance = row[1].distanceTo(feature[1])
                        if distance <= detection_threshold:
                            conflicts.append((feature_class, feature[0], feature[2], feature[3], max(0, distance - radius)))
                            if not find_all_conflicts:
                                break
                if not find_all_conflicts and len(conflicts) > 0: # ugly, fix
                    break
            if not find_all_conflicts and len(conflicts) > 0:
                    break
        if len(conflicts) > 0:
            conflicting_features.append((row[0], row[2], conflicts))
            
print(conflicting_features)

""" Conflict Table
- Running Line Handle (whatever handle is)
- Conflict Layer Name (whatever layer is)
- Conflict Handle (whatever handle is)
- Conflict Feature Class (string)
- Distance (float)
fields = arcpy.ListFields(parameters[0].valueAsText)
		for field in fields:
			if field.name == parameters[3].valueAsText:
costFieldType = [field.type, field.length]
"""
        



        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
