from aiohttp import web

async def upload_file(request: web.Request) -> web.Response:
    if not request.content_type.startswith('multipart/'):
        return web.json_response(
            {'error':'Ожидаемые данные multipart/form-data'}, status=400)
    
    reader = await request.multipart()
    size = 0
    name = None

    while True:
        field = await reader.next()
        if field is None:
            break

        if field.filename:
            name = field.filename

            while True:
                chunk = await field.read_chunk()
                if not chunk:
                    break
                size += len(chunk)

        else: await field.release()

    if name is None:
        return web.json_response({
            'error': 'Файл не найден'
        }, status=200)

    return web.json_response({
        'Название файла': name,
        'Размер в байтах': size,
        'Размер в кбайтах': round(size / 1024, 2),
        'Размер в мбайтах': round(size / (1024*1024), 2),
    }, status=200)

if __name__ == '__main__':
    app = web.Application()
    app.add_routes([web.post('/api/upload/', upload_file)])
    web.run_app(app, host='127.0.0.1', port=8080)