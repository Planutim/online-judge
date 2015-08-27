from django.http import HttpResponse

from judge.models import Judge
from judge.rabbitmq.connection import vhost


def auth_user(request):
    return ['deny', 'allow'][Judge.objects.filter(name=request.GET.get('username'),
                                                  auth_key=request.GET.get('password')).exists()]


def auth_vhost(request):
    return HttpResponse(['deny', 'allow'][request.GET.get('vhost') == vhost and
                                          Judge.objects.filter(name=request.GET.get('username')).exists()])


EXCHANGE_PERMS = {
    'broadcast': {'read'},
    'submission-response': {'write'},
    'ping': {'write'}
}


def auth_resource(request):
    if (not Judge.objects.filter(name=request.GET.get('username')).exists() or
            request.GET.get('vhost') != vhost):
        return HttpResponse('deny')
    type = request.GET.get('resource')
    name = request.GET.get('name')
    permission = request.GET.get('permission')
    if type == 'queue':
        if name.startswith('amq.gen'):
            return HttpResponse(['deny', 'allow'][permission in {'read', 'write', 'configure'}])
        elif name.startswith('submission'):
            return HttpResponse(['deny', 'allow'][permission == 'read'])
        else:
            return HttpResponse('deny')
    elif type == 'exchange':
        return HttpResponse(['deny', 'allow'][permission in EXCHANGE_PERMS.get(name, ())])
    else:
        return HttpResponse('deny')
