import json

from type import IOpenAPI

final_content = ''
schemas = {}

with open('./openapi.json', mode='r', encoding='utf-8') as f:
    openapi: IOpenAPI = json.load(f)
    for schema in openapi['components']['schemas']:
        print(schema)
        for propertiy in openapi['components']['schemas'][schema]['properties']:
            if schemas.get(schema) is None:
                schemas[schema] = {
                    propertiy: openapi['components']['schemas'][schema]['properties'][propertiy]['type']
                }
            else:
                schemas[schema].update({
                    propertiy: openapi['components']['schemas'][schema]['properties'][propertiy]['type']
                })
        else:
            if schemas.get(schema) is None:
                schemas[schema] = "any"
                final_content += f'''
type {schema} = any
'''
            else:
                final_content += f'''
interface {schema} {schemas[schema]}
'''
            print(schemas, schema)

    final_content += 'type Schema = {resource: {'
    for path in openapi['paths']:
        for path_method in openapi['paths'][path]:
            api = openapi['paths'][path][path_method]
            
            print()
            content = ''
            parameters = api.get('parameters')
            if parameters:
                content += 'params: ' + json.dumps({i['name']: i['schema']['type'] for i in parameters}, ensure_ascii=False).replace('"', '') + '\n'
            request_body = api.get('requestBody')
            if request_body:
                content += f'body:' + request_body['content']['application/json']['schema'].get('$ref').split('/')[-1]

        final_content += f'''
"{path}": {{
    {path_method.upper()}: {{
        {content}
    }}
}}
'''

with open('./schema.ts', mode='w', encoding='utf-8') as f:
    f.write(f'{final_content}' + '}}')
    f.close()