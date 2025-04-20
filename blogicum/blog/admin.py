from django.contrib import admin
from .models import Category
from .models import Location
from .models import Post

admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Post)
