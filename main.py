import json

from type import IOpenAPI

final_content = ''
schemas = {}

with open('./openapi.json', mode='r', encoding='utf-8') as f:
    openapi: IOpenAPI = json.load(f)
    for schema in openapi['components']['schemas']:
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
interface {schema} {json.dumps(schemas[schema], ensure_ascii=False).replace('"', '')}
'''

    final_content += 'type Schema = {resource: {'
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
                content += f'body:' + request_body['content']['application/json']['schema'].get('$ref').split('/')[-1] + '\n'
            responses = api.get('responses')
            if responses:
                for response_code in responses:
                    if response_code == '201':
                        if responses['201'].get('content'):
                            content += 'response: ' + responses['201']['content']['application/json']['schema'].get('$ref').split('/')[-1]
                        else:
                            content += 'response: any'
                    else: content += 'response: any'
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