from distutils.log import log
from .models import FollowersCount, Profile,Post,Likepost,RoomMember
from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from itertools import chain
import random
from django.core import serializers
from agora_token_builder import RtcTokenBuilder
from django.forms.models import model_to_dict
import time
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.middleware.csrf import get_token

# Create your views here.

@login_required(login_url='signin')
def index (request):
    
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    user_following_list=[]
    feed=[]
    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)
    for username in user_following_list:
        feed_lists=Post.objects.filter(user=username)
        feed.append(feed_lists)

    feed_list=list(chain(*feed))
    
    all_users=User.objects.all()
    
    final_suggestions_list=[x for x in all_users if (x not in user_following)]
    final_suggestions_list.remove(user_object)
    random.shuffle(final_suggestions_list)

    username_profile=[]
    username_profile_list=[]

    for users in final_suggestions_list:
        username_profile.append(users.id)
    
    for ids in username_profile:
        profile_lists=Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)
    suggestions_username_profile_list=list(chain(*username_profile_list))

    
    
    return render(request,'index.html',{'user_profile':user_profile,'posts':feed_list,'suggestions':suggestions_username_profile_list[:4]})

@login_required(login_url='signin')
def like_post(request):
    username=request.user.username
    if request.method =='POST':
        post_id=request.body.decode('utf-8')
        like_filter=Likepost.objects.filter(post_id=post_id,username=username).first()
        if like_filter is not None:
            stats={
                'status': 'liked'
            }
        else:
            stats={
                'status': 'notliked'
            }
        return JsonResponse(stats,safe=True)

    else:    
        post_id=request.GET.get('post_id')
        post=Post.objects.get(id=post_id)
        like_filter=Likepost.objects.filter(post_id=post_id,username=username).first()
        if like_filter==None:
            new_like=Likepost.objects.create(post_id=post_id,username=username)
            new_like.save()
            post.no_of_likes=post.no_of_likes+1
            post.save()
            result={
                'count':post.no_of_likes,
                'status':'liked'
            }    
        else:
            like_filter.delete()
            post.no_of_likes=post.no_of_likes-1
            post.save()
            result={
                'count':post.no_of_likes,
                'status':'disliked'
            }
        return JsonResponse(result,safe=True)  

@login_required(login_url='signin')
def profile(request,pk):
    if request.method=='POST':
        user=request.user.username
        ide=request.POST['ide']
        post=Post.objects.get(id=ide)
        post.delete()
        return redirect('/profile/'+user)
    else:    
        user_object=User.objects.get(username=pk)
        user_profile=Profile.objects.get(user=user_object)
        user_post=Post.objects.filter(user=pk)
        user_post_length=len(user_post)

        follower=request.user.username
        user=pk

        if FollowersCount.objects.filter(follower=follower,user=user).first():
            button_text='Unfollow'
        else:
            button_text='Follow'
        user_followers=len(FollowersCount.objects.filter(user=pk))
        user_following=len(FollowersCount.objects.filter(follower=pk))

        context={
            'user_object':user_object,
            'user_profile':user_profile,
            'user_post_length':user_post_length,
            'user_post':user_post,
            'button_text':button_text,
            'user_followers':user_followers,
            'user_following': user_following,
            'followers':'followers',
            'following':'following'
        }
        return render(request,'profile.html',context)

@login_required(login_url='signin')
def follow(request):
    if request.method=='POST':
        print(request.POST['follower'])
        follower=request.POST['follower']
        user=request.POST['user']
        page=request.POST['page']

        if FollowersCount.objects.filter(follower=follower,user=user).first():
            delete_follower=FollowersCount.objects.get(follower=follower,user=user)
            delete_follower.delete()
            if page =='index':
                return redirect('/')
            else:
                return redirect('/profile/'+user)
        else:
            newfollower=FollowersCount.objects.create(follower=follower,user=user)
            newfollower.save()
            if page=='index':
                return redirect('/')
            else:
                return redirect('/profile/'+user)

    else:
        return redirect('/')

@login_required(login_url='signin')
def upload(request):
       if request.method == 'POST':
            if request.FILES.get('image_upload'):
                user = request.user.username
                image = request.FILES.get('image_upload')
                caption = request.POST['caption']
                new_post = Post.objects.create(user=user, image=image, caption=caption)
                new_post.save()
                return redirect('/')
            else:
                messages.info(request,'Please select a photo')
                return redirect('upload')
       else:
            return render(request,'upload.html')

@require_POST
@csrf_exempt
def generate_csrf_token(request):
    response = JsonResponse({'success': True})
    response.set_cookie('csrftoken', get_token(request))
    return response

