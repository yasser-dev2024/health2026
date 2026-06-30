from uuid import uuid4


VISITOR_SESSION_KEY = 'visitor_id'


def get_visitor_id(request):
    visitor_id = request.session.get(VISITOR_SESSION_KEY)
    if not visitor_id:
        visitor_id = uuid4().hex
        request.session[VISITOR_SESSION_KEY] = visitor_id
        request.session.modified = True
    return visitor_id
