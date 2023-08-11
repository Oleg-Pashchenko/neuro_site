def my_custom_context(request):
    # Возвращаемый словарь будет добавлен в контекст каждой страницы
    lang = request.session.get('language', 'english')
    return {'lang': lang}