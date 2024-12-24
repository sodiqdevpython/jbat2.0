from .models import Message, Organizations

def unread_messages(request):
    if request.user.is_authenticated:
        unread_messages = Message.objects.filter(recipient=request.user, is_read=False).order_by('-timestamp')[:10]
        return {'unread_messages': unread_messages, 'unread_count': unread_messages.count()}
    return {'unread_messages': [], 'unread_count': 0}


def user_organization(request):
    """
    Joriy foydalanuvchining user_profile bo‘lsa,
    organization ni topib, 'organization' nomi bilan context ga qo‘shib beradi.
    """
    if not request.user.is_authenticated:
        return {}

    user_profile = getattr(request.user, 'user_profile', None)
    if not user_profile:
        return {}

    org = Organizations.objects.filter(admin=user_profile).first()
    return {'organization': org}