from django.contrib import admin
from .models import Profile, Education, WorkExperience

admin.site.register(Profile)
admin.site.register(Education)
admin.site.register(WorkExperience)
from .models import Conversation, Message, CandidateEmailLog

admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(CandidateEmailLog)
