import arcpy
class ToolValidator(object):
  """Class for validating a tool's parameter values and controlling
  the behavior of the tool's dialog."""

  def __init__(self):
    """Setup arcpy and the list of tool parameters."""
    self.params = arcpy.GetParameterInfo()

  def initializeParameters(self):
    """Refine the properties of a tool's parameters.  This method is
    called when the tool is opened."""
    self.params[3].filter.list = []
    feature_class = self.params[2].valueAsText
    field_name = self.params[5].valueAsText
    if feature_class and field_name:
        unique_list = []
        with arcpy.da.SearchCursor(feature_class, field_name) as cursor:
            for row in cursor:
                if not row[0] in unique_list:
                    unique_list.append(row[0])
        self.params[3].filter.list = sorted(unique_list)
    return

  def updateParameters(self):
    """Modify the values and properties of parameters before internal
    validation is performed.  This method is called whenever a parameter
    has been changed."""
    feature_class = self.params[2].valueAsText
    field_name = self.params[5].valueAsText
    self.params[2].setErrorMessage('{} | {}'.format(feature_class, field_name))
    if feature_class and field_name:
        unique_list = []
        with arcpy.da.SearchCursor(feature_class, field_name) as cursor:
            for row in cursor:
                if not row[0] in unique_list:
                    unique_list.append(row[0])
        self.params[3].filter.list = sorted(unique_list)
    return

  def updateMessages(self):
    """Modify the messages created by internal validation for each tool
    parameter.  This method is called after internal validation."""
    return
