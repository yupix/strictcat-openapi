import json

from type import IOpenAPI

final_content = ''
schemas = {}

def parse_ref(ref: str):
    return ref.split('/')[-1]



with open('./openapi.json', mode='r', encoding='utf-8') as f:
    openapi: IOpenAPI = json.load(f)

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
                        print(nullable, _property)
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

            print(property_type)
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
export type {schema} = any
'''
            else:
                final_content += f'''
export interface {schema} {json.dumps(schemas[schema], ensure_ascii=False).replace('"', '')}
'''

    final_content += 'export type Schema = {resource: {'
    for path in openapi['paths']:
        for path_method in openapi['paths'][path]:
            api = openapi['paths'][path][path_method]
            
            content = ''
            parameters = api.get('parameters')
            after_path = path
            if parameters:
                for param in parameters:
                    after_path = after_path.replace(f'{param["name"]}', f':{param["name"]}').replace('{', '').replace('}', '')
                content += 'params: ' + json.dumps({i['name']: i['schema']['type'] for i in parameters}, ensure_ascii=False).replace('"', '') + '\n'
            request_body = api.get('requestBody')
            if request_body:
                request_type = Property(request_body['content']['application/json']['schema'], request_body.get('required', False)).parse()
                if len(request_type[0].keys()) > 0:
                    content += f'body: ' + json.dumps(request_type[0], ensure_ascii=False).replace('"', '') + '\n'
            
            responses = api.get('responses')
            if responses:
                
                for response_code in responses:
                    if response_code == '201' or '200':
                        if responses[response_code].get('content'):
                            response_type, nullable = Property(responses[response_code]['content']['application/json']['schema']).parse()
                            content += 'response: ' + json.dumps(response_type, ensure_ascii=False).replace('"', '')

                        else:
                            content += 'response: any'
                    else: content += 'response: any'
                    break
            else:
                content += 'response: any'

        final_content += f'''
"{after_path}": {{
    {path_method.upper()}: {{
        {content}
    }}
}}
'''

with open('./schema.ts', mode='w', encoding='utf-8') as f:
    f.write(f'{final_content}' + '}}')
    f.close()