{%- macro getter(field, type) -%}
    {% if 'uint' in field['type'] -%}
    get{{field.c_name}}(self) -> int:
        return self._{{field.name}}
    {% elif 'int' in field['type'] -%}
    get{{field.c_name}}(self) -> int:
        return self._{{field.name}}
    {% elif 'void' == field['type'] -%}
    get{{field.c_name}}(self) -> None:
        return None
    {% elif 'bool' == field['type'] -%}
    get{{field.c_name}}(self) -> bool:
        return self._{{field.name}}
    {% elif 'text' == field['type'] -%}
    get{{field.c_name}}(self) -> str:
        return self._{{field.name}}
    {% elif 'data' == field['type'] -%}
    get{{field.c_name}}(self) -> bytes:
        return self._{{field.name}}
    {% elif 'list' == field['type'] -%}
    get{{field.c_name}}(self) -> list:
        return self._{{field.name}}
    {% elif 'enum' == field['type'] -%}
    get{{field.c_name}}(self) -> {{field.sub_type.module_name}}:
        return self._{{field.name}}
    {% else -%}
    get{{field.c_name}}(self) -> {{field.type.module_name}}:
        return self._{{field.name}}
    {% endif %}
{%- endmacro -%}
{% macro setter(field) -%}
    {% if 'int' in field['type'] -%}
    set{{field.c_name}}(self, _{{field.name}}:int) -> None:
        self._{{field.name}} = _{{field.name}}
    {% elif 'bool' == field['type'] -%}
    set{{field.c_name}}(self, _{{field.name}}:bool) -> None:
        self._{{field.name}} = _{{field.name}}
    {% elif 'text' == field['type'] -%}
    set{{field.c_name}}(self, _{{field.name}}:str) -> None:
        self._{{field.name}} = _{{field.name}}
    {% elif 'data' == field['type'] -%}
    set{{field.c_name}}(self, _{{field.name}}:bytes) -> None:
        self._{{field.name}} = _{{field.name}}
    {% elif 'list' == field['type'] -%}
    set{{field.c_name}}(self, _{{field.name}}:list) -> None:
        self._{{field.name}} = _{{field.name}}
    {% elif 'void' == field['type'] -%}
    set{{field.c_name}}(self) -> None:
        pass
    {% elif 'enum' == field['type'] -%}
    set{{field.c_name}}(self, _{{field.name}}:{{field.sub_type.module_name}}) -> None:
        self._{{field.name}} = _{{field.name}}.value
    {% else -%}
    set{{field.c_name}}(self, _{{field.name}}:{{field.type.module_name}}) -> None:
        self._{{field.name}} = _{{field.name}}
    {% endif %}
{%- endmacro -%}
{% macro initialize(field) -%}
    {% if 'int' in field['type'] -%}
    self._{{field.name}}:int
    {% elif 'bool' == field['type'] -%}
    self._{{field.name}}:bool
    {% elif 'text' == field['type'] -%}
    self._{{field.name}}:str
    {% elif 'data' == field['type'] -%}
    self._{{field.name}}:bytes
    {% elif 'list' == field['type'] -%}
    self._{{field.name}}:list
    {% elif 'void' == field['type'] -%}
    self._{{field.name}}:None
    {% elif 'enum' == field['type'] -%}
    self._{{field.name}}:{{field.sub_type.module_name}}
    {% else -%}
    self._{{field.name}}:{{field.type.module_name}}
    {% endif %}
{%- endmacro -%}
import capnp
from {{file.filename | replace('.', '_') | replace('/', '.')}} import (
    {%- for node in code.nodes %}
    {{node.module_name}} as _capnp_{{node.module_name}},{% endfor %}
)
from enum import Enum
### Enum Definitions
{%- for node in code.nodes if node["type"] == "enum" %}
class {{node.module_name}}(Enum):
    {%- for enumerant in node.enum.enumerants %}
    {{enumerant.name}} = {{enumerant.codeOrder}}
    {%- endfor %}
{%- endfor %}

### Structure Definitions
{%- for node in code.nodes[::-1] if node["type"] == "struct" %}
class {{node.module_name}}:
    def __init__(self):
        {% for field in node.struct.fields -%}
        {{ initialize(field) | indent(4) }}
        {%- endfor %}
    def _serialize(self) -> capnp._capnp_{{node.module_name}}:
        builder = capnp._capnp_{{node.module_name}}()
        {%- for field in node.struct.fields %}
        {%- if "struct" in field.type %}
        builder.{{field.name}} = self._{{field.name}}._serialize()
        {%- else %}
        builder.{{field.name}} = self._{{field.name}}
        {%- endif %}
        {%- endfor %}
        return builder
    
    def to_bytes(self) -> bytes:
        return self._serialize().to_bytes()
    {% for field in node.struct.fields %}
    def {{ getter(field, "Reader")}}
    {%- endfor %}
    {%- for field in node.struct.fields %}
    def {{ setter(field)}}
    {%- endfor %}
{%- endfor %}
