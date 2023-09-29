from urllib.parse import urlparse, urlunparse, parse_qs, urlencode


def remove_parameters_from_url(url, *args):
    parsed_url = urlparse(url)
    cleaned_query = ''

    parsed_query = parsed_url.query
    if parsed_query:
        params_to_remove = [*args]
        query_params = parsed_query.split('&')
        query_params = [param for param in query_params if param.split('=')[0] not in params_to_remove]
        cleaned_query = '&'.join(query_params)

    # Создаем новый URL-адрес без параметров
    cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, cleaned_query, parsed_url.fragment))

    return cleaned_url


def add_param_to_url(url, name, value):
    url_parts = urlparse(url)
    params = parse_qs(url_parts.query)
    params[name] = value

    # Reconstruct the URL.
    new_query_string = urlencode(params, doseq=True)
    new_url_parts = list(url_parts)
    new_url_parts[4] = new_query_string

    return urlunparse(new_url_parts)