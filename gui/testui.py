import json
import sys
from json import dumps

from PyQt5 import QtWidgets

from qt_jsonschema_form import WidgetBuilder


app = QtWidgets.QApplication(sys.argv)

builder = WidgetBuilder()

schema = {
    "type": "object",
    "title": "Number fields and widgets",
    "properties": {
        "schema_path": {
            "title": "Schema path",
            "type": "string"
        },
        "text": {
            "type": "string",
            "maxLength": 20
        },
        "integerRangeSteps": {
            "title": "Integer range (by 10)",
            "type": "integer",
            "minimum": 55,
            "maximum": 100,
            "multipleOf": 10
        },
        "sky_colour": {
            "type": "string"
        },
        "boolean": {
            "type": "boolean",

        },
        "enum": {
            "type": "boolean",
            "enum": [True, False]

        },
        "names": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "maxItems": 2,
        }
    }
}

with open("config.schema.json", "r", encoding="utf8") as f:
    schema = json.load(f)

ui_schema = {
    "schema_path": {
        "ui:widget": "filepath"
    },
    "sky_colour": {
        "ui:widget": "colour"
    },
    "enum": {
        "ui:widget": "enum",
    }

}
form = builder.create_form(schema, None)
form.widget.state = {"maxFps": 120}
form.show()
form.widget.on_changed.connect(lambda d: print(dumps(d, indent=4)))

app.exec_()
