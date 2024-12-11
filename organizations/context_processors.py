from .models import Message

def unread_messages(request):
    if request.user.is_authenticated:
        unread_messages = Message.objects.filter(recipient=request.user, is_read=False).order_by('-timestamp')[:10]
        return {'unread_messages': unread_messages, 'unread_count': unread_messages.count()}
    return {'unread_messages': [], 'unread_count': 0}