from django.http import JsonResponse
from sign.models import Event, Guest
from django.core.exceptions import ValidationError,ObjectDoesNotExist
from django.db.utils import IntegrityError
import time
from django.contrib import auth as django_auth
import base64
import time, hashlib

# 用户认证
def user_auth(request):
    get_http_auth = request.META.get('HTTP_AUTHORIZATION', b'')
    auth = get_http_auth.split()
    try:
        auth_parts = base64.b64decode(auth[1]).decode('utf-8').partition(':')
    except IndexError:
        return "null"
    username, password = auth_parts[0], auth_parts[2]
    user = django_auth.authenticate(username=username, password=password)
    if user is not None:
        django_auth.login(request, user)
        return "Success"
    else:
        return "Fail"

# 添加发布会接口
def add_event(request):
    # 增加签名和时间戳
    sign_result = user_sign()
    if sign_result == "error":
        return JsonResponse({'status':10011,'message':'request error'})
    elif sign_result == "sign null":
        return JsonResponse({'status':10012,'message':'user sign null'})
    elif sign_result == "timeout":
        return JsonResponse({'status':10013,'message':'user sign timeout'})
    elif sign_result == "sign fail":
        return JsonResponse({'status': 10014, 'message': 'user sign error'})

    eid = request.POST.get('eid','')
    name = request.POST.get('name','')
    limit = request.POST.get('limit','')
    status = request.POST.get('status','')
    address = request.POST.get('address','')
    start_time = request.POST.get('start_time','')

    if eid == '' or name == '' or limit == '' or address == '' or start_time == '':
        return JsonResponse({'status':10021,'message':'parameter error'})

    result = Event.objects.filter(id=eid)
    if result:
        return JsonResponse({'status':10022,'message':'event id already exists'})

    result = Event.objects.filter(name=name)
    if result:
        return JsonResponse({'status':10023,'message':'event name already exits'})

    if status == '':
        status = 1

    try:  # 将数据插入数据库，若有日期格式错误，则抛出ValidationError异常
        Event.objects.create(id=eid,name=name,limit=limit,address=address,status=int(status),start_time=start_time)
    except ValidationError as e:
        error = 'start_time format error.It must be in YYYY-MM-DD HH:MM:SS format.'
        return JsonResponse({'status':10024,'message':'error'})

    return JsonResponse({'status':200,'message':'add event success.'})

# 查询发布会接口
def get_event_list(request):
    auth_result = user_auth(request) # 调用认证函数
    if auth_result == "null":
        return JsonResponse({'status':10011,'message':'user auth null'})
    if auth_result == 'fail':
        return JsonResponse({'status':10012,'message':'user auth fail'})
    eid = request.GET.get("eid","")
    name = request.GET.get("name","")

    if eid == '' and name =='':
        return JsonResponse({'status':10021,'message':'parameter error.'})

    if eid != '':
        event = {}
        try:
            result = Event.objects.get(id=eid)
        except ObjectDoesNotExist:
            return JsonResponse({'status':10022,'message':'query result is empty'})
        else:
            event['name'] = result.name
            event['limit'] = result.limit
            event['status'] = result.status
            event['address'] = result.address
            event['start_time'] = result.start_time
            return JsonResponse({'status':200,'message':'success','data':event})

    if name != '':
        datas = []
        results = Event.objects.filter(name__contains=name)
        if results:
            for r in results:
                event = {}
                event['name'] = r.name
                event['limit'] = r.limit
                event['status'] = r.status
                event['address'] = r.address
                event['start_time'] = r.start_time
                datas.append(event)
            return JsonResponse({'status':200,'message':'success','data':datas})
        else:
            return JsonResponse({'status':10022,'message':'query result is empty'})


