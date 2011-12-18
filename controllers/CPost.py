#!/usr/bin/env python
#coding:utf-8
from config.Runtime import *
from config.Globals import *
from models import MPost
from models.MLanguage import MLanguage
import time

class PostAdd:
    def GET(self):
        return render.TIndex(MLanguage.GetAllLangs())

    def POST(self):
        interval = int(time.time()) - session['Status']['LastPublishTime']
        if interval < GLOBAL_DEFAULT_POST_PUBLISH_INTERVAL:
            return render.TMessage("<span class='msg-error'>写的也忑快了吧，慢点儿提交吧，请 %d 秒之后重新尝试</span><br /><a href='javascript:history.go(-1);'>返回之前的页面</a>" % (GLOBAL_DEFAULT_POST_PUBLISH_INTERVAL - interval))
            
        code_title = web.input()['code_title'].strip()
        code_priviledge = int(web.input()['code_priviledge'].strip())
        code_content = web.input()['code_content'].strip()
        code_language_type = int(web.input()['code_language_type'].strip())
        
        if session['UserID'] == -1 and code_priviledge == GLOBAL_PRIVILEDGE_PRIVATE:
            return render.TMessage("<span class='msg-error'>匿名用户不允许将代码设置为仅自己可见状态</span><br /><a href='javascript:history.go(-1);'>返回之前的页面</a>")

        if not len(code_content):
            return render.TMessage("<span class='msg-error'>外面PM2.5这么严重, 宅在家里至少写点代码再提交吧</span><br /><a href='javascript:history.go(-1);'>返回之前的页面</a>")

        if not MLanguage.IsSupportLang(code_language_type):
            return render.TMessage("<span class='msg-error'>未知的语言类型</span><br /><a href='javascript:history.go(-1);'>返回之前的页面</a>")

        if not len(code_title):
            code_title = GLOBAL_DEFAULT_POST_TITLE

        post = {
            'user_id':session['UserID'],
            'priviledge':code_priviledge,
            'language_type':code_language_type,
            'title':code_title,
            'content':code_content,
            'publish_time':int(time.time()),
            'last_edit_time':int(time.time())
            }

        r = MPost.Post.Insert2DB(post)
        if r['Status'] == -1:
            return render.TMessage("<span class='msg-error'>操作失败: [" + r["ErrorMsg"]  + "]。请修正错误后重新尝试。</span><br /><a href='javascript:history.go(-1)'>返回之前的页面</a>")

        #更新一些状态
        session['Status']['LastPublishTime'] = int(time.time())

        short_url = "http://snippet-code.com/" + r['link']
        msg = "<div style='margin-top:15px;'>快使用该链接与大家分享代码吧<input type='text' class='shorturl-input' value='" + short_url + "' /></div>"
        msg += "<div style='margin-top:5px;'>"
        msg += "您还可以执行以下操作" 
        msg += "</div>"
        msg += "<div style='margin-top:5px;'>"
        msg += "<a class='button-a' href='/post/view/"+ str(r['post_id'])  + "' target='_blank'>查看</a>"
        msg += "<a class='button-a' href='/post/genimg/"+ str(r['post_id'])  + "' target='_blank'>生成图片</a>"
        if session['UserID'] != -1:
            msg += "<a class='button-a' href='/post/edit/"+ str(r['post_id'])  + "' target='_blank'>编辑</a>"
            msg += "<a class='button-a' href='/post/del/"+ str(r['post_id'])  + "' target='_blank'>删除</a>"
        msg += "<a class='button-a' href='/post/add' target='_blank'>新建代码片段</a>"
        msg += "</div>"
        return render.TMessage("<span class='msg-success'>发布成功啦.</span><br />" + msg)


class PostView:
    def GET(self, post_id):
        try:
            pid = int(post_id)
        except:
            return render.TMessage("<span class='msg-error'>参数传递异常</span><br /><br /><a href='/'>返回主页</a>")

        post = MPost.Post.QueryDB(post_id = pid)
        if not post:
            return render.TMessage("<span class='msg-error'>失败: [查看该代码片段发生异常]</span><br /><a href='/'>返回主页</a>")

        #检查查看的权限
        if post['priviledge'] == GLOBAL_PRIVILEDGE_PRIVATE:
            if session['UserID'] != post['user_id']:
                return render.TMessage("<span class='msg-error'>对不起，您没有权限查看此代码片段</span><br /><a href='/'>返回主页</a>")
        
        return render.TPostView(post)