@login_required(login_url='signin')
def search(request):
    user_object=User.objects.get(username=request.user.username)
    user_profile=Profile.objects.get(user=user_object)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        username=request.body.decode('utf-8')
        username_objects=User.objects.filter(username__icontains=username)
        username_profile=Profile.objects.filter(user__in=username_objects)
        post_list = serializers.serialize('json', username_profile)
        user_object_list=serializers.serialize('json',username_objects )
        post_list=json.loads(post_list)
        user_object_list=json.loads(user_object_list)
        # for users in username_object:
        #     username_profile.append(users.id)
        # for ids in username_profile:
        #     profile=Profile.objects.get(id_user=ids)
        #     username_profile_ls.append(profile)
        # print(username_profile_ls)
        i=0
        for account in user_object_list:
            post_list[i]['fields']['name']=account['fields']['username']
            i=i+1
            
        print(post_list)
        print(user_object_list)
        post_list=json.dumps(post_list)
        return HttpResponse(post_list,content_type="text/json-comment-filtered")
    elif request.method=='POST':
        username=request.POST['username']
        username_object=User.objects.filter(username__icontains=username)

        username_profile=[]
        username_profile_list=[]
        for users in username_object:
            username_profile.append(users.id)
        for ids in username_profile:
            profile=Profile.objects.get(id_user=ids)
            username_profile_list.append(profile)
      
    return render(request,'search.html',{'user_profile':user_profile,'username_profile_list':username_profile_list})

def signup(request):
    if request.method=='POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password==password2:
            if User.objects.filter(email=email).exists():
               messages.info(request,'Email taken')
               return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request,'Username Taken')
                return redirect('signup')

            else:
                user=User.objects.create_user(username=username,email=email,password=password)
                user.save()

                #log user in and redirect to settings page
                user_login= auth.authenticate(username=username,password=password)
                auth.login(request,user_login)

                #create a profile object for the new user

                user_model=User.objects.get(username=username)
                new_profile=Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('setting')
        else:
            messages.info(request,'Password not matching')
            return redirect('signup')        
    else:
        return render(request,'signup.html')

def signin(request):

    if request.method =='POST':
        username=request.POST['username']
        password=request.POST['password']

        user=auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(request,user)
            return redirect('/')
        else:
            messages.info(request,'Credentials invalid')
            return redirect('signin')

    else:
        return render(request,'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(login_url='signin')
def setting(request):
    user_object=User.objects.get(username=request.user.username)
    user_profile=Profile.objects.get(user=request.user)
    if request.method=='POST':
        if request.FILES.get('image')==None:
            image=user_profile.profileimg
            username=request.POST['name']
            location=request.POST['location']
            bio=request.POST['bio']
            
            user_object.username=username
            user_profile.profileimg=image
            user_profile.bio=bio
            user_profile.location=location
            user_profile.save()
            user_object.save()
        if request.FILES.get('image')!=None:
            username=request.POST['name']
            image=request.FILES.get('image')
            location=request.POST['location']
            bio=request.POST['bio']

            user_object.username=username
            user_profile.profileimg=image
            user_profile.bio=bio
            user_profile.location=location
            user_profile.save()
            user_object.save()
        return redirect('setting')
    return render(request,'setting.html',{'user_profile':user_profile})

@login_required(login_url='signin')
def createandgettoken(request):
    appId='bb17f5192b644411a6489891e1279dda'
    appCertificate='b0a2d3c700ae42388ee3a020a255c9fa'
    username=request.user.username
    channelName=request.user.username+"121"
    uid= random.randint(1,230)
    expirationTimeinsecs=3600*24
    currentTimeStamp=time.time()
    privilegeExpiredTs= currentTimeStamp+expirationTimeinsecs
    role=1
    token= RtcTokenBuilder.buildTokenWithUid(appId, appCertificate, channelName, uid, role, privilegeExpiredTs)
    return JsonResponse({'room':channelName,'name':username, 'token':token,'uid':uid},safe=False)

@login_required(login_url='signin')
def room(request):
    return render(request,'room.html')

@login_required(login_url='signin')
def createMember(request):
    name=request.GET.get('name')
    uid=request.GET.get('UID')
    room=request.GET.get('room_name')
    member=RoomMember.objects.create(name=name,uid=uid,room_name=room)
    member.save()
    return JsonResponse({'name':member.name}, safe=False)


@login_required(login_url='signin')
def getMember(request):
    uid = request.GET.get('UID')
    room_name = request.GET.get('room_name')

    member = RoomMember.objects.get(
        uid=uid,
        room_name=room_name,
    )
    name = member.name
    return JsonResponse({'name':member.name}, safe=False)

@login_required(login_url='signin')
def deleteMember(request):
    name=request.GET.get('name')
    uid=request.GET.get('UID')
    room=request.GET.get('room_name')
    member=RoomMember.objects.get(name=name,uid=uid,room_name=room)
    member.delete()
    return JsonResponse('Member deleted', safe=False)

@login_required(login_url='signin')
def followdisplay(request):
    if request.GET.get('val') == 'followers':
        followers=FollowersCount.objects.filter(user=request.GET.get('user'))
        return render(request,'followering.html',{'followers':followers,'title':'Followers'})
    else:
        following=FollowersCount.objects.filter(follower=request.GET.get('user'))
        return render(request,'followering.html',{'following':following,'title':'Following'})





