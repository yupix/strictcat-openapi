import json
import os
from urllib import request
from typing import Union

from dotenv import load_dotenv

from type import IOpenAPI

load_dotenv()

env = os.environ

final_content = ''
schemas = {}

def parse_ref(ref: str):
    return ref.split('/')[-1]



def add_or_update(data: dict[str, dict], key: str, add_content: Union[dict, str]):
    if data.get(key):
        data[key].update(add_content)
    else:
        data[key] = add_content
    return data


use_export = 'export ' if env.get('USE_EXPORT').lower() == 'true' else ''

with request.urlopen(env.get('OPENAPI_URL')) as res:
    openapi: IOpenAPI = json.loads(res.read())

    class Property:
        def __init__(self, property: dict[str, str], required_inversion: bool=False) -> None:
            self.property = property
            self.property_type = property.keys()
            self.property_required = property.get('required', [])
            self.required_inversion = required_inversion
        
        def check_nullable(self, nullable: bool):
            if self.required_inversion:
                nullable = not nullable
            return '?' if nullable else ''

        def parse(self):
            def check_ref(property: dict[str, str], items:bool=False):
                property_keys = property.keys()
                if '$ref' in property_keys:
                    property_type = parse_ref(property['$ref'])
                    return property_type + '[]' if items else property_type, self.check_nullable(property.get('nullable',False))
                elif items and property.get('items'):
                    if property['items'].get('items'):
                        if 'items' not in property['items']['items']:
                            return property['items']['items'], self.check_nullable(property.get('nullable',False))
                        return check_ref(property['items']['items'], items=True), self.check_nullable(property.get('nullable',False))
                    else:
                        return property['items']['type'] + '[]', self.check_nullable(property.get('nullable',False))


                elif 'properties' in property_keys:
                    property_type = {}
                    for _property in property['properties']:
                        _property_type, nullable = check_ref(property['properties'][_property])
                        nullable = self.check_nullable(_property in self.property_required)
                        property_type[_property + nullable] = _property_type if _property_type not in ['array', 'either'] else 'any'
                    return property_type, self.check_nullable(property.get('nullable',False))
                elif 'items' in property_keys:
                    return check_ref(property['items'], items=True)
                elif 'enum' in property_keys:
                    property_type = ''
                    for enum in property['enum']:
                        property_type += f'\'{enum}\' |'
                    return property_type.rstrip('|'), self.check_nullable(property.get('nullable',False))
                else:
                    return property['type'] if property.get('type') else 'any', self.check_nullable(property.get('nullable',False))

            property_type, nullable = check_ref(self.property)

            if property_type in ['either', 'array']:
                return 'any', nullable

            return property_type, nullable

        def generate(self):
            pass

    for schema in openapi['components']['schemas']:
        for propertiy_name in openapi['components']['schemas'][schema]['properties']:
            property = openapi['components']['schemas'][schema]['properties'][propertiy_name]
            property_type, nullable = Property(property).parse()
            if schemas.get(schema) is None:
                schemas[schema] = {propertiy_name: property_type}
            else:
                schemas[schema].update({propertiy_name: property_type})
        else:
            if schemas.get(schema) is None:
                schemas[schema] = "any"
                final_content += f'''
{use_export}type {schema} = any\n
'''
            else:
                final_content += f'''
{use_export}interface {schema} {json.dumps(schemas[schema], ensure_ascii=False).replace('"', '')}
'''

    final_content += use_export + 'type Schema = {resource: {'
    for path in openapi['paths']:
        _request_content = {}
        for path_method in openapi['paths'][path]:
            _path_method = path_method.upper()
            api = openapi['paths'][path][path_method]
            
            content = ''
            parameters = api.get('parameters')
            after_path = path
            _request_content.update({_path_method: {}})
            _request_content_base = _request_content[_path_method]
            if parameters:
                
                for param in parameters:
                    nullable = '?' if param.get('required', True) is False else ''
                    if param.get('in') == 'path':  # pathじゃないやつはおかしくなる可能性ある
                        after_path = after_path.replace(f'{param["name"]}{nullable}', f':{param["name"]}').replace('{', '').replace('}', '')
                        add_or_update(_request_content_base, 'params', {param['name']: param['schema']['type']})
                    if param.get('in') == 'query':
                        add_or_update(_request_content_base, 'query', {f'{param["name"]}{nullable}': param['schema']['type']})


            request_body = api.get('requestBody')
            if request_body:
                request_type = Property(request_body['content']['application/json']['schema'], request_body.get('required', False)).parse()
                if isinstance(request_type[0], str) or len(request_type[0].keys()) > 0:
                    add_or_update(_request_content_base, 'body', request_type[0])
            responses = api.get('responses')
            if responses:
                
                for response_code in responses:
                    if response_code == '201' or '200':
                        if responses[response_code].get('content'):
                            response_type, nullable = Property(responses[response_code]['content']['application/json']['schema']).parse()
                            add_or_update(_request_content_base, 'response', response_type)

                        else:
                            add_or_update(_request_content_base, 'response', 'any')
                    else: add_or_update(_request_content_base, 'response', 'any')
                    break
            else:
                content += '        response: any'
        content += json.dumps(_request_content, ensure_ascii=False, indent=4).replace('"', '')

        final_content += f'''
"{after_path}": {content}
'''

with open('./schema.ts', mode='w', encoding='utf-8') as f:
    f.write(f'{final_content}' + '}}')
    f.close()
