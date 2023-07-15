#custom

from django.core.wsgi import get_wsgi_application


from whitenoise import WhiteNoise
from .settings import STATIC_ROOT


application = get_wsgi_application()
application = WhiteNoise(application, root=STATIC_ROOT)
