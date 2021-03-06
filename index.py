#!/usr/bin/env python
import web
import os
import time
import config
from urllib import quote
import sys

# load config file
root = config.root
try:
    os.chdir(os.path.dirname(__file__))
except:
    pass
types = [
    ".h",".cpp",".cxx",".cc",".c",".cs",".html",".js",
    ".php",".java",".py",".rb",".as",".jpeg",".jpg",".png",
    ".gif",".ai",".psd",".mp3",".avi",".rmvb",".mp4",".wmv",
    ".mkv",".doc",".docx",".ppt",".pptx",".xls",".xlsx",
    ".zip",".tar",".gz",".7z",".rar",".pdf",".txt",".exe",
    ".apk"
]

render = web.template.render('template')

urls = (
    '/favicon.ico',"Ico",
   '/(.*).html', 'static',
    '/(.*)','Index',
)
class static:
    def GET(self, path):
        path = os.path.join(root, path + '.html')
        web.header('Content-Type','text/html')
        return open(path, 'rb').read()

class Ico:
    def GET(self):
        return open(os.path.join(os.path.join(os.path.join('static','img'),'favicon.ico'))).read()

class Index:
    def GET(self,path):
        # list all the files
        if path == '':
            list = []
            item = os.listdir(root)
            item = sorted(item, key = str.lower)
            
            for i in item:
                if i[0] == '.' or os.path.isdir(os.path.join(root, i)):
                    continue
                temp = {}
                if sys.platform == 'win32':
                    temp['name'] = i.decode('gbk')
                else:
                    temp['name'] = i

                temp['type'] = '.' + i.split('.')[-1]
                
                try:
                    types.index(temp['type'])
                except:
                    temp['type'] = "general"


                temp["time"] = time.strftime("%H:%M:%S %Y-%m-%d",
                        time.localtime(os.path.getmtime(os.path.join(root, i))))
                
                size = os.path.getsize(os.path.join(root, i))
                if size < 1024:
                    size = str(size) + ".0 B"
                elif size < 1024 * 1024:
                    size = "%0.1f KB" % (size/1024.0)
                elif size < 1024 * 1024 * 1024:
                    size = "%0.1f MB" % (size/1024.0/1024.0)
                else :
                    size = "%0.1f GB" % (size/1024.0/1024.0/1024.0)
                
                temp["size"] = size
                if sys.platform == 'win32':
                    temp["encode"] = i.decode('gbk')
                else:
                    temp["encode"] = quote(i)

                list.append(temp)
            if web.input().has_key('delete'):
                yield render.layout(list, True)
            else:
                yield render.layout(list)
        
        # return a file
        else:
            web.header('Content-Type','application/octet-stream')
            size = os.path.getsize(os.path.join(root,path))
            file = open(os.path.join(root,path), 'rb')
            if size < 1024 * 10 * 10:
                web.header('Content-disposition', 'attachment; filename=%s' % path)
                web.header('Content-Length','%s' % size)
                yield file.read()
            else:
                web.header('Transfer-Encoding','chunked')
                while True:
                    content = file.read(1024 * 10 * 10)
                    if (len(content) == 0):
                        break
                    yield content
            
    def DELETE(self,filename):
        try:
            if sys.platform != 'win32':
                filename = filename.encode('utf-8')
            os.remove(os.path.join(root,filename))
        except:
            return "success" 


    def POST(self,filename):

        # save a file to disk
        x = web.input(file={})
        
        if 'file' in x:
            filepath= x.file.filename.replace('\\','/')     # replaces the windows-style slashes with linux ones.
            filename = filepath.split('/')[-1]              # splits the and chooses the last part (the filename with extension)
            filename = unicode(filename, "utf8")
            fout = open(os.path.join(root,filename),'wb')    # creates the file where the uploaded file should be stored
            fout.write(x.file.file.read())                  # writes the uploaded file to the newly created file.
            fout.close()                                    # closes the file, upload complete.
            
        return "<script>parent.location.reload()</script>" 

# start the application
# it's adaptable to both uwsgi start & python start
app = web.application(urls,globals())
application = app.wsgifunc()

if __name__ == "__main__":
    app.run()
    