# 添加嘉宾接口
def add_guest(request):
    eid = request.POST.get('eid','')
    # get('sth','default_value')sth表示要获取的内容，对应到字典中的key，default_value则对应到字典中的value，
    # default_vaule的意义是：当sth不存在时，显示默认值default_value.
    realname = request.POST.get('realname','')
    phone = request.POST.get('phone','')
    email = request.POST.get('email','')

    if eid == '' or realname == '' or phone == '' or email == '':
        return JsonResponse({'status':10021,'message':'parameter error.'})

    result = Event.objects.filter(id=eid)
    if not result:
        return JsonResponse({'status':10022,'message':'event id null.'})

    result = Event.objects.get(id=eid).status
    if not result:
        return JsonResponse({'status':10023,'message':'event status is not available.'})

    event_limit = Event.objects.get(id=eid).limit
    guest_limit = Guest.objects.filter(event_id=eid)  # 根据发布会id获取已添加的嘉宾数

    if len(guest_limit) >= event_limit:
        return JsonResponse({'status':10024,'message':'event number is full.'})

    event_time = Event.objects.get(id=eid).start_time
    etime = str(event_time).split(".")[0]
    print("用.分割完的字符串类型的时间时啥样子？",etime)
    timeArray = time.strptime(etime,"%Y-%m-%d %H:%M:%S")
    e_time = int(time.mktime(timeArray))

    now_time = str(time.time())
    ntime = now_time.split(".")[0]
    n_time = int(ntime)

    if n_time >= e_time:
        return JsonResponse({'status':10025,'message':'event has started.'})

    try:
        Guest.objects.create(realname=realname,phone=int(phone),email=email,sign=0,event_id=int(eid))
    except IntegrityError:
        return JsonResponse({'status':10026,'message':'the event guest phone number repeat.'})

    return JsonResponse({'status':200,'message':'add guest success.'})

# 嘉宾查询接口
def get_guest_list(request):
    eid = request.GET.get("eid","")
    phone = request.GET.get("phone","")

    if eid =='':
        return JsonResponse({'status':10021,'message':'eid cannot be empty'})

    if eid !='' and phone == '':
        datas = []
        results = Guest.objects.filter(event_id=eid)
        if results:
            for r in results:
                guest = {}
                guest['realname'] = r.realname
                guest['phone'] = r.phone
                guest['email'] = r.email
                guest['sign'] = r.sign
                datas.append(guest)
            return JsonResponse({'status':200,'message':'success.','data':datas})
        else:
            return JsonResponse({'status':10022,'message':'query result is empty'})

        if eid != '' and phone != '':
            guest = {}
            try:
                result = Guest.objects.get(phone=phone,event_id=eid)
            except ObjectDoesNotExist:
                return JsonResponse({'status':10022,'message':'query result is empty'})
            else:
                guest['realname'] = result.realname
                guest['phone'] = result.phone
                guest['email'] = result.email
                guest['sign'] = result.sign
                return JsonResponse({'status':200,'message':'success','data':guest})


# 嘉宾签到接口
def user_sign(request):
    eid =  request.POST.get('eid','')       # 发布会id
    phone =  request.POST.get('phone','')   # 嘉宾手机号

    if eid =='' or phone == '':
        return JsonResponse({'status':10021,'message':'parameter error'})

    result = Event.objects.filter(id=eid)
    if not result:
        return JsonResponse({'status':10022,'message':'event id null'})

    result = Event.objects.get(id=eid).status
    if not result:
        return JsonResponse({'status':10023,'message':'event status is not available'})

    event_time = Event.objects.get(id=eid).start_time     # 发布会时间
    timeArray = time.strptime(str(event_time), "%Y-%m-%d %H:%M:%S")
    e_time = int(time.mktime(timeArray))

    now_time = str(time.time())          # 当前时间
    ntime = now_time.split(".")[0]
    n_time = int(ntime)

    if n_time >= e_time:
        return JsonResponse({'status':10024,'message':'event has started'})

    result = Guest.objects.filter(phone=phone)
    if not result:
        return JsonResponse({'status':10025,'message':'user phone null'})

    result = Guest.objects.filter(phone=phone,event_id=eid)
    if not result:
        return JsonResponse({'status':10026,'message':'user did not participate in the conference'})

    result = Guest.objects.get(event_id=eid,phone=phone).sign
    if result:
        return JsonResponse({'status':10027,'message':'user has sign in'})
    else:
        Guest.objects.filter(phone=phone).update(sign='1')
        return JsonResponse({'status':200,'message':'sign success'})

def user_sign(request):
    if request.method == 'POST':
        client_time = request.POST.get('time','') # 客户端时间戳
        client_sign = request.POST.get('sign','') # 客户端签名
    else:
        return "error"

    if client_time == '' or client_sign == '':
        return "sign null"

    # 服务器时间
    now_time = time.time()
    server_time = str(now_time).split('.')[0]  # 将时间戳转化为字符串类型，并截取小数点前的时间
    # 获取时间差
    time_difference = int(server_time) - int(client_time)
    if time_difference >= 60:
        return "timeout"

    # 签名检查
    md5 = hashlib.md5()
    sign_str = client_time + "&Guest-Bugmaster"
    sign_bytes_utf8 = sign_str.encode(encoding="utf-8")
    md5.update(sign_bytes_utf8)
    server_sign = md5.hexdigest()

    if server_sign != client_sign:
        return "sign fail"
    else:
        return "sign success"