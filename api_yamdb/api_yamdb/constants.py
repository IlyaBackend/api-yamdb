VERSION = 'v1'

ROLE_USER = 'user'
ROLE_MODERATOR = 'moderator'
ROLE_ADMIN = 'admin'
MY_USER_PROFILE = 'me'
ROLE_CHOICES = [
    (ROLE_USER, 'Аутентифицированный пользователь'),
    (ROLE_MODERATOR, 'Модератор'),
    (ROLE_ADMIN, 'Администратор')
]

ROLE_MAX_LENGTH = max(len(role[0]) for role in ROLE_CHOICES)

CONFIRMATION_CODE_MAX_LENGTH = 255
EMAIL_MAX_LENGTH = 254
USERNAME_MAX_LENGTH = 150
FIRST_NAME_MAX_LENGTH = 150
LAST_NAME_MAX_LENGTH = 150

REGULAR_USERNAME = r'^[\w.@+-]+\Z'
