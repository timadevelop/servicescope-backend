REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        "rest_framework_api_key.permissions.HasAPIKey",
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework_social_oauth2.authentication.SocialAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'saas_core.paginations.MyPagination',
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'PAGINATE_BY': 10,                 # Default to 10
    # Allow client to override, using `?page_size=xxx`.
    'PAGINATE_BY_PARAM': 'page_size',
    # Maximum limit allowed when using `?page_size=xxx`
    'MAX_PAGINATE_BY': 100,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend', ],
    'DATETIME_FORMAT': "%Y-%m-%dT%H:%M:%S%z",
    'DATETIME_INPUT_FORMATS': ["%Y-%m-%dT%H:%M:%S%z"]
}
