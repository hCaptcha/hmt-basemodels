"""
The VIA Format intends to define a standard HMT format for data files that contain results
and the annotations associated with that image data.  Each file takes the general form of:

{
    "datapoints": [{
        "task_uri": "https://mydomain.com/image.jpg",
        "metadata": {
            "filename": "image.jpg"
        },
        "class_attributes": {
            "0": {
                # This nested class_attributes field will soon be deprecated
                "class_attributes": {
                    "dog": False,
                    "cat": False
                }
            }
        },
        "regions": [{
            "region_attributes": {
                "region_key": "region_value"
            },
            "shape_attributes": {
                "coords": [x1, y1, x2, y2, x3, y3, x4, y4],
                "name": "shape_type"
            }
        }],
    }]
}


"""
from marshmallow import Schema, fields


class RegionAttributesSchema(Schema):
    region_attributes = fields.Dict(keys=fields.Str())
    shape_attributes = fields.Dict(keys=fields.Str())


class ClassAttributeSchema(Schema):
    # inner class attributes field not required, here for legacy purposes
    class_attributes = fields.Dict(keys=fields.Str())
    regions = fields.Nested(RegionAttributesSchema, many=True)


class DatapointSchema(Schema):
    task_uri = fields.Url(required=True)
    metadata = fields.Dict(keys=fields.Str())
    class_attributes = fields.Dict(values=fields.Nested(ClassAttributeSchema))


class ViaDataManifest(Schema):
    """ Main entrypoint to define the VIA Data Format """
    datapoints = fields.Nested(DatapointSchema, many=True, required=True)
    version = fields.Integer(default=1)
