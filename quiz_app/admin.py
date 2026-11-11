from django.contrib import admin
from .models import Quiz, Question, Option, Participant, Moderator

admin.site.register(Moderator)
admin.site.register(Participant)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Option)
